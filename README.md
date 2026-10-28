# Wind Forecast Portal (UK day-ahead, Elexon)

Web app that shows (1) the latest wind-generation forecast that was available when the
day-ahead purchase decision had to be made, and (2) how accurate those forecasts are.
Scope: national wind only (Elexon FUELHH actuals, WINDFOR forecasts), January 2026.

> AI tools disclosure: this project was built with the assistance of Claude (Anthropic).

## Structure
- `backend/app/` – FastAPI service: `elexon.py` (API client), `data.py` (cache loader),
  `selection.py` (latest-forecast-at-cutoff logic), `metrics.py` (accuracy metrics), `main.py` (endpoints)
- `backend/scripts/fetch_data.py` – pulls real Elexon data into `backend/data/*.csv`
- `backend/scripts/make_sample_data.py` – SYNTHETIC data, only for running without network
- `backend/tests/` – pytest unit + API tests
- `.github/workflows/ci.yml` – runs tests on every push
- `frontend/` – React app (Day 2)

## Run
```bash
cd backend
pip install -r requirements.txt
python -m scripts.fetch_data          # real Jan 2026 data (needs internet)
uvicorn app.main:app --reload         # http://localhost:8000/docs
python -m pytest -q
```
Or `docker compose up --build`. If `backend/data/actuals.csv` is missing, the API falls back to
the synthetic sample and `/api/config` returns `using_sample_data: true`.

## Key assumptions
- Decision cutoff: day-ahead for delivery day D is decided on D-1 at **09:00 UK time**
  (configurable via `DECISION_CUTOFF` env var or `?cutoff=HH:MM`).
- For each target half-hour, the forecast used = latest `publishTime` <= cutoff.
- Error = forecast − actual (positive = over-forecast, i.e. risk of under-buying).

## API
`/api/config`, `/api/actuals`, `/api/forecast/latest`, `/api/metrics`, `/api/horizon-error`
(all accept `start`, `end` dates; see `/docs`).

## Live app
TODO (Day 2)
