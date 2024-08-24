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
formatted_total_net = "{:,}".format(round(current_total_net))


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



## Create additional date ranges
additional_ranges = []
for i in range(0, 22):
    additional_start_date = start_date - timedelta(days=num_days * i)
    additional_end_date = end_date - timedelta(days=num_days * i)
    additional_ranges.append((additional_start_date, additional_end_date))

# Convert additional date ranges to Persian format
additional_ranges_persian = [(gregorian_to_persian(start), gregorian_to_persian(end)) for start, end in additional_ranges]


all_ranges_dfs = []

# Adding additional date range data
for idx, (start, end) in enumerate(additional_ranges_persian):
    additional_filtered_df = df_orders[(df_orders['Date_Formatted'] >= start) & (df_orders['Date_Formatted'] <= end)]

    # Apply category filter if necessary
    if selected_category != 'All Categories':
        additional_filtered_df = additional_filtered_df[additional_filtered_df['Category'] == selected_category]
    additional_filtered_df['Range_Number'] = idx

    all_ranges_dfs.append(additional_filtered_df)


combined_df = pd.concat(all_ranges_dfs, ignore_index=True)
combined_df_sorted = combined_df.sort_values(by='Date_Formatted')

all_dates= sorted_dates 
daily_quantity_combined = combined_df.groupby('Date_Formatted')['Quantity'].sum().reset_index()

# Reindex with all possible dates and fill missing values with 0
daily_quantity_combined = daily_quantity_combined.set_index('Date_Formatted').reindex(all_dates, fill_value=0).reset_index()

# Rename the index column back to 'Date_Formatted'
daily_quantity_combined.rename(columns={'index': 'Date_Formatted'}, inplace=True)




# Create a single bar chart with all the data
fig_combined = px.bar(daily_quantity_combined, x='Date_Formatted', y='Quantity', title='Total Quantity per Day - All Date Ranges Combined', color_discrete_sequence=['#636EFA'])
fig_combined.update_xaxes(type='category')

line_positions = [end for start, end in additional_ranges_persian]

line_pos = []
for i in line_positions:
  if i in combined_df['Date_Formatted'].unique():
    line_pos.append(i)


# Display the combined chart with the red lines
  # Create the bar chart
fig_combined = px.bar(
    daily_quantity_combined,
    x='Date_Formatted',
    y='Quantity',
    title='Total Quantity per Day - All Date Ranges Combined',
    color_discrete_sequence=['#636EFA']
)



# Add red vertical lines at the start of each date range
for line_date in line_pos:
    print(line_date)
    
    # Add vertical line
    fig_combined.add_vline(x=line_date, fillcolor='red')
# Ensure the x-axis is categorical
fig_combined.update_xaxes(type='category')



# Calculate the average quantity for each segment between red lines
total_quantities = []
average_quantities = []

# Loop through each segment between red lines
for i, ii in additional_ranges_persian:
    end_line = ii
    start_line = i
    print(f'{start_line} and {end_line}')

    # Filter data between the start and end lines
    segment_df = combined_df_sorted[(combined_df_sorted['Date_Formatted'] >= start_line) & 
                                    (combined_df_sorted['Date_Formatted'] <= end_line)]


    if not segment_df.empty:
        # Calculate th-e average quantity for this segment
        tot_quantity = segment_df['Quantity'].sum()
        avg_quantity = tot_quantity / num_days
        total_quantities.append((end_line, tot_quantity))
        average_quantities.append((end_line, round(avg_quantity)))


# Handle the final segment after the last red line
#if len(line_positions) > 0:
#    final_segment_df = combined_df_sorted[combined_df_sorted['Date_Formatted'] >= line_positions[-1]]
#    if not final_segment_df.empty:
#        tot_quantity = final_segment_df['Quantity'].sum()
#        total_quantities.append((final_segment_df['Date_Formatted'].max(), tot_quantity))
        
# Add a trace for the trend line
trend_line_dates = [date for date,_ in average_quantities]
trend_line_values = [quantity for _, quantity in average_quantities]


fig_combined.add_trace(
    go.Scatter(x=[date for date in trend_line_dates],
               y=trend_line_values,
               mode='lines+markers',
               line=dict(color='red', dash='dash'),
               name='Total Trend')
)


# Display the combined chart with the red lines and the trend line
st.plotly_chart(fig_combined)


import numpy as np

