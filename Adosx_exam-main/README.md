# DealerOS Reconciliation
Django REST Framework + SQLite backend and React/Vite frontend for reconciling the supplied CSVs.

## Run
Python 3.11+, Node 18+, Git required.
```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r backend/requirements.txt
cd backend
python manage.py migrate --run-syncdb
python manage.py import_data
python manage.py runserver
```
In another terminal:
```bash
cd frontend
npm install
npm run dev
```
Tests: from `backend/`, run `python -m pytest`.

## Architecture
`backend/reconcile/importer.py` contains reference/amount/date cleaners.
`management/commands/import_data.py` imports all rows using upserts.
`compare.py` is the comparison engine; `views.py` applies organization scoping before returning JSON.
React fetches `/api/disagreements/` through the Vite proxy.

## API
`GET /api/disagreements/?org=ORG-A&reason=VALUE_MISMATCH&sort=-value`
`org` is required. Optional `reason` and `sort` values: `value`, `-value`, `date`, `-date`.
The JSON response contains `summary` and transaction-level `results`.

## Screenshots
Run both servers, select ORG-A/ORG-B, capture the full report, a reason-filtered view, and the API JSON response. Save images under `docs/screenshots/` and embed with relative Markdown paths.

## Agent and review answers
Before submission, replace this section with your actual agent workflow and personally verified checks. Do not claim an agent mistake you did not observe.
1. AI mistake and check that caught it: [write your real example].
2. Least confident area and what you would verify: [write honestly].
3. First second-day improvement and why: [one concrete item].

## Scope
No authentication, pagination, Docker, or production deployment configuration. Cross-org mismatches are assigned to A's org with B-side location/value redacted; orphan B rows use B's location to determine ownership.
