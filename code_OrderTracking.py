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



# Row A
a2, a3, a4 = st.columns(3)
image = Image.open('dgland_icon.png')
st.image(image, width=100)  # Change 100 to the desired width in pixels
a2.metric("Wind", "9 mph", "-8%")
a3.metric("Humidity", "86%", "4%")
a4.metric("Temperture", "33", "3%")
