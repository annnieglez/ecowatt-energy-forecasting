'''This file performs an initial exploration of the data and outputs important details, 
    such as the number of rows and columns, data types, unique values, categorical columns, 
    and checks for null and duplicated values.'''


def initial_chk(data_frame):
    '''This function performs an initial exploration of the data and outputs important details.

    It checks:
        - The number of columns and rows
        - The data types of each column
        - The count of unique values in each column
        - Identifies potential categorical columns (columns with < 20 unique values)
        - Outputs the unique values count for categorical columns

    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame to explore.
    
    Returns:
        - None: This function prints the results directly and does not return a value.
    '''
       
    # Display the number of columns and rows
    print(f"Number of columns: {data_frame.shape[1]} and rows: {data_frame.shape[0]}")

    # Show data types of each column
    print("\nData types:")
    print(data_frame.dtypes)

    # Display the unique values count for each column
    print("\nUnique values count:")
    unique_values_count = data_frame.nunique()
    print(unique_values_count)

    # Identify categorical columns (those with less than 20 unique values)
    categorical_columns = unique_values_count[unique_values_count < 20].index
    print(f"\nThese columns appear to be categorical (less than 20 unique values):\n{categorical_columns}")

    # Show the unique value count for categorical columns
    print("\nUnique value count for categorical columns:")
    for col in categorical_columns:
        print('')
        print(data_frame[col].value_counts())


def check_null(data_frame):
    '''
    Check for NaN and missing values in each column and print the total per column.
    
    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame to check for null values.
    
    Returns:
        - None: This function prints the count of null values for each column and does not return a value.
    '''

    print("\nCount of null values:")
    print(data_frame.isnull().sum())

    print("\nCount of missing(" ") values:")
    print(data_frame.eq(" ").sum())    

def check_duplicated(data_frame):
    '''
    Check for duplicated values in the data frame and print the total.
    
    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame to check for duplicates.
    
    Returns:
        - None: This function prints the count of duplicated rows and does not return a value.
    '''

    print("\nCount of duplicated values:")
    print(data_frame.duplicated().sum())

def check(data_frame):
    '''
    A function to call all the functions for the data exploration.

    Parameters:
        - data_frame (pd.DataFrame): The input DataFrame to explore.
    
    Returns:
        - None: This function calls other functions and does not return a value.
    '''
    
    initial_chk(data_frame)
    check_null(data_frame)
    check_duplicated(data_frame)

def check_settlement_period(demand_dict):
    """
    For each year, return dates where settlement_period count is exactly 46 or 50.

    Parameters:
        - demand_dict (dict): Dictionary with year as key and DataFrame as value.

    Returns:
        - dict: Dictionary with years as keys and dicts containing lists of dates
                with 46 and 50 settlement periods.
    """
    result = {}

    for year, df in demand_dict.items():
        if 'settlement_period' in df.columns and 'settlement_date' in df.columns:
            # Group by date and count number of unique settlement_periods per day
            counts = df.groupby('settlement_date')['settlement_period'].nunique()

            # Find dates where count is exactly 46 or 50
            dates_46 = counts[counts == 46].index
            dates_50 = counts[counts == 50].index

            result[year] = {
                '46_periods': dates_46,
                '50_periods': dates_50
            }

    return result

