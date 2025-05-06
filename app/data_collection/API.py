import requests
import pandas as pd
import os
import glob
import json

from utils import data_cleaning as dc

bank_holidays = ['01-01-2019', '19-04-2019', '22-04-2019', '06-05-2019', '27-05-2019',
                '26-08-2019', '25-12-2019', '26-12-2019', '01-01-2020', '10-04-2020',
                '13-04-2020', '08-05-2020', '25-05-2020', '31-08-2020', '25-12-2020',
                '28-12-2020', '01-01-2021', '02-04-2021', '05-04-2021', '03-05-2021',
                '31-05-2021', '30-08-2021', '27-12-2021', '28-12-2021','03-01-2022', 
                '15-04-2022', '18-04-2022', '02-05-2022', '03-06-2022', '29-08-2022',
                '26-12-2022', '27-12-2022', '02-01-2023', '07-04-2023', '10-04-2023', 
                '01-05-2023', '08-05-2023', '29-05-2023', '28-08-2023', '25-12-2023',
                '26-12-2023', '01-01-2024', '29-03-2024', '01-04-2024', '06-05-2024',
                '27-05-2024', '26-08-2024', '25-12-2024', '26-12-2024', '01-01-2025',
                '18-04-2025', '21-04-2025', '05-05-2025', '26-05-2025', '25-08-2025',
                '25-12-2025', '26-12-2025', '01-01-2026', '03-04-2026', '06-04-2026',
                '04-05-2026', '25-05-2026', '31-08-2026', '25-12-2026', '28-12-2026']

# Project directories
script_dir = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(script_dir, "../../data")
# Demand data path
demand_path = os.path.join(data_path, "electricity_demand")
uk_demand_path = os.path.join(demand_path, "uk")
# Carbon mix data path
carbon_mix_path = os.path.join(data_path, "carbon_intensity")
uk_carbon_mix_path = os.path.join(carbon_mix_path, "uk")

def collect_data(resource_id, SELECTED_COLUMNS, order_by):

  try:
    url = 'https://api.neso.energy/api/3/action/datastore_search_sql'
    
    sql = f'''
          SELECT 
            {SELECTED_COLUMNS}
          FROM "{resource_id}" 
          ORDER BY {order_by}
          LIMIT 10000
          '''
    
    params = {'sql': sql}

    response = requests.get(url, params=params)
    print("Response status code:", response.status_code)
    data = response.json()
    df = pd.DataFrame(data['result']['records'])

    return df, True
  except Exception as e:
    print("Error during API request or JSON parsing:", e)
    return pd.DataFrame(), False
  
def filter_demand_data_update(dataframe):

  # Load the existing merged data
  uk_demand_merged = pd.read_csv(os.path.join(data_path, "uk_demand_merged_update.csv"))
  
  # Copy the new data to avoid modifying the original dataframe
  df = dataframe.copy()

  # Convert columns to lowercase
  uk_demand_update = dc.snake(df)
  
  # Extract the relevant columns
  uk_demand_update_cleaned = uk_demand_update[["settlement_date", "settlement_period", "nd", "tsd", "forecast_actual_indicator"]]

  # Convert to datetime format
  uk_demand_update_cleaned = dc.convert_to_datetime(uk_demand_update_cleaned, columns=["settlement_date"]) 
  uk_demand_merged = dc.convert_to_datetime(uk_demand_merged, columns=["settlement_date"])

  # Filter the data to include only the last updates
  uk_demand_update_cleaned = uk_demand_update_cleaned[(uk_demand_update_cleaned["forecast_actual_indicator"] == "A") & (uk_demand_update_cleaned["tsd"] > 500)]

  last_date = uk_demand_merged["settlement_date"].max()
  last_settlement_period = uk_demand_merged[uk_demand_merged["settlement_date"] == last_date]["settlement_period"].max()

  if last_settlement_period < 48:
      uk_demand_update_cleaned = uk_demand_update_cleaned[
          (uk_demand_update_cleaned["settlement_date"] == last_date) & 
          (uk_demand_update_cleaned["settlement_period"] > last_settlement_period)
      ]
  else:
      uk_demand_update_cleaned = uk_demand_update_cleaned[
          uk_demand_update_cleaned["settlement_date"] > last_date
      ]
  
  if len(uk_demand_update_cleaned) == 0:
    print("No new data to update.")
    return uk_demand_merged
  else:
    print("New data available for update.")
    
    # Drop the forecast_actual_indicator column
    uk_demand_update_cleaned = uk_demand_update_cleaned.drop(columns=["forecast_actual_indicator"])

    # Add holiday column
    uk_demand_update_cleaned = dc.add_holiday_column(uk_demand_update_cleaned, bank_holidays) 

    # Concatenate the new data with the existing data
    uk_demand_merged_update = pd.concat([uk_demand_merged, uk_demand_update_cleaned], ignore_index=True)
    
    # Rewrite the existing file with the new data
    uk_demand_merged_update = uk_demand_merged_update.sort_values(by=["settlement_date", "settlement_period"])
    uk_demand_merged_update = uk_demand_merged_update.reset_index(drop=True)
    uk_demand_merged_update.to_csv(os.path.join(data_path, "uk_demand_merged_update.csv"), index=False)

    return uk_demand_merged_update

