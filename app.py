"""Streamlit dashboard for pH compliance screening in Andhra Pradesh groundwater."""
from pathlib import Path
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from data_utils import load_and_profile

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "groundwater_screening_models.joblib"
METRICS_PATH = ROOT / "results" / "model_comparison.csv"
CONFUSION_PATH = ROOT / "results" / "confusion_matrices.json"

st.set_page_config(page_title="Smart Groundwater Quality Assessment", layout="wide")
st.title("Smart Groundwater Quality Assessment and Nitrate Screening Using Machine Learning")
st.caption("Andhra Pradesh dataset • Revised prediction target: pH compliance screening")
st.warning(
    "Important scope change: the selected Andhra Pradesh CSV has no usable nitrate readings. "
    "This version therefore screens pH compliance only. It does not predict nitrate or certify "
    "overall drinking-water potability."
)

try:
    df, features, location_cols, date_cols, metadata = load_and_profile()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Raw records", f"{metadata['raw_rows']:,}")
c2.metric("Records with numeric pH", f"{metadata['records_used']:,}")
c3.metric("Predictor parameters", len(features))

st.subheader("Target definition")
st.markdown(
    f"- **Within range (0):** pH from {metadata['ph_min_acceptable']} to {metadata['ph_max_acceptable']} inclusive.\n"
    f"- **Outside range (1):** pH below {metadata['ph_min_acceptable']} or above {metadata['ph_max_acceptable']}.\n"
    "- The pH measurement itself is excluded from model predictors to prevent direct target leakage."
)
counts = pd.Series(metadata["target_counts"], dtype="int64")
st.bar_chart(counts)

tab1, tab2, tab3 = st.tabs(["Data Explorer", "pH Screening", "Model Comparison"])

with tab1:
    st.subheader("Dataset preview")
    st.dataframe(df.head(100), use_container_width=True)
    st.subheader("Predictor coverage")
    coverage = df[features].notna().mean().sort_values(ascending=False)
    st.bar_chart(coverage)
    st.subheader("Summary statistics")
    st.dataframe(df[features].describe().T, use_container_width=True)

with tab2:
    st.subheader("Estimate pH compliance class from other chemistry parameters")
    if not MODEL_PATH.exists():
        st.info("Train the models first by running train.bat. The trained model bundle will appear here.")
    else:
        bundle = joblib.load(MODEL_PATH)
        model_names = list(bundle["models"])
        selected = st.selectbox(
            "Model",
            model_names,
            index=model_names.index(bundle["best_model_name"]),
        )
        st.caption("Enter available laboratory measurements. Blank values are imputed using training-set medians.")
        values = {}
        cols = st.columns(2)
        for i, feature in enumerate(bundle["features"]):
            with cols[i % 2]:
                med = float(df[feature].median()) if df[feature].notna().any() else 0.0
                values[feature] = st.number_input(
                    feature.replace("_", " "),
                    value=med,
                    format="%.4f",
                    key=f"input_{feature}",
                )
        if st.button("Estimate pH compliance", type="primary"):
            sample = pd.DataFrame([{k: values[k] for k in bundle["features"]}])
            model = bundle["models"][selected]
            pred = int(model.predict(sample)[0])
            prob = float(model.predict_proba(sample)[0, list(model.classes_).index(1)])
            if pred == 0:
                st.success(
                    f"Model estimate: within the pH range. "
                    f"Estimated outside-range probability: {prob:.1%}"
                )
            else:
                st.error(
                    f"Model estimate: outside the pH range. "
                    f"Estimated outside-range probability: {prob:.1%}"
                )
            st.caption(
                "This is a statistical screening estimate, not a substitute for measuring pH "
                "or laboratory testing."
            )

with tab3:
    st.subheader("Held-out test metrics")
    if METRICS_PATH.exists():
        metrics = pd.read_csv(METRICS_PATH)
        st.dataframe(metrics, use_container_width=True)
        ml_metrics = metrics[metrics["Model"] != "Majority Baseline (not ML)"]
        if not ml_metrics.empty and "F1_macro" in ml_metrics.columns:
            st.subheader("Macro F1 comparison")
            st.bar_chart(ml_metrics.set_index("Model")["F1_macro"])
        comparison_plot = ROOT / "results" / "model_comparison.png"
        if comparison_plot.exists():
            st.image(str(comparison_plot), caption="Model comparison plot")
    else:
        st.info("No training metrics found. Run train.bat first.")

    st.divider()
    st.subheader("Confusion Matrices")
    st.caption(
        "Rows represent actual classes and columns represent predicted classes. "
        "Class 0 = within pH range; Class 1 = outside pH range."
    )

    if CONFUSION_PATH.exists():
        try:
            with CONFUSION_PATH.open("r", encoding="utf-8") as file:
                confusion_matrices = json.load(file)

            model_order = ["Logistic Regression", "Decision Tree", "Random Forest"]
            available_models = [name for name in model_order if name in confusion_matrices]
            available_models += [
                name for name in confusion_matrices if name not in available_models
            ]

            matrix_columns = st.columns(min(3, max(1, len(available_models))))
            for index, model_name in enumerate(available_models):
                matrix = np.asarray(confusion_matrices[model_name], dtype=int)
                if matrix.shape != (2, 2):
                    st.warning(f"Skipping {model_name}: expected a 2×2 confusion matrix.")
                    continue

                tn, fp, fn, tp = matrix.ravel()
                with matrix_columns[index % len(matrix_columns)]:
                    st.markdown(f"**{model_name}**")
                    fig, ax = plt.subplots(figsize=(4.2, 3.6))
                    image = ax.imshow(matrix, cmap="Blues")
                    ax.set_title("Actual vs predicted")
                    ax.set_xlabel("Predicted class")
                    ax.set_ylabel("Actual class")
                    ax.set_xticks([0, 1], labels=["Within (0)", "Outside (1)"])
                    ax.set_yticks([0, 1], labels=["Within (0)", "Outside (1)"])
                    threshold = matrix.max() / 2 if matrix.size else 0
                    for row in range(2):
                        for col in range(2):
                            ax.text(
                                col,
                                row,
                                f"{matrix[row, col]:,}",
                                ha="center",
                                va="center",
                                color="white" if matrix[row, col] > threshold else "black",
                                fontsize=12,
                                fontweight="bold",
                            )
                    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
                    fig.tight_layout()
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)

                    st.markdown(
                        f"- **True negatives:** {tn:,}\n"
                        f"- **False positives:** {fp:,}\n"
                        f"- **False negatives:** {fn:,}\n"
                        f"- **True positives:** {tp:,}"
                    )

            st.info(
                "For this project, false negatives are especially important: they are samples "
                "that are actually outside the pH range but the model predicts as within range."
            )
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            st.error(f"Could not read the confusion-matrix file: {exc}")
    else:
        st.warning(
            "Confusion matrices not found. Expected file: "
            f"{CONFUSION_PATH}. Run training again to generate it."
        )
