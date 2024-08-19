import streamlit as st
import pandas as pd
import plotly.express as px
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




# Group data by date for the current and previous periods
current_grouped_df = current_filtered_df.groupby('Date_Formatted').agg({'Quantity': 'sum'}).reset_index()
previous_grouped_df = previous_filtered_df.groupby('Date_Formatted').agg({'Quantity': 'sum'}).reset_index()

# Merge the current and previous dataframes on the Date_Formatted column
merged_df = pd.merge(current_grouped_df, previous_grouped_df, on='Date_Formatted', how='outer', suffixes=('_current', '_previous')).fillna(0)

# Convert the 'Date_Formatted' back to Gregorian for plotting
merged_df['Date_Gregorian'] = merged_df['Date_Formatted'].apply(persian_to_gregorian)

# Create the bar plot for total quantity
fig = go.Figure()

# Bar plot for current period quantities
fig.add_trace(go.Bar(
    x=merged_df['Date_Gregorian'],
    y=merged_df['Quantity_current'],
    name='Current Period',
    marker_color='blue',
    text=merged_df['Quantity_current'],
    textposition='auto'
))

# Bar plot for previous period quantities
fig.add_trace(go.Bar(
    x=merged_df['Date_Gregorian'],
    y=merged_df['Quantity_previous'],
    name='Previous Period',
    marker_color='lightblue',
    text=merged_df['Quantity_previous'],
    textposition='auto'
))
# Trend line for the total quantity
fig.add_trace(go.Scatter(
    x=merged_df['Date_Gregorian'],
    y=merged_df['Quantity'],
    mode='lines+markers',
    name='Total Quantity (Current + Previous)',
    line=dict(color='red', dash='dash'),
    marker=dict(size=6, color='red')
))



# Customize layout
fig.update_layout(
    title='Total Quantity for Selected Date Ranges',
    xaxis_title='Date',
    yaxis_title='Quantity',
    barmode='group',
    plot_bgcolor='white',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='lightgrey'),
    legend_title_text='Legend'
)

# Display the plot
st.plotly_chart(fig, use_container_width=True)

