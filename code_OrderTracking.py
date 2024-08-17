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

# Row A
b1, b2, b3 = st.columns(3)
b1.selectbox('Select Date', date_val)
b2.selectbox('Select Category', category_val)
b3.selectbox('Select Brand', color_val)

# Row B
a2, a3, a4 = st.columns(3)
a2.metric("Overall Price", formatted_total_sales, "-8%")
#a3.metric("Overall Volume", formatted_total_volume, "4%")
#a3.metric("Overall Volume", f"{formatted_total_volume} M", "4%")
a4.metric("Overal Net Price", formatted_total_net, "3%")
