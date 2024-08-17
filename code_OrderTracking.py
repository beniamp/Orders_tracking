import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import numpy as np
import streamlit as st
from PIL import Image
#import pyodbc as odbc


# Page setting
st.set_page_config(layout="wide")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

image = Image.open('dgland_icon.png')
st.image(image, width=100)  # Change 100 to the desired width in pixels


df_orders = pd.read_csv('Orders.csv')

# calculating 3 metrics in second row
total_sales = df_orders['TotalPrice'].sum()
formatted_total_sales = "{:,}".format(total_sales)

total_volume = df_orders['Quantity'].sum()
formatted_total_volume = "{:,}".format(total_volume)

total_net = df_orders['TotalNetPrice'].sum()
formatted_total_net = "{:,}".format(total_net)


# Unique date values
date_val = df_orders['Date_Formatted'].unique()
category_val = df_orders['Category'].unique()
color_val = df_orders['ColorName'].unique()

# Formatting date values
df_orders['Date_Formatted'] = df_orders['Date_Formatted'].fillna('0000-00-00')
df_orders = df_orders[df_orders['Date_Formatted'] != '0000-00-00']

# Convert dates to integer format
df_orders['Date_value'] = df_orders['Date_Formatted'].str.replace('-', '').astype(str)
sorted_dates = sorted(df_orders['Date_Formatted'].unique())

# Row A
b1, b2, b3 = st.columns(3)
selected_date = b1.selectbox('Select Date', sorted_dates)
b2.selectbox('Select Category', category_val)
b3.selectbox('Select Brand', color_val)
# Define a helper function to get the past 7 days
def get_past_dates(date_str, days=7):
    date_index = sorted_dates.index(date_str)
    if date_index - (days - 1) >= 0:
        return sorted_dates[date_index - (days - 1):date_index + 1]
    return sorted_dates[:date_index + 1]


# Get the past 7 days including the selected date
past_8_days = get_past_dates(selected_date, days=8)
past_7_days = past_8_days[1:]


# Get the 7 days before the last 7 days
if len(past_7_days) >= 7:
    past_14_days = get_past_dates(past_8_days[0], days=7)
else:
    past_14_days = []

# Filter DataFrames
df_current_week = df_orders[df_orders['Date_Formatted'].isin(past_7_days)]
df_previous_week = df_orders[df_orders['Date_Formatted'].isin(past_14_days)]

# Calculate metrics for current week
current_total_sales = df_current_week['TotalPrice'].sum()
current_total_volume = df_current_week['Quantity'].sum()
current_total_net = df_current_week['TotalNetPrice'].sum()

# Calculate metrics for previous week
previous_total_sales = df_previous_week['TotalPrice'].sum()
previous_total_volume = df_previous_week['Quantity'].sum()
previous_total_net = df_previous_week['TotalNetPrice'].sum()

# Calculate Growth Percentage
sales_growth = ((current_total_sales - previous_total_sales) / previous_total_sales) * 100 if previous_total_sales else 0
volume_growth = ((current_total_volume - previous_total_volume) / previous_total_volume) * 100 if previous_total_volume else 0
net_growth = ((current_total_net - previous_total_net) / previous_total_net) * 100 if previous_total_net else 0

# Formatting the metrics
formatted_total_sales = "{:,}".format(current_total_sales)
formatted_total_volume = "{:,}".format(current_total_volume)
formatted_total_net = "{:,}".format(current_total_net)



# Row B: Metrics display
st.write(f"Calculated Weekdays: From {past_7_days[0]} to {past_7_days[-1]}")
st.write(f"Previous Calculated Weekdays: From {past_14_days[0]} to {past_14_days[-1]}")
a2, a3, a4 = st.columns(3)
a2.metric("Overall Price", formatted_total_sales, f"{sales_growth:.2f}%")
a3.metric("Overall Volume", formatted_total_volume, f"{volume_growth:.2f}%")
a4.metric("Overall Net Price", formatted_total_net, f"{net_growth:.2f}%")
