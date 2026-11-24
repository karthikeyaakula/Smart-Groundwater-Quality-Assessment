"""Project configuration for Andhra Pradesh groundwater pH-compliance screening."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATASET_FILENAME = "gwq_chemical_parameter_manual_cgwb_ap_1961_2025.csv"
DATASET_PATH = DATA_DIR / DATASET_FILENAME

# BIS IS 10500:2012 acceptable pH range; no relaxation outside this range.
PH_MIN_ACCEPTABLE = 6.5
PH_MAX_ACCEPTABLE = 8.5

MIN_NUMERIC_COVERAGE = 0.30
MAX_FEATURE_MISSING_SHARE = 0.70
TEST_SIZE = 0.20
RANDOM_STATE = 42
MAX_CV_FOLDS = 5
RANDOM_FOREST_TREES = 160
MAX_WORKERS = 4
