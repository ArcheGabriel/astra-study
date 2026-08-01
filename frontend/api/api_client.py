from __future__ import annotations

from typing import Any

import requests


class ApiException(Exception):
    """
    Raised when the backend returns an error response.
    """

    pass


# Generation requests (RAG pipeline + GPT call) may take several minutes.
GENERATION_TIMEOUT = 600


class ApiClient:
    """
    Base HTTP client used by all frontend services.
    """

    def __init__(
        self,
        base_url: str,
        access_token: str | None = None,
        timeout: int = 300,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
        }

        if self.access_token:
            headers["Authorization"] = (
                f"Bearer {self.access_token}"
            )

        return headers

    def set_access_token(
        self,
        token: str | None,
    ) -> None:
        self.access_token = token

    def clear_access_token(self) -> None:
        self.access_token = None

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        files=None,
        stream: bool = False,
    ) -> requests.Response:
        """
        Execute an HTTP request.
        """

        kwargs = {
            "headers": self.headers,
            "timeout": self.timeout,
            "params": params,
            "stream": stream,
        }

        if files is not None:
            kwargs["files"] = files
        elif json is not None:
            kwargs["json"] = json

        try:
            response = requests.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ApiException(
                f"Unable to connect to Astra Study backend: {exc}"
            ) from exc

        return response

    def _handle_json_response(
        self,
        response: requests.Response,
    ) -> Any:

        if response.status_code == 204:
            return None

        try:
            payload = response.json()
        except ValueError as exc:
            raise ApiException(
                "Server returned an invalid JSON response."
            ) from exc

        if response.ok:
            return payload

        if isinstance(payload, dict):

            if "detail" in payload:
                raise ApiException(str(payload["detail"]))

            if "message" in payload:
                raise ApiException(str(payload["message"]))

        raise ApiException(
            f"Request failed ({response.status_code})."
        )

    def get(
        self,
        endpoint: str,
        *,
        params: dict | None = None,
    ) -> Any:

        response = self._request(
            "GET",
            endpoint,
            params=params,
        )

        return self._handle_json_response(
            response,
        )

    def get_bytes(
        self,
        endpoint: str,
    ) -> bytes:
        """
        Download binary data.
        """

        response = self._request(
            "GET",
            endpoint,
        )

        if not response.ok:

            try:
                payload = response.json()

                raise ApiException(
                    payload.get(
                        "detail",
                        payload.get(
                            "message",
                            "Download failed.",
                        ),
                    )
                )

            except ValueError:

                raise ApiException(
                    "Download failed."
                )

        return response.content

    def post(
        self,
        endpoint: str,
        *,
        json: dict | None = None,
        files=None,
    ) -> Any:

        response = self._request(
            "POST",
            endpoint,
            json=json,
            files=files,
        )

        return self._handle_json_response(
            response,
        )

    def stream_post(
        self,
        endpoint: str,
        *,
        json: dict,
    ):
        """
        Open a Server-Sent Events POST request.
        """

        response = self._request(
            "POST",
            endpoint,
            json=json,
            stream=True,
        )

        if response.ok:
            return response

        self._handle_json_response(response)
        raise ApiException("Streaming request failed.")

    def patch(
        self,
        endpoint: str,
        *,
        json: dict,
    ) -> Any:

        response = self._request(
            "PATCH",
            endpoint,
            json=json,
        )

        return self._handle_json_response(
            response,
        )

    def delete(
        self,
        endpoint: str,
    ) -> None:

        response = self._request(
            "DELETE",
            endpoint,
        )

        self._handle_json_response(
            response,
        )
