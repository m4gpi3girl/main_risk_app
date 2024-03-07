#------------------------

# import packages
import streamlit as st
import pandas as pd
import folium
import streamlit_folium
from streamlit_folium import folium_static
import os
import requests
import json
from modules import bulk_pc_lookup

# ------------------------

# import data
main_risk = 'main_risk_data_with_pc.xlsx'
df = pd.read_excel(main_risk)

# qa check
st.write(df.shape[0])
st.write(df.head())
a = df['Site Postcode'].nunique()
st.write(f"unique postcodes: {a}")

# -------------------------

# match data w lat, lon, rgn
postcodes = df['Site Postcode'].tolist()
op = bulk_pc_lookup(postcodes)
op_df = pd.DataFrame(op)

# qa check
st.write(op_df.shape[0])
st.write(op_df.head())
b = op_df['Postcode'].nunique()
st.write(f"unique postcodes: {b}")
# -------------------------

