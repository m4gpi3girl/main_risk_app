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
from datetime import datetime

# ------------------------

st.set_page_config(page_title="Main Fund Risk App", layout="wide")

# import data
main_risk = 'main_risk_data_with_pc.xlsx'
df = pd.read_excel(main_risk)

# qa check
#st.write(df.shape[0])
#st.write(df.head())
#a = df['Site Postcode'].nunique()
#st.write(f"unique postcodes: {a}")

# -------------------------

# match data w lat, lon, rgn
postcodes = df['Site Postcode'].tolist()
op = bulk_pc_lookup(postcodes)
op_df = pd.DataFrame(op)

# qa check
#st.write(op_df.shape[0])
#st.write(op_df.head())
#b = op_df['Postcode'].nunique()
#st.write(f"unique postcodes: {b}")

# -------------------------

# investigate non-matches
#if st.button('See rows with no match'):
#    df1 = df
#    df2 = op_df
#    df1 = df1.rename(columns={'Site Postcode':'Postcode'})
#    # Merge the dataframes based on the specified columns
#    merged_df = pd.merge(df1, df2, on='Postcode', how='left', indicator=True)
#    # Create a third dataframe containing rows from df1 not present in df2
#    not_in_df2 = merged_df[merged_df['_merge'] == 'left_only'].drop('_merge', axis=1)
#    st.write(not_in_df2)

# manual solution to non-matches
manual_data = [['GL14 2SB', 51.824143, -2.499481, "South West"],
               ['IP3 9PZ', 52.037232, 1.19297, "East of England"],
               ['S60 2AH', 53.424011, -1.354178, "Yorkshire and The Humber"],
               ['PR1 2QA', 53.758851, -2.697817, "North West"],
               ['PO1 2DR', 50.797242, -1.08973, 'South East']
               ]

manual_pc = pd.DataFrame(manual_data, columns=['Postcode', 'Latitude', 'Longitude', 'Region'])
               
# --------------------------------

# merge data together

test = pd.merge(df, manual_pc, left_on="Site Postcode", right_on = "Postcode", how="inner")


folium_data = pd.merge(df, op_df, left_on='Site Postcode', right_on="Postcode", how='inner')
folium_data.dropna(subset=['Latitude'], axis=0)


#st.write(folium_data.head())
#st.write(folium_data.shape[0])

#st.write(test.head())
#st.write(test.shape[0])

new = pd.concat([folium_data, test], ignore_index=True)
new.drop_duplicates(subset=['Investment Name'], inplace=True)
#new.drop_duplicates()
#st.write(new['Postcode'].nunique())
#st.write(new.shape[0])
#st.write(list(new))

#st.write(new)
#st.write(new.shape[0])
#st.write(new['Investment Name'].nunique())
#res = pd.concat([folium_data, test])

# ----------------------------------------

# sort out the data
#st.write(list(new))

new.to_excel("matcheddata.xlsx")
new["Site Expected or Actual Start Date (for Multi-Site Builds this reflects the earliest date)"] = pd.to_datetime(new["Site Expected or Actual Start Date (for Multi-Site Builds this reflects the earliest date)"], format='%d/%m/%Y')

# Calculate default start and end dates
default_start_date = new["Site Expected or Actual Start Date (for Multi-Site Builds this reflects the earliest date)"].min()
default_end_date = new["Site Expected or Actual Start Date (for Multi-Site Builds this reflects the earliest date)"].max()



# filters in sidebar
min_grant, max_grant = new['Grant Amount'].min(), new['Grant Amount'].max()
selected_min_grant, selected_max_grant = st.sidebar.slider('Grant Amount Range (£)', min_grant, max_grant, (min_grant, max_grant))

min_disbursed, max_disbursed = new['Disbursed Amount'].min(), new['Disbursed Amount'].max()
selected_min_disbursed, selected_max_disbursed = st.sidebar.slider('Disbursed Amount Range (£)', min_disbursed, max_disbursed, (min_disbursed, max_disbursed))

start_date = st.sidebar.date_input("Date (Earliest)", value=default_start_date)
end_date = st.sidebar.date_input("Date (Latest)", value=default_end_date)

min_disbursement, max_disbursement = new['Proportion of Capital Disbursed'].min(), new['Proportion of Capital Disbursed'].max()
selected_min_disbursement, selected_max_disbursement = st.sidebar.slider('Proportion of Capital Disbursed', min_disbursement, max_disbursement, (min_disbursement, max_disbursement))

def update_map(min_grant, max_grant, min_disbursed, max_disbursed, start_date, end_date, min_disbursement, max_disbursement):

    total_sites = 0

    m = folium.Map(location=[new['Latitude'].mean(), new['Longitude'].mean()], zoom_start=6)

    for idx, row in new.iterrows():

        if (min_grant <= row['Grant Amount'] <= max_grant) and \
        (min_disbursed <= row['Disbursed Amount'] <= max_disbursed) and \
        (min_disbursement <= row['Proportion of Capital Disbursed'] <= max_disbursement) and \
        (start_date <= pd.to_datetime(row["Site Expected or Actual Start Date (for Multi-Site Builds this reflects the earliest date)"], format='%d/%m/%Y').dt.date <= end_date):

            folium.Marker(location=[row['Latitude'], row['Longitude']],
                            icon=folium.Icon(color='red'),
                        ).add_to(m)
            # Increment total sites
            total_sites += 1

    # Display the total sites above the map
    st.markdown(f"**Total Sites: {total_sites}**")

    # Display the map
    folium_static(m)

# Display the widgets and the map
update_map(selected_min_grant, selected_max_grant, selected_min_disbursed, selected_max_disbursed, start_date, end_date, selected_min_disbursement, selected_max_disbursement)

st.write(new)


st.write(new)


