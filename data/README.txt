DATASET SETUP

1. Download the West Bengal resource from the CGWB/National Water Data Portal:
   https://nwdp.nwic.gov.in/en/dataset/ground-water-quality-manual-chemical-parameters-cgwb-f-gfg
2. Select the resource named similar to:
   Ground Water Quality Chemical Parameters CGWB West Bengal (1961 - 2025) Manual CSV
3. Save the downloaded file in this folder as:
   cgwb_west_bengal_groundwater.csv
4. Run inspect_data.bat before training.

The CSV is intentionally not bundled or committed. Nitrate unit information in the column header is checked by the code. If the header does not state the nitrate basis, confirm it from the resource metadata before setting NITRATE_BASIS_OVERRIDE in config.py.
