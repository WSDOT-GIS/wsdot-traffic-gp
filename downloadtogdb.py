import arcpy
import os
import travelerinfogp

out_path = "TravelerInfo.gdb"
arcpy.env.overwriteOutput = True
arcpy.management.CreateFileGDB('.', out_name=out_path)
for name in travelerinfogp.urls.viewkeys():
    data = travelerinfogp.travelerinfo.getTravelerInfo(name)
    travelerinfogp.createTable("%s/%s" % (out_path, name), None, data, "Data/Templates.gdb")