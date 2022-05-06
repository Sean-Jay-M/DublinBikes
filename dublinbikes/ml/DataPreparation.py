import re

import pandas as pd

regOne = re.compile('.*-.*-.*01:00:00')
regTwo = re.compile('.*-.*-.*02:00:00')
regThree = re.compile('.*-.*-.*03:00:00')
regFour = re.compile('.*-.*-.*04:00:00')
        
def clean_bike_data(bike_df):
    print("Sort bike data by Station, Hour")
    grouped_stations = bike_df.sort_values(['number', 'last_update'])
    print("Remove duplicates of bike data")
    bike_df = grouped_stations.drop_duplicates()
    print("---After dropping duplicates---")
    print("Bike data shape:", bike_df.shape)
    print("Bike data head:\n", bike_df.head())
    # numberTwo = dropped[dropped['number'] == 2]
    print("Get the unique station ids")
    stations = bike_df['number'].unique()
    print("Number of stations:", len(stations))

    station_df_list = []
    for station_id in stations:
        print("Current station id:", station_id)
        station_df = bike_df[bike_df['number'] == station_id]
        print("Bike data shape for station", station_id, ":", station_df.shape)
        print(station_df.head(2))
        print("Round to current hour: make regular expression, group by the hour and get the mean")
        station_df['last_update'] = station_df['last_update'].astype('str')
        station_df['last_update'] = station_df['last_update'].str[:-6]
        station_df['last_update'] = station_df['last_update'] + ':00:00'
        print("remove hours 1 - 4: the hours that dublinbikes are not in operation")
        
        filter = station_df['last_update'].str.contains(regOne)
        station_df = station_df[~filter]
        filter = station_df['last_update'].str.contains(regTwo)
        station_df = station_df[~filter]
        filter = station_df['last_update'].str.contains(regThree)
        station_df = station_df[~filter]
        filter = station_df['last_update'].str.contains(regFour)
        station_df = station_df[~filter]
        print(station_df.head(2))
        station_df = station_df.groupby(['last_update'], as_index=False).mean()
        print(station_df.head(2))
        station_df_list.append(station_df)
    print("station_df_list size:", len(station_df_list))
    return station_df_list


def clean_weather_data(weather_df):
    print("Remove Weather Hours 1 - 4")
    weather_df['date_time'] = weather_df['date_time'].astype('str')
    filter = weather_df['date_time'].str.contains(regOne)
    weather_df = weather_df[~filter]
    filter = weather_df['date_time'].str.contains(regTwo)
    weather_df = weather_df[~filter]
    filter = weather_df['date_time'].str.contains(regThree)
    weather_df = weather_df[~filter]
    filter = weather_df['date_time'].str.contains(regFour)
    weather_df = weather_df[~filter]
    print("weather_df.shape:", weather_df.shape)
    print(weather_df.head(2))
    print(weather_df.tail(2))
    return weather_df


def join_bike_weather_data(station_df_list, weather_df):
    combined_df_list = []
    weather_df_reset = weather_df.reset_index()
    print("Filter bike data by weather data and then join them")
    for station_df in station_df_list:
        station_df = station_df[station_df.last_update.isin(weather_df.date_time)]
        station_df.reset_index()
        combined_df = station_df.set_index('last_update').join(weather_df_reset.set_index('date_time'), how='inner')
        combined_df = combined_df.reset_index()
        combined_df.rename(columns={'level_0':'last_update'}, inplace=True)
        # combined_df = pd.concat([station_df, weather_df_reset], axis=1)
        print("Shape of station data after joining:", combined_df.shape)
        print(combined_df.head(2))
        print(combined_df.tail(2))
        # print("combined_df")
        # print(combined_df.head(2))
        combined_df_list.append(combined_df)
    return combined_df_list


def derive_feature(combined_df_list):
    derived_df_list = []
    print("Make new columns")
    for station_df in combined_df_list:
        station_df['last_update'] = pd.to_datetime(station_df['last_update'])
        print("station_df.head(5), id=", station_df['number'][0])
        print(station_df.head(5))
        print("station_df.tail(5), id=", station_df['number'][0])
        print(station_df.tail(5))
        station_df['hour'] = pd.to_datetime(station_df['last_update'], format='%H:%M:%S').dt.hour
        station_df['day'] = pd.to_datetime(station_df['last_update'], format='%H:%M:%S').dt.dayofweek
        station_df['day_time'] = station_df['day'].astype(str) + station_df['hour'].astype(str)
        print("station_df.head(5), id=", station_df['number'][0])
        print(station_df.head(5))
        print("station_df.tail(5), id=", station_df['number'][0])
        print(station_df.tail(5))
        derived_df_list.append(station_df)
    derived_df_list[0].info()
    return derived_df_list


