"""Open the official CGWB/NWDP groundwater dataset page."""
import webbrowser
from config import DATA_DIR, DATASET_PATH

URL = "https://nwdp.nwic.gov.in/en/dataset/ground-water-quality-manual-chemical-parameters-cgwb-f-gfg"

if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("Official CGWB groundwater chemical-parameter dataset:")
    print(URL)
    print("\nDownload the West Bengal (1961-2025) Manual CSV resource.")
    print(f"Save it as: {DATASET_PATH}")
    webbrowser.open(URL)
