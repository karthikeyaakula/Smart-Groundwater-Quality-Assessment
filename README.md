# Smart Groundwater Quality Assessment and Nitrate Screening Using Machine Learning

**Original project title retained as requested.**

## Revised Andhra Pradesh scope

The selected Andhra Pradesh CGWB manual chemical-parameter CSV contains 10,950 records, but the `Nitrate N (mgN/L)` field has no numeric readings. The original nitrate-exceedance target therefore cannot be constructed from this file. This version does not fabricate nitrate values or labels.

To continue with the available dataset, the supervised target is changed to **pH compliance screening** using the pH requirement in BIS IS 10500:2012:

- Class 0 — pH is within 6.5–8.5 inclusive.
- Class 1 — pH is below 6.5 or above 8.5.

The pH measurement is excluded from predictors. The model uses other available chemical measurements to estimate the pH-compliance class. The three original algorithms are unchanged:

1. Logistic Regression
2. Decision Tree
3. Random Forest

**Important:** This is not nitrate screening, an overall Water Quality Index, or a drinking-water potability classifier. BIS compliance includes many chemical, physical and microbiological requirements that are not all represented in this dataset. A model prediction is not a laboratory measurement or certification.

## Dataset

Expected file:

`data/gwq_chemical_parameter_manual_cgwb_ap_1961_2025.csv`

The dataset is not bundled. Keep your existing CSV in the `data` folder.

The previously inspected coverage showed approximately 99% pH availability, 99.9% electrical-conductivity availability, 97% chloride availability, 78% sulphate availability and 86.5% total-hardness availability. TDS was available for only about 17.6% of records and is excluded by the configured 30% numeric-coverage threshold. Coverage is recalculated from the CSV at runtime.

## Methodology

1. Read the CSV with common encodings and separators.
2. Normalize column names and parse numeric values.
3. Treat blank, BDL and censored entries such as `<0.01` as missing; do not invent substitute measurements.
4. Derive the binary target from measured pH and the BIS range.
5. Exclude pH from predictors to prevent direct target leakage.
6. Exclude metadata and predictors with more than 70% missingness.
7. Median imputation is fitted inside each model pipeline using training data only.
8. Use an 80/20 stratified train/test split and up to five-fold stratified cross-validation on the training split.
9. Compare the three original classifiers using accuracy, balanced accuracy, macro precision/recall/F1, ROC-AUC and outside-range recall. Include a majority-class baseline.

A random stratified split may put samples from the same station in both train and test sets. The reported metrics are an initial benchmark; station-grouped validation should be considered if reliable station IDs are available.

## Run on the existing Windows / Snapdragon X environment

Do not reinstall Python or recreate your virtual environment if it is already working.

From the project root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe inspect_data.py
.\.venv\Scripts\python.exe train.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Or use the existing `inspect_data.bat`, `train.bat` and `run_app.bat`.

## Generated outputs

- `models/groundwater_screening_models.joblib`
- `results/model_comparison.csv`
- `results/classification_reports.json`
- `results/confusion_matrices.json`
- `results/feature_importance.csv`
- `results/run_summary.json`
- `results/model_comparison.png`
- Per-model confusion-matrix PNG files

## Reference

Bureau of Indian Standards, IS 10500:2012, *Drinking Water — Specification*, Table 1: pH acceptable range 6.5–8.5, with no relaxation. See the reference link in the project report or the official standard.
