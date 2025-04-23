'''This file groups functions for data cleaning, such as 
    formatting columns to a consistent format.'''

import pandas as pd
from datetime import datetime

def extract_columns(demand_dict, columns):
    """
    Extract specific columns from a dictionary of DataFrames.

    Parameters:
        - demand_dict (dict): Dictionary containing DataFrames.
        - columns (list): List of columns to extract.

    Returns:
        - dict: Dictionary with DataFrames containing only the specified columns.
    """
    
    extracted_dict = {}
    for year, df in demand_dict.items():
        extracted_dict[year] = df[columns]
        print(f'Columns {columns} extracted from data {year}')
    
    return extracted_dict

def snake(data_frame):
    '''
    Converts column names to snake_case (lowercase with underscores).
    
    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame whose columns need to be formatted.

    Returns:
        - pd.DataFrame: DataFrame with column names in snake_case.
    '''

    data_frame.columns = [column.lower().replace(" ", "_").replace(")", "").replace("(", "") for column in data_frame.columns]

    return data_frame

def convert_to_datetime(data_frame, columns):
    '''
    Converts specified columns to datetime.date format using multiple known formats.
    
    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame.
        - columns (str or list): Column name or list of column names to convert to datetime.
    
    Returns:
        - pd.DataFrame: The DataFrame with specified columns converted to datetime.date.
    '''
    
    if isinstance(columns, str):
        columns = [columns]

    formats_to_try = [
        "%d-%b-%Y",     # 27-Oct-2019 or 27-OCT-2019 (4-digit year)
        "%d-%b-%y",     # 31-Dec-23 (2-digit year)
        "%Y-%m-%d",     # 2025-03-06 (ISO format)
        "%Y-%m-%dT%H:%M:%S",  # 2009-01-01T00:00:00 (with 'T' separator)
        "%Y-%m-%dT%H:%M",     # 2019-01-01T00:00 (newly added)
        "%Y-%m-%d %H:%M:%S"
    ]

    def try_parsing_date(text):
        original = str(text).strip().replace('"', '').replace("'", "")
        
        # Convert the month abbreviation to title case (e.g., "DEC" -> "Dec")
        original = original.title()

        for fmt in formats_to_try:
            # Try parsing with each format, catching any exceptions that occur
            try:
                return pd.to_datetime(original, format=fmt)
            except ValueError:
                continue  # If a format fails, continue trying the next format
        print(f"Warning: Unable to parse date '{original}'. Returning NaT.") 
        return pd.NaT  # Return NaT if nothing matches

    data_frame_copy = data_frame.copy()

    for col in columns:
        data_frame_copy[col] = data_frame_copy[col].apply(try_parsing_date)
        data_frame_copy[col] = data_frame_copy[col]

    return data_frame_copy

def add_holiday_column(df, holidays):
    """
    Adds a binary column 'is_bank_holiday' indicating if the settlement_date is a UK bank holiday.

    Parameters:
        - df (DataFrame): The demand data.
        - holidays (list): List of bank holiday dates in 'DD-MM-YYYY' format.

    Returns:
        - DataFrame: Original DataFrame with added 'is_bank_holiday' column.
    """
    # Convert strings to datetime.date
    holidays = [datetime.strptime(date, "%d-%m-%Y").date() for date in holidays]

    # Add new column
    df['is_bank_holiday'] = df['settlement_date'].dt.date.isin(holidays)

    return df

def extract_settlement_period_and_date(data_frame, column):
    '''
    Extracts settlement period and date from the specified column.
    
    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame containing the settlement period column.
        - column (str): The name of the column to extract settlement period and date from.
    
    Returns:
        - pd.DataFrame: The modified DataFrame with new columns for settlement period and date.
    '''

    df = data_frame.copy()

    # Ensure the column is in datetime format
    df[column] = pd.to_datetime(df[column])

    # Extract the settlement date (date only)
    df['settlement_date'] = df[column].dt.normalize()

    # Calculate the settlement period (each period is 30 minutes, so: hour * 2 + minute / 30)
    df['settlement_period'] = df[column].dt.hour * 2 + df[column].dt.minute // 30 + 1

    # Drop the original datetime column
    df.drop(columns=[column], inplace=True)

    return df

