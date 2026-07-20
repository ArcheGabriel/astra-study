"""
Cross Encoder based reranker implementation.

This module implements the production-ready reranker used by Astra Study.

The reranker receives the candidates returned by Hybrid Retrieval, computes semantic relevance scores using a Cross Encoder model,
and returns a reranked list.

Unlike embedding models, a Cross Encoder jointly encodes the (query, document) pair, making it significantly more accurate for relevance estimation.
"""

from __future__ import annotations

import logging
import time
from typing import Final

import torch
from sentence_transformers import CrossEncoder

from app.config.settings import settings
from app.reranking.base import BaseReranker
from app.reranking.exceptions import (
    CandidateFormatError,
    EmptyCandidateError,
    InvalidQueryError,
    InvalidTopKError,
    ModelLoadError,
    PredictionError,
)
from app.reranking.models import (
    RerankedChunk,
    RerankingResult,
)
from app.search.hybrid.models import HybridSearchResult

logger = logging.getLogger(__name__)


class CrossEncoderReranker(BaseReranker):
    """
    Cross Encoder implementation of the reranker.

    The model scores every (query, document) pair independently
    and returns a relevance score.

    The scores are then used to reorder the retrieved candidates.

    Notes
    -----
    This class is thread-safe after initialization.

    The model is loaded only once during construction.
    """

    DEFAULT_BATCH_SIZE: Final[int] = 32

    DEFAULT_MAX_LENGTH: Final[int] = 512

    def __init__(
        self,
        *,
        model_name: str | None = None,
        device: str | None = None,
        batch_size: int | None = None,
        max_length: int | None = None,
    ) -> None:
        """
        Initialize the reranker.

        Parameters
        ----------
        model_name:
            HuggingFace model identifier.

        device:
            cpu / cuda / cuda:0 / mps

        batch_size:
            Batch size used during inference.

        max_length:
            Maximum sequence length.
        """

        self._model_name = (
            model_name
            or settings.RERANKER_MODEL
        )

        self._device = (
            device
            or self._detect_device()
        )

        self._batch_size = (
            batch_size
            or getattr(
                settings,
                "RERANKER_BATCH_SIZE",
                self.DEFAULT_BATCH_SIZE,
            )
        )

        self._max_length = (
            max_length
            or getattr(
                settings,
                "RERANKER_MAX_LENGTH",
                self.DEFAULT_MAX_LENGTH,
            )
        )

        logger.info(
            (
                "Loading Cross Encoder '%s' "
                "on '%s' "
                "(batch_size=%d, max_length=%d)"
            ),
            self._model_name,
            self._device,
            self._batch_size,
            self._max_length,
        )

        start = time.perf_counter()

        try:

            self._model = CrossEncoder(
                model_name=self._model_name,
                device=self._device,
                max_length=self._max_length,
            )

        except Exception as exc:

            raise ModelLoadError(
                model_name=self._model_name,
                reason=str(exc),
            ) from exc

        elapsed = time.perf_counter() - start

        logger.info(
            "Cross Encoder loaded successfully "
            "in %.2f seconds.",
            elapsed,
        )
    
    @staticmethod
    def _detect_device() -> str:
        """
        Automatically determine the best available inference device.

        Priority
        --------
        1. CUDA
        2. Apple Metal (MPS)
        3. CPU
        """

        if torch.cuda.is_available():
            return "cuda"

        if (
            hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        ):
            return "mps"

        return "cpu"

    @property
    def model_name(self) -> str:
        """
        Name of the underlying HuggingFace model.
        """

        return self._model_name

    @property
    def device(self) -> str:
        """
        Device used for inference.
        """

        return self._device

    @property
    def batch_size(self) -> int:
        """
        Batch size used during inference.
        """

        return self._batch_size

    @property
    def max_length(self) -> int:
        """
        Maximum sequence length accepted by the model.
        """

        return self._max_length

    @property
    def model(self) -> CrossEncoder:
        """
        Returns the loaded CrossEncoder instance.

        This property is primarily useful for testing.
        """

        return self._model

    def _validate_query(
        self,
        query: str,
    ) -> None:
        """
        Validate the user query before inference.
        """

        if not isinstance(query, str):
            raise InvalidQueryError()

        if not query.strip():
            raise InvalidQueryError()

    def _validate_top_k(
        self,
        top_k: int,
    ) -> None:
        """
        Validate the requested top_k value.
        """

        if top_k <= 0:
            raise InvalidTopKError(top_k)

    def _validate_candidates(
        self,
        candidates: list[HybridSearchResult],
    ) -> None:
        """
        Validate retrieval candidates before reranking.
        """

        if not candidates:
            raise EmptyCandidateError()

        for candidate in candidates:

            if candidate is None:
                raise CandidateFormatError(
                    "Candidate cannot be None."
                )

            if not isinstance(candidate.text, str):
                raise CandidateFormatError(
                    "Candidate text must be a string."
                )

            if not candidate.text.strip():
                raise CandidateFormatError(
                    "Candidate text cannot be empty."
                )
    
    def _prepare_sentence_pairs(
        self,
        *,
        query: str,
        candidates: list[HybridSearchResult],
    ) -> list[tuple[str, str]]:
        """
        Convert retrieved candidates into CrossEncoder inputs.

        Each candidate becomes a tuple:

        (query, document_text)

        Returns
        -------
        list[tuple[str, str]]
        """

        return [
            (
                query,
                candidate.text,
            )
            for candidate in candidates
        ]

    def _sort_results(
        self,
        *,
        candidates: list[HybridSearchResult],
        scores: list[float],
    ) -> list[RerankedChunk]:
        """
        Combine retrieval results with reranker scores and
        sort them in descending order.
        """

        ranked_pairs = sorted(
            zip(candidates, scores, strict=True),
            key=lambda pair: pair[1],
            reverse=True,
        )

        reranked: list[RerankedChunk] = []

        for rank, (candidate, score) in enumerate(
            ranked_pairs,
            start=1,
        ):
            reranked.append(
                RerankedChunk(
                    result=candidate,
                    reranker_score=float(score),
                    rank=rank,
                )
            )

        return reranked
    
    def rerank(
        self,
        *,
        query: str,
        candidates: list[HybridSearchResult],
        top_k: int,
    ) -> RerankingResult:
        """
        Rerank retrieved candidates using the Cross Encoder.

        Parameters
        ----------
        query:
            User query.

        candidates:
            Retrieved candidates from Hybrid Search.

        top_k:
            Number of candidates to return.

        Returns
        -------
        RerankingResult
        """

        self._validate_query(query)
        self._validate_top_k(top_k)
        self._validate_candidates(candidates)

        logger.debug(
            "Starting reranking for %d candidates.",
            len(candidates),
        )
        logger.debug(
            "Requested top_k=%d",
            top_k,
        )

        sentence_pairs = self._prepare_sentence_pairs(
            query=query,
            candidates=candidates,
        )

        start = time.perf_counter()

        try:

            scores = self.model.predict(
                sentence_pairs,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
            )

        except Exception as exc:
            raise PredictionError(
                reason=str(exc),
            ) from exc

        elapsed = time.perf_counter() - start

        logger.debug(
            "Cross Encoder inference completed in %.3f seconds.",
            elapsed,
        )

        scores = list(map(float, scores))

        reranked = self._sort_results(
            candidates=candidates,
            scores=scores,
        )

        reranked = reranked[:top_k]
        
        if not reranked:
            logger.warning(
                "Reranker returned no candidates."
            )

        else:
            logger.debug(
                "Highest reranker score: %.4f",
                reranked[0].reranker_score,
            )

        logger.info(
            "Reranking completed. Returned %d/%d candidates.",
            len(reranked),
            len(candidates),
        )

        return RerankingResult(
            query=query,
            total_candidates=len(candidates),
            returned_candidates=len(reranked),
            results=tuple(reranked),
        )