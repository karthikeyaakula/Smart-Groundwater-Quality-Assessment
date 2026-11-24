"""Inspect the Andhra Pradesh groundwater CSV and pH-target readiness."""
import json
from data_utils import find_dataset_file, read_csv_safely, load_and_profile
from data_utils import numeric_series, detect_ph_column, normalize_column_name

def main():
    path = find_dataset_file()
    if path is None:
        raise FileNotFoundError("Put the Andhra Pradesh CGWB CSV in the project's data folder.")
    raw = read_csv_safely(path)
    print(f"File: {path}")
    print(f"Rows: {len(raw):,}")
    print(f"Columns: {len(raw.columns)}")
    print("\nOriginal column names:")
    for col in raw.columns:
        print(f" - {col}")
    mapping = {str(c): normalize_column_name(c) for c in raw.columns}
    original, normalized = detect_ph_column(mapping)
    ph = numeric_series(raw[original])
    print(f"\nDetected pH column: {original}")
    print(f"Numeric pH readings: {int(ph.notna().sum()):,} ({ph.notna().mean():.1%})")
    if ph.notna().any():
        print(f"pH minimum: {ph.min():.4f}")
        print(f"pH maximum: {ph.max():.4f}")
        print(f"Within 6.5–8.5: {int(ph.between(6.5, 8.5, inclusive='both').sum()):,}")
        print(f"Outside 6.5–8.5: {int(((ph < 6.5) | (ph > 8.5)).sum()):,}")
    try:
        df, features, locations, dates, metadata = load_and_profile(path)
        print("\nTRAINING READINESS")
        print(json.dumps(metadata, indent=2, default=str))
        print(f"\nSelected predictors ({len(features)}): {features}")
    except Exception as exc:
        print(f"\nTraining readiness check failed: {exc}")
        raise

if __name__ == "__main__":
    main()
