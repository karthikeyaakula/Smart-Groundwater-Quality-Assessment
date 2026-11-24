"""Train the unchanged Logistic Regression, Decision Tree and Random Forest models."""
from __future__ import annotations
import json, os, re, time
from pathlib import Path
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, classification_report,
    confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from config import MAX_CV_FOLDS, MAX_WORKERS, RANDOM_FOREST_TREES, RANDOM_STATE, ROOT, TEST_SIZE
from data_utils import load_and_profile

MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"

def make_models():
    return {
        "Logistic Regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=3000, class_weight="balanced", random_state=RANDOM_STATE)),
        ]),
        "Decision Tree": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", DecisionTreeClassifier(max_depth=7, min_samples_leaf=4, class_weight="balanced", random_state=RANDOM_STATE)),
        ]),
        "Random Forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", RandomForestClassifier(
                n_estimators=RANDOM_FOREST_TREES, min_samples_leaf=2,
                class_weight="balanced_subsample", random_state=RANDOM_STATE,
                n_jobs=min(MAX_WORKERS, max(1, os.cpu_count() or 1)),
            )),
        ]),
    }

def class_one_probability(model, x):
    classes = list(model.classes_)
    return model.predict_proba(x)[:, classes.index(1)]

def save_confusion_matrix(name, matrix):
    fig, ax = plt.subplots(figsize=(4.8, 4.0))
    ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=["Within pH range", "Outside pH range"],
    ).plot(ax=ax, cmap="Blues", colorbar=False, values_format="d")
    ax.set_title(f"{name} – pH compliance")
    fig.tight_layout()
    safe = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    fig.savefig(RESULTS_DIR / f"confusion_matrix_{safe}.png", dpi=140)
    plt.close(fig)

def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df, features, location_cols, date_cols, metadata = load_and_profile()
    x = df[features].replace([np.inf, -np.inf], np.nan)
    y = df["ph_compliance"].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    cv_folds = min(MAX_CV_FOLDS, int(y_train.value_counts().min()))
    if cv_folds < 2:
        raise ValueError("Not enough minority-class examples for stratified cross-validation.")
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=RANDOM_STATE)

    baseline = DummyClassifier(strategy="most_frequent").fit(x_train, y_train)
    base_pred = baseline.predict(x_test)
    rows = [{
        "Model": "Majority Baseline (not ML)",
        "Accuracy": accuracy_score(y_test, base_pred),
        "Balanced_Accuracy": balanced_accuracy_score(y_test, base_pred),
        "Precision_macro": precision_score(y_test, base_pred, average="macro", zero_division=0),
        "Recall_macro": recall_score(y_test, base_pred, average="macro", zero_division=0),
        "F1_macro": f1_score(y_test, base_pred, average="macro", zero_division=0),
        "ROC_AUC": np.nan,
        "Outside_Range_Recall": recall_score(y_test, base_pred, pos_label=1, zero_division=0),
        "CV_F1_macro_mean": np.nan, "CV_F1_macro_std": np.nan,
        "Training_and_CV_seconds": 0.0,
    }]

    fitted, reports, matrices, cv_rows = {}, {}, {}, {}
    for name, model in make_models().items():
        start = time.perf_counter()
        scores = cross_val_score(model, x_train, y_train, cv=cv, scoring="f1_macro", n_jobs=1)
        model.fit(x_train, y_train)
        elapsed = time.perf_counter() - start
        pred = model.predict(x_test)
        prob = class_one_probability(model, x_test)
        cm = confusion_matrix(y_test, pred, labels=[0, 1])
        rows.append({
            "Model": name,
            "Accuracy": accuracy_score(y_test, pred),
            "Balanced_Accuracy": balanced_accuracy_score(y_test, pred),
            "Precision_macro": precision_score(y_test, pred, average="macro", zero_division=0),
            "Recall_macro": recall_score(y_test, pred, average="macro", zero_division=0),
            "F1_macro": f1_score(y_test, pred, average="macro", zero_division=0),
            "ROC_AUC": roc_auc_score(y_test, prob),
            "Outside_Range_Recall": recall_score(y_test, pred, pos_label=1, zero_division=0),
            "CV_F1_macro_mean": float(np.mean(scores)),
            "CV_F1_macro_std": float(np.std(scores)),
            "Training_and_CV_seconds": round(elapsed, 3),
        })
        reports[name] = classification_report(
            y_test, pred, labels=[0, 1],
            target_names=["Within pH range", "Outside pH range"],
            output_dict=True, zero_division=0,
        )
        matrices[name] = cm.tolist()
        save_confusion_matrix(name, cm)
        fitted[name] = model
        cv_rows[name] = [float(v) for v in scores]

    metrics = pd.DataFrame(rows)
    ml = metrics[metrics["Model"] != "Majority Baseline (not ML)"]
    best = str(ml.sort_values("CV_F1_macro_mean", ascending=False).iloc[0]["Model"])
    metrics.to_csv(RESULTS_DIR / "model_comparison.csv", index=False)
    (RESULTS_DIR / "classification_reports.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    (RESULTS_DIR / "confusion_matrices.json").write_text(json.dumps(matrices, indent=2), encoding="utf-8")

    rf = fitted["Random Forest"].named_steps["classifier"]
    pd.DataFrame({"Feature": features, "Importance": rf.feature_importances_}).sort_values(
        "Importance", ascending=False
    ).to_csv(RESULTS_DIR / "feature_importance.csv", index=False)

    summary = {
        **metadata, "train_rows": int(len(x_train)), "test_rows": int(len(x_test)),
        "test_size": TEST_SIZE, "random_state": RANDOM_STATE,
        "cross_validation_folds": cv_folds, "cv_macro_f1_by_model": cv_rows,
        "best_model_by_training_cv_macro_f1": best,
        "baseline_test_accuracy": float(rows[0]["Accuracy"]),
        "model_selection": "Highest mean macro F1 on stratified CV folds within training data; held-out test set reserved for final reporting.",
        "evaluation_warning": "Random stratified split may place samples from the same station in both train and test sets. Treat results as an initial benchmark; station-grouped validation is recommended where station identifiers are reliable.",
        "scope_limitation": "The target is pH-range compliance only. This is not a nitrate model, overall water-quality index, or drinking-water potability classifier.",
    }
    (RESULTS_DIR / "run_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    joblib.dump({
        "models": fitted, "best_model_name": best, "features": features,
        "target_name": "ph_compliance", "target_column": metadata["target_column"],
        "target_threshold": [metadata["ph_min_acceptable"], metadata["ph_max_acceptable"]],
        "target_unit": "pH", "metadata": metadata, "random_state": RANDOM_STATE,
    }, MODELS_DIR / "groundwater_screening_models.joblib", compress=3)

    fig, ax = plt.subplots(figsize=(8, 4))
    chart = ml
    ax.bar(chart["Model"], chart["F1_macro"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Macro F1-score")
    ax.set_title("Model comparison – pH compliance screening")
    ax.tick_params(axis="x", rotation=10)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "model_comparison.png", dpi=140)
    plt.close(fig)

    print("\nANDHRA PRADESH GROUNDWATER DATA SUMMARY")
    print(json.dumps(summary, indent=2, default=str))
    print("\nMODEL COMPARISON")
    print(metrics.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print(f"\nSelected model by training CV macro F1: {best}")
    print(f"Model bundle: {MODELS_DIR / 'groundwater_screening_models.joblib'}")
    print(f"Results: {RESULTS_DIR}")

if __name__ == "__main__":
    main()
