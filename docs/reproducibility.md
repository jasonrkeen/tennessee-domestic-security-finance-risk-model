# Reproducibility and dashboard verification

## Supported locked environment

Use CPython 3.14.4 on Windows x64, the environment targeted by the lock and CI.
The lock includes application, testing and transitive dependencies with hashes.
It does not freeze source API responses, operating-system binaries or historical
acquisition metadata. Other Python/platform combinations are not covered by this
lock's validation; generate and test a separate lock before claiming support.

From the repository root in PowerShell:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Confirm the printed Python version is 3.14.4. `requirements.txt` and
`requirements-dev.txt` retain broad input requirements; installing them alone
does not reproduce this environment. The GitHub workflow uses the hash lock.

## Preserving research data

The dashboard reads existing CSVs and PDFs. It does not run `main.py`, fetch
sources, or write results. A clean checkout offers the committed final report
without requiring an API call or generated county data. To explore saved results,
use a separate checkout with copies of the appropriate `outputs/` and optional
`data/processed/` files. Do not point a validation run at the original project.
Raw and generated data remain excluded from Git.

Coverage displayed in metrics and tables comes from the loaded files and may
retain historical labels. The dashboard deliberately does not join in a newer
review by county alone: matching names would not establish matched source
vintages. Read the final report's separate reviewed assessment and limitations.
Scenario controls operate on display copies and do not replace baseline scores.

The regression suite compares scoring against the frozen synthetic baseline
from `bb6f0b5`. Dashboard tests exercise empty and populated saved-output states,
county filtering, coverage caveats and file preservation. Requests-based live
HTTP is blocked during tests. This is not a system-wide network sandbox or an
end-to-end live-source ingestion test. Do not regenerate the baseline from the
candidate merely to make tests pass.

## Updating dependencies deliberately

The lock was generated with pip-tools 7.6.2 and pip 26.0.1 on CPython 3.14.4,
Windows x64. Use a disposable tooling environment rather than changing a working
research environment:

```powershell
py -3.14 -m venv .venv-lock
.\.venv-lock\Scripts\python.exe -m pip install pip==26.0.1 pip-tools==7.6.2
$env:CUSTOM_COMPILE_COMMAND = 'python -m piptools compile --generate-hashes --strip-extras --output-file=requirements-lock.txt requirements-lock.in'
.\.venv-lock\Scripts\python.exe -m piptools compile --generate-hashes --strip-extras --output-file=requirements-lock.txt requirements-lock.in
```

The three explicit version constraints in `requirements-lock.in` preserve the
reviewed numerical/dashboard versions. A deliberate upgrade requires editing
those constraints or passing the appropriate pip-tools upgrade options, reviewing
the resulting lock diff, installing into a fresh environment, and running the
full offline suite and dashboard checks. Never update frozen expected scores as
part of a routine dependency refresh. Add temporary environments to your local
Git exclusions if they are not already ignored.

## Scope of CI

The workflow runs on pull requests, pushes to `master`, and manual dispatch. It
has read-only repository permissions and uploads test results, not datasets.
Successful synthetic tests establish bounded regression behavior; they do not
establish complete source reporting, calibrated prediction, or deployment readiness.

References: [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)
and [pip-tools](https://pip-tools.pypa.io/en/stable/).
