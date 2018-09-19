wsdot-traffic-gp
================

This package is used for consuming the [WSDOT Traveler Information API] REST endpoints.

[![Build Status](https://travis-ci.org/WSDOT-GIS/wsdot-traffic-gp.svg?branch=master)](https://travis-ci.org/WSDOT-GIS/wsdot-traffic-gp)

Setup
-----

### Install package ###

To install this package onto your computer using pip, use the following command. For more information on installing packages, see the [Installing Packages] tutorial from the *PyPA Python Packaging User Guide*.

#### All users (requires admin access)

```console
pip install wsdottraffic
```
#### For current user only

```console
pip install wsdottraffic --user
```

If you are running this command from PowerShell, you will need to have administrator privileges.

```PowerShell
Start-Process pip "install wsdottraffic" -Verb RunAs
```

### Default access code ###

You can set a default access code, so you don't need to provide it via function parameter or script argument, by setting an environment variable called `WSDOT_TRAFFIC_API_CODE` to the default access code.

Modules
-------
See the modules' [docstrings] for more details on how to use the scripts.

### wsdottraffic ###

This module provides the ability to query the REST endpoints and return the results as a dictionary.

Scripts
-------

You can get help for any of the scripts using the `-h` argument.

```console
python -m wsdottraffic -h
```

### wsdottraffic.dumpjson / wsdottraffic ###

Downloads data from API and exports JSON files: one with the data and one with automatically detected field definitions.

```console
python -m wsdottraffic
```

or

```console
wsdottraffic
```

Notes for developers
--------------------

### Unit tests (`wsdottraffic.tests`) ###

Unit tests are defined in the `wsdottraffic/tests` folder.

These are test scripts for use with the [unittest] Python module.

[ArcGIS]:http://resources.arcgis.com/
[docstrings]:https://en.wikipedia.org/wiki/Docstring#Python
[Installing Packages]:https://packaging.python.org/tutorials/installing-packages/
[unittest]:https://docs.python.org/3/library/unittest.html
[WSDOT Traveler Information API]:http://www.wsdot.wa.gov/Traffic/api/