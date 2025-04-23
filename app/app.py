# Streamlit Libraries
import streamlit as st
from streamlit_option_menu import option_menu

# Standard Libraries
import os
import pickle

# Data Libraries
import pandas as pd

# Importing pages
import _pages.home as home
import _pages.data_eda as eda
import _pages.forecast as fore
import _pages.model_results as ml

# Custom API
from data_collection import API as api

# Paths
script_dir = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(script_dir, "../data")
models_path = os.path.join(script_dir, "./models")

# Only run update once per session
if 'script_ran' not in st.session_state:
    api.update_database()
    st.session_state.script_ran = True

def main():
    st.set_page_config(page_title="EcoWatt Assistant", layout="wide", page_icon="💡", initial_sidebar_state="collapsed")

    st.markdown(
        """
        <style>
        body { background-color: #FF5733; }
        </style>
        """, 
        unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        selected = option_menu(
            menu_title=None, 
            options=["Home", "Historical Demand Data", "Forecast Model Results"], 
            icons=['house', 'info-circle', 'bar-chart', 'robot'], 
            menu_icon="robot", 
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#fafafa"},
                "icon": {"color": "#0B1B29", "font-size": "25px"},
                "nav-link": {"font-size": "13px", "text-align": "left", "margin":"5px", "color": "#000000", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "green"}
            }
        )

    # Navigation
    if selected == "Home":
        home.home_page()

    elif selected == "Historical Demand Data":
        eda.data_eda_page()

    #elif selected == "Forecasts":
    #    st.write("Please enter your OpenAI API Key in the sidebar to continue...")

    elif selected == "Forecast Model Results":
        #ml.show_model_results()
        st.write("Please enter your OpenAI API Key in the sidebar to continue...")

if __name__ == "__main__":
    main()
