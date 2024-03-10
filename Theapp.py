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
from modules import get_icon_colour

# ------------------------

st.set_page_config(page_title="Main Fund Risk App", initial_sidebar_state="expanded", layout="wide")

st.header("Main Fund Risk Status Map and Data")
st.subheader("Use the sidebar to filter the map and data results on the main page. The icon colour of the map point represents the risk rating for that site.")

df = pd.read_excel("matcheddata.xlsx")

df= df.rename(columns={"Site Expected or Actual Start Date (for Multi-Site Builds this reflects the earliest date)":"Date"})

df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True)

min_date = df["Date"].min()  # Get the minimum date from the column
max_date = df["Date"].max()  # Get the maximum date from the column

st.sidebar.write("## Filter Options")

selected_date = st.sidebar.date_input("Select a Site Expected/Actual Start Date", value=min_date)
selected_date = pd.to_datetime(selected_date)

min_weeks = round(df['Build Period'].min())
max_weeks = round(df['Build Period'].max())

build_period_min, build_period_max = st.sidebar.slider('Select Build Period (Weeks)', min_weeks, max_weeks, (min_weeks, max_weeks))

min_grant, max_grant = round(df['Grant Amount'].min()), round(df['Grant Amount'].max())
selected_min_grant, selected_max_grant = st.sidebar.slider('Select Range for Grant Amount (£)', min_grant, max_grant, (min_grant, max_grant))

min_disbursed, max_disbursed = round(df['Disbursed Amount'].min()), round(df['Disbursed Amount'].max())
selected_min_disbursed, selected_max_disbursed = st.sidebar.slider('Select Range for Disbursed Amount (£)', min_disbursed, max_disbursed, (min_disbursed, max_disbursed))

min_disbursement, max_disbursement = df['Proportion of Capital Disbursed'].min(), df['Proportion of Capital Disbursed'].max()
selected_min_disbursement, selected_max_disbursement = st.sidebar.slider('Proportion of Capital Disbursed (%)', min_disbursement, max_disbursement, (min_disbursement, max_disbursement))


#st.write(df)

def filter_data(df, selected_date, selected_min_grant, selected_max_grant, selected_min_disbursed, selected_max_disbursed, selected_min_disbursement, selected_max_disbursement, build_period_min, build_period_max):
    
    filtered_df = df[
        (df["Date"] >= selected_date) &  # Filter by date
        (df["Grant Amount"] >= selected_min_grant) &  # Filter by grant amount
        (df["Grant Amount"] <= selected_max_grant) &
        (df["Build Period"] >= build_period_min) &  # Filter by grant amount
        (df["Build Period"] <= build_period_max) &
        (df["Disbursed Amount"] >= selected_min_disbursed) &  # Filter by disbursed amount
        (df["Disbursed Amount"] <= selected_max_disbursed) &
        (df["Proportion of Capital Disbursed"] >= selected_min_disbursement) &  # Filter by proportion of capital disbursed
        (df["Proportion of Capital Disbursed"] <= selected_max_disbursement)
    ]
    num_rows_filtered = len(filtered_df)  # Count the number of rows in the filtered DataFrame
    st.write("Results")
    st.write(num_rows_filtered)
    return filtered_df

# Filter data based on user selections
filtered_df = filter_data(df.copy(), selected_date, selected_min_grant, selected_max_grant, selected_min_disbursed, selected_max_disbursed, selected_min_disbursement, selected_max_disbursement, build_period_min, build_period_max)

col1, col2 = st.columns(2)

with col1:
    # Create the map (assuming you have Latitude and Longitude columns)
    m = folium.Map(location=[filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()], zoom_start=6)

    for idx, row in filtered_df.iterrows():
        icon_colour = get_icon_colour(row['Risk Rating'])
        folium.Marker(location=[row['Latitude'], row['Longitude']],
                    icon=folium.Icon(color=icon_colour), popup=(row['Investment Name'])
                    ).add_to(m)

    # Display the map
    folium_static(m, width=500, height=400)

with col2:

    region_counts = filtered_df.groupby('Region').size().to_frame(name='Count').reset_index()
    st.subheader("Sites* by Region (Filtered)")
    st.dataframe(region_counts)
    st.warning("*Please note, if multi-site, only one site is counted here")

filtered_df = filtered_df.drop(columns=['Site Name', 'Count'])
st.subheader("Filtered Results")
st.success("Hover over the table in the top right to download the results as a CSV file.")
st.write(filtered_df)