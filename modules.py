# import packages
import streamlit as st
import pandas as pd
import folium
import streamlit_folium
from streamlit_folium import folium_static
import os
import requests
import json

def bulk_pc_lookup(postcodes):
    # set up the api request
    url = "https://api.postcodes.io/postcodes"
    headers = {"Content-Type": "application/json"}
    
    # divide postcodes into batches of 100
    postcode_batches = [postcodes[i:i + 100] for i in range(0, len(postcodes), 100)]
    
    # to store the results
    postcode_data = []
    
    for batch in postcode_batches:
        # specify our input data and response, specifying that we are working with data in json format
        data = {"postcodes": batch}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        # check for successful response
        if response.status_code == 200:
            results = response.json()["result"]
            
            for result in results:
                postcode = result["query"]
                
                if result["result"] is not None:
                    lsoa = result["result"]["codes"]["lsoa"]
                    latitude = result["result"]["latitude"]
                    longitude = result["result"]["longitude"]
                    region = result["result"]["region"]
                    postcode_data.append({"Postcode": postcode, 
                                          "Latitude": latitude, 
                                          "Longitude": longitude, 
                                          "Region": region})
        else:
            # handle errors for each batch
            print(f"Error in batch: {response.status_code}")
    
    return postcode_data

def get_icon_colour(risk_rating):
    if risk_rating == "Green":
        return "green"
    elif risk_rating == "Red":
        return "red"
    elif risk_rating == "Amber":
        return "orange"
    else:
        return "black"  # Default color