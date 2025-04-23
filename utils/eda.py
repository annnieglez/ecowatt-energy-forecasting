
# Standard Libraries
import os

# Data Handling & Computation
import pandas as pd
import numpy as np

# Visualization Libraries
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

# ==============================
# Directory Setup
# ==============================

# Define the directory name for saving images
OUTPUT_DIR = "./images"

# Check if the directory exists, if not, create it
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ==============================
# Plot Styling & Customization
# ==============================

# Set a Minimalist Style
sns.set_style("whitegrid")

# Customize Matplotlib settings for a modern look
mpl.rcParams.update({
    'axes.edgecolor': 'grey',       
    'axes.labelcolor': 'black',     
    'xtick.color': 'black',         
    'ytick.color': 'black',         
    'text.color': 'black'           
})

# Colors for late and not late orders
my_color_1 = "#8F2C78" # Purple
my_color_2 = "#1F4E79" # Blue

# Define a custom colormap from light to dark shades of purple
custom_cmap = mpl.colors.LinearSegmentedColormap.from_list(
    "custom_purple", ["#F5A7C4", "#8F2C78", "#5C0E2F"]
)

# ==============================
# Font Configuration
# ==============================

# Path to the custom font file
FONT_PATH = '../utils/fonts/Montserrat-Regular.ttf'

# Add the font to matplotlib's font manager
font_manager.fontManager.addfont(FONT_PATH)

# Set the font family to Montserrat
plt.rcParams['font.family'] = 'Montserrat'

# ==============================
# Visualization Functions
# ==============================

def plot_box_plots(dataframe, x, y, title):

    # Create a copy of the dataframe
    df = dataframe.copy()

    plt.subplots(figsize=(10, 6))
    sns.boxplot(x=df[x], y=df[y],
                data=df,
                palette='rocket',
                hue=df["is_bank_holiday"],
                showfliers= True,
                legend=False)
    plt.title(f"{title}")
    plt.xlabel("Year")
    plt.ylabel("Demand (MW)")
    plt.grid(True, which='both', axis='y', linestyle='--', alpha=0.7)
    plt.show()

def plot_box_plots_multi(dataframe, x, y, title):

    # Create a copy of the dataframe
    df = dataframe.copy()

    plt.subplots(figsize=(10, 6))
    sns.boxplot(x=df[x], y=df[y],
                data=df,
                palette='rocket',
                hue=df[x],
                showfliers= True,
                legend=False)
    plt.title(f"{title}")
    plt.xlabel("Year")
    plt.ylabel("Demand (MW)")
    plt.grid(True, which='both', axis='y', linestyle='--', alpha=0.7)
    plt.show()
