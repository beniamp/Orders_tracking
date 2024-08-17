import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from xlsxwriter import Workbook
import numpy as np
#import pyodbc as odbc


# Defining the Component of Connection String
# DRIVER_NAME = "{ODBC Driver 17 for SQL Server}"
# SERVER_NAME = "aminpour-lap"
# DATABASE_NAME = "order_management"
# USERNAME = "DGSERVICE\b.aminpour"



#connection_string = f"""
#    DRIVER={DRIVER_NAME};
#    SERVER={SERVER_NAME};
#    DATABASE={DATABASE_NAME};
#    Trusted_Connection=yes;




#conn = odbc.connect(connection_string, pooling=False)
#cursor = conn.cursor()


# Returning All the Values from Fields and Records in Desired Table 
#query1 = """
#    SELECT * 
#    FROM order_management.dbo.orders_0101_0505
#"""

#result = cursor.execute(query1).fetchall()
# Page setting
st.set_page_config(layout="wide")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)



# Coverting our Sql Based Table into Pandas Dataframe
#df_orders = pd.read_sql(query1, conn)
# Reading data from csv file
df = pd.read_csv('BalanceV2.csv')
df_orders = pd.read_csv('Orders.csv')
df_orders = df_orders[['ProductNameColor', 'Quantity', 'ColorName', 'Date_Formatted', 'Category', ]]
df_stocks = pd.read_csv('Stocks.csv')