def preprocess_datetime(data_frame, column):
    '''
    Extracts time-based features from column, including a season column based on the month.
    
    Parameters:
        - data_frame (pd.DataFrame): The dataset containing the date column.
    
    Returns:
        - pd.DataFrame: The modified dataframe with new time-based columns.
    '''

    df = data_frame.copy()

    # Mapping days to numbers
    day_mapping = {
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6,
        'Sunday': 7
    }

    df['year'] = df[column].dt.year
    df['day'] = df[column].dt.day
    df['month'] = df[column].dt.month
    df['day_of_week'] = df[column].dt.day_name()
    df['day_of_week'] = df['day_of_week'].map(day_mapping)

    # Add a season column based on the month
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Autumn'

    df['season'] = df['month'].apply(get_season)

    # Ensure 'settlement_date' is a datetime (date only)
    df['settlement_date'] = pd.to_datetime(df['settlement_date']).dt.date

    # Create a timedelta column based on settlement_period (each period is 30 min)
    df['settlement_time'] = pd.to_timedelta((df['settlement_period'] - 1) * 30, unit='m')

    # Combine date and time into full datetime
    df['settlement_date'] = pd.to_datetime(df['settlement_date'].astype(str)) + df['settlement_time']

    # Drop the helper column if not needed
    df.drop(columns='settlement_time', inplace=True)

    # Optional: sort by new datetime
    df = df.sort_values(by='settlement_date')

    return df

def add_time(data_frame, column):
    '''
    Extracts time-based features from column, including a season column based on the month.
    
    Parameters:
        - data_frame (pd.DataFrame): The dataset containing the date column.
    
    Returns:
        - pd.DataFrame: The modified dataframe with new time-based columns.
    '''

    df = data_frame.copy()

    # Ensure 'settlement_date' is a datetime (date only)
    df['settlement_date'] = pd.to_datetime(df['settlement_date']).dt.date

    # Create a timedelta column based on settlement_period (each period is 30 min)
    df['settlement_time'] = pd.to_timedelta((df['settlement_period'] - 1) * 30, unit='m')

    # Combine date and time into full datetime
    df['settlement_date'] = pd.to_datetime(df['settlement_date'].astype(str)) + df['settlement_time']

    # Drop the helper column if not needed
    df.drop(columns='settlement_time', inplace=True)

    # Optional: sort by new datetime
    df = df.sort_values(by=["settlement_date", "settlement_period"])

    return df

