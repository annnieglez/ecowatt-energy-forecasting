''' Home Page for EcoWatt Dashboard.
    This page provides an overview of the EcoWatt application, its features, and how to navigate through the app.
'''

# Libraries
import streamlit as st
from datetime import datetime

def home_page():
    '''Function to display the Home page of the EcoWatt app.'''

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

    # --- Header ---
    st.title("🌍 EcoWatt")
    st.subheader("UK Energy Insights • Forecasts • Real-Time Carbon Awareness")

    # --- Intro ---
    st.markdown("""
    Welcome to **EcoWatt**, your all-in-one dashboard for tracking and forecasting the UK's energy landscape. Whether you're an energy analyst, policy enthusiast, or eco-conscious citizen, EcoWatt helps you understand:
    - **Current & historical electricity generation**
    - **Real-time carbon intensity and renewable share**
    - **Forecasts** for demand, solar, wind generation, and carbon intensity
    - **Live green hour estimator** to help you use energy when it’s cleanest
    """)

    # --- Quick Stats ---
    st.markdown("### 🔍 Key Stats (Snapshot)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Today", datetime.now().strftime("%A, %B %d"))

    with col2:
        st.metric("Forecast Carbon Intensity", "value here")

    with col3:
        st.metric("Forecast: Greenest Hour", "2:00PM - 3:00PM")

    # --- Features ---
    st.markdown("### ⚙️ What You Can Do with EcoWatt")

    st.markdown("""
    - 📈 **Energy Trends**: Explore electricity generation by source, and monitor historical patterns.
    - 🌀 **Renewable Forecasting**: See tomorrow's wind & solar predictions, and plan smarter.
    - 🔋 **Carbon Intensity Forecasting**: Find out when electricity is cleanest, today or in the coming days.
    - ⏱️ **Green Hour Estimator**: Get real-time recommendations on the best times to use energy sustainably.
    - 📊 **Demand Forecast**: Monitor expected demand for better grid awareness.
    """)

    # --- How to Navigate ---
    st.markdown("### 🧭 Navigation Guide")

    st.markdown("""
    Use the menu on the left to explore:
    - **📊 Historical Demand Data** — Analyze historical generation, demand & carbon intensity
    - **🔮 Forecasts** — View upcoming solar, wind, and demand predictions
    - **🌿 Green Hours** — Discover the best time to use energy today
    - **🤖 Green Chatbot** — Ask questions about energy trends and forecasts
    """)

    # --- Data Sources ---
    st.markdown("### 📚 Data Sources")
    st.markdown("""
    - **National Grid**: Real-time and historical data on electricity generation and carbon intensity
    - **Carbon Intensity API**: Forecasts and live data on carbon intensity
    """)

    # --- Footer ---
    st.markdown("---")
    st.caption("Made with 💚 by the EcoWatt Team")