def filter_carbon_data_update(dataframe):

  # Load the existing data
  carbon_mix = pd.read_csv(os.path.join(data_path, "carbon_and_mix_update.csv"))
  
  # Copy the new data to avoid modifying the original dataframe
  df = dataframe.copy()

  # Drop NAN rows
  df = df.dropna()

  # Convert columns to lowercase
  carbon_mix_update = dc.snake(df)

  # Convert to datetime format
  carbon_mix = dc.convert_to_datetime(carbon_mix, columns=["settlement_date"])
  carbon_mix_update = dc.convert_to_datetime(carbon_mix_update, columns=["datetime"]) 

  # Drop the generation_perc column
  carbon_mix_update_cleaned = carbon_mix_update.drop(columns=["generation_perc"])

  # Dropping other columns that are not needed.
  carbon_mix_update_cleaned = carbon_mix_update_cleaned.drop(columns=[col for col in carbon_mix_update_cleaned.columns if 'perc' in col])

  # Extracting setellment period and settlement date from datetime
  carbon_mix_update_cleaned = dc.extract_settlement_period_and_date(carbon_mix_update_cleaned, "datetime")

  # Filter the data to include only the last updates
  last_date = carbon_mix["settlement_date"].max()
  print("Last date:", last_date)
  last_settlement_period = carbon_mix[carbon_mix["settlement_date"] == last_date]["settlement_period"].max()
  print("Last settlement period:", last_settlement_period)

  if last_settlement_period < 48:
      print("Filtering for last settlement period and subsequent dates")
      carbon_mix_update_cleaned = carbon_mix_update_cleaned[
          ((carbon_mix_update_cleaned["settlement_date"] == last_date) & 
           (carbon_mix_update_cleaned["settlement_period"] > last_settlement_period)) |
          (carbon_mix_update_cleaned["settlement_date"] > last_date)
      ]
  else:
      carbon_mix_update_cleaned = carbon_mix_update_cleaned[
          carbon_mix_update_cleaned["settlement_date"] > last_date
      ]
  
  if len(carbon_mix_update_cleaned) == 0:
    print("No new data to update.")
    return carbon_mix
  else:
    print("New data available for update.")

    numeric_columns = ['low_carbon', 'fossil', 'zero_carbon', 'renewable',
                       'nuclear', 'storage', 'hydro', 'wind_emb', 'imports', 'gas',
                       'carbon_intensity', 'coal', 'generation', 'other',
                       'biomass', 'wind', 'solar']

    for col in numeric_columns:
        if col in carbon_mix_update_cleaned.columns:
            
            # Convert to numeric, forcing errors to NaN
            carbon_mix_update_cleaned[col] = pd.to_numeric(carbon_mix_update_cleaned[col], errors='coerce')
        else:
            print(f"Column {col} not found in the dataframe.")
  
    # Add carbon columns
    carbon_mix_update_cleaned = dc.create_carbon_columns(carbon_mix_update_cleaned)

    # Concatenate the new data with the existing data
    carbon_mix_update_cleaned = carbon_mix_update_cleaned[numeric_columns + ["settlement_date", "settlement_period", "low_vs_fossil", 
                                                                             "zero_vs_fossil", "renewable_vs_fossil", "green_score"]]
    
    carbon_mix_update_cleaned_merge = pd.concat([carbon_mix, carbon_mix_update_cleaned], ignore_index=True)

    # Rewrite the existing file with the new data
    carbon_mix_update_cleaned_merge = carbon_mix_update_cleaned_merge.sort_values(by=["settlement_date", "settlement_period"])
    carbon_mix_update_cleaned_merge = carbon_mix_update_cleaned_merge.reset_index(drop=True)
    carbon_mix_update_cleaned_merge.to_csv(os.path.join(data_path, "carbon_and_mix_update.csv"), index=False)

    return carbon_mix_update_cleaned_merge

def update_database():
  # Collect the data for demand
  resource_id = "177f6fa4-ae49-4182-81ea-0c6b35f26ca6"
  SELECTED_COLUMNS = '''"SETTLEMENT_DATE", "SETTLEMENT_PERIOD", "ND", "TSD", "FORECAST_ACTUAL_INDICATOR"'''
  order_by = '''"SETTLEMENT_DATE" ASC, "SETTLEMENT_PERIOD" ASC'''
  # Merge with existing data
  uk_demand_update, respd = collect_data(resource_id, SELECTED_COLUMNS, order_by)
  
  if respd == True:
    # Filter the data
    uk_demand_merged_update = filter_demand_data_update(uk_demand_update)

  # Collect carbon mix data
  resource_id = "f93d1835-75bc-43e5-84ad-12472b180a98"
  SELECTED_COLUMNS = "*"
  order_by = '''"DATETIME" DESC'''
  carbon_mix_update, respc = collect_data(resource_id, SELECTED_COLUMNS, order_by)
  
  if respc == True:

    # Filter the carbon mix data
    carbon_mix_update_cleaned = filter_carbon_data_update(carbon_mix_update)

   
  # Merge the two dataframes
  data_uk_merged = pd.merge(uk_demand_merged_update, carbon_mix_update_cleaned, how="left", left_on=["settlement_date", "settlement_period"], right_on=["settlement_date", "settlement_period"])

  # Correcting time 
  data_uk_merged = dc.add_time(data_uk_merged, "settlement_date")

  # Saving the data to a CSV file
  data_uk_merged = dc.drop_nan_rows(data_uk_merged)
  data_uk_merged = data_uk_merged.sort_values(by=["settlement_date", "settlement_period"])
  data_uk_merged = data_uk_merged.reset_index(drop=True)
  data_uk_merged.to_csv(os.path.join(data_path, "data_uk_merged_generation_demand_update.csv"), index=False)