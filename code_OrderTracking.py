import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import numpy as np
import streamlit as st
from PIL import Image
from convertdate import persian
from datetime import datetime
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
df_orders['Category'] = df_orders['Category'].replace('گوشی موبایل ', 'گوشی موبایل')
categories = ['All Categories'] + df_orders['Category'].unique().tolist()
color_val = df_orders['ColorName'].unique()




# Formatting date values
df_orders['Date_Formatted'] = df_orders['Date_Formatted'].fillna('0000-00-00')
df_orders = df_orders[df_orders['Date_Formatted'] != '0000-00-00']

# Convert dates to integer format
df_orders['Date_value'] = df_orders['Date_Formatted'].str.replace('-', '').astype(str)
sorted_dates = sorted(df_orders['Date_Formatted'].unique())

# Function to convert Persian date to Gregorian date
def persian_to_gregorian(persian_date_str):
    year, month, day = map(int, persian_date_str.split('-'))
    gregorian_date = persian.to_gregorian(year, month, day)
    return datetime(gregorian_date[0], gregorian_date[1], gregorian_date[2])


sorted_dates_gregorian = [persian_to_gregorian(date) for date in sorted_dates]

# Row A
b1, b2 = st.columns(2)
selected_date = b1.selectbox('Select Date', sorted_dates)
selected_category = b2.selectbox('Select Category', categories)

# Filter DataFrame by selected category
if selected_category == 'All Categories':
    filtered_df = df_orders
else:
    filtered_df = df_orders[df_orders['Category'] == selected_category]

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
    second_past_7_days = get_past_dates(past_8_days[0], days=7)
else:
    second_past_7_days = []

past_14_days = second_past_7_days + past_7_days

# Filter DataFrames
df_current_week = filtered_df[filtered_df['Date_Formatted'].isin(past_7_days)]
df_previous_week = filtered_df[filtered_df['Date_Formatted'].isin(second_past_7_days)]

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
# Check if past_7_days and past_14_days have sufficient elements before accessing
if past_7_days:
    st.write(f"Calculated Weekdays: From {past_7_days[0]} to {past_7_days[-1]}")
else:
    st.write("Calculated Weekdays: Not enough data to display")

if second_past_7_days:
    st.write(f"Previous Weekdays: From {second_past_7_days[0]} to {second_past_7_days[-1]}")
else:
    st.write("Previous Weekdays: Not enough data to display")

a2, a3, a4 = st.columns(3)
a2.metric("Overall Price", formatted_total_sales, f"{sales_growth:.2f}%")
a3.metric("Overall Volume", formatted_total_volume, f"{volume_growth:.2f}%")
a4.metric("Overall Net Price", formatted_total_net, f"{net_growth:.2f}%")



filtered_df = filtered_df.dropna(subset=['Date'])
# Customizing persian month to corresponding month name by dictionary
persian_months = {'01': 'Far', '02': 'Ord', '03': 'Kho',
        '04': 'Tir', '05': 'Mor', '06': 'Sha',
        '07': 'Meh', '08': 'Aba', '09': 'Aza',
        '10': 'Dey', '11': 'Bah', '12': 'Esf' }


def format_persian_date(date_str):
        if date_str is None:
            return None
        parts = date_str.split('-')
        if len(parts) == 3:
            year, month, day = parts
            persian_month = persian_months.get(month, month)
            return f'{persian_month} {day}'
        return date_str

filtered_df['FormattedDate_p'] = filtered_df['Date_Formatted'].apply(format_persian_date)


def sales_over_time(df, past_14_days):
    # Filter the data to include only the past 14 days
    df_filtered = df[df['Date_Formatted'].isin(past_14_days)]
    
    # Group by 'Date_Formatted' and sum up 'Quantity'
    daily_sales = df_filtered.groupby(['Date_Formatted', 'FormattedDate_p']).sum()['Quantity'].reset_index()
    
    # Create a DataFrame with all possible dates in the past 14 days
    full_dates = pd.DataFrame({'Date_Formatted': past_14_days})
    full_dates['FormattedDate_p'] = full_dates['Date_Formatted'].apply(format_persian_date)
    
    # Merge with the actual sales data to fill missing dates with 0
    full_sales = pd.merge(full_dates, daily_sales, on=['Date_Formatted', 'FormattedDate_p'], how='left').fillna(0)
    
    # Convert any NaNs in Quantity to 0
    full_sales['Quantity'] = full_sales['Quantity'].astype(int)
    
    # Sort by date to ensure proper plotting
    full_sales = full_sales.sort_values(by='Date_Formatted')
    
    # Calculate the average quantity
    average_quantity = full_sales['Quantity'].mean()
    
    # Create a line plot
    fig = px.line(full_sales, x='FormattedDate_p', y='Quantity', title='Sales Over Time', color_discrete_sequence=['red'])
    
    # Add a horizontal line for the average quantity
    fig.add_shape(
        type='line',
        x0=full_sales['FormattedDate_p'].min(),
        y0=average_quantity,
        x1=full_sales['FormattedDate_p'].max(),
        y1=average_quantity,
        line=dict(color='green', dash='dash'),
        xref='x',
        yref='y'
    )
    
    # Add a label for the average line
    fig.add_annotation(
        x=full_sales['FormattedDate_p'].max(),
        y=average_quantity,
        text=f'Average: {round(average_quantity)}',
        showarrow=False,
        yshift=10,
        font=dict(color='black')
    )
    
    # Customize the x-axis to show only the filtered dates
    fig.update_xaxes(type='category', title_text='Date')

    return fig

# Generate the figure
fig_sales = sales_over_time(filtered_df, past_14_days)
st.plotly_chart(fig_sales)
