''' This is a Streamlit app for EcoWatt, a UK energy insights platform. 
    It provides real-time data, forecasts, and carbon awareness features.
    The app is structured with a home page, data exploration, forecasting, and a chatbot interface.'''

# Streamlit Libraries
import streamlit as st
from streamlit_option_menu import option_menu

# Standard Libraries
import os

# Importing pages
import _pages.home as home
import _pages.data_eda as eda
import _pages.forecast as fore
import _pages.chat as chat

def main():
    '''Main function to run the Streamlit app.'''

    # Set the app configuration
    st.set_page_config(page_title="EcoWatt Assistant", layout="wide", page_icon="💡", initial_sidebar_state="collapsed")

    st.markdown(
        """
        <style>
        /* Change the background color for the entire Streamlit app */
        body {
            background-color: #FF5733;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    # Sidebar menu
    with st.sidebar:
        selected = option_menu(
            menu_title=None, 
            options=["Home", "Historical Demand Data", "Forecasts", "Green Chatbot"], 
            icons=['house', 'info-circle', 'bar-chart', 'robot'], 
            menu_icon="robot", 
            default_index=0,
            styles={"container": {"padding": "5!important", "background-color": "#fafafa"},
                    "icon": {"color": "#0B1B29", "font-size": "25px"},
                    "nav-link": {"font-size": "13px", "text-align": "left", "margin":"5px", "color": "#000000", "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "green"}})

    # Main content based on selected menu item

    # Home    
    if selected == "Home":
        home.home_page()

    # Data EDA
    if selected == "Historical Demand Data":
        eda.data_eda_page()

    # Forecasts
    if selected == "Forecasts":
        st.write("Please enter your OpenAI API Key in the sidebar to continue...")

    # Travel Assistant
    if selected == "Green Energy Chatbot":
        st.write("Please enter your OpenAI API Key in the sidebar to continue...")

if __name__ == "__main__":
    main()

