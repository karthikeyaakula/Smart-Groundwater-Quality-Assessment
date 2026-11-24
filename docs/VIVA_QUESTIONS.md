# Viva Questions and Short Answers

1. **What problem does the project address?**  
   It explores West Bengal groundwater chemistry and screens for nitrate measurements above a documented reference limit using other available chemistry measurements.

2. **Which dataset is used?**  
   The CGWB West Bengal manual groundwater chemical-parameter CSV from the National Water Data Portal.

3. **Why is the nitrate field excluded from model inputs?**  
   Nitrate is used to construct the target label. Including it as an input would cause direct target leakage and make the task trivial.

4. **What does target 1 mean?**  
   The measured nitrate concentration is above the configured reference threshold. It does not mean the entire water sample is unsafe.

5. **Which algorithms are compared?**  
   Logistic Regression, Decision Tree and Random Forest.

6. **Why use Logistic Regression?**  
   It is a relatively simple linear classification baseline.

7. **Why use Decision Tree?**  
   It can model nonlinear decision boundaries and is relatively easy to interpret.

8. **Why use Random Forest?**  
   It combines multiple trees and can reduce variance compared with a single tree.

9. **Why median imputation?**  
   Median imputation is robust to skewed measurements and outliers. It is fitted inside each pipeline using training data only.

10. **Why standardize for Logistic Regression?**  
    The parameters have different scales. Standardization helps the optimization process and prevents large-scale variables from dominating.

11. **Why report macro F1 and balanced accuracy?**  
    Nitrate-exceedance labels may be imbalanced. Macro and balanced metrics give attention to both classes.

12. **What is the difference between test data and cross-validation?**  
    Cross-validation on training data is used for model comparison; the held-out test split is reserved for final evaluation.

13. **Does a model prediction prove water is safe?**  
    No. It predicts a rule-derived nitrate-exceedance label from other chemistry parameters. Direct laboratory measurement is required.

14. **What is target leakage?**  
    Leakage occurs when information used to create the target is also included in predictors. The nitrate measurement is excluded from the input features.

15. **What is a limitation of the current split?**  
    Repeated measurements from one station may appear in both training and testing. Station-grouped validation would better assess generalization to unseen wells.
