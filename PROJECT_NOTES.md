# Project notes — Andhra Pradesh revision

- Preserve the original project title.
- Preserve Logistic Regression, Decision Tree and Random Forest.
- The selected Andhra Pradesh CSV has no numeric nitrate values; nitrate exceedance cannot be trained.
- Revised target: pH compliance, based on BIS IS 10500:2012 acceptable pH range 6.5–8.5.
- Target 0 = within range; target 1 = outside range.
- Exclude the pH measurement from predictors.
- Do not describe the output as nitrate prediction, overall water-quality classification, or potability certification.
- Current pH data coverage was about 99%; actual usable rows and class counts are recalculated at runtime.
- If only one target class exists after cleaning, training correctly stops rather than fabricating a second class.
- Random row-wise train/test split can overstate generalization when the same station appears in both splits. Grouped validation is a recommended next methodological improvement.