# Inject custom CSS to style the select box
st.markdown("""
    <style>
    .stSelectbox > div > div > div > div:first-child:hover {
        background-color: #e8ffe8;  /* Light green background on hover */
    }
    .stSelectbox > div > div > div > div:first-child:focus-within {
        border-color: #66bb6a;  /* Darker green border on focus */
    }
    .stSelectbox > div > div > div > div:first-child > div {
        color: #4CAF50;  /* Green text */
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Replace null dates with a placeholder in both DataFrames
df['Date'] = df['Date'].fillna('0000-00-00')
df = df[df['Date'] != '0000-00-00']
df_orders['Date_Formatted'] = df_orders['Date_Formatted'].fillna('0000-00-00')

# Convert dates to integer format
df['Date_value'] = df['Date'].str.replace('-', '').astype(str)
df_orders['Date_value'] = df_orders['Date_Formatted'].str.replace('-', '').astype(str)

# Sidebar for date selection
sorted_dates = sorted(df['Date'].unique())

# Slider for date range selection
start_idx, end_idx = st.slider(
    "Select Date Range",
    min_value=0,
    max_value=len(sorted_dates) - 1,
    value=(0, len(sorted_dates) - 1),
    step=1,
)

# Get the selected start and end dates
start_date = sorted_dates[start_idx]
end_date = sorted_dates[end_idx]

st.write(f"Selected date range: {start_date} to {end_date}")

# Convert selected dates to integer format
start_date_int = start_date.replace('-', '')
end_date_int = end_date.replace('-', '')

# Filter the data by the selected date range
# Include rows where 'Date' is '0000-00-00' (placeholder for null)
filtered_df = df[
    (df['Date_value'] >= start_date_int) & (df['Date_value'] <= end_date_int)
]

# For df_orders, keep rows with null dates as well
filtered_df2 = df_orders[
    (df_orders['Date_value'] >= start_date_int) & (df_orders['Date_value'] <= end_date_int) |
    (df_orders['Date_Formatted'] == '0000-00-00')
]


# Count the number of unique dates in the range
count_dates = len(filtered_df['Date'].unique())
st.write(f"Number of dates between selected range: {count_dates}")

# Category filter with 'All Categories' option
categories = ['All Categories'] + df['Category'].unique().tolist()
selected_category = st.selectbox('Select Category', categories)


# Filter DataFrame by selected category
if selected_category != 'All Categories':
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    df_stocks = df_stocks[df_stocks['Category'] == selected_category]



# Brand filter with 'All Brands' option
if selected_category != 'All Categories':
    brands = ['All Brands'] + filtered_df['Brand'].unique().tolist()
else:
    brands = ['All Brands'] + df['Brand'].unique().tolist()

selected_brand = st.selectbox('Select Brand', brands)

# Filter DataFrame by selected brand
if selected_brand != 'All Brands':
    filtered_df = filtered_df[filtered_df['Brand'] == selected_brand]
    df_stocks = df_stocks[df_stocks['Brand'] == selected_brand]  # Apply brand filter to stocks as well



# Display the final filtered data count
st.success(f"**Total products in selected filters:** {filtered_df.shape[0]}")


# Aggregating stock data by Name, Category, Brand
agg_stock = df_stocks.groupby(['ProductColorName', 'Category', 'Brand', 'Color'], as_index=False).agg({'Quantity': 'sum'}).rename(columns={'Quantity': 'Quantity_stock', 
                                                                                                                                  'Category': 'CategoryS', 
                                                                                                                                  'Brand': 'BrandS',
                                                                                                                                  'Color': 'ColorS'})

# Merging aggregated stock data with filtered orders
merged_df = pd.merge(filtered_df2, agg_stock, left_on='ProductNameColor', right_on='ProductColorName', how='right')




# Filter the DataFrame where Date_Formatted is NaN and Quantity_stock is not 0
df8 = merged_df[(merged_df['Date_Formatted'].isna()) & (merged_df['Quantity_stock'] != 0)]

# Step 2: Replace values based on the given conditions
df8.loc[:, 'Quantity'] = df8['Quantity'].fillna(0)
df8 = df8[['ProductColorName', 'Quantity', 'Quantity_stock']]
df8 = df8.rename(columns={'Quantity': 'TotalVolume', 'Quantity_stock': 'MaxAvailability'})


# df8 now contains the filtered and updated data

# Proceed with the rest of the analysis using the filtered_df


# Assuming 'ProductColorNameS' is the column name for product identifiers
# Calculate the total volume ordered for each product
product_total_volume = filtered_df.groupby('Product')['Volume'].sum().reset_index(name='TotalVolume')


# Calculate maximum availability for each product
product_max_availability = df.groupby('Product')['Availability'].max().reset_index(name='MaxAvailability')

# Merge these two DataFrames on 'ProductNameColor' (for overall product data)
product_data = pd.merge(product_total_volume, product_max_availability, on='Product')


# Define restock number
restock_number = 2


# Calculate Order Rate (Orders Per Day)
product_data['Order_Rate'] = product_data['TotalVolume'] / count_dates

# Calculate Stock Ratio
product_data['Restock_Ratio'] = product_data['Order_Rate'] / product_data['MaxAvailability'].replace(0, 0.1)



# Function to determine action status based on restock point
def determine_action_status(product_data):
    restock_point = product_data['Restock_Ratio']
    stock = product_data['MaxAvailability']
    
    if restock_point > 1 and stock == 0:
        return "Brown Type 1"
    elif 0.05 < restock_point and stock != 0 and round(product_data['MaxAvailability'] / product_data['Order_Rate']) < 10:
        return "Red"
    elif 0.01 < restock_point <= 1 and round(product_data['MaxAvailability'] / product_data['Order_Rate']) < 30:
        return "Yellow"
    elif 0.01 < restock_point <= 0.05 and round(product_data['MaxAvailability'] / product_data['Order_Rate']) > 30:
        return 'Green'
    elif 0.001 < restock_point < 0.01 or round(product_data['MaxAvailability'] / product_data['Order_Rate']) > 90:
        return "Brown Type 2"
    else:
        return 'Grey'

# Apply the function to determine action status
product_data['ActionStatus'] = product_data.apply(determine_action_status, axis=1)
product_data['DaysRemaining'] = round(product_data['MaxAvailability'] / product_data['Order_Rate'])



product_data2 = product_data[product_data['ActionStatus'] == 'Brown Type 1']


product_data3 = product_data[product_data['ActionStatus'] == 'Red']
product_data3['DaysRemaining'] = round(product_data3['MaxAvailability'] / product_data3['Order_Rate'])


product_data4 = product_data[product_data['ActionStatus'] == 'Yellow']
product_data4['DaysRemaining'] = round(product_data4['MaxAvailability'] / product_data4['Order_Rate'])


product_data7 = product_data[product_data['ActionStatus'] == 'Green']
product_data7['DaysRemaining'] = round(product_data7['MaxAvailability'] / product_data7['Order_Rate'])

product_data5 = product_data[product_data['ActionStatus'] == 'Grey']
product_data5['DaysRemaining'] = round(product_data5['MaxAvailability'] / product_data5['Order_Rate'])

product_data6 = product_data[product_data['ActionStatus'] == 'Brown Type 2']
product_data6['DaysRemaining'] = round(product_data6['MaxAvailability'] / product_data6['Order_Rate'])


# Custom HTML and CSS for different colored boxes and tables
st.markdown("""
    <style>
    .custom-box {
        padding: 20px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        font-size: 18px;
        color: #ffffff; /* White text color */
        margin-bottom: 10px; /* Space between the box and table */
    }
    .box-brown { background-color: #803400; }
    .box-red { background-color: #db2c12; }
    .box-yellow { background-color: #fae525; }
    .box-green { background-color: #1aba47; }
    .box-grey { background-color: #d6d6d6; }
    .box-brown2 { background-color: #cc7700; }
    </style>
    <div class="custom-box box-brown">
        💩
    </div>
""", unsafe_allow_html=True)
st.write("موجودی صفر / سفارش بالا ")
st.write(product_data2)
st.caption(f"Number of Products: {product_data2.shape[0]}")

st.markdown("""
    <div class="custom-box box-red">
        🚨 
    </div>
""", unsafe_allow_html=True)
st.write("موجود کردن در اولین فرصت")
st.write(product_data3)
st.caption(f"Number of Products: {product_data3.shape[0]}")

st.markdown("""
    <div class="custom-box box-yellow">
        📅
    </div>
""", unsafe_allow_html=True)
st.write("برنامه ریزی برای موجود کردن کالا")
st.write(product_data4)
st.caption(f"Number of Products: {product_data4.shape[0]}")


st.markdown("""
    <div class="custom-box box-green">
        🙌
    </div>
""", unsafe_allow_html=True)
st.write("حاشیه نسبتا امن موجودی کنونی")
st.write(product_data7)
st.caption(f"Number of Products: {product_data7.shape[0]}")

st.markdown("""
    <div class="custom-box box-grey">
        ❓
    </div>
""", unsafe_allow_html=True)
st.write("کالاهای مریض")
st.write(product_data5)
st.caption(f"Number of Products: {product_data5.shape[0]}")

st.markdown("""
    <div class="custom-box box-brown2">
        🙊🙈🙉
    </div>
""", unsafe_allow_html=True)
st.write("(فروش کم) موجودی بیش از میزان تقاضا")
st.write(product_data6)
st.caption(f"Number of row: {product_data6.shape[0]}")
st.write("(فروش صفر ) موجودی بیش از میزان تقاضا")
st.write(df8)
st.caption(f"Number of Products: {df8.shape[0]}")




