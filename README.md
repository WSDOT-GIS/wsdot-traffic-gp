wsdot-traffic-gp
================

The scripts in this repository can be used to consume [WSDOT Traveler Information API] REST endpoints in [ArcGIS]  software.

[![Build Status](https://travis-ci.org/WSDOT-GIS/wsdot-traffic-gp.svg?branch=master)](https://travis-ci.org/WSDOT-GIS/wsdot-traffic-gp)

Setup
-----
Before using `wsdottraffic.gp` you should run the `createtemplates.py` script.  This will create the `Data\Templates.gdb` file geodatabase.

### Default access code ###
You can set a default access code, so you don't need to provide it via function parameter, by setting an environment variable called `WSDOT_TRAFFIC_API_CODE` to the default access code.

Modules
-------
See the modules' [docstrings] for more details on how to use the scripts.

### wsdottraffic ###
This module provides the ability to query the REST endpoints and return the results as a dictionary.

* Note that this script has no ArcGIS dependencies and can be run without any ArcGIS software installed.

#### wsdottraffic.gp ####
Consume the REST endpoints and return the results as a file geodatabase.

#### wsdottraffic.armcalc  ####
Consumes the ArmCalc web service.

[ArcGIS]:http://resources.arcgis.com/
[docstrings]:https://en.wikipedia.org/wiki/Docstring#Python
[WSDOT Traveler Information API]:http://www.wsdot.wa.gov/Traffic/api/