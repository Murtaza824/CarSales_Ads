import streamlit as st
import os
import pandas as pd
import plotly.express as px
import numpy as np
import altair as alt
import pydeck as pdk
import googlemaps
from googlemaps import convert

st.set_page_config(layout="wide")
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 3rem;
                    padding-right: 3rem;
                }
        </style>
        """, unsafe_allow_html=True)


### Code for dataframe
payer_df = pd.read_csv('payer_dataset_extract.csv')
payer_df = payer_df.drop(['sub_npi','billing_code_modifier', 'provider_group_id_type', 'provider_group_id', 'negotiation_arrangement','billing_class'], axis=1)

_ = """
api_key = os.getenv('api_key')
client = googlemaps.Client()

def geocode(client, address=None, place_id=None, components=None, bounds=None, region=None, language=None):
   
   params = {}
   
   if address:
    params["address"] = address
    
   if place_id:
    params["place_id"] = place_id

   if components:
    params["components"] = convert.components(components)

   if bounds:
    params["bounds"] = convert.bounds(bounds)

   if region:
    params["region"] = region

   if language:
    params["language"] = language

   response = client._request("/maps/api/geocode/json", params)

   if response.get('status') == 'OK':
       location = response['results'][0]['geometry']['location']
       lat = location['lat']
       lng = location['lng']
       return lat, lng
   else:
      return None, None

for i in payer_df['provider_zip_code']:
   lat, lng = geocode(client, address=i)
   payer_df['lat'] = lat
   payer_df['lng'] = lng