def adjust_dst_periods(df):
    
    # Iterate through the rows to identify DST changes (usually in March and October)
    for date in df['settlement_date'].unique():
        
        # Check if the length of data for the given date is 46 (indicating DST change)
        if len(df.loc[(df['settlement_date'] == date)]) == 46:
            print(f"Adjusting periods for date: {date}")
            # If there are 46 periods, it means DST has been applied
            
            # Add a temporary column to store the updated settlement_period values
            df['temp_settlement_period'] = df['settlement_period']

            # Shift periods from 3 to 5, 4 to 6, etc., for periods 3 to 46
            for period in range(3, 47):
                df.loc[(df['settlement_date'] == date) & (df['settlement_period'] == period), 'temp_settlement_period'] = period + 2

            # After the loop, update the original column with the new values
            df['settlement_period'] = df['temp_settlement_period']

            # Drop the temporary column
            df.drop('temp_settlement_period', axis=1, inplace=True)

            # Now add rows for periods 2 and 3 (new periods after the shift)
            new_data = [
                {'settlement_date': date, 'settlement_period': 3, 'nd': None, 'tsd': None},
                {'settlement_date': date, 'settlement_period': 4, 'nd': None, 'tsd': None}
            ]

            # Add the new rows to the DataFrame
            df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)

            # Calculate the average for periods 2 and 3 for the DST change
            for period in [3, 4]:
                # Calculate the mean for 'ND' and 'TSD' columns using the last 3 weeks of data for the same period
                avg_nd_value = df.loc[(df['settlement_date'] < date) & 
                                          (df['settlement_period'] == period), 'nd'].tail(21).mean()
                avg_tsd_value = df.loc[(df['settlement_date'] < date) & 
                                           (df['settlement_period'] == period), 'tsd'].tail(21).mean()

                # Assign the calculated average to the current date and period for both 'ND' and 'TSD'
                df.loc[(df['settlement_date'] == date) & (df['settlement_period'] == period), 'nd'] = int(avg_nd_value)
                df.loc[(df['settlement_date'] == date) & (df['settlement_period'] == period), 'tsd'] = int(avg_tsd_value)


            print(f"New legth for date {date} is {len(df.loc[(df['settlement_date'] == date)])}")

        # Check if the length of data for the given date is 50 (indicating the DST end)
        if len(df.loc[(df['settlement_date'] == date)]) == 50:
            print(f"Adjusting periods for date: {date}")

            # Implement the logic to adjust periods for DST end (October)
            for period in range(7, 51):
                df.loc[(df['settlement_date'] == date) & (df['settlement_period'] == period), 'settlement_period'] = period - 2

            # Step 3: Handle duplicates of 5 and 6
            # Find the rows where settlement_period is 3, 5, and 4, 6
            rows_3 = df[(df['settlement_date'] == date) & (df['settlement_period'] == 3)]
            rows_5 = df[(df['settlement_date'] == date) & (df['settlement_period'] == 5)]
            rows_4 = df[(df['settlement_date'] == date) & (df['settlement_period'] == 4)]
            rows_6 = df[(df['settlement_date'] == date) & (df['settlement_period'] == 6)]

            avg_nd_3_5 = (rows_3['nd'].values[0] + rows_5['nd'].values[0]) / 2
            avg_tsd_3_5 = (rows_3['tsd'].values[0] + rows_5['tsd'].values[0]) / 2

            avg_nd_4_6 = (rows_4['nd'].values[0] + rows_6['nd'].values[0]) / 2
            avg_tsd_4_6 = (rows_4['tsd'].values[0] + rows_6['tsd'].values[0]) / 2

            # Assign these averages to settlement_period 3 and 4
            df.loc[(df['settlement_date'] == date) & (df['settlement_period'] == 3), 'nd'] = int(avg_nd_3_5)
            df.loc[(df['settlement_date'] == date) & (df['settlement_period'] == 3), 'tsd'] = int(avg_tsd_3_5)

            df.loc[(df['settlement_date'] == date) & (df['settlement_period'] == 4), 'nd'] = int(avg_nd_4_6)
            df.loc[(df['settlement_date'] == date) & (df['settlement_period'] == 4), 'tsd'] = int(avg_tsd_4_6)

            # Remove the first occurrences of 5 and 6
            df = df.drop(rows_5.index[0])  # Drop first 5
            df = df.drop(rows_6.index[0])  # Drop first 6

            print(f"New legth for date {date} is {len(df.loc[(df['settlement_date'] == date)])}")

    df['nd'] = pd.to_numeric(df['nd'], errors='coerce') 
    df['tsd'] = pd.to_numeric(df['tsd'], errors='coerce')

    return df

def resample(data_frame, col = 'time'):
    weather_copy = data_frame.copy()

    # Dummy row at 23:30:00 with NaNs (will be filled by ffill)
    last_time = weather_copy[col].max()
    next_half_hour = last_time + pd.Timedelta(minutes=60)

    dummy_row = pd.DataFrame([{col: next_half_hour}])
    weather_copy = pd.concat([weather_copy, dummy_row], ignore_index=True)

    # Now resample
    data_frame = weather_copy.set_index(col).resample('30min').ffill().reset_index()
    data_frame = data_frame.drop(data_frame.index[-1])

    return data_frame

def one_hot_encode(data_frame, column):
    '''
    One-hot encodes a specified column in the DataFrame.
    
    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame.
        - column (str): The name of the column to one-hot encode.
    
    Returns:
        - pd.DataFrame: The modified DataFrame with one-hot encoded columns.
    '''

    # Create dummy variables for the specified column
    dummies = pd.get_dummies(data_frame[column], prefix=column)
    dummies = dummies.astype(int)  # Convert to integer type
    # Concatenate the original DataFrame with the new dummy variables
    data_frame = pd.concat([data_frame, dummies], axis=1)

    # Drop the original column
    data_frame.drop(column, axis=1, inplace=True)

    return data_frame

