# vm-ublox-map
Map of bikes being tracked using Ublox data

## plotter.py
This is used to generate the CSV files that are turned into geoJSON datasets for Mapbox.

It is responsible for:
* Removing all duplicate frame number coordinates except most recent coordinate
* Calculating the UTC offset
* Removing bad lines
* POSTing to API to determine stolen bike state

## plotter.html & stolenplotter.html
These are the actual HTML pages to view the map.

* stolenplotter.html shows only bikes that are marked as stolen
* plotter.html shows all bikes 
