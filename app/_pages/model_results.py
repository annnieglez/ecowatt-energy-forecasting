import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
import os
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, root_mean_squared_error
import numpy as np
import datetime

# Test split datetime for demonstration purposes
split_datetime = pd.to_datetime("2023-05-21 15:00:00") 

# Project directories
script_dir = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(script_dir, "../../data")
model_prediction_file = "preds_data_up_to_2_days.csv"

@st.cache_data() 
def get_data_frame():
    df = pd.read_csv(os.path.join(data_path, model_prediction_file))
    df.reset_index(inplace=True)
    print(df.head())
    df["settlement_date"] = pd.to_datetime(df["settlement_date"])
    return df

@st.cache_resource(show_spinner=False)
def plot_actual_vs_pred(df, target, zoom = False, word="30_min", key = "h"):

    chart_df = df[["settlement_date", target, f"{target}_predicted_{word}"]].copy()

    chart_df["Set"] = chart_df["settlement_date"].apply(
        lambda x: "Test" if x >= split_datetime else "Train"
    )

    chart_df = chart_df.melt(id_vars=["settlement_date", "Set"], 
                             value_vars=[target, f"{target}_predicted_{word}"],
                             var_name="Type", value_name="Value")
    
    # Define a color map for clarity
    color_map = {
        "Actual": "white",        # Real observed data
        "Prediction (Train)": "blue",   # Model prediction on train
        "Prediction (Test)": "orange"   # Model prediction on test
    }

    # Rename values in 'Type' for cleaner legend
    chart_df["Type"] = chart_df["Type"].replace({
        target: "Actual",            # Actual data
        f"{target}_predicted_{word}": "Prediction"  
    })

    # Separate the test and train predictions into different colors
    chart_df.loc[(chart_df["Set"] == "Train") & (chart_df["Type"] == "Prediction"), "Type"] = "Prediction (Train)"
    chart_df.loc[(chart_df["Set"] == "Test") & (chart_df["Type"] == "Prediction"), "Type"] = "Prediction (Test)"

    y_axis_title = ""
    if target == "nd" or target == "solar" or target == "wind":
        y_axis_title = "Generation (MW)"
        if target == "nd":
            text = "National Demand"
        elif target == "solar":
            text = "Solar Generation"
        elif target == "wind":
            text = "Wind Generation"
    else:
        y_axis_title = "Carbon Intensity (gCO2/kWh)"
        text = "Carbon Intensity"

    # Create Plotly Express line chart
    fig = px.line(
        chart_df,
        x="settlement_date",
        y="Value",
        color="Type",
        labels={"settlement_date": "Date", "Value": y_axis_title},
        color_discrete_map=color_map
    )

    # Style updates
    if not zoom:
        fig.update_layout(
            showlegend=True,
            legend_title_text=None,
            xaxis_title='Date',
            title=dict(
                text=text,  # Customizable plot title
                font=dict(family="Montserrat", size=20, color="white"),
                x=0.5,  # Centering the title
                xanchor="center"
            ),
            font=dict(family="Montserrat", color="black"),
            hovermode='x unified'
        )
    else:
        fig.update_layout(
            showlegend=True,
            legend_title_text=None,
            xaxis_title='Date',
            font=dict(family="Montserrat", color="black"),
            hovermode='x unified'
        )        

    # Customize the legend font and style
    fig.update_layout(
        legend=dict(
            font=dict(family="Montserrat", size=12),
            itemsizing='constant',
            itemclick='toggleothers',
            itemdoubleclick='toggle',
            title=None
        )
    )

    # Update legend item colors to match the plot
    for trace in fig.data:
        trace.legendgroup = trace.name
        trace.showlegend = True

    # Uniform hover formatting
    fig.update_traces(hovertemplate='%{y:.2f}')

    return fig
    # Show plot in Streamlit
#    st.plotly_chart(fig, use_container_width=True, key=key)

