# Chunking evaluation artifacts (Stage 5)

Structural before/after evaluation of the chunking pipeline, produced by
`evaluation/chunking_report.py`. **Offline only** — no Qdrant, no DB, no
application state is touched.

## Definitions

| Term | Meaning |
|------|---------|
| **pre** / **baseline** | repository state at commit `888fc8c` (pre-chunking-refactor) |
| **stage14** | Stage 5 frozen tree: approved Stage 1–4 + the two review-gate fixes |
| **stage6** | current working tree: Stage 1–5 + Stage 6 structural-atomicity (ContentSegment) |
| corpus | `tests/test_documents/{Attention,LLM,apjspeech}.pdf` |

`comparison_stage5_to_stage6.txt` is the Stage 6 primary comparison;
`comparison_pre_to_stage6.txt` is historical context vs the pre-refactor tree.

The Docling extraction is run **once** (working-tree code) and frozen to
`blocks_<doc>.json`, then the identical blocks are chunked by each tree. This
isolates the comparison to chunking behaviour and removes Docling/OCR
run-to-run noise.

## Files

- `blocks_<doc>.json` — frozen Docling extraction (source blocks). Input to
  both trees. `blocks_LLM.json` is ~1 MB; the rest are small.
- `baseline_<doc>.json` / `.txt` — report for commit `888fc8c`
- `stage14_<doc>.json` / `.txt` — report for the current working tree
- `comparison.json` / `comparison.txt` — direct metric deltas

## Reproduce

```bash
# 1. (re)extract — needs the Docling models; slow
uv run python -m evaluation.chunking_report extract \
    --doc tests/test_documents/Attention.pdf --out evaluation/artifacts/blocks_Attention.json

# 2. analyze the current tree
uv run python -m evaluation.chunking_report analyze \
    --blocks evaluation/artifacts/blocks_Attention.json \
    --out evaluation/artifacts/stage14_Attention.json \
    --out-text evaluation/artifacts/stage14_Attention.txt --runs 3

# 3. analyze the pre-refactor tree (throwaway worktree)
git worktree add --detach /tmp/wt_pre 888fc8c
cp evaluation/chunking_report.py /tmp/wt_pre/evaluation/
cp .env /tmp/wt_pre/.env
( cd /tmp/wt_pre && "$PWD/../<repo>/.venv/Scripts/python" -m evaluation.chunking_report analyze \
    --blocks evaluation/artifacts/blocks_Attention.json \
    --out evaluation/artifacts/baseline_Attention.json --runs 3 )
git worktree remove /tmp/wt_pre

# 4. compare
uv run python -m evaluation.chunking_report compare \
    --baseline evaluation/artifacts/baseline_*.json \
    --after evaluation/artifacts/stage14_*.json \
    --out-json evaluation/artifacts/comparison.json \
    --out-text evaluation/artifacts/comparison.txt
```

The analyze step re-runs chunking `--runs` times on the same blocks and reports
`determinism.identical`. Separate process invocations produce byte-identical
JSON.
