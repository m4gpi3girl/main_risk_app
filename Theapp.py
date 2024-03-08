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
from datetime import datetime

# ------------------------

st.set_page_config(page_title="Main Fund Risk App", initial_sidebar_state="expanded", layout="wide")

df = pd.read_excel("matcheddata.xlsx")

df= df.rename(columns={"Site Expected or Actual Start Date (for Multi-Site Builds this reflects the earliest date)":"Date"})

df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True)

min_date = df["Date"].min()  # Get the minimum date from the column
max_date = df["Date"].max()  # Get the maximum date from the column

selected_date = st.sidebar.date_input("Select a Site Expected/Actual Start Date", value=min_date)
selected_date = pd.to_datetime(selected_date)

min_grant, max_grant = df['Grant Amount'].min(), df['Grant Amount'].max()
selected_min_grant, selected_max_grant = st.sidebar.slider('Grant Amount Range (£)', min_grant, max_grant, (min_grant, max_grant))

min_disbursed, max_disbursed = df['Disbursed Amount'].min(), df['Disbursed Amount'].max()
selected_min_disbursed, selected_max_disbursed = st.sidebar.slider('Disbursed Amount Range (£)', min_disbursed, max_disbursed, (min_disbursed, max_disbursed))

min_disbursement, max_disbursement = df['Proportion of Capital Disbursed'].min(), df['Proportion of Capital Disbursed'].max()
selected_min_disbursement, selected_max_disbursement = st.sidebar.slider('Proportion of Capital Disbursed (%)', min_disbursement, max_disbursement, (min_disbursement, max_disbursement))


#st.write(df)

def filter_data(df, selected_date, selected_min_grant, selected_max_grant, selected_min_disbursed, selected_max_disbursed, selected_min_disbursement, selected_max_disbursement):
    
    filtered_df = df[
        (df["Date"] >= selected_date) &  # Filter by date
        (df["Grant Amount"] >= selected_min_grant) &  # Filter by grant amount
        (df["Grant Amount"] <= selected_max_grant) &
        (df["Disbursed Amount"] >= selected_min_disbursed) &  # Filter by disbursed amount
        (df["Disbursed Amount"] <= selected_max_disbursed) &
        (df["Proportion of Capital Disbursed"] >= selected_min_disbursement) &  # Filter by proportion of capital disbursed
        (df["Proportion of Capital Disbursed"] <= selected_max_disbursement)
    ]
    num_rows_filtered = len(filtered_df)  # Count the number of rows in the filtered DataFrame
    st.write("### Results")
    st.write(num_rows_filtered)
    return filtered_df

# Filter data based on user selections
filtered_df = filter_data(df.copy(), selected_date, selected_min_grant, selected_max_grant, selected_min_disbursed, selected_max_disbursed, selected_min_disbursement, selected_max_disbursement)

col1, col2 = st.columns(2)

with col1:
    # Create the map (assuming you have Latitude and Longitude columns)
    m = folium.Map(location=[filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()], zoom_start=6)

    for idx, row in filtered_df.iterrows():
        folium.Marker(location=[row['Latitude'], row['Longitude']],
                    icon=folium.Icon(color='red'),
                    ).add_to(m)

    # Display the map
    folium_static(m, width=500, height=400)

with col2:

    region_counts = filtered_df.groupby('Region').size().to_frame(name='Count').reset_index()
    st.subheader("Sites by Region (Filtered)")
    st.dataframe(region_counts)

filtered_df = filtered_df.drop(columns=['Unnamed: 2', 'Site Name', 'Count'])
st.subheader("Filtered Results")
st.write(filtered_df)