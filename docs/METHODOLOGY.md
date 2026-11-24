# Methodology

## 1. Dataset
Use the West Bengal manual chemical-parameter CSV published by CGWB through the National Water Data Portal. Download it manually and save it as `data/cgwb_west_bengal_groundwater.csv`.

## 2. Target construction
The CGWB dataset does not supply an independent potable/non-potable label. This project creates a narrower `nitrate_exceedance` target from the measured nitrate value. BIS IS 10500:2012 gives an acceptable nitrate limit of 45 mg/L as NO3. For a nitrate-N column in mgN/L, convert the equivalent threshold as:

`45 × 14.0067 / 62.0049 ≈ 10.165 mg N/L`.

Target 1 means the measured nitrate result is above the applicable threshold. Target 0 means it is at or below the threshold. If the column heading does not reveal the unit basis, training stops until the user confirms the unit in `config.py`.

The nitrate column used to create the target is deliberately excluded from the feature matrix. Predictors are other numeric chemistry measurements only.

## 3. Preprocessing
- Normalize headers and retain location/date metadata for display.
- Convert numeric measurements; treat censored values such as `<0.01` and BDL as missing.
- Exclude records with missing/censored nitrate because their target cannot be derived.
- Detect numeric chemistry features and exclude metadata, nitrate target field, constant fields and fields with more than 70% missingness.
- Remove exact duplicate rows.
- Impute predictor missing values with median inside each training pipeline.
- Scale features for Logistic Regression; tree-based models do not require scaling.

## 4. Algorithms
- Logistic Regression: linear baseline; median imputation and standard scaling.
- Decision Tree: nonlinear tree classifier; median imputation.
- Random Forest: ensemble of decision trees; median imputation and capped worker count.

All three use class weighting to mitigate class imbalance.

## 5. Evaluation
Use an 80:20 stratified train/test split with random state 42. Compare models with accuracy, balanced accuracy, macro precision, macro recall, macro F1, ROC-AUC, positive-class (nitrate-exceedance) recall and confusion matrices. Use up to five-fold stratified cross-validation on the training split to select the model by mean macro F1. Include a majority-class baseline.

## 6. Limitations
The target is derived from a regulatory reference threshold and is not an independently assigned laboratory class. The model predicts the dataset's nitrate-exceedance rule from other chemistry values. It is not a potability model and does not replace direct nitrate measurement or full laboratory water-quality testing.
