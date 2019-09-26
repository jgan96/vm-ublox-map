# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 23:49:37 2019

@author: jgan
"""

#Import the folium package for making maps
import folium
import requests as r
from ratelimiter import RateLimiter
from requests.auth import HTTPBasicAuth
import json
from pandas.io.json import json_normalize
import pandas as pd
from folium.plugins import MarkerCluster
from datetime import datetime
import time
import numpy as np
import config

def getISOFmt(t):
    fmt = '%d-%m-%Y %H:%M'

    # convert string to datetime obj
    dt = datetime.strptime(t, fmt)

    # get iso 8601 format
    isofmt = dt.isoformat(timespec='minutes')

    return isofmt

def getUnixTS(t):
    fmt = '%d-%m-%Y %H:%M'

    # convert string to datetime obj
    dt = datetime.strptime(t, fmt)

    # convert time obj to unix timestamp
    ts = time.mktime(dt.timetuple())

    return ts

def getUTCOffset(t):
    # get time difference in minutes
    offset = int(time.time() - getUnixTS(t)) / 60
    #offset = int(getUnixTS('26-08-2019 10:00') - getUnixTS(t)) / 60 # fake time for testing

    return offset

def queryBike(frameNum):
    bike = pd.DataFrame()

    body = {
        "framenumber": frameNum
    }

    response = r.post('https://backoffice.vanmoof.com/api/isBikeStolen',
                      auth=(config.API_USER, config.API_PASS), data=body)
    # print(response.text)
    if response.status_code == 200:
        data = response.json()

        b = {
            "GMT time": getISOFmt(row['GMT time']),
            "UTC offset": [row['UTC offset']],
            "IMEI": [row['IMEI']],
            "MAC address": [row['MAC address']],
            "Frame number": [row['Frame number']],
            "lat": [row['latitude']],
            "long": [row['longitude']],
            "stolen": data['result']
        }
        bike = pd.DataFrame(b)
    else:
        print(response.status_code)
    # print(data['result'])

    return bike

def createFoliumMap(bikes):
    # create a marker cluster
    mc = MarkerCluster().add_to(mapWorld)

    for index,row in bikes.iterrows():
        lat = row["lat"]
        lon = row["long"]
        name = row["Frame number"]
        newMarker = folium.Marker([lat, lon], popup=name)
        newMarker.add_to(mc)

    #Save the map:
    mapWorld.save(outfile='tempMap.html')

if __name__ == "__main__":
    #Create a map, centered (0,0), and zoomed out a bit:
    mapWorld = folium.Map(location=[0, 0],zoom_start=3)

    #stolenBikes = pd.DataFrame(columns=['GMT time', 'UTC offset', 'IMEI', 'MAC address', 'Frame number', 'lat', 'long'])
    stolenBikes = pd.DataFrame(columns=['GMT time', 'UTC offset', 'IMEI', 'MAC address', 'Frame number', 'lat', 'long', 'stolen']) # where stolen is a bool

    c = input("Enter name of CSV to read: ")
    trackings = pd.read_csv(c)
    #print(trackings)

    # check if frame number is missing
    trackings = trackings.dropna(axis=0, subset=['Frame number'])
    trackings.reset_index(drop=True, inplace=True)
    #print(trackings)

    # add an UTC offset column and calculate offset
    trackings.insert(0, 'UTC offset', np.nan)
    print("Calculating UTC offset...")
    for index,row in trackings.iterrows():
        print("[", end=' ')
        print(index + 1, end=' ')
        print("/", end=' ')
        print(len(trackings.index), end=' ')
        print("]", end=' ')

        trackings.at[index, 'UTC offset'] = getUTCOffset(row['GMT time'])
        print(getUTCOffset(row['GMT time']))

    # sort by UTC offset (most recent first)
    print("Sorting most recent first...")
    trackings = trackings.sort_values(by=['UTC offset'], ascending=True)

    # check for duplicates and only keep most recent duplicate
    print("Removing duplicates...")
    trackings.drop_duplicates(subset='Frame number', keep='first', inplace=True)

    # drop trackings older than 72 hours
    print("Removing entries older than 72 hours...")
    trackings.drop(trackings[trackings['UTC offset'] > 4320].index, inplace=True)

    # reset index
    trackings.reset_index(drop=True, inplace=True)

    # rate limit to 10 calls per 2 seconds
    rate_limiter = RateLimiter(max_calls=10, period=2)

    # check if frame number is stolen via api
    for index,row in trackings.iterrows():
        with rate_limiter:
            print("[", end=' ')
            print(index + 1, end=' ')
            print("/", end=' ')
            print(len(trackings.index), end=' ')
            print("]", end=' ')
            print(row['Frame number'], end=' ')
            print("Stolen:", end=' ')

            bike = queryBike(row['Frame number'])

            print(bike["stolen"])

            stolenBikes = stolenBikes.append(bike)

            stolenBikes.to_csv('stolenBikes.csv')
    # convert to geojson
    # upload to dataset api?

    createFoliumMap(stolenBikes)