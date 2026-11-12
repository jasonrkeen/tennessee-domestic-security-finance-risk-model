> This file mirrors `.github/copilot-instructions.md`; keep both in sync when either changes.

# CLAUDE.md — Tennessee Domestic Security & Illicit Finance Risk Intelligence Model

## Purpose
County-level OSINT model for Tennessee domestic security, illicit-finance vulnerability, operational-risk context, and non-scoring reference appendices.

## Tech stack
- Python; dependencies in `requirements.txt`
- Key libraries: `pandas`, `numpy`, `requests`, `matplotlib`, `reportlab`, `python-dotenv`, `openpyxl`, `streamlit`, `plotly`, `pdfplumber`

## Folder structure
- `docs/` (methodology, source reviews, final report and release notes)
- `src/` (collection, preparation, scoring and reporting)
- `tests/` (offline regression fixtures and dashboard checks)
- `README.md`
- `app.py`
- `main.py`
- `requirements.txt`

## Setup, run, test
Use CPython 3.14.4 on Windows x64 and the hash lock; see `docs/reproducibility.md`.
In an isolated virtual environment:
```bash
python -m pip install --require-hashes -r requirements-lock.txt
python -m pip check
python -m pytest -q
python -m streamlit run app.py
```
The offline suite uses synthetic fixtures and temporary outputs. Do not run
`main.py` or source processors merely to view or test the saved-output release.
Preserve the dated final report, original data and frozen expected scores during
presentation-only changes. Source refreshes and scoring changes need separate review.

## Conventions observed
- Functions use type hints; keep annotating new code.
- Uses `dataclasses` for structured config/results.
- Config lives in: `src/config.py`; avoid hardcoding parameters elsewhere.
- API keys are loaded from a local `.env` via python-dotenv; `.env` must stay uncommitted.
- Raw data (`data/raw/`) is gitignored; download/fetch it via the pipeline, do not commit it.
- Public data sources referenced: ACLED, Census.
- Write paths relative to the repo root (no absolute local paths).

## Output artifacts
- A PDF report is produced with `reportlab`; keep it in sync with model changes.
- Streamlit dashboard: `app.py` (run with `streamlit run <file>`).
- Charts are generated with matplotlib / plotly.

## Guardrails
- Never commit secrets, API keys, tokens, or `.env` files.
- Do not commit large raw datasets or binaries; keep data fetched or documented with its source.
- Keep analysis source-backed: cite data sources and assumptions; label scenario/forecast outputs as model estimates, not facts.
- Preserve reproducibility: no unseeded randomness, no hidden manual steps.
