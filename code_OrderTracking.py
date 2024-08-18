import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from convertdate import persian
from datetime import datetime, timedelta

# Page setting
st.set_page_config(layout="wide")

# Load custom CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Display image
image = Image.open('dgland_icon.png')
st.image(image, width=100)  # Adjust width as needed

# Load dataset
df_orders = pd.read_csv('Orders.csv')

# Calculate metrics
total_sales = df_orders['TotalPrice'].sum()
formatted_total_sales = "{:,}".format(total_sales)

total_volume = df_orders['Quantity'].sum()
formatted_total_volume = "{:,}".format(total_volume)

total_net = df_orders['TotalNetPrice'].sum()
formatted_total_net = "{:,}".format(total_net)

# Clean up category data
df_orders['Category'] = df_orders['Category'].replace('گوشی موبایل ', 'گوشی موبایل')
categories = ['All Categories'] + df_orders['Category'].unique().tolist()

# Formatting and cleaning date values
df_orders['Date_Formatted'] = df_orders['Date_Formatted'].fillna('0000-00-00')
df_orders = df_orders[df_orders['Date_Formatted'] != '0000-00-00']

# Ensure date is a string format
df_orders['Date_value'] = df_orders['Date_Formatted'].str.replace('-', '').astype(str)
sorted_dates = sorted(df_orders['Date_Formatted'].unique())

# Function to convert Persian date to Gregorian date
def persian_to_gregorian(persian_date_str):
    year, month, day = map(int, persian_date_str.split('-'))
    gregorian_date = persian.to_gregorian(year, month, day)
    return f'{gregorian_date[0]:04}-{gregorian_date[1]:02}-{gregorian_date[2]:02}'

# Convert Persian dates to Gregorian (keeping as string)
sorted_dates_persian = sorted_dates 
sorted_dates_gregorian = [persian_to_gregorian(date) for date in sorted_dates_persian]

# Convert Gregorian strings to datetime objects (only for date selection)
sorted_dates_gregorian_dt = [datetime.strptime(date, '%Y-%m-%d') for date in sorted_dates_gregorian]

# Date range selection using calendar widget
b1, b2 = st.columns(2)
start_date, end_date = b1.date_input(
    "Select Date Range",
    value=[sorted_dates_gregorian_dt[0], sorted_dates_gregorian_dt[-1]],
    min_value=sorted_dates_gregorian_dt[0],
    max_value=sorted_dates_gregorian_dt[-1]
)
selected_category = b2.selectbox('Select Category', categories)

# Convert selected Gregorian dates back to Persian format
start_date_persian = sorted_dates_persian[sorted_dates_gregorian_dt.index(start_date)]
end_date_persian = sorted_dates_persian[sorted_dates_gregorian_dt.index(end_date)]

# Calculate the number of days in the selected range
num_days = (end_date - start_date).days + 1

# Calculate the previous date range
previous_start_date = start_date - timedelta(days=num_days)
previous_end_date = end_date - timedelta(days=num_days)

# Convert previous Gregorian dates back to Persian format
previous_start_date_persian = sorted_dates_persian[sorted_dates_gregorian_dt.index(previous_start_date)]
previous_end_date_persian = sorted_dates_persian[sorted_dates_gregorian_dt.index(previous_end_date)]

# Filter DataFrame by date and category
filtered_dates_persian = [date for date in sorted_dates if start_date_persian <= date <= end_date_persian]
filtered_df = df_orders[df_orders['Date_Formatted'].isin(filtered_dates_persian)]

# Filter DataFrame by current and previous date ranges
current_filtered_df = df_orders[(df_orders['Date_Formatted'] >= start_date_persian) & (df_orders['Date_Formatted'] <= end_date_persian)]
previous_filtered_df = df_orders[(df_orders['Date_Formatted'] >= previous_start_date_persian) & (df_orders['Date_Formatted'] <= previous_end_date_persian)]

# Apply category filter if necessary
if selected_category != 'All Categories':
    current_filtered_df = current_filtered_df[current_filtered_df['Category'] == selected_category]
    previous_filtered_df = previous_filtered_df[previous_filtered_df['Category'] == selected_category]

# Calculate metrics for the current date range
current_total_sales = current_filtered_df['TotalPrice'].sum()
current_total_volume = current_filtered_df['Quantity'].sum()
current_total_net = current_filtered_df['TotalNetPrice'].sum()

# Calculate metrics for the previous date range
previous_total_sales = previous_filtered_df['TotalPrice'].sum()
previous_total_volume = previous_filtered_df['Quantity'].sum()
previous_total_net = previous_filtered_df['TotalNetPrice'].sum()

# Calculate growth percentages
sales_growth = ((current_total_sales - previous_total_sales) / previous_total_sales) * 100 if previous_total_sales else 0
volume_growth = ((current_total_volume - previous_total_volume) / previous_total_volume) * 100 if previous_total_volume else 0
net_growth = ((current_total_net - previous_total_net) / previous_total_net) * 100 if previous_total_net else 0

# Formatting the metrics
formatted_total_sales = "{:,}".format(current_total_sales)
formatted_total_volume = "{:,}".format(current_total_volume)
formatted_total_net = "{:,}".format(current_total_net)

st.write(f'Domain of period time: {num_days}')
st.write(f'C
