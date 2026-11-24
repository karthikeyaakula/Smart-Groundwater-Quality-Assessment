"""Load, clean and prepare Andhra Pradesh groundwater data for pH compliance."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd

from config import (
    DATA_DIR, DATASET_PATH, MAX_FEATURE_MISSING_SHARE, MIN_NUMERIC_COVERAGE,
    PH_MIN_ACCEPTABLE, PH_MAX_ACCEPTABLE,
)

META_TOKENS = {
    "id", "code", "serial", "sl", "no", "sample", "station", "well", "site",
    "name", "state", "district", "block", "village", "tehsil", "taluk", "mandal",
    "location", "latitude", "longitude", "lat", "long", "easting", "northing",
    "date", "time", "year", "month", "season", "remark", "comment", "address",
    "agency", "department", "source", "basin", "river", "tributary",
}
LOCATION_TOKENS = {
    "state", "district", "block", "village", "tehsil", "taluk", "mandal",
    "station", "location", "site", "well", "latitude", "longitude", "lat", "long",
}
DATE_TOKENS = {"date", "time", "year", "period", "season"}

def normalize_column_name(value: Any) -> str:
    s = str(value).strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_") or "unnamed_column"

def find_dataset_file() -> Path | None:
    if DATASET_PATH.is_file():
        return DATASET_PATH
    if not DATA_DIR.exists():
        return None
    candidates = sorted(p for p in DATA_DIR.glob("*.csv") if p.is_file())
    return candidates[0] if len(candidates) == 1 else None

def read_csv_safely(path: Path) -> pd.DataFrame:
    errors = []
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            df = pd.read_csv(path, encoding=enc, low_memory=False)
            if df.shape[1] == 1:
                for sep in (";", "\t", "|"):
                    alt = pd.read_csv(path, encoding=enc, sep=sep, low_memory=False)
                    if alt.shape[1] > 1:
                        df = alt
                        break
            if df.empty or df.shape[1] < 2:
                raise ValueError("CSV is empty or has fewer than two columns.")
            return df
        except Exception as exc:
            errors.append(f"{enc}: {exc}")
    raise ValueError("Could not read CSV: " + " | ".join(errors))

def numeric_series(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.strip()
    s = s.replace({
        "": pd.NA, "-": pd.NA, "--": pd.NA, "—": pd.NA, "–": pd.NA,
        "NA": pd.NA, "N/A": pd.NA, "n/a": pd.NA, "na": pd.NA,
        "NULL": pd.NA, "null": pd.NA, "BDL": pd.NA, "bdl": pd.NA,
        "Below Detection Limit": pd.NA, "#N/A": pd.NA,
    })
    s = s.str.replace(",", "", regex=False)
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)

def _has_token(name: str, tokens: set[str]) -> bool:
    return bool(set(name.split("_")) & tokens)

def detect_ph_column(original_to_normalized: dict[str, str]) -> tuple[str, str]:
    matches = []
    for original, normalized in original_to_normalized.items():
        # Match explicit pH token or the full phrase. Do not mistake phosphate for pH.
        if re.search(r"\bp\s*h\b", str(original), flags=re.I) or "potential_of_hydrogen" in normalized:
            matches.append((str(original), normalized))
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one pH measurement column; found {[m[0] for m in matches]}. "
            "Check the CSV headings before training."
        )
    return matches[0]

def load_and_profile(path: Path | None = None):
    path = path or find_dataset_file()
    if path is None:
        raise FileNotFoundError(
            f"No unambiguous CSV found in {DATA_DIR}. Expected {DATASET_PATH.name}."
        )
    raw = read_csv_safely(path)
    raw_rows = len(raw)
    original_to_normalized = {}
    names, seen = [], {}
    for original in raw.columns:
        base = normalize_column_name(original)
        seen[base] = seen.get(base, 0) + 1
        unique = base if seen[base] == 1 else f"{base}_{seen[base]}"
        original_to_normalized[str(original)] = unique
        names.append(unique)
    raw.columns = names
    raw = raw.loc[:, ~raw.columns.str.startswith("unnamed_column")].copy()

    original_ph_heading, ph_col = detect_ph_column(original_to_normalized)
    date_cols = [c for c in raw.columns if _has_token(c, DATE_TOKENS)]
    location_cols = [c for c in raw.columns if _has_token(c, LOCATION_TOKENS)]
    excluded_meta = set(date_cols + location_cols)

    numeric = {}
    for col in raw.columns:
        if col in excluded_meta or _has_token(col, META_TOKENS):
            continue
        values = numeric_series(raw[col])
        nonempty = max(int(raw[col].notna().sum()), 1)
        coverage = float(values.notna().sum()) / nonempty
        if coverage >= MIN_NUMERIC_COVERAGE and values.nunique(dropna=True) >= 3:
            numeric[col] = values
    numeric[ph_col] = numeric_series(raw[ph_col])

    if int(numeric[ph_col].notna().sum()) == 0:
        raise ValueError(f"pH column '{original_ph_heading}' contains no numeric readings.")

    df = raw.copy()
    for col, values in numeric.items():
        df[col] = values
    valid = df.loc[df[ph_col].notna()].copy()
    valid["ph_compliance"] = (
        (valid[ph_col] < PH_MIN_ACCEPTABLE) | (valid[ph_col] > PH_MAX_ACCEPTABLE)
    ).astype(int)

    features = [
        col for col, values in numeric.items()
        if col != ph_col
        and values.notna().mean() >= (1.0 - MAX_FEATURE_MISSING_SHARE)
        and values.nunique(dropna=True) > 1
    ]
    if len(features) < 2:
        raise ValueError(
            "Fewer than two usable non-pH chemistry predictors remain. "
            "Review coverage before relaxing the missingness threshold."
        )

    before_dedup = len(valid)
    duplicate_count = int(valid.duplicated().sum())
    valid = valid.drop_duplicates().reset_index(drop=True)
    counts = valid["ph_compliance"].value_counts().sort_index()
    if len(counts) != 2:
        raise ValueError(
            "The pH compliance target contains only one class after cleaning. "
            f"Counts: {counts.to_dict()}. A two-class supervised comparison cannot run."
        )
    if int(counts.min()) < 5:
        raise ValueError(
            f"The minority pH class has only {int(counts.min())} records; "
            "there are too few examples for a reliable stratified comparison."
        )

    station_col = next(
        (c for c in location_cols if any(t in c for t in ("station", "well", "site"))),
        None,
    )
    metadata = {
        "source_file": path.name,
        "state_scope": "Andhra Pradesh dataset selected by the user",
        "raw_rows": int(raw_rows),
        "rows_with_valid_ph": int(before_dedup),
        "duplicate_rows_removed": duplicate_count,
        "records_used": int(len(valid)),
        "target_column": ph_col,
        "source_target_heading": original_ph_heading,
        "target_name": "ph_compliance",
        "target_definition": f"1 if pH < {PH_MIN_ACCEPTABLE} or pH > {PH_MAX_ACCEPTABLE}; otherwise 0",
        "ph_min_acceptable": PH_MIN_ACCEPTABLE,
        "ph_max_acceptable": PH_MAX_ACCEPTABLE,
        "target_counts": {str(int(k)): int(v) for k, v in counts.items()},
        "predictor_features": features,
        "location_columns": location_cols,
        "station_group_column": station_col,
        "date_columns": date_cols,
        "missing_predictor_cells": int(valid[features].isna().sum().sum()),
        "missing_by_feature": {c: int(valid[c].isna().sum()) for c in features},
        "ph_missing_or_censored_dropped": int(raw_rows - int(numeric[ph_col].notna().sum())),
        "leakage_note": "Measured pH is used only to derive the target and is excluded from predictors.",
        "scope_limitation": "This is pH-range compliance screening only, not an overall drinking-water potability assessment.",
    }
    return valid, features, location_cols, date_cols, metadata
