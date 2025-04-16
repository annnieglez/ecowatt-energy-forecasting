'''This module contains the data EDA page for the Streamlit app. It includes functions to display and interact with energy 
    demand and generation data. The app is designed to also provide insights into carbon intensity over time.
    The page allows users to filter data by date range and energy sources, and visualize the data using Plotly charts.
    The page also includes options to view data as percentages and group by fuel categories.'''

# Streamlit Libraries
import streamlit as st

# Standard Libraries
import os
from datetime import timedelta, datetime

# Data Libraries
import pandas as pd
import plotly.express as px

# Data path relative to current script
script_dir = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(script_dir, "../../data")

def data_eda_page():
    '''Function to display the Data EDA page of the EcoWatt app. This page provides insights into energy generation and carbon intensity over time.'''

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

    # Load and Prepare Data
    df = pd.read_csv(os.path.join(data_path, "data_uk_merged_generation_demand.csv"))

    # Rename columns for better readability in the plot
    df.rename(columns={'solar': 'Solar', 'wind': 'Wind', 'hydro': 'Hydro', 'nuclear': 'Nuclear', 'gas': 'Gas', 'coal': 'Coal', 'biomass': 'Biomass', 'other': 'Other', 'wind_emb': 'Wind Embedded'}, inplace=True)

    # Ensure that the datetime column is in the correct format
    df['settlement_date'] = pd.to_datetime(df['settlement_date'])

    all_sources = ['Solar', 'Wind', 'Hydro', 'Nuclear', 'Gas', 'Coal', 'Biomass', 'Other', 'Wind Embedded']

    # Get the latest data row
    latest_row = df.sort_values("settlement_date").iloc[-1]
    latest_timestamp = latest_row["settlement_date"]
    latest_demand = latest_row["nd"]
    latest_generation = latest_row["generation"]-latest_row["imports"]
    latest_carbon_intensity = latest_row["carbon_intensity"]

    # Display latest summary metrics
    with st.container():
        st.markdown("### 🔍 Latest Report Summary")
        col_a, col_b, col_c, col_d = st.columns([2.5,2,2,2])
        col_a.metric("📅 Date", latest_timestamp.strftime('%Y-%m-%d %H:%M'))
        col_b.metric("⚡ National Demand", f"{latest_demand:,.0f} MW")
        col_c.metric("🏭 Generation", f"{latest_generation:.0f} MW")
        col_d.metric("💨 Carbon Intensity", f"{latest_carbon_intensity:.0f} gCO₂/kWh")

    # Default date range: last 14 days from the latest date in the dataset
    default_end = df['settlement_date'].max()
    default_start = default_end - timedelta(days=14)

    # Visual Divider between Summary and Filters
    st.markdown("---")
    st.markdown("### 🛠️ Filter Options")
    st.markdown("Use the filters below to customize the data view by time range and energy source. You can also toggle percentage or category view.")

    # Filters Section 
    with st.container():
        col1, col2, col3, col4 = st.columns([1.0, 1.0, 4.9, 2])

        # Date range selection
        with col1:
            st.markdown("#### Start date")
            start_date = st.date_input(
                "Start date", value=default_start,
                min_value=df['settlement_date'].min(),
                max_value=default_end,
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("#### End date")
            end_date = st.date_input(
                "End date", value=default_end,
                min_value=start_date,
                max_value=df['settlement_date'].max(),
                label_visibility="collapsed"
            )

        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())  # this gives 23:59:59.999999

        # Energy source selection
        with col3:
            st.markdown("#### Energy Sources")
            energy_sources = st.multiselect(
                "Select energy sources to stack:",
                all_sources,
                default=['Solar', 'Wind', 'Hydro'], label_visibility="collapsed"
            )

        # Toggle for percentage view and category view
        with col4:
            st.markdown("#### Options for Generation")
            col41, col42 = st.columns([1.6,3])
            with col41:
                percentage_view = st.checkbox("View as %")
            with col42:
                category_view = st.checkbox("Group by Fuel Category")

    # Prepare Base Data 
    filtered_df = df[(df['settlement_date'] >= pd.to_datetime(start_datetime)) & (df['settlement_date'] <= pd.to_datetime(end_datetime))]
    plot_df = filtered_df.copy()    

    # Adjust columns based on toggles
    if category_view:
        category_map = {
            'Fossil Fuels': ['Gas', 'Coal'],
            'Zero-Carbon': ['Solar', 'Wind', 'Hydro', 'Wind Embedded'],
            'Low Carbon': ['Nuclear', 'Biomass'],
            'Other': ['Other']
        }

        # Create a list of all categories
        all_categories = list(category_map.keys())

        # Create a new DataFrame to hold the categories
        df_cat = pd.DataFrame({'settlement_date': plot_df['settlement_date']})

        # Sum the energy sources based on the category mapping
        for category, sources in category_map.items():
            df_cat[category] = plot_df[sources].sum(axis=1)

        # Datframe is rescribe with the categories
        plot_df = df_cat
        energy_sources = all_categories
        
        # Total generation for all the sources
        total_base = plot_df[all_categories].sum(axis=1) if percentage_view else None
    else:
        # Total generation for all the sources
        total_base = plot_df[all_sources].sum(axis=1) if percentage_view else None

    if percentage_view:
        # Percentage calculation for seleted energy sources based on the total generation
        for col in energy_sources:
            plot_df[col] = plot_df[col] / total_base * 100

    # Melt data for plotting
    melted = plot_df[['settlement_date'] + energy_sources].melt(
        id_vars='settlement_date',
        value_vars=energy_sources,
        var_name='Energy Source',
        value_name='Generation (MW)' if not percentage_view else 'Generation (%)'
    )

    # Custom color scale for plot
    color_map = {
        'Solar': '#FDB813',  # Bright yellow
        'Wind': '#1E90FF',  # Dodger blue
        'Hydro': '#00BFFF',  # Deep sky blue
        'Nuclear': '#FF6347',  # Tomato red
        'Gas': '#9370DB',  # Medium purple
        'Coal': '#696969',  # Dim gray
        'Biomass': '#8FBC8F',  # Dark sea green
        'Other': '#A9A9A9',  # Dark gray
        'Wind Embedded': '#87CEEB',  # Sky blue
        'Fossil Fuels': '#FF4500',  # Orange red
        'Renewables': '#32CD32',  # Lime green
        'Low Carbon': '#4682B4',  # Steel blue
    }

    # Generation Plot
    fig = px.area(
            melted,
            x='settlement_date',
            y='Generation (MW)' if not percentage_view else 'Generation (%)',
            color='Energy Source',
            color_discrete_map=color_map,
        )
    fig.update_layout(xaxis_title='Date', font=dict(family="Montserrat", color="black"), hovermode='x unified')
    fig.update_traces(hovertemplate='%{y:.2f}')

    # Carbon Intensity Plot
    fig2 = px.line(
        filtered_df,
        x='settlement_date',
        y='carbon_intensity',
        labels={'settlement_date': 'Date', 'carbon_intensity': 'Carbon Intensity (gCO2/kWh)'},
    )
    fig2.update_layout(xaxis_title='Date', font=dict(family="Montserrat", color="black"), hovermode='x unified')
    fig2.update_traces(
        hovertemplate='%{y:.2f}',
        line=dict(color='red', width=2),
        name='Carbon Intensity',
        showlegend=True 
    )

    # Demand Plot
    fig3 = px.line(
        filtered_df,
        x='settlement_date',
        y=['nd', 'tsd'],
        labels={'settlement_date': 'Date', 'value': 'Demand (MW)', 'nd': 'National Demand', 'tsd': 'Transmission System Demand'}, 
        color_discrete_map={"nd": "blue", "tsd": "orange"}
    )
    fig3.update_layout(showlegend=True, 
                       legend_title_text=None, 
                       xaxis_title='Date', 
                       font=dict(family="Montserrat", 
                                color="black"), 
                        hovermode='x unified')
    fig3.for_each_trace(lambda trace: trace.update(name='National Demand' if trace.name == 'nd' else 'System Demand'))
    fig3.update_traces(hovertemplate='%{y:.2f}')

    # Show plots in Streamlit
    st.markdown("# Stacked Energy Generation Over Time")
    st.plotly_chart(fig, use_container_width=True, click_event=True)

    st.markdown("# Carbon Intensity Over Time")
    st.plotly_chart(fig2, use_container_width=True, click_event=True)

    st.markdown("# Demand Over Time")
    st.plotly_chart(fig3, use_container_width=True, click_event=True)
