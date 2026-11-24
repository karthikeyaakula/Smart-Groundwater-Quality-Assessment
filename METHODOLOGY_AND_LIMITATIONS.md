# Methodology and limitations

## Target and reference
BIS IS 10500:2012 specifies pH 6.5–8.5 as the acceptable range and states no relaxation outside it. The binary project target is 0 for an observed pH within the range and 1 for an observed pH outside the range.

## Leakage control
The observed pH value creates the target and is excluded from all model features. Metadata such as district, station, date and coordinates are not fed to the classifiers. Other chemistry measurements are candidate predictors subject to the configured coverage threshold.

## Model comparison
The project keeps Logistic Regression, Decision Tree and Random Forest. Imputation and scaling are fitted within pipelines. The held-out test set is not used for model selection; cross-validation macro F1 on the training split selects the reported best model.

## Limitations
- This is pH compliance screening only.
- The dataset does not support nitrate prediction because nitrate is entirely missing.
- A pH-compliant sample can still violate other chemical or microbiological standards.
- The dataset may contain repeated measurements from the same station. Random splitting can create station-level leakage; station-grouped validation is preferable when station IDs are dependable.
- Model probability estimates are statistical estimates, not calibrated laboratory results unless calibration is separately tested.
- Missing and censored values are not replaced with guessed measurements.