def create_carbon_columns(data_frame):
    '''
    Creates new columns for carbon intensity based on the original column.
    
    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame.
    
    Returns:
        - pd.DataFrame: The modified DataFrame with new carbon intensity columns.
    '''

    df = data_frame.copy()

    # Create new columns based on the original column

    df['low_vs_fossil'] = df['low_carbon'] / df['fossil']
    df['zero_vs_fossil'] = df['zero_carbon'] / df['fossil']
    df['renewable_vs_fossil'] = df['renewable'] / df['fossil']
    df['green_score'] = (df['solar'] + df['wind']) / df['carbon_intensity']

    return df

def create_rolling_features(data_frame, columns, type= 'hours', window_size=48, pos = 10):
    '''
    Creates rolling mean and standard deviation features for specified columns.
    
    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame.
        - columns (list): List of column names to create rolling features for.
        - window_size (int): Size of the rolling window (default is 48).
    
    Returns:
        - pd.DataFrame: The modified DataFrame with new rolling features.
    '''

    df = data_frame.copy()

    # Create rolling mean and std features
    for column in columns:
        if type == 'weeks':
            window = window_size*7*48
        elif type == 'hours':
            window = window_size * 2
        elif type == 'days':
            window = window_size * 48
        elif type == 'months':
            window = window_size * 48 * 30
        elif type == 'years':
            window = window_size * 48 * 365
        else:
            raise ValueError("Invalid type. Choose from 'weeks', 'hours', 'days', 'months', or 'years'.")
        
        shift_label = ["30_min", "1_hour", "2_hour", "3_hours", "6_hours", "12_hours", "1_day", "2_days", "3_days", "5_days", "1_week", "2_week"]
        shift_size = [1, 2, 4, 6, 12, 24, 48, 96, 144, 240, 336, 672]

        df[f'{column}_rolling_{window_size}_{type}_for_{shift_label[pos]}'] = df[column].rolling(window=window).mean().shift(shift_size[pos])
        df[f'{column}_rolling_std_{window_size}_{type}_for_{shift_label[pos]}'] = df[column].rolling(window=window).std().shift(shift_size[pos])
        df[f'{column}_rolling_max_{window_size}_{type}_for_{shift_label[pos]}'] = df[column].rolling(window=window).max().shift(shift_size[pos])
        df[f'{column}_rolling_min_{window_size}_{type}_for_{shift_label[pos]}'] = df[column].rolling(window=window).min().shift(shift_size[pos])
    
    return df

def check_time_increase(data_frame, time_col, price_col):
    '''
    Checks if the time column increases by one hour. If not, it fills in missing rows with average prices.
    
    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame with time and price columns.
        - time_col (str): The name of the time column.
        - price_col (str): The name of the price column.
    
    Returns:
        - pd.DataFrame: The modified DataFrame with filled missing rows and adjusted prices.
    '''

    df = data_frame.copy()
    df2 = df.copy()

    # Sort the DataFrame by time
    df.sort_values(by=[time_col], inplace=True)

    # Check for missing hours and duplicates
    for i in range(1, len(df)):
        current_time = df.iloc[i][time_col]
        previous_time = df.iloc[i - 1][time_col]

        # Check if the time difference is greater than 1 hour
        if current_time - previous_time > pd.Timedelta(hours=1):
            # Calculate the number of missing hours
            missing_hours = int((current_time - previous_time).total_seconds() / 3600) - 1

            # Create new rows for the missing hours
            for j in range(1, missing_hours + 1):
                new_time = previous_time + pd.Timedelta(hours=j)
                # Calculate the average price for the previous 3 weeks
                avg_price = df[(df[time_col] < new_time) & (df[time_col] >= new_time - pd.Timedelta(weeks=3))][price_col].mean()
                new_row = {time_col: new_time, price_col: avg_price}
                df2 = pd.concat([df2, pd.DataFrame([new_row])], ignore_index=False)

                print(f"Added missing row for time: {new_time} with average price: {avg_price}")
        elif current_time - previous_time == pd.Timedelta(hours=0):
            # If the time is duplicated, calculate the average price and keep one row
            avg_price = (df.iloc[i][price_col] + df.iloc[i - 1][price_col]) / 2
            prev_index = df.index[i - 1]
            dup_index = df.index[i]
            df2.at[prev_index, price_col] = avg_price
            df2.drop(index=dup_index, inplace=True)
            print(f"Removed duplicate row for time: {current_time} and set average price: {avg_price}")

    df2.sort_values(by=[time_col], inplace=True)
    return df2.reset_index(drop=True)

