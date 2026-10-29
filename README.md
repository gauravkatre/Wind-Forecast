
# Wind Forecast Portal — UK Day-Ahead Wind Forecast Accuracy

A full-stack web application for analyzing UK national wind-generation forecasts against actual generation data from Elexon for January 2026.

The portal identifies the latest forecast available at the day-ahead purchasing decision cutoff and evaluates its accuracy against actual wind generation. It provides a FastAPI backend and a React dashboard for exploring forecast errors over time and across forecast horizons.

## Overview

Wind generation is variable, making accurate forecasting important for electricity purchasing and balancing decisions. This project evaluates how well day-ahead wind forecasts match actual generation by selecting only forecasts that were available at the decision cutoff.

### Key Objectives

- Retrieve actual wind-generation and forecast data from Elexon.
- Reconstruct the forecast available at the day-ahead decision cutoff.
- Compare selected forecasts with actual generation for each half-hour delivery period.
- Calculate forecast accuracy metrics and analyze error patterns.
- Visualize actual versus forecast generation, daily errors, and forecast-horizon errors.

**Scope:** UK national wind generation, January 1–31, 2026.

## Features

- **Elexon Data Integration:** Fetches actual and forecast data from Elexon's API.
- **Decision-Time Forecast Selection:** Selects the latest forecast published on or before the configured cutoff.
- **Forecast Accuracy Analysis:** Calculates MAE, RMSE, and bias.
- **Actual vs. Forecast Visualization:** Compares forecast generation with actual generation.
- **Daily Error Analysis:** Examines forecast errors across delivery days.
- **Forecast-Horizon Analysis:** Investigates how forecast errors vary with the time between publication and delivery.
- **REST API:** Exposes configuration, actuals, forecasts, and accuracy metrics through FastAPI.
- **Sample Data Fallback:** Supports local development when real data is unavailable.
- **Automated Testing:** Includes pytest unit tests and API tests.
- **Continuous Integration:** Runs tests through GitHub Actions on every push.
- **Docker Support:** Supports running the application using Docker Compose.

## Tech Stack

| Component | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Data Processing | Pandas, NumPy |
| Data Source | Elexon API |
| Frontend | React, Vite |
| Charts | Recharts |
| Testing | Pytest |
| CI/CD | GitHub Actions |
| Containerization | Docker, Docker Compose |
| Data Storage | CSV-based local cache |

## Project Structure

```text
wind-forecast-portal/
├── backend/
│   ├── app/
│   │   ├── elexon.py
│   │   ├── data.py
│   │   ├── selection.py
│   │   ├── metrics.py
│   │   └── main.py
│   ├── scripts/
│   │   ├── fetch_data.py
│   │   └── make_sample_data.py
│   ├── data/
│   │   ├── actuals.csv
│   │   └── forecasts.csv
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
└── README.md
```

### Backend Modules

- `elexon.py` — Elexon API client for retrieving source data.
- `data.py` — Data loading and local cache management.
- `selection.py` — Selects the latest eligible forecast at the decision cutoff.
- `metrics.py` — Calculates forecast accuracy metrics.
- `main.py` — Defines the FastAPI application and API endpoints.

### Data Scripts

- `fetch_data.py` — Fetches real Elexon data for January 2026.
- `make_sample_data.py` — Generates synthetic data for development and testing.

## Data Sources

The project uses two Elexon datasets:

- **FUELHH:** Half-hourly fuel-type generation data, used to obtain national wind-generation actuals.
- **WINDFOR:** Wind-generation forecast data, including publication timestamps and forecast delivery periods.

The data-fetching script retrieves the required January 2026 data and stores it locally as CSV files.

**Data integrity:** Synthetic data is provided only for development and testing. Results generated from synthetic data must not be presented as real-world forecast performance.

## Forecast Selection Methodology

### 1. Decision Cutoff

For a delivery day `D`, the default purchasing decision cutoff is **09:00 UK local time on day D-1**.

The cutoff can be configured through the `DECISION_CUTOFF` environment variable or the `cutoff` query parameter, where supported.

### 2. Selecting the Forecast

For each target half-hour delivery period, the system selects the most recently published forecast that satisfies:

\[
t_{\text{publish}} \leq t_{\text{cutoff}}
\]

This prevents forecasts published after the purchasing decision cutoff from being used in the day-ahead evaluation.

### 3. Calculating Forecast Error

\[
e_t = F_t - A_t
\]

Where:

- \(F_t\) = Selected forecast generation.
- \(A_t\) = Actual generation.
- \(e_t\) = Forecast error.

**Interpretation:**

- Positive error: Generation was over-forecast.
- Negative error: Generation was under-forecast.
- Zero error: Forecast matched actual generation.

Over-forecasting can contribute to under-purchasing relative to actual wind output, but the actual commercial impact depends on the purchasing and balancing strategy.

## Forecast Accuracy Metrics

### Mean Absolute Error (MAE)

\[
MAE = \frac{1}{N}\sum_{t=1}^{N}|F_t-A_t|
\]

Measures the average absolute difference between forecast and actual generation.

### Root Mean Squared Error (RMSE)

\[
RMSE = \sqrt{\frac{1}{N}\sum_{t=1}^{N}(F_t-A_t)^2}
\]

Penalizes larger forecast errors more heavily.

### Mean Bias Error (Bias)

\[
Bias = \frac{1}{N}\sum_{t=1}^{N}(F_t-A_t)
\]

