# vm-ublox-map
Map of bikes being tracked using Ublox data

## plotter.py
This is used to generate the CSV files that are turned into geoJSON datasets for Mapbox.

It is responsible for:
* Removing all duplicate frame number coordinates except most recent coordinate
* Calculating the UTC offset
* Removing empty frame numbers
* Removing entries older than 72 hours
* POSTing to API to determine stolen bike state

The input CSV data is just a copy/paste from the /admin/uBlox page in backoffice. Headers are the following:

```GMT time,IMEI,MAC address,Frame number,latitude,longitude,uncertainty,maps url```

## plotter.html & stolenplotter.html
These are the actual HTML pages to view the map.

* [stolenplotter.html](https://jgan96.github.io/vm-ublox-map/stolenplotter.html) shows only bikes that are marked as stolen
* [plotter.html](https://jgan96.github.io/vm-ublox-map/plotter.html) shows all bikes 