product_quantities_by_range = []

# Filter the date ranges to include only those that have data in df_orders
filtered_additional_ranges_persian = []
for start, end in additional_ranges_persian:
    if df_orders[(df_orders['Date_Formatted'] >= start) & (df_orders['Date_Formatted'] <= end)].shape[0] > 0:
        filtered_additional_ranges_persian.append((start, end))

# Iterate over the filtered date ranges and calculate quantities
for idx, (start, end) in enumerate(filtered_additional_ranges_persian):
    # Filter the DataFrame for the current date range
    additional_filtered_df = df_orders[(df_orders['Date_Formatted'] >= start) & (df_orders['Date_Formatted'] <= end)]

    # Apply category filter if necessary
    if selected_category != 'All Categories':
        additional_filtered_df = additional_filtered_df[additional_filtered_df['Category'] == selected_category]
    
    # Group by Product Name and sum the quantities
    product_quantities = additional_filtered_df.groupby('ProductName')['Quantity'].sum().reset_index()
    
    # Add a column for the date range as the column name
    product_quantities[f'{start} to {end}'] = product_quantities['Quantity']
    
    # Keep only the necessary columns
    product_quantities = product_quantities[['ProductName', f'{start} to {end}']]
    
    # Append the result to the list
    product_quantities_by_range.append(product_quantities)

# Combine all the results into a single DataFrame by merging on ProductName
if product_quantities_by_range:
    summary_df = product_quantities_by_range[0]
    for df in product_quantities_by_range[1:]:
        summary_df = pd.merge(summary_df, df, on='ProductName', how='outer')

    # Fill NaN values with 0 (if a product has no sales in a date range)
    summary_df.fillna(0, inplace=True)

    # Calculate the total quantity across all date ranges for sorting (optional)
    summary_df['Total Quantity'] = summary_df.drop('ProductName', axis=1).sum(axis=1)
    
    # Calculate the maximum quantity and the corresponding date range
    summary_df['Max Quantity'] = summary_df.drop(['ProductName', 'Total Quantity'], axis=1).max(axis=1)
    summary_df['Max Quantity Date Range'] = summary_df.drop(['ProductName', 'Total Quantity', 'Max Quantity'], axis=1).idxmax(axis=1)
    
    # Sort the DataFrame by Total Quantity (optional)
    summary_df = summary_df.sort_values(by='Total Quantity', ascending=False)


    # Display the summary table
    st.write("Total Quantity by Product for Each Date Range")
    st.write(summary_df)
else:
    st.write("No valid date ranges with data found.")



# Assuming summary_df is already created and contains the necessary data

# Create a list of distinct product names from the summary_df
product_names = summary_df['ProductName'].unique()

# Widget for selecting a product
selected_product = st.selectbox('Select Product', product_names)

# Function to get trend data for the selected product
def get_trend_data(product_name, summary_df):
    # Filter the summary_df for the selected product
    product_data = summary_df[summary_df['ProductName'] == product_name]
    
    # Extract the date ranges and quantities
    date_ranges = product_data.columns[1:-2]  # Exclude ProductName, Total Quantity, Max Quantity, Max Quantity Date Range
    quantities = product_data.iloc[0, 1:-3]  # Get the quantities for the selected product
    
    # Create a DataFrame to sort date ranges
    trend_data = pd.DataFrame({'Date Range': date_ranges, 'Quantity': quantities})
    
    # Sort the DataFrame by Date Range in descending order
    trend_data = trend_data.sort_values(by='Date Range', ascending=False)
    
    return trend_data

# Get trend data for the selected product
trend_data = get_trend_data(selected_product, summary_df)

# Create the trend line chart
fig_trend = go.Figure()

# Add trace for the trend line
fig_trend.add_trace(
    go.Scatter(
        x=trend_data['Date Range'],
        y=trend_data['Quantity'],
        mode='lines+markers',
        line=dict(color='blue', width=2),
        marker=dict(size=8, color='blue'),
        name='Quantity Trend'
    )
)

# Update layout of the chart
fig_trend.update_layout(
    title=f'Quantity Trend for {selected_product}',
    xaxis_title='Date Range',
    yaxis_title='Quantity',
    xaxis=dict(tickangle=-45, categoryorder='total descending'),  # Ensure dates are in descending order
    plot_bgcolor='white'
)

# Display the trend line chart
st.plotly_chart(fig_trend)

