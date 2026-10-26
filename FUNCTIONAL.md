# FUNCTIONAL.md — Used-Car Price Estimator

Based on `PRD.md`. The user fills in six inputs and gets a fair-price estimate, a low–high range, and the top reasons behind the number. All values below come from the actual columns in `used-cars.csv` (3,915 listings, model years 1998–2024, $2,000–$250,000).

## Inputs

| Input | How it's entered | Allowed values |
|---|---|---|
| Brand | Dropdown | The 56 brands in the data, spelled exactly as they appear (e.g. `Toyota`, `BMW`, `Land`, `Alfa`, `smart`) |
| Model | Dropdown, filtered by the chosen brand | The models present for that brand (1,849 across the dataset, including trim, e.g. `Camry Hybrid XLE`) |
| Year | Number | Any whole year; typical range 1998–2024 |
| Mileage | Number (miles) | Any whole number ≥ 0; typical range 100–300,000 |
| Fuel type | Dropdown | `Gasoline`, `Hybrid`, `Plug-In Hybrid`, `Diesel`, `E85 Flex Fuel`, `Unknown` — the six values in the data |
| Transmission | Dropdown | `Automatic`, `Manual`, `CVT`, `Not specified` — grouped from the 60 raw values in the data (e.g. `A/T`, `8-Speed A/T` → Automatic; `6-Speed M/T` → Manual; `CVT Transmission`, `Variable` → CVT; junk values like `2`, `F`, `–` → Not specified) |

Not inputs in v1: the CSV also contains `accident_reported` and `clean_title`. Accident history is a stretch goal; title status is unused.

## Output

- **Estimated fair price** in US dollars, rounded (e.g. `$21,400`, not `$21,437.82`).
- **A low–high range**, always shown next to the estimate — never a single number on its own. The range widens when the inputs are unusual or the data for that car is sparse.
- **Top 3 factors**, plain English and directional, e.g. *"low mileage added value"*, *"high mileage pulled it down"*, *"this model sells at a premium"*.

## Unusual inputs

- **Year older than 1998 or newer than 2024:** still show an estimate, flagged with *"our data doesn't cover this year — treat as a rough guide."*
- **Mileage above 300,000:** still show an estimate, flagged as beyond our data.
- **Very old car with very high mileage:** estimate lands near the cheapest listings, with the low–high range widened and the reliability disclaimer shown.
- **`Unknown` fuel or `Not specified` transmission:** perfectly valid — they exist in the data.
- **Blank or non-numeric year/mileage:** show a short message and don't attempt an estimate; the app never crashes on bad input.
- **Model not offered for the selected brand:** can't be chosen (the model list comes from the brand selection); if reached anyway, ask the user to pick from the list.

## Three example cars

| Car | Expected behavior |
|---|---|
| **2019 Toyota Camry, 80,000 miles, Gasoline, Automatic** | A sensible mid-range family-sedan estimate: clearly below a 2023 car of any kind, clearly above a 2008 one. The two 2018 Camry Hybrids in the data ($23,995 at 69,641 mi; $29,500 at 22,000 mi) show the direction: more miles, lower price. |
| **2023 BMW, 20,000 miles** | High estimate. The 38 BMWs from 2022–2024 with under 30,000 miles in the data sell for roughly $47,000–$57,000, so the estimate should land near the top of the overall range. |
| **2008 Ford, 200,000 miles** | Low estimate, likely under $10,000 — a comparable 2007 Ford Explorer Sport Trac with 228,000 miles is listed at $3,850. Raise the mileage by another 50,000 and the estimate must drop further. |

Sanity rule across all three: newer + fewer miles = more money, and every change in input moves the estimate in the expected direction.