"""

num_of_providers_linked_to_entity = payer_df.groupby(['provider_state','reporting_entity_name_in_network_files'])['provider_name'].count().sort_values(ascending=False).reset_index()
nego_rate_per_entity = payer_df.groupby(['provider_state','reporting_entity_name_in_network_files','negotiated_type'])['negotiated_rate'].mean().reset_index()
nego_rate_per_provider = payer_df.groupby(['provider_state','provider_name','negotiated_type'])['negotiated_rate'].mean().reset_index()
nego_rate_by_prov_state = payer_df.groupby(['provider_state','reporting_entity_name_in_network_files','negotiated_type'])['negotiated_rate'].mean().reset_index()
#prov_state_bypayer = payer_df.groupby(['provider_state','reporting_entity_name_in_network_files'])['negotiated_rate'].mean()



st.title('Healthcare Payer Data Across the U.S.')

st.markdown("""
This app allows you to explore healthcare payer data across the U.S.
You can calculate the price of a service based on the negotiated rate for a given payer, provider, and state.
Further below, you can filter and play around with the data across different dimensions.
""")

st.sidebar.header('Filter Data')

state = st.sidebar.selectbox('Select State', ['All'] + list(payer_df['provider_state'].unique()))
payer = st.sidebar.selectbox('Select Payer', ['All'] + list(payer_df['reporting_entity_name_in_network_files'].unique()))
provider = st.sidebar.selectbox('Select Provider', ['All'] + list(payer_df['provider_name'].unique()))
negotiated_type = st.sidebar.selectbox('Select Negotiation Type', ['All'] + list(payer_df['negotiated_type'].unique()))
billing_code = st.sidebar.selectbox('Select Billing Code', ['All'] + list(payer_df['billing_code_name'].unique()))

#st.sidebar.header('Data Filtering')

# Filter data based on user selection
filtered_df = payer_df
filtered_df['negotiated_type'] = filtered_df['negotiated_type'].replace('negotiatied', 'negotiated')


if state != 'All':
    filtered_df = filtered_df[filtered_df['provider_state'] == state]
    num_of_providers_linked_to_entity = num_of_providers_linked_to_entity[num_of_providers_linked_to_entity['provider_state'] == state]
    nego_rate_per_entity = nego_rate_per_entity[nego_rate_per_entity['provider_state'] == state]

if payer != 'All':
    filtered_df = filtered_df[filtered_df['reporting_entity_name_in_network_files'] == payer]
    num_of_providers_linked_to_entity = num_of_providers_linked_to_entity[num_of_providers_linked_to_entity['reporting_entity_name_in_network_files'] == payer]
    nego_rate_per_entity = nego_rate_per_entity[nego_rate_per_entity['reporting_entity_name_in_network_files'] == payer]

if provider != 'All':
    filtered_df = filtered_df[filtered_df['provider_name'] == provider]
    num_of_providers_linked_to_entity = num_of_providers_linked_to_entity[num_of_providers_linked_to_entity['provider_name'] == provider]
    nego_rate_per_provider = nego_rate_per_provider[nego_rate_per_provider['provider_name'] == provider]

if negotiated_type != 'All':
    filtered_df = filtered_df[filtered_df['negotiated_type'] == negotiated_type]
    nego_rate_per_entity = nego_rate_per_entity[nego_rate_per_entity['negotiated_type'] == negotiated_type]
    nego_rate_per_provider = nego_rate_per_provider[nego_rate_per_provider['negotiated_type'] == negotiated_type]
    nego_rate_by_prov_state = nego_rate_by_prov_state[nego_rate_by_prov_state['negotiated_type'] == negotiated_type]

if billing_code != 'All':
    filtered_df = filtered_df[filtered_df['billing_code_name'] == billing_code]


st.subheader('Price Calculator')
rows_other = st.columns(7)
state_calc = rows_other[0].selectbox('Select state', ['All'] + list(payer_df['provider_state'].unique()))
payer_calc = rows_other[1].selectbox('Select payer', ['All'] + list(payer_df['reporting_entity_name_in_network_files'].unique()))
provider_calc = rows_other[2].selectbox('Select provider', ['All'] + list(payer_df['provider_name'].unique()))
negotiated_type_calc = rows_other[3].selectbox('Select negotiated type', ['All'] + list(payer_df['negotiated_type'].unique()))
number_input = rows_other[4].number_input('Enter the billed charge', min_value=0, step=100)
procedure_type = rows_other[5].selectbox('Select procedure type', ['All'] + list(payer_df['billing_code_name'].unique()))

rows_other[6].write('')
rows_other[6].write('')
calculate = rows_other[6].button('Calculate')

if calculate:
    query_conditions = []
    if state_calc != 'All':
        query_conditions.append(f'provider_state == "{state_calc}"')
    if payer_calc != 'All':
        query_conditions.append(f'reporting_entity_name_in_network_files == "{payer_calc}"')
    if provider_calc != 'All':
        query_conditions.append(f'provider_name == "{provider_calc}"')
    if negotiated_type_calc != 'All':
        query_conditions.append(f'negotiated_type == "{negotiated_type_calc}"')
    if procedure_type != 'All':
        query_conditions.append(f'billing_code_name == "{procedure_type}"')
    
    query_string = ' & '.join(query_conditions)
    
    #st.write(f"Debug: Query string: {query_string}")
    #st.write(f"Debug: Original dataframe shape: {payer_df.shape}")
    
    if query_string:
        filtered_data = payer_df.query(query_string)
        #st.write(f"Debug: Filtered data shape: {filtered_data.shape}")
        #st.write("Debug: First 5 rows of filtered data:")
        #st.dataframe(filtered_data.head())
    else:
        filtered_data = payer_df
    
    if not filtered_data.empty:
          if negotiated_type_calc == 'negotiated':
            negotiated_rate = filtered_data['negotiated_rate'].mean()
            #st.write(f'The average negotiated rate is ${avg_negotiated_rate:.2f}')
            st.write(f'Your bill after taking into account the negotiated rate is ${negotiated_rate:.2f}')
          elif negotiated_type_calc == 'per diem':
            negotiated_rate = filtered_data['negotiated_rate'].mean()
            #st.write(f'The average negotiated rate is ${avg_negotiated_rate:.2f}')
            st.write(f'Your bill after taking into account the negotiated rate is ${negotiated_rate:.2f}')
          elif negotiated_type_calc == 'fee schedule':
            negotiated_rate = filtered_data['negotiated_rate'].mean()
            #st.write(f'The average negotiated rate is ${avg_negotiated_rate:.2f}')
            st.write(f'Your bill after taking into account the negotiated rate is ${negotiated_rate:.2f}')
          elif negotiated_type_calc == 'percentage':
            avg_negotiated_rate = filtered_data['negotiated_rate'].mean() / 100
            negotiated_rate = number_input * avg_negotiated_rate
            #st.write(f'The average negotiated rate is ${avg_negotiated_rate:.2f}')
            st.write(f'Your bill after taking into account the negotiated rate is ${negotiated_rate:.2f}')
          elif negotiated_type_calc == 'derived':
            negotiated_rate = filtered_data['negotiated_rate'].mean()
            #st.write(f'The average negotiated rate is ${avg_negotiated_rate:.2f}')
            st.write(f'Your bill after taking into account the negotiated rate is ${negotiated_rate:.2f}')
          elif number_input == 0:
            negotiated_rate = 0
            #st.write(f'The average negotiated rate is ${avg_negotiated_rate:.2f}')
            st.write(f'Your bill after taking into account the negotiated rate is ${negotiated_rate:.2f}')
          else:
            avg_negotiated_rate = filtered_data['negotiated_rate'].mean()
            #st.write(f"Debug: Average negotiated rate: ${avg_negotiated_rate:.2f}")
            negotiated_rate = avg_negotiated_rate
            st.write(f'The average negotiated rate is ${avg_negotiated_rate:.2f}')
            st.write(f'Your bill after taking into account the negotiated rate is ${negotiated_rate:.2f}')
    else:
        st.write('No data available for the selected criteria.')
        #st.write("Debug: Unique values in relevant columns:")
        #for col in ['provider_state', 'reporting_entity_name_in_network_files', 'provider_name', 'negotiated_type']:
            #st.write(f"{col}: {payer_df[col].unique()}")

st.divider()

# Display filtered dataframe
st.subheader('Filtered Data')
st.dataframe(filtered_df)

# Display summary statistics
st.subheader('Summary Statistics')
st.write(f"Number of records: {len(filtered_df)}")
st.write(f"Average negotiated rate: ${filtered_df['negotiated_rate'].mean():.2f}")
median_nego = round(filtered_df.query('negotiated_type == "negotiated"')['negotiated_rate'].median(), 2)
st.write(f"Median negotiated rate: ${median_nego}")

st.divider()

rows = st.columns(2)
rows[0].markdown('Number of Providers per Insurance Company')
rows[0].dataframe(num_of_providers_linked_to_entity)
rows[1].markdown('Negotiated Rate per Insurance Company')
rows[1].dataframe(nego_rate_per_entity)


#Display number of providers per Insurance Company
#st.subheader('Number of Providers per Insurance Company')
#st.dataframe(num_of_providers_linked_to_entity)

#Display nego rate per Insurance Company
#st.subheader('Negotiated Rate per Insurance Company')
#st.dataframe(nego_rate_per_entity)

#Display nego rate per provider
#st.subheader('Negotiated Rate per Provider')
#st.dataframe(nego_rate_per_provider)

#Display nego rate per provider state
#st.subheader('Negotiated Rate per Provider State')
#st.dataframe(nego_rate_by_prov_state)

         
# Create a bar chart of average negotiated rates by billing code
st.subheader('Average Negotiated Rates by Insurance Company')
avg_rates1 = payer_df.groupby('reporting_entity_name_in_network_files')['negotiated_rate'].mean().sort_values(ascending=False).reset_index()
fig1 = px.bar(avg_rates1, x='reporting_entity_name_in_network_files', y='negotiated_rate', width=1000, height=800)
fig1.update_layout(xaxis_title='Insurance Company', yaxis_title='Average Negotiated Rate ($)')
st.plotly_chart(fig1)

st.subheader('Average Negotiated Rates by State')
avg_rates2 = payer_df.groupby('provider_state')['negotiated_rate'].mean().reset_index()
fig2 = px.scatter(avg_rates2, x='provider_state', y='negotiated_rate', width=1000, height=800)
fig2.update_layout(xaxis_title='Provider State', yaxis_title='Average Negotiated Rate ($)')
st.plotly_chart(fig2)

__ = """
def map(data, lat, lon, zoom):
    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 50,
            },
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=data,
                    get_position=["lon", "lat"],
                    radius=100,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
            ],
        )
    )
st.subheader('Provider Locations')
map(payer_df, payer_df['lat'], payer_df['lng'], 11)
"""

st.write('')
st.write('')
st.write('')
st.write('')