def check_time_increase_in_weather(data_frame, time_col):
    '''
    Checks if the time column increases by one hour. If not, it fills in missing rows with average prices.
    
    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame with time and price columns.
        - time_col (str): The name of the time column.
        - price_col (str): The name of the price column.
    
    Returns:
        - pd.DataFrame: The modified DataFrame with filled missing rows and adjusted prices.
    '''

    df = data_frame.copy()
    df2 = df.copy()

    # Remove timezone for logic checks
    df[time_col] = pd.to_datetime(df[time_col]).dt.tz_localize(None)
    df2[time_col] = pd.to_datetime(df2[time_col]).dt.tz_localize(None)

    # Sort by time
    df.sort_values(by=[time_col], inplace=True)
    df2.sort_values(by=[time_col], inplace=True)

    # Get numeric columns to process
    numeric_cols = df.drop(columns=[time_col]).columns.tolist()

    # Loop through and check for time issues
    for i in range(1, len(df)):
        current_time = df.iloc[i][time_col]
        previous_time = df.iloc[i - 1][time_col]

        # Case 1: Missing hour(s)
        if current_time - previous_time > pd.Timedelta(hours=1):
            missing_hours = int((current_time - previous_time).total_seconds() / 3600) - 1
            for j in range(1, missing_hours + 1):
                new_time = previous_time + pd.Timedelta(hours=j)
                new_row = {time_col: new_time}

                for col in numeric_cols:
                    avg_val = df[
                        (df[time_col] < new_time) &
                        (df[time_col] >= new_time - pd.Timedelta(weeks=3))
                    ][col].mean()
                    new_row[col] = avg_val

                df2 = pd.concat([df2, pd.DataFrame([new_row])], ignore_index=False)
                print(f"🕑 Added missing row for: {new_time} → interpolated values")

        # Case 2: Duplicate time
        elif current_time == previous_time:
            prev_index = df.index[i - 1]
            dup_index = df.index[i]

            for col in numeric_cols:
                avg_val = (df.iloc[i][col] + df.iloc[i - 1][col]) / 2
                df2.at[prev_index, col] = avg_val

            df2.drop(index=dup_index, inplace=True)
            print(f"⚠️ Removed duplicate for time: {current_time} → averaged values")

    # Final sort & reset index
    df2.sort_values(by=[time_col], inplace=True)
    return df2.reset_index(drop=True)



def create_lag_features(data_frame, columns, type= 'hours', window_size=48,pos = 0):

    df = data_frame.copy()

    # Create rolling mean and std features
    for column in columns:
        if type == 'weeks':
            window = window_size*7*48
        elif type == 'hours':
            window = window_size * 2
        elif type == 'days':
            window =window_size * 48
        elif type == 'months':
            window = window_size * 48 * 30
        elif type == 'years':
            window = window_size * 48 * 365
        else:
            raise ValueError("Invalid type. Choose from 'weeks', 'hours', 'days', 'months', or 'years'.")
        

        shift_label = ["30_min", "1_hour", "2_hour", "3_hours", "6_hours", "12_hours", "1_day", "2_days", "3_days", "5_days", "1_week", "2_week"]
        shift_size = [1, 2, 4, 6, 12, 24, 48, 96, 144, 240, 336, 672]

        df[f'{column}_lag_{window_size}_{type}_for_{shift_label[pos]}'] = df[column].shift(shift_size[pos]).shift(window)    

    return df

def drop_nan_rows(data_frame):
    """
    Drop rows with NaN values from the DataFrame and return the number of rows dropped.

    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame to clean.

    Returns:
        - int: The number of rows dropped.
    """
    initial_row_count = data_frame.shape[0]
    cleaned_data_frame = data_frame.dropna()
    final_row_count = cleaned_data_frame.shape[0]

    rows_dropped = initial_row_count - final_row_count
    print(f"Number of rows dropped due to NaN values: {rows_dropped}")

    return cleaned_data_frame