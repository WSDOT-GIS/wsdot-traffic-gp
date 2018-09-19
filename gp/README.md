Geoprocessing Scripts
=====================

This folder contains the removed geoprocessing tools which require arcpy.


### wsdottraffic.gp ###
Consume the REST endpoints and return the results as a file geodatabase.

* Requires ArcPy
* Should work with either ArcGIS Desktop or ArcGIS Pro, and the versions of Python that they come with.


Scripts
-------

### wsdottraffic.gp / wsdottrafficgp ###

* Downloads data from API
* Creates feature class and tables if not already existing
* If tables exist, truncates them
* Inserts the data into feature classes and tables inside of a file geodatabase.
* Zips the file geodatabase (which is a folder w/ `.gdb` extension).

```console
python -m wsdottraffic.gp.creategdb
```

or

```console
wsdottrafficgp
```

### wsdottraffic.gp.multipointtopoint / multipointtopoint ###

Calls the [Multipart to Singlepart] tool for each multipoint feature class in a geodatabase. Added feature classes will have the same name as its source, but with the added suffix *_singlepart*.

```console
python -m wsdottraffic.gp.multipointtopoint YourGDBNameHere.gdb
```

or

```console
multipointtosinglepoint YourGDBNameHere.gdb
```
