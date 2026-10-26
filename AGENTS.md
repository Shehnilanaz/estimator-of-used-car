# AGENTS.md

## Project context

- Used-car price estimator, built per the AI Vibe Coding course Session 2 plan: `/Users/shehnilayasir/Downloads/session-2-build-steps.md` (the full step sequence and prompt pack).
- Stack per TECHNICAL.md: pandas + scikit-learn (RandomForestRegressor) + Streamlit, deployable to Railway via `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.
- Dataset `used-cars.csv` (3,915 rows) is in the workspace; an original copy also remains at `/Users/shehnilayasir/Documents/AI-Vibe-Coding/car-price-estimator/used-cars.csv`.

## Environment (verified 2026-10-25)

- macOS; Python 3.12.1 venv at `.venv` with pandas 3.1.0, scikit-learn 1.9.1, streamlit 1.66.1 installed from `requirements.txt`.
- Run the app: `.venv/bin/streamlit run app.py` → http://localhost:8501 (add `--server.headless true` in background sessions; port 8501 is in use → use 8502).
- Git not initialized; global git identity (`user.name` / `user.email`) unset — set both before the first commit or it fails.

## Course progress

- Done: Step 0 (venv/.gitignore), Step 1 PRD.md, Step 2 FUNCTIONAL.md, Step 3 TECHNICAL.md, Step 4 app built + verified end-to-end in a browser, Step 5 explain-it (plain-English top-3 factors via typical-car ablation; 3 closest real listings by model/family/brand tier then price distance).
- Next: Step 6 test cars (2023 BMW/20k high, 2008 Ford/200k low, +50k drops), Step 7 GitHub/Railway deploy. Git prep prompt from Step 0 also still pending.

## Gotchas

- Handout assumes Windows; this machine is macOS: `source .venv/bin/activate`, `python3`.
- Never use the CSV's raw `transmission` column as a model feature — 60 messy values (`2`, `F`, `–`); `group_transmission()` in app.py collapses them to 4 groups. Same rule applies anywhere the CSV is read again.
- The model retrains on every app start (a few seconds — normal); `@st.cache_resource` keeps it in memory across widget interactions.
- Default UI choices are deliberate (Toyota + brand's most common model + Gasoline-first fuel list); an alphabetical default landed on Diesel and skewed estimates.
