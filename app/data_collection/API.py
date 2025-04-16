import requests
import pandas as pd
import os
import glob
import json

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


file_path = "../data"
demand_path = os.path.join(file_path, "electricity_demand")
	
# Exploring the data
uk_demand_path = os.path.join(demand_path, "uk")

file = os.path.join(uk_demand_path, 'demanddataupdate.csv')

# Read the file
df = pd.read_csv(file)
print(f'Update demand data loaded')

from utils import data_cleaning as dc

def collect_demand_data():
  
  resource_id = "177f6fa4-ae49-4182-81ea-0c6b35f26ca6"
  url = 'https://api.neso.energy/api/3/action/datastore_search_sql'
  
  sql = f'''
        SELECT 
          "SETTLEMENT_DATE", 
          "SETTLEMENT_PERIOD", 
          "ND", 
          "TSD",
          "FORECAST_OR_ACTUAL_INDICATOR"
        FROM "{resource_id}" 
        ORDER BY "SETTLEMENT_DATE" DESC, "SETTLEMENT_PERIOD" ASCE 
        LIMIT 10000
        '''
  
  params = {'sql': sql}

  response = requests.get(url, params=params)
  data = response.json()
  df = pd.DataFrame(data['result']['records'])

  return df

def filter_demand_data_update():
  uk_demand_update = dc.snake(df)
  
uk_demand_update_cleaned = uk_demand_update[["settlement_date", "settlement_period", "nd", "tsd", "forecast_actual_indicator"]]

# Convert to datetime format
uk_demand_update_cleaned = dc.convert_to_datetime(uk_demand_update_cleaned, columns=["settlement_date"]) 

# Filter the data to include only the last updates
uk_demand_update_cleaned = uk_demand_update_cleaned[(uk_demand_update_cleaned["forecast_actual_indicator"] == "A") & (uk_demand_update_cleaned["tsd"] > 500)]
uk_demand_update_cleaned = uk_demand_update_cleaned[uk_demand_update_cleaned["settlement_date"] > uk_demand_merged["settlement_date"].max()]
uk_demand_update_cleaned = uk_demand_update_cleaned.drop(columns=["forecast_actual_indicator"])


uk_demand_update_cleaned = dc.add_holiday_column(uk_demand_update_cleaned, bank_holidays) 
uk_demand_merged_update = pd.concat([uk_demand_merged, uk_demand_update_cleaned], ignore_index=True)
uk_demanduk_demand_merged_update_merged = uk_demand_merged_update.sort_values(by=["settlement_date", "settlement_period"])
uk_demand_merged_update = uk_demand_merged_update.reset_index(drop=True)

def collect_update_carbon_mix():
  
  resource_id = "f93d1835-75bc-43e5-84ad-12472b180a98"
  url = 'https://api.neso.energy/api/3/action/datastore_search_sql'
  
  sql = f'''
        SELECT 
          "SETTLEMENT_DATE", 
          "SETTLEMENT_PERIOD", 
          "ND", 
          "TSD",
          "FORECAST_OR_ACTUAL_INDICATOR"
        FROM "{resource_id}" 
        ORDER BY "SETTLEMENT_DATE" DESC, "SETTLEMENT_PERIOD" ASCE 
        LIMIT 10000
        '''
  
  params = {'sql': sql}

  response = requests.get(url, params=params)
  data = response.json()
  df = pd.DataFrame(data['result']['records'])

  return df
