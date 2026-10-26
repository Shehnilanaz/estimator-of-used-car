# TECHNICAL.md — Used-Car Price Estimator

Based on `PRD.md` and `FUNCTIONAL.md`. Beginner-friendly Python, one screen, no database.

## The stack

- **pandas** — loads `used-cars.csv` into a table we can filter and train on.
- **scikit-learn (`RandomForestRegressor`)** — learns how price relates to the six inputs by building many decision trees on the data and averaging them.
- **Streamlit** — turns plain Python into a browser UI (dropdowns, number boxes, results) with no web-development knowledge needed.

## Files to create

| File | Purpose |
|---|---|
| `app.py` | The whole app: load data → train model → show the form → display estimate, range, and factors |
| `requirements.txt` | The three libraries, so installs are one command locally and automatic on Railway |
| `used-cars.csv` | The dataset (already in the project folder) |

Supporting docs already exist: `PRD.md`, `FUNCTIONAL.md`, `TECHNICAL.md`.

## Which columns the model uses

| Role | Columns |
|---|---|
| Features (inputs) | `brand`, `model`, `year`, `mileage_miles`, `fuel_type`, `transmission` |
| Target (what it learns) | `price_usd` |
| Unused in v1 | `accident_reported`, `clean_title` |

Two data-shaping rules carry over from `FUNCTIONAL.md`:

- `transmission` is first grouped into `Automatic` / `Manual` / `CVT` / `Not specified` (the raw column has 60 messy values).
- Words must become numbers before the model can learn from them. Each category (brand, model, fuel, transmission) gets converted to numeric columns; if the user picks a combination the model has never seen, the app handles it gracefully instead of crashing.

## How the model trains when the app starts

1. Streamlit runs `app.py`.
2. pandas reads `used-cars.csv` (3,915 rows).
3. The six feature columns are prepared (transmission grouping + word-to-number conversion).
4. `RandomForestRegressor` fits on all 3,915 rows — **a few seconds, and that's normal**; it happens once per app start.
5. The trained model is kept in memory while the user clicks around; every input change triggers one prediction, then the app shows:
   - the rounded estimate,
   - a low–high range taken from the spread of the individual trees' predictions (wider when inputs are unusual or rare),
   - the top 3 factors, by comparing this prediction against a typical-car prediction and reporting which inputs moved it most and in which direction.

Retraining only repeats when the app restarts.

## Libraries (for requirements.txt)

- `pandas` — data loading and shaping
- `scikit-learn` — the RandomForestRegressor
- `streamlit` — the browser UI

## Run it locally

macOS (this machine):

1. `source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `streamlit run app.py`
4. Open `http://localhost:8501` (if the port is busy, Streamlit uses 8502 — or run with `--server.port 8502`)

On Windows (per the course handout): activate with `.venv\Scripts\activate` instead of step 1; everything else is the same.

## Deploy to Railway (later)

1. Push the project to a GitHub repo.
2. Railway: **New Project → Deploy from GitHub repo** → pick the repo.
3. Railway installs everything from `requirements.txt` automatically.
4. Set the start command exactly:

   ```
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```

   (`$PORT` is the port Railway hands the app — the `0.0.0.0` lets the public internet reach it.)
5. Open the Railway-generated public URL — the same screen as localhost. First deploy takes a few minutes (build + model training); future deploys happen on every git push.
