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

