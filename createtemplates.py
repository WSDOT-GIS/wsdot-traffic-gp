'''
Creates the templates file geodatabase.
Created on May 31, 2012

@author: Jeff Jacobson
'''
import sys, os, travelerinfogp, arcpy
from os import path

if __name__ == '__main__':
    # Get the .. directory
    dataDir = path.abspath("Data")

    # Create the data dir if it does not exist already.
    if not path.exists(dataDir):
        arcpy.AddMessage("Creating directory, %s..." % dataDir)
        os.mkdir(dataDir)
    else:
        arcpy.AddMessage("%s already exists.  Skipping creation step." % dataDir)

    # Create the Templates GDB
    arcpy.env.overwriteOutput = True
    gdbName = "Templates.gdb"
    gdbPath = path.join(dataDir, gdbName)
    arcpy.AddMessage("Creating %s..." % gdbPath)
    arcpy.management.CreateFileGDB(dataDir, gdbName)
    for key in travelerinfogp.fieldsDict:
        arcpy.AddMessage("Creating %s in %s..." % (key, gdbPath))
        travelerinfogp.createTable(path.join(gdbPath, key))
    arcpy.AddMessage("Completed")