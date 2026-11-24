# Smart Groundwater Quality Assessment and Nitrate Screening Using Machine Learning

## Revised scope for the Andhra Pradesh dataset

The project title is retained. The selected Andhra Pradesh CGWB chemical-parameter dataset contains no usable nitrate readings, so nitrate-exceedance classification is not possible with this file. The implemented prediction task is therefore **pH compliance screening**.

The target is derived from BIS IS 10500:2012: pH within 6.5–8.5 is class 0; pH outside that range is class 1. The pH measurement used to construct the target is excluded from the predictor variables to prevent direct leakage.

The project retains the original supervised algorithms: Logistic Regression, Decision Tree and Random Forest. Their performance is compared using a stratified holdout test set and cross-validation on the training data.

The resulting models estimate pH compliance from other measured chemistry parameters. They do not predict nitrate, calculate a complete water-quality index, assess microbiological safety, or certify water as potable. Direct laboratory measurements remain necessary for regulatory decisions.
