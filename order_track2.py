import streamlit as st
import pandas as pd
import altair as alt
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
df_orders['Gregorian_Date'] = df_orders['Date_Formatted'].apply(persian_to_gregorian)

# Date range selection using calendar widget
b1, b2 = st.columns(2)
sorted_dates_gregorian = sorted(df_orders['Gregorian_Date'].unique())
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
filtered_df = df_orders[
    (df_orders['Gregorian_Date'] >= start_date) &
    (df_orders['Gregorian_Date'] <= end_date)
]

# Filter DataFrame by category if necessary
if selected_category != 'All Categories':
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

# Calculate metrics for the current date range
current_total_sales = filtered_df['TotalPrice'].sum()
current_total_volume = filtered_df['Quantity'].sum()
current_total_net = filtered_df['TotalNetPrice'].sum()

# Filter DataFrame for previous date range
previous_filtered_df = df_orders[
    (df_orders['Gregorian_Date'] >= previous_start_date) &
    (df_orders['Gregorian_Date'] <= previous_end_date)
]
if selected_category != 'All Categories':
    previous_filtered_df = previous_filtered_df[previous_filtered_df['Category'] == selected_category]

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
st.write(f'Current period range: {start_date_persian} to {end_date_persian}')
st.write(f'Previous period range: {previous_start_date_persian} to {previous_end_date_persian}')

# Display metrics
a2, a3, a4 = st.columns(3)
a2.metric("Overall Price", formatted_total_sales, f"{sales_growth:.2f}%")
a3.metric("Overall Volume", formatted_total_volume, f"{volume_growth:.2f}%")
a4.metric("Overall Net Price", formatted_total_net, f"{net_growth:.2f}%")

# Function to create and return the Altair plot
def create_plot():
    # Prepare data for Altair
    df_orders_to_plot = df_orders.copy()
    if selected_category != 'All Categories':
        df_orders_to_plot = df_orders_to_plot[df_orders_to_plot['Category'] == selected_category]

    # Sort the DataFrame by Gregorian date for consistency
    df_orders_to_plot = df_orders_to_plot.sort_values(by='Gregorian_Date')

    # Altair plot
    bar_chart = alt.Chart(df_orders_to_plot).mark_bar(opacity=0.6).encode(
        x=alt.X('Gregorian_Date:T', title='Date'),
        y=alt.Y('Quantity:Q', title='Quantity'),
        color=alt.value('blue'),
        tooltip=['Gregorian_Date:T', 'Quantity:Q']
    ).properties(
        title='Daily Quantity'
    )

    # Calculate sums for each range and plot trend lines
    range_sums = []
    for i in range(num_days, len(sorted_dates_gregorian) + 1, num_days):
        range_sum = df_orders_to_plot[
            (df_orders_to_plot['Gregorian_Date'] >= sorted_dates_gregorian[i-num_days]) &
            (df_orders_to_plot['Gregorian_Date'] < sorted_dates_gregorian[i])
        ]['Quantity'].sum()
        range_sums.append(range_sum)
    
    # Create trend line data
    trend_data = pd.DataFrame({
        'Date': [sorted_dates_gregorian[i*num_days-1] for i in range(len(range_sums))],
        'Sum': range_sums
    })

    trend_line = alt.Chart(trend_data).mark_line(color='red', strokeDash=[5, 5]).encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Sum:Q', title='Quantity'),
        tooltip=['Date:T', 'Sum:Q']
    ).properties(
        title='Trend Line (Sum of Ranges)'
    )

    # Combine charts
    combined_chart = bar_chart + trend_line
    return combined_chart

# Button to generate plot
if st.button('Generate Plot'):
    plot = create_plot()
    st.altair_chart(plot, use_container_width=True)
