# UK Electricity Demand Data

This folder contains CSV files related to electricity demand in the UK. Below is a brief description of the data:

## File Description
- **demandata_"year" CSV Files**: Contain historical electricity demand data for various regions in the UK (raw download from [NESO](https://www.neso.energy/data-portal/historic-demand-data)).
- **demandataupdate**: Latest demand data report at the moment of this project download from [NESO](https://www.neso.energy/data-portal/daily-demand-update) (4/2025).
- **uk_demand_merged**: Data of the different years after cleaning and preprocessing.
- **uk_demand_merge_update**: 

## Usage
These files can be used for energy forecasting, trend analysis, and other data-driven insights.

## Notes
- The `API.py` script that runs when opening the Streamlit app checks `uk_demand_merge_update` and updates it.