Measures systematic over-forecasting or under-forecasting.

- Positive bias indicates systematic over-forecasting.
- Negative bias indicates systematic under-forecasting.
- Bias near zero indicates little average signed error, although individual errors may still be large.

Metrics should be calculated using valid, matched forecast–actual observations.

## Getting Started

### Prerequisites

- Python 3.10 or later, compatible with the project's dependencies.
- Node.js and npm.
- Internet access to fetch real Elexon data.
- Docker and Docker Compose for containerized deployment.

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd wind-forecast-portal
```

Replace `<YOUR_REPOSITORY_URL>` with your GitHub repository URL.

### 2. Set Up the Backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Fetch Real Elexon Data

```bash
python -m scripts.fetch_data
```

This script should retrieve the required January 2026 actuals and forecasts and save them to `backend/data/`.

Check the script output and generated files to confirm that both datasets were downloaded successfully.

### 4. Start the Backend API

Run from the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- **API:** http://localhost:8000
- **Swagger Documentation:** http://localhost:8000/docs
- **ReDoc Documentation:** http://localhost:8000/redoc

### 5. Start the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend at:

http://localhost:5173

If the backend runs at a different URL, configure `VITE_API_URL` according to the frontend's environment-variable implementation.

### 6. Run Tests

From the `backend/` directory:

```bash
python -m pytest -q
```

The tests cover forecast selection logic, metric calculations, and API behavior.

### 7. Run with Docker

From the repository root:

```bash
docker compose up --build
```

Expected service ports:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

Actual ports depend on the Docker Compose configuration.

## API Reference

The application exposes the following endpoints:

| Endpoint | Purpose |
|---|---|
| `/api/config` | Returns application configuration and data-source status. |
| `/api/actuals` | Returns actual wind-generation observations. |
| `/api/forecast/latest` | Returns the selected day-ahead forecasts. |
| `/api/metrics` | Returns aggregate forecast accuracy metrics. |
| `/api/horizon-error` | Returns forecast-error analysis by forecast horizon. |

### Example Requests

```http
GET /api/config
GET /api/actuals?start=2026-01-01&end=2026-01-31
GET /api/forecast/latest?start=2026-01-01&end=2026-01-31
GET /api/metrics?start=2026-01-01&end=2026-01-31
GET /api/horizon-error?start=2026-01-01&end=2026-01-31
```

All endpoints support `start` and `end` date parameters where implemented. Refer to Swagger documentation for the exact parameter support, response formats, and schemas.

## Sample Data and Fallback Behavior

The project includes a script to generate synthetic data for development environments where network access is unavailable.

```bash
cd backend
python -m scripts.make_sample_data
```

If `backend/data/actuals.csv` is missing, the API is designed to fall back to synthetic sample data.

The `/api/config` endpoint reports this state through `using_sample_data`.

Example response:

```json
{
  "using_sample_data": true
}
```

The actual API response may contain additional fields.

**Important:** Always check `using_sample_data` before interpreting charts or metrics. Synthetic data is not evidence of actual UK wind-forecast performance.

## Testing and Continuous Integration

The backend test suite uses pytest to validate core application behavior, including:

- Latest-forecast selection at the decision cutoff.
- Forecast-error and accuracy-metric calculations.
- API endpoint responses.
- Expected behavior when data is missing or sample data is used.

GitHub Actions runs the configured test workflow on every push.

Run the tests locally before pushing changes:

```bash
cd backend
python -m pytest -q
```

## Key Assumptions and Limitations

- The analysis covers UK national wind generation for January 2026 only.
- The default day-ahead decision cutoff is 09:00 UK local time on the day before delivery.
- Forecast selection uses publication timestamps, not download timestamps.
- Forecasts published after the cutoff must not be included in the selected day-ahead forecast.
- Actual and forecast observations must be aligned to the same delivery half-hour.
- Missing observations and duplicate records can affect reported metrics.
- Results depend on the availability, completeness, and interpretation of source data.
- The project provides forecast analysis, not an electricity trading recommendation or a complete model of market settlement.
- Timezone handling must account for UK daylight-saving transitions. January 2026 uses GMT, but other UK dates may use a different UTC offset.

## Dashboard

The React dashboard is designed to provide:

- Actual versus forecast generation charts.
- Forecast accuracy metric cards.
- Daily forecast-error analysis.
- Forecast-horizon error visualization.
- Date-range filtering for the analysis period.

## Live Demo

**Status:** Coming soon.

- **Frontend:** Add the deployed application URL when available.
- **Backend API:** Add the deployed API URL when available.
- **API Documentation:** Add the deployed `/docs` URL when available.

## Future Improvements

- Deploy the frontend and FastAPI backend.
- Add date-range and decision-cutoff controls to the dashboard.
- Display data freshness, coverage, and missing-observation warnings.
- Compare forecasts across alternative decision cutoffs.
- Add unit-aware chart labels and downloadable analysis reports.
- Expand evaluation to additional months and forecast horizons.
- Add reproducible data-refresh workflows and stronger integration tests.

## AI Tools Disclosure

This project was built with the assistance of Claude (Anthropic).

AI tools were used as development assistance. Data retrieval, forecast selection, metric calculations, and displayed results should be validated against the implemented code and source data.

## License

Add a `LICENSE` file and specify the project's license before distributing or reusing the code.

## Acknowledgements

- Elexon for electricity-system data and API access.
- The open-source Python and JavaScript ecosystems.