def show_model_results():

    # Set the page font to Montserrat
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Montserrat', sans-serif;
        }

        h1, h2, h3, h4, h5, h6, p, div, input, select, textarea, button {
            font-family: 'Montserrat', sans-serif !important;
        }
        /* Target labels inside multiselect dropdowns */
        .stMultiSelect label, .stMultiSelect div[data-baseweb="select"] * {
            font-family: 'Montserrat', sans-serif !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    df = get_data_frame()

    st.title("Forecast Model Results")

    st.write("""
    This page shows the results of our various forecasting models, each of which uses data from a different lookback period:""")

    # Create tabs for each forecast horizon.
    tabs = st.tabs([
        "30 Min", "1 Hour", "2 Hours", "3 Hours", "6 Hours", "12 Hours", 
        "1 Day", "2 Days" 
    ])

    # In each tab, load or simulate data corresponding to that forecast horizon.
    # Replace the dummy data and chart code below with your actual model predictions and metrics.

    with tabs[0]:
        
        # Create a DataFrame to hold the data
        data = pd.DataFrame({
            "Feature": ["National Demand", "Solar Forecast", "Wind Forecast", "Carbon Intensity"],
            "Model": ["XGBRegressor", "XGBRegressor", "XGBRegressor", "XGBRegressor"],
            "R2": [0.9965, 0.9941, 0.9954, 0.9918],
            "RMSE": [366.8971, 188.9431, 287.2552, 5.6111],
            "Most Important Features": [
            "Demand mean the previous hour.",
            "Solar generation mean the previous hour.",
            "Wind generation mean the previous hour.",
            "Carbon intensity mean the previous hour."
            ]
        })

        # Display the table
        #st.markdown("### Model Results Summary")
        #st.table(data)

        st.markdown("### Forecast")
        
        # Generate predictions
        target_cols = ["nd", "solar", "wind", "carbon_intensity"]
        df = df[df["settlement_date"] >= pd.to_datetime("2021-01-01")]

        # Simulate predictions for the last 30 minutes
        for target in target_cols:
            fig = plot_actual_vs_pred(df, target, False, word="30_min", key=f"1_{target}")
            st.plotly_chart(fig, use_container_width=True, key=f"1_{target}")

            one_week_df = df[
                (df["settlement_date"] >= split_datetime) &
                (df["settlement_date"] < split_datetime + pd.Timedelta(days=7))
            ]
            fig = plot_actual_vs_pred(one_week_df, target, True, word="30_min", key = f"11_{target}")
            st.plotly_chart(fig, use_container_width=True, key=f"11_{target}")

    with tabs[1]:
        # Create a DataFrame to hold the data
        data = pd.DataFrame({
            "Feature": ["National Demand", "Solar Forecast", "Wind Forecast", "Carbon Intensity"],
            "Model": ["XGBRegressor", "XGBRegressor", "XGBRegressor", "XGBRegressor"],
            "R2": [0.9927, 0.988, 0.9898, 0.9823],
            "RMSE": [528.4164, 269.938, 425.9937, 8.2712],
            "Most Important Features": [
            "Demand the previous hour.",
            "Solar generation the previous hour.",
            "Wind generation the previous hour.",
            "Carbon intensity the previous hour."
            ]
        })

        # Display the table
        #st.markdown("### Model Results Summary")
        #st.table(data)

        st.markdown("### Forecast")
        

        # Generate predictions
        target_cols = ["nd", "solar", "wind", "carbon_intensity"]
     
        # Simulate predictions for the last 30 minutes
        for target in target_cols:
            fig = plot_actual_vs_pred(df, target, False, word="1_hour", key = f"22_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"22_{target}")
            one_week_df = df[
                (df["settlement_date"] >= split_datetime) &
                (df["settlement_date"] < split_datetime + pd.Timedelta(days=7))
            ]
            fig = plot_actual_vs_pred(one_week_df, target, True, word="1_hour", key = f"2_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"2_{target}")
    with tabs[2]:
        # Create a DataFrame to hold the data
        data = pd.DataFrame({
            "Feature": ["National Demand", "Solar Forecast", "Wind Forecast", "Carbon Intensity"],
            "Model": ["XGBRegressor", "XGBRegressor", "XGBRegressor", "XGBRegressor"],
            "R2": [0.9733, 0.9582, 0.9659, 0.9433],
            "RMSE": [1014.6025, 503.197, 778.5678, 14.7921],
            "Most Important Features": [
            "Demand the previous week.",
            "Solar generation the previous day.",
            "Wind mean generation the previous hour.",
            "Carbon intensity mean the previous hour."
            ]
        })

        # Display the table
        #st.markdown("### Model Results Summary")
        #st.table(data)

        st.markdown("### Forecast")
        
        # Generate predictions
        target_cols = ["nd", "solar", "wind", "carbon_intensity"]
     
        # Simulate predictions for the last 30 minutes
        for target in target_cols:
            fig = plot_actual_vs_pred(df, target, False, word="2_hour", key = f"3_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"3_{target}")
            one_week_df = df[
                (df["settlement_date"] >= split_datetime) &
                (df["settlement_date"] < split_datetime + pd.Timedelta(days=7))
            ]
            fig = plot_actual_vs_pred(one_week_df, target, True, word="2_hour", key = f"31_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"31_{target}")

    with tabs[3]:
        # Create a DataFrame to hold the data
        data = pd.DataFrame({
            "Feature": ["National Demand", "Solar Forecast", "Wind Forecast", "Carbon Intensity"],
            "Model": ["XGBRegressor", "XGBRegressor", "XGBRegressor", "XGBRegressor"],
            "R2": [0.9623, 0.9295, 0.9397, 0.9055],
            "RMSE": [1203.9759, 653.9311, 1035.4401, 19.089],
            "Most Important Features": [
            "Demand the previous week.",
            "Solar generation the previous day.",
            "Wind generation the previous hour.",
            "Carbon intensity the previous hour."
            ]
        })

        # Display the table
        #st.markdown("### Model Results Summary")
        #st.table(data)

        st.markdown("### Forecast")
        
        # Generate predictions
        target_cols = ["nd", "solar", "wind", "carbon_intensity"]
     
        # Simulate predictions for the last 30 minutes
        for target in target_cols:
            fig = plot_actual_vs_pred(df, target, False, word="3_hour", key = f"4_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"4_{target}")
            one_week_df = df[
                (df["settlement_date"] >= split_datetime) &
                (df["settlement_date"] < split_datetime + pd.Timedelta(days=7))
            ]
            fig = plot_actual_vs_pred(one_week_df, target, True, word="3_hour", key = f"41_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"41_{target}")

    with tabs[4]:
        # Create a DataFrame to hold the data
        data = pd.DataFrame({
            "Feature": ["National Demand", "Solar Forecast", "Wind Forecast", "Carbon Intensity"],
            "Model": ["XGBRegressor", "XGBRegressor", "XGBRegressor", "XGBRegressor"],
            "R2": [0.9623, 0.9295, 0.9397, 0.9055],
            "RMSE": [1203.9759, 653.9311, 1035.4401, 19.089],
            "Most Important Features": [
            "Demand the previous week.",
            "Solar generation the previous day.",
            "Wind generation the previous hour.",
            "Carbon intensity the previous hour."
            ]
        })

        # Display the table
        #st.markdown("### Model Results Summary")
        #st.table(data)

        st.markdown("### Forecast")
        
        # Generate predictions
        target_cols = ["nd", "solar", "wind", "carbon_intensity"]
     
        # Simulate predictions for the last 30 minutes
        for target in target_cols:
            fig = plot_actual_vs_pred(df, target, False, word="6_hour", key = f"6_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"6_{target}")
            one_week_df = df[
                (df["settlement_date"] >= split_datetime) &
                (df["settlement_date"] < split_datetime + pd.Timedelta(days=7))
            ]
            fig = plot_actual_vs_pred(one_week_df, target, True, word="6_hour", key = f"61_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"61_{target}")
    with tabs[5]:
        # Create a DataFrame to hold the data
        data = pd.DataFrame({
            "Feature": ["National Demand", "Solar Forecast", "Wind Forecast", "Carbon Intensity"],
            "Model": ["XGBRegressor", "XGBRegressor", "XGBRegressor", "XGBRegressor"],
            "R2": [0.9623, 0.9295, 0.9397, 0.9055],
            "RMSE": [1203.9759, 653.9311, 1035.4401, 19.089],
            "Most Important Features": [
            "Demand the previous week.",
            "Solar generation the previous day.",
            "Wind generation the previous hour.",
            "Carbon intensity the previous hour."
            ]
        })

        # Display the table
        #st.markdown("### Model Results Summary")
        #st.table(data)

        st.markdown("### Forecast")
        
        # Generate predictions
        target_cols = ["nd", "solar", "wind", "carbon_intensity"]
     
        # Simulate predictions for the last 30 minutes
        for target in target_cols:
            fig = plot_actual_vs_pred(df, target, False, word="12_hour", key = f"12_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"12_{target}")
            one_week_df = df[
                (df["settlement_date"] >= split_datetime) &
                (df["settlement_date"] < split_datetime + pd.Timedelta(days=7))
            ]
            fig = plot_actual_vs_pred(one_week_df, target, True, word="12_hour", key = f"121_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"121_{target}")
    with tabs[6]:
        # Create a DataFrame to hold the data
        data = pd.DataFrame({
            "Feature": ["National Demand", "Solar Forecast", "Wind Forecast", "Carbon Intensity"],
            "Model": ["XGBRegressor", "XGBRegressor", "XGBRegressor", "XGBRegressor"],
            "R2": [0.9623, 0.9295, 0.9397, 0.9055],
            "RMSE": [1203.9759, 653.9311, 1035.4401, 19.089],
            "Most Important Features": [
            "Demand the previous week.",
            "Solar generation the previous day.",
            "Wind generation the previous hour.",
            "Carbon intensity the previous hour."
            ]
        })

        # Display the table
        #st.markdown("### Model Results Summary")
        #st.table(data)

        st.markdown("### Forecast")
        
        # Generate predictions
        target_cols = ["nd", "solar", "wind", "carbon_intensity"]
     
        # Simulate predictions for the last 30 minutes
        for target in target_cols:
            fig = plot_actual_vs_pred(df, target, False, word="1_day", key =f"1110_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"1110_{target}")
            one_week_df = df[
                (df["settlement_date"] >= split_datetime) &
                (df["settlement_date"] < split_datetime + pd.Timedelta(days=7))
            ]
            fig = plot_actual_vs_pred(one_week_df, target, True, word="1_day", key = f"111_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"111_{target}")
    with tabs[7]:
        # Create a DataFrame to hold the data
        data = pd.DataFrame({
            "Feature": ["National Demand", "Solar Forecast", "Wind Forecast", "Carbon Intensity"],
            "Model": ["XGBRegressor", "XGBRegressor", "XGBRegressor", "XGBRegressor"],
            "R2": [0.9623, 0.9295, 0.9397, 0.9055],
            "RMSE": [1203.9759, 653.9311, 1035.4401, 19.089],
            "Most Important Features": [
            "Demand the previous week.",
            "Solar generation the previous day.",
            "Wind generation the previous hour.",
            "Carbon intensity the previous hour."
            ]
        })

        # Display the table
        #st.markdown("### Model Results Summary")
        #st.table(data)

        st.markdown("### Forecast")
        
        # Generate predictions
        target_cols = ["nd", "solar", "wind", "carbon_intensity"]
     
        # Simulate predictions for the last 30 minutes
        for target in target_cols:
            fig = plot_actual_vs_pred(df, target, False, word="2_day", key = f"222_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"222_{target}")
            one_week_df = df[
                (df["settlement_date"] >= split_datetime) &
                (df["settlement_date"] < split_datetime + pd.Timedelta(days=7))
            ]
            fig =plot_actual_vs_pred(one_week_df, target, True, word="1_day", key = f"2220_{target}")
            st.plotly_chart(fig, use_container_width=True, key = f"2220_{target}")
    st.markdown("---")
    st.write("### Model: CatBoostRegressor")
    st.write("R2 vatiates between 0.99 and 0.6 for all models.")

