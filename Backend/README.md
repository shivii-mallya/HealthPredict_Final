# Predictive Hospital Resource Allocation — Member 3 Backend

## Purpose
This is the simple backend/resource-logic component for the hackathon.

It takes a future admission prediction from Member 1 and converts it into:
- expected ICU admissions
- expected general admissions
- required bed-days
- required staff
- required medical-supply units
- supply shortage/sufficiency status

## Actual files inspected
- `Daily_Admissions_Data (1).xlsx`
  - `Daily_Admissions`: 30 usable daily records from October 2024
  - `Raw_Data`: 500 patient records
- `Inventory_Data.xlsx`
  - 500 usable inventory records
  - resources include: Gloves, IV Drip, Surgical Mask, Ventilator, X-ray Machine

The workbook contains total/footer/source rows, so the backend explicitly filters those out.

## Important limitation in the current data
The admissions data has only one month of aggregated history, so the backend does NOT claim to perform forecasting.
Member 1's ML model is responsible for future prediction.

The current backend uses transparent historical ratios to translate Member 1's predicted total admissions into resource requirements.

## Member 1 integration
For now, `member1_predictions_placeholder.csv` contains one random-looking placeholder prediction generated with a fixed seed.

Current placeholder:
- forecast date: 2027-01-01
- prediction source: PLACEHOLDER_RANDOM_MEMBER1_OUTPUT

When Member 1 is ready, replace that value with the real ML output. The backend does not need to be rewritten.

Expected minimum input:
`predicted_total_admissions`

## Run
Install:
```bash
pip install pandas openpyxl
```

Run:
```bash
python backend.py
```

## Output
The main output is a dictionary/report containing:
- predicted demand
- required resources
- current tracked inventory
- shortage/sufficient status

Member 4 can import:
```python
from backend import load_data, build_resource_report
```

Then:
```python
admissions, inventory = load_data()
report = build_resource_report(120, admissions, inventory)
```

## Why the logic is explainable
For example:
- ICU rate = historical ICU admissions / total admissions
- bed-days per admission = historical total bed-days / total admissions
- staff per admission = historical staff required / total admissions
- supply units per admission = historical supply usage / total admissions

Then:
`required resource = predicted admissions × historical rate`

## Inventory limitation
The current inventory file contains stock by item, but the admissions file does not say exactly how many Gloves/IV Drips/Masks were consumed per patient.
Therefore the prototype compares required medical-supply *units* with the combined stock of:
- Gloves
- IV Drip
- Surgical Mask

Ventilators and X-ray Machines are kept in the inventory dataset but are not converted into demand requirements yet because there is no reliable historical usage mapping for them.

This should be clearly stated during the hackathon presentation rather than inventing unsupported conversion rules.
