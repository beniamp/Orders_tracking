import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from convertdate import persian
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np



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
    return datetime(gregorian_date[0], gregorian_date[1], gregorian_date[2])

# Convert Persian dates to Gregorian
sorted_dates_persian = sorted_dates 
sorted_dates_gregorian = [persian_to_gregorian(date) for date in sorted_dates_persian]

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

# Convert the selected Gregorian dates back to Persian format
start_date_persian = gregorian_to_persian(start_date)
end_date_persian = gregorian_to_persian(end_date)

# Calculate the number of days in the selected range
num_days = (end_date - start_date).days + 1

# Calculate the previous date range
previous_start_date = start_date - timedelta(days=num_days)
previous_end_date = end_date - timedelta(days=num_days)

previous_start_date_persian = gregorian_to_persian(previous_start_date)
previous_end_date_persian = gregorian_to_persian(previous_end_date)

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
st.write(f'Current period range:{start_date_persian} to {end_date_persian}')
st.write(f'Previous period range:{previous_start_date_persian} to {previous_end_date_persian}')

# Display metrics
a2, a3, a4 = st.columns(3)
a2.metric("Overall Price", formatted_total_sales, f"{sales_growth:.2f}%")
a3.metric("Overall Volume", formatted_total_volume, f"{volume_growth:.2f}%")
a4.metric("Overall Net Price", formatted_total_net, f"{net_growth:.2f}%")

# Customizing Persian month to corresponding month name by dictionary
persian_months = {'01': 'Far', '02': 'Ord', '03': 'Kho',
                  '04': 'Tir', '05': 'Mor', '06': 'Sha',
                  '07': 'Meh', '08': 'Aba', '09': 'Aza',
                  '10': 'Dey', '11': 'Bah', '12': 'Esf'}

def format_persian_date(date_str):
    if not date_str:
        return None
    parts = date_str.split('-')
    if len(parts) == 3:
        year, month, day = parts
        persian_month = persian_months.get(month, month)
        return f'{persian_month} {day}'
    return date_str


# Aggregate total quantity per day for the current date range
daily_quantity = current_filtered_df.groupby('Date_Formatted')['Quantity'].sum().reset_index()


# Create additional date ranges
additional_ranges = []
for i in range(1, 6):
    additional_start_date = start_date - timedelta(days=num_days * i)
    additional_end_date = end_date - timedelta(days=num_days * i)
    additional_ranges.append((additional_start_date, additional_end_date))

# Convert additional date ranges to Persian format
additional_ranges_persian = [(gregorian_to_persian(start), gregorian_to_persian(end)) for start, end in additional_ranges]



# Combine the current, previous, and additional date ranges
all_ranges_dfs = [current_filtered_df, previous_filtered_df]

# Adding additional date range data
for idx, (start, end) in enumerate(additional_ranges_persian):
    additional_filtered_df = df_orders[(df_orders['Date_Formatted'] >= start) & (df_orders['Date_Formatted'] <= end)]
    
    # Apply category filter if necessary
    if selected_category != 'All Categories':
        additional_filtered_df = additional_filtered_df[additional_filtered_df['Category'] == selected_category]
    
    all_ranges_dfs.append(additional_filtered_df)

# Concatenate all dataframes into one
combined_df = pd.concat(all_ranges_dfs)

# Sort the combined DataFrame by date
combined_df_sorted = combined_df.sort_values(by='Date_Formatted')

# Aggregate total quantity per day for all ranges combined
daily_quantity_combined = combined_df_sorted.groupby('Date_Formatted')['Quantity'].sum().reset_index()

# Convert the dates to readable Persian format for plotting
daily_quantity_combined['Date_Formatted'] = daily_quantity_combined['Date_Formatted'].apply(format_persian_date)

# Create a single bar chart with all the data
fig_combined = px.bar(daily_quantity_combined, x='Date_Formatted', y='Quantity', title='Total Quantity per Day - All Date Ranges Combined')

# Add red vertical lines at the start of each date range
line_positions = [
    start_date_persian,
    previous_start_date_persian,
] + [start for start, end in additional_ranges_persian]

for line_date in line_positions:
    # Convert line_date to Gregorian format for plotting (since it's in Persian format)
    formatted_line_date = format_persian_date(line_date)

    # Add vertical line
    fig_combined.add_vline(x=formatted_line_date, line=dict(color='red', width=2))

# Display the combined chart with the red lines

# Calculate the average quantity for each segment between red lines
average_quantities = []
#line_positions_gregorian = [date for date in line_positions]

# Loop through each segment between red lines
for i in range(len(line_positions) - 1):
    start_line = line_positions[i]
    end_line = line_positions[i + 1]
    print(f'{start_line} and {end_line}')

    # Filter data between the start and end lines
    segment_df = combined_df_sorted[(combined_df_sorted['Date_Formatted'] >= end_line) & 
                                    (combined_df_sorted['Date_Formatted'] < start_line)]
    print(segment_df)

    if not segment_df.empty:
        # Calculate the average quantity for this segment
        avg_quantity = segment_df['Quantity'].sum()
        average_quantities.append((end_line, avg_quantity))

# Add the final segment from the last red line to the end of the data
final_segment_df = combined_df_sorted[combined_df_sorted['Date_Formatted'] >= line_positions_gregorian[-1].strftime('%Y-%m-%d')]

if not final_segment_df.empty:
    avg_quantity = final_segment_df['Quantity'].sum()
    average_quantities.append((final_segment_df['Date_Formatted'].max(), avg_quantity))

# Add a trace for the trend line
trend_line_dates = [date for date, _ in average_quantities]
trend_line_values = [quantity for _, quantity in average_quantities]

fig_combined.add_trace(
    go.Scatter(x=[format_persian_date(date) for date in trend_line_dates],
               y=trend_line_values,
               mode='lines+markers',
               line=dict(color='blue', dash='dash'),
               name='Average Trend')
)

# Display the combined chart with the red lines and the trend line



st.plotly_chart(fig_combined)


