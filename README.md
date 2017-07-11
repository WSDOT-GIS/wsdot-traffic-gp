wsdot-traffic-gp
================

The scripts in this repository can be used to consume [WSDOT Traveler Information API] REST endpoints in [ArcGIS]  software.

[![Build Status](https://travis-ci.org/WSDOT-GIS/wsdot-traffic-gp.svg?branch=master)](https://travis-ci.org/WSDOT-GIS/wsdot-traffic-gp)

Setup
-----

### Default access code ###
You can set a default access code, so you don't need to provide it via function parameter, by setting an environment variable called `WSDOT_TRAFFIC_API_CODE` to the default access code.

Modules
-------
See the modules' [docstrings] for more details on how to use the scripts.

### wsdottraffic ###
This module provides the ability to query the REST endpoints and return the results as a dictionary.

* Note that this script has no ArcGIS dependencies and can be run without any ArcGIS software installed.
* Should run in either v2.7+ or v3.5.2+ of Python.

#### wsdottraffic.gp ####
Consume the REST endpoints and return the results as a file geodatabase.

* Requires ArcPy
* Should work with either ArcGIS Desktop or ArcGIS Pro, and the versions of Python that they come with.

#### wsdottraffic.armcalc  ####
Consumes the ArmCalc web service.

* Should run in either v2.7+ or v3.5.2+ of Python.
* No ArcGIS required.


Scripts
-------

### Notes for developers ###

The example below shows how to run one of the scripts from within the project directory

```console
python -m src.wsdot.traffic.gp.creategdb
```

### creategdb.py ###

* Downloads data from API
* Creates feature class and tables if not already existing
* If tables exist, truncates them
* Inserts the data into feature classes and tables inside of a file geodatabase.
* Zips the file geodatabase (which is a folder w/ `.gdb` extension).

### createtemplates.py ###

Creates a file geodatabase of template feature classes and tables. This script isn't really usually necessary, as the `creategdb.py` script will only create the tables if they don't already exist.

### dumpjson.py ###

Downloads data from API and exports JSON files: one with the data and one with automatically detected field definitions.

### Unit tests (`test_*.py`) ###

These are test scripts for use with the [unittest] Python module.

### PowerShell scripts for developers ###

The PowerShell scripts are intended for use by developers working on this project and are not used by consumers of the library. Use the [Get-Help] command for more info on these scripts.

[ArcGIS]:http://resources.arcgis.com/
[docstrings]:https://en.wikipedia.org/wiki/Docstring#Python
[Get-Help]:https://msdn.microsoft.com/en-us/powershell/reference/5.1/microsoft.powershell.core/get-help
[unittest]:https://docs.python.org/3/library/unittest.html
[WSDOT Traveler Information API]:http://www.wsdot.wa.gov/Traffic/api/