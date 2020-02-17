#!/usr/bin/env python
# coding: utf-8

# In[4]:


import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

get_ipython().system("conda install -c conda-forge geopy --yes # uncomment this line if you haven't completed the Foursquare API lab")
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

#!conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library

print('Libraries imported.')


# In[5]:


import seaborn as sns
import matplotlib.pyplot as plt


# In[6]:


get_ipython().system("wget -q -O 'newyork_data.json' https://cocl.us/new_york_dataset")
print('Data downloaded!')
with open('newyork_data.json') as json_data:
    newyork_data = json.load(json_data)


# In[7]:


# define the dataframe columns
column_names = ['Borough', 'Neighborhood', 'Latitude', 'Longitude'] 

# instantiate the dataframe
neighborhoods = pd.DataFrame(columns=column_names)

neighborhoods_data = newyork_data['features']

for data in neighborhoods_data:
    borough = neighborhood_name = data['properties']['borough'] 
    neighborhood_name = data['properties']['name']
        
    neighborhood_latlon = data['geometry']['coordinates']
    neighborhood_lat = neighborhood_latlon[1]
    neighborhood_lon = neighborhood_latlon[0]
    
    neighborhoods = neighborhoods.append({'Borough': borough,
                                          'Neighborhood': neighborhood_name,
                                          'Latitude': neighborhood_lat,
                                          'Longitude': neighborhood_lon}, ignore_index=True)


# In[8]:


address = 'New York City, NY'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of New York City are {}, {}.'.format(latitude, longitude))


# In[9]:


manhattan_data = neighborhoods[neighborhoods['Borough'] == 'Manhattan'].reset_index(drop=True)
manhattan_data.head()


# In[10]:


address = 'Manhattan, NY'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Manhattan are {}, {}.'.format(latitude, longitude))


# In[11]:


CLIENT_ID = "3PDKD4AMG35QPRO51VZZSFW52MDEIWTI0EF0QC5USZYCDQAI" # your Foursquare ID
CLIENT_SECRET = "4BKYTYDXFUXSM1Q0BU1JYX3HNRP5PMMTN3F4N4BMSTD0PKAX"

 # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[31]:


# create map of New York using latitude and longitude values
map_newyork = folium.Map(location=[latitude, longitude], zoom_start=10)

# add markers to map
for lat, lng, borough, neighborhood in zip(neighborhoods['Latitude'], neighborhoods['Longitude'], neighborhoods['Borough'], neighborhoods['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        labels=True,
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_newyork) 
    
    
neighborhood_latitude = manhattan_data.loc[0, 'Latitude'] # neighborhood latitude value
neighborhood_longitude = manhattan_data.loc[0, 'Longitude'] # neighborhood longitude value

neighborhood_name = manhattan_data.loc[0, 'Neighborhood'] # neighborhood name

print('Latitude and longitude values of {} are {}, {}.'.format(neighborhood_name, 
                                                               neighborhood_latitude, 
                                                               neighborhood_longitude))    
    
# type your answer here
LIMIT = 100 # limit of number of venues returned by Foursquare API

radius = 50 # define radius


# create URL
url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
    CLIENT_ID, 
    CLIENT_SECRET, 
    VERSION, 
    neighborhood_latitude, 
    neighborhood_longitude, 
    radius, 
    LIMIT)
map_newyork


# In[13]:





results = requests.get(url).json()
#results


# In[14]:


# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[15]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head()


# In[16]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        #print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[17]:


# type your answer here

manhattan_venues = getNearbyVenues(names=manhattan_data['Neighborhood'],
                                   latitudes=manhattan_data['Latitude'],
                                   longitudes=manhattan_data['Longitude']
                                  )


# In[18]:


manhattan_venues['venue_cat'] = manhattan_venues['Venue Category']

df = manhattan_venues.groupby(['Neighborhood','Venue Category'], as_index=False).agg({'venue_cat':'count'})

df['venue_cat'] = df['venue_cat'].astype(int)

df['Venue Category'].value_counts()

#variety within a neighboorhood
v_df = df.groupby(['Neighborhood'], as_index=False).agg({'Venue Category':'count'})
v_df


# In[19]:


manhattan_venues['venue_cat'] = manhattan_venues['Venue Category']

df = manhattan_venues.groupby(['Neighborhood','Venue Category'], as_index=False).agg({'venue_cat':'count'})

df['venue_cat'] = df['venue_cat'].astype(int)

df

#df.sort_values(by=['venue_cat'])

df_1=df.groupby(['Neighborhood','Venue Category'],as_index=False).agg({'venue_cat':'max'})
#df_1.groupby(['Neighborhood','Venue Category']).size().sort_values(ascending=False)
df_1 = df_1.loc[df_1['venue_cat']>4]
#df_1
df_1.Neighborhood.value_counts()


# In[20]:


#histogram creation
df_1.plot.hist(by='Neighborhood',bins=25)


# In[21]:


sns.set(style='whitegrid')
plt.figure(figsize=(10,8))
ax = sns.boxplot(x = 'venue_cat', data = df_1, orient="v")


# In[22]:


df_2 = df_1.loc[df_1['venue_cat']>6]

sns.set(style='darkgrid')
plt.figure(figsize=(50,30))
ax = sns.countplot(x='Neighborhood', data=df_2)


# In[23]:


grouped_df=df_2.groupby(['Neighborhood','Venue Category'], as_index=False).agg({'venue_cat':'max'})
grouped_df = grouped_df.rename(columns={'venue_cat':'Volume'})
grouped_df['venue_name_loc'] = grouped_df['Neighborhood'].str.cat(grouped_df['Venue Category'], sep ="-") 

grouped_df

ax = grouped_df.plot.bar(x='venue_name_loc', y='Volume', rot='vertical',label='Venue Volume')

