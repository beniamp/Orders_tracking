import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from convertdate import persian
from datetime import datetime, timedelta

# Page setting
st.set_page_config(layout="wide")

# Load dataset
df_orders = pd.read_csv('Orders.csv')

# Clean up category data
df_orders['Category'] = df_orders['Category'].replace('گوشی موبایل ', 'گوشی موبایل')
categories = ['All Categories'] + df_orders['Category'].unique().tolist()

# Formatting and cleaning date values
df_orders['Date_Formatted'] = df_orders['Date_Formatted'].fillna('0000-00-00')
df_orders = df_orders[df_orders['Date_Formatted'] != '0000-00-00']

# Function to convert Persian date to Gregorian date
def persian_to_gregorian(persian_date_str):
    year, month, day = map(int, persian_date_str.split('-'))
    gregorian_date = persian.to_gregorian(year, month, day)
    return datetime(gregorian_date[0], gregorian_date[1], gregorian_date[2])

# Convert Persian dates to Gregorian
sorted_dates = sorted(df_orders['Date_Formatted'].unique())
sorted_dates_gregorian = [persian_to_gregorian(date) for date in sorted_dates]

# Date range selection using calendar widget
b1, b2 = st.columns(2)
start_date, end_date = b1.date_input(
    "Select Date Range",
    value=[sorted_dates_gregorian[0], sorted_dates_gregorian[-1]],
    min_value=sorted_dates_gregorian[0],
    max_value=sorted_dates_gregorian[-1]
)
selected_category = b2.selectbox('Select Category', categories)

# Convert Gregorian dates back to Persian format
def gregorian_to_persian(gregorian_date):
    persian_date = persian.from_gregorian(gregorian_date.year, gregorian_date.month, gregorian_date.day)
    return f'{persian_date[0]:04}-{persian_date[1]:02}-{persian_date[2]:02}'

# Calculate the number of days in the selected range
num_days = (end_date - start_date).days + 1

# Get previous date ranges of the same length
previous_start_date = start_date - timedelta(days=num_days)
previous_end_date = end_date - timedelta(days=num_days)

# Filter DataFrame by the selected date range
current_filtered_df = df_orders[(df_orders['Date_Formatted'] >= gregorian_to_persian(start_date)) & (df_orders['Date_Formatted'] <= gregorian_to_persian(end_date))]

# Filter DataFrame by the previous date range
previous_filtered_df = df_orders[(df_orders['Date_Formatted'] >= gregorian_to_persian(previous_start_date)) & (df_orders['Date_Formatted'] <= gregorian_to_persian(previous_end_date))]

# Apply category filter if necessary
if selected_category != 'All Categories':
    current_filtered_df = current_filtered_df[current_filtered_df['Category'] == selected_category]
    previous_filtered_df = previous_filtered_df[previous_filtered_df['Category'] == selected_category]

# Function to create the bar chart with trend line
def create_bar_chart_with_trend(current_df, previous_df, num_days):
    # Combine current and previous DataFrames
    combined_df = pd.concat([current_df, previous_df])
    
    # Group data by date and sum the quantities
    daily_sales = combined_df.groupby('Date_Formatted').sum()['Quantity'].reset_index()
    
    # Sort by date
    daily_sales = daily_sales.sort_values(by='Date_Formatted')
    
    # Convert dates to Persian
    daily_sales['FormattedDate_p'] = daily_sales['Date_Formatted'].apply(gregorian_to_persian)
    
    # Create the bar chart
    fig = go.Figure()
    
    # Add bars for the current date range
    fig.add_trace(go.Bar(
        x=daily_sales['FormattedDate_p'][:num_days], 
        y=daily_sales['Quantity'][:num_days],
        name='Current Period',
        marker_color='blue'
    ))
    
    # Add bars for the previous date range
    fig.add_trace(go.Bar(
        x=daily_sales['FormattedDate_p'][num_days:], 
        y=daily_sales['Quantity'][num_days:],
        name='Previous Period',
        marker_color='lightblue'
    ))
    
    # Add a line trend connecting averages of each period
    current_avg = daily_sales['Quantity'][:num_days].mean()
    previous_avg = daily_sales['Quantity'][num_days:].mean()
    
    fig.add_trace(go.Scatter(
        x=[daily_sales['FormattedDate_p'][0], daily_sales['FormattedDate_p'][num_days-1]],
        y=[current_avg, current_avg],
        mode='lines+markers',
        name='Current Avg Trend',
        line=dict(color='red', dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=[daily_sales['FormattedDate_p'][num_days], daily_sales['FormattedDate_p'].iloc[-1]],
        y=[previous_avg, previous_avg],
        mode='lines+markers',
        name='Previous Avg Trend',
        line=dict(color='green', dash='dash')
    ))
    
    # Set titles and layout
    fig.update_layout(
        title="Sales Over Time with Trend Line",
        xaxis_title="Date",
        yaxis_title="Quantity",
        barmode='group'
    )
    
    return fig

# Generate the chart
fig = create_bar_chart_with_trend(current_filtered_df, previous_filtered_df, num_days)
st.plotly_chart(fig)
