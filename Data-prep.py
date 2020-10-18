import pandas as pd
from geopy.geocoders import Nominatim
import multiprocessing as mp
from tqdm import tqdm
import pickle


# def my_function(coords):
#     location = geo_locator.reverse(coords)
#     return location.raw['address']

full_data = pd.read_excel('data/covid_scenario.xlsx')
data = full_data[['zid', 'x', 'y']].drop_duplicates()
# inputs = data['y'].astype(str) + ', ' + data['x'].astype(str)
# geo_locator = Nominatim(user_agent="myGeocoder")
#
# pool = mp.Pool(mp.cpu_count())
#
# location_data = [pool.apply(my_function, args=(row,)) for row in tqdm(inputs)]
#
# with open('location_data.pkl', 'wb') as handle:
#     pickle.dump(location_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('location_data.pkl', 'rb') as handle:
    location_data = pickle.load(handle)

data['state'] = [x['state'] for x in location_data]

state_districts = []
suburbs = []
for address in location_data:
    if address['state'] == 'Москва':
        try:
            state_district = address['state_district']
            suburb = address['city']
        except:
            try:
                state_district= address['state_district']
                suburb = address['town']
            except:
                try:
                    state_district = address['state_district']
                    suburb = address['suburb']
                except:
                    try:
                        state_district = address['state_district']
                        suburb = address['village']
                    except:
                        state_district = address['city']
                        suburb = address['suburb']
    else:
        try:
            state_district = address['county']
            suburb = address['city']
        except:
            try:
                state_district = address['county']
                suburb = address['city']
            except:
                try:
                    state_district = address['county']
                    suburb = address['hamlet']
                except:
                    try:
                        state_district = address['county']
                        suburb = address['neighbourhood']
                    except:
                        try:
                            state_district = address['county']
                            suburb = address['town']
                        except:
                            try:
                                state_district = address['county']
                                suburb = address['village']
                            except:
                                try:
                                    state_district = address['county']
                                    suburb = address['allotments']
                                except:
                                    try:
                                        state_district = address['county']
                                        suburb = address['road']
                                    except:
                                        try:
                                            state_district = address['county']
                                            suburb = address['suburb']
                                        except:
                                            try:
                                                state_district = address['state_district']
                                                suburb = address['county']
                                            except:
                                                state_district = address['county']
                                                suburb = None
    state_districts.append(state_district)
    suburbs.append(suburb)

data['state_district'] = state_district
data['suburb'] = suburbs
data = data[['zid', 'state', 'state_district', 'suburb']]

data2 = full_data.merge(data, on='zid', how='left')
data3 = data2[data2['state'] == 'Москва'].groupby(['date', 'state_district', 'suburb']).sum()

BINS = [1, 5, 10, 15, 20, 30, 40, 50, 60, 100]
for i in BINS:
    data3



data.groupby(['state', 'state_district', 'suburb']).size()
