wsdot-traffic-gp
================

The scripts in this repository can be used to consume [WSDOT Traveler Information API](http://wsdot.wa.gov/Traffic/api/) REST endpoints in [ArcGIS](http://resources.arcgis.com/) software.

## Setup ##
Before using `travelerinfogp.py` you must run the `createtemplates.py` script.  This will create the `Data\Templates.gdb` file geodatabase.

## Scripts ##
See the scripts' [docstrings](https://en.wikipedia.org/wiki/Docstring#Python) for more details on how to use the scripts.

### `travelerinfo.py` ###
`travelerinfo.py` can be used as a script or module.  As a script it will simply query one of the Traveler Info API REST endpoints and print the JSON results.
It can also be imported as a module, providing the ability to query the REST endpoints and return the results as a dictionary.

* Note that this script has no ArcGIS dependencies and can be run without any ArcGIS software installed.

### `travelerinfogp.py` ###
This is a geoprocessing script that can consume the REST endpoints and return the results as a table.  Can be used as a stand-alone script or imported as a module.

## License ##
Licensed under the [MIT License](http://www.opensource.org/licenses/MIT)