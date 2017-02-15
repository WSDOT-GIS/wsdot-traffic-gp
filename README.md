wsdot-traffic-gp
================

The scripts in this repository can be used to consume [WSDOT Traveler Information API] REST endpoints in [ArcGIS]  software.

[![Build Status](https://travis-ci.org/WSDOT-GIS/wsdot-traffic-gp.svg?branch=master)](https://travis-ci.org/WSDOT-GIS/wsdot-traffic-gp)

Setup
-----
Before using `travelerinfogp.py` you should run the `createtemplates.py` script.  This will create the `Data\Templates.gdb` file geodatabase.

### Default access code ###
You can set a default access code, so you don't need to provide it via function parameter, by setting an environment variable called `WSDOT_TRAFFIC_API_CODE` to the default access code.

Scripts
-------
See the scripts' [docstrings] for more details on how to use the scripts.

### `travelerinfo.py` ###
`travelerinfo.py` can be used as a script or module.  As a script it will simply query one of the Traveler Info API REST endpoints and print the JSON results.
It can also be imported as a module, providing the ability to query the REST endpoints and return the results as a dictionary.

* Note that this script has no ArcGIS dependencies and can be run without any ArcGIS software installed.

### `travelerinfogp.py` ###
This is a geoprocessing script that can consume the REST endpoints and return the results as a table.  Can be used as a stand-alone script or imported as a module.

[ArcGIS]:http://resources.arcgis.com/
[docstrings]:https://en.wikipedia.org/wiki/Docstring#Python
[WSDOT Traveler Information API]:http://www.wsdot.wa.gov/Traffic/api/