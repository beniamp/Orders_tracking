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


df_orders = ps.read_csv('Orders.csv')

# calculating 3 metrics in second row
total_sales = df_orders['TotalPrice'].sum()
total_volume = df_orders['Quantity'].sum()
total_net = df_orders['TotalNetPrice'].sum()


# Row A
b1, b2, b3 = st.columns(3)
b1.selectbox('Select Date', ['Cat', 'Dog'])
b2.selectbox('Select Category', ['Cat', 'Dog'])
b3.selectbox('Select Brand', ['Cat', 'Dog'])

# Row B
a2, a3, a4 = st.columns(3)
a2.metric("Overall Price", total_sales, "-8%")
a3.metric("Overall Volume", total_volume, "4%")
a4.metric("Overal Net Price", total_net, "3%")
