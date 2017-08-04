"""Creates point versions of multipoint feature classes
"""

import argparse
import arcpy


def multipoint_to_point_fc(fgdb_path):
    """Creates point feature classes corresponding to each multipoint feature class in a file geodatabase.
    """
    # TODO: Loop through feature classes.
    # For each multipoint feature class, create a point feature class.
    # Each point in the multipoint will have a record in the new point feature class with duplicate data.

    if not arcpy.Exists(fgdb_path):
        arcpy.AddError("Not found: %s" % fgdb_path)

    # Store old workspace value so it can be restored
    old_workspace = arcpy.env.workspace
    old_overwrite = arcpy.env.overwriteOutput

    try:
        # Set workspace to FGDB so feature classes can be listed.
        arcpy.env.workspace = fgdb_path
        arcpy.env.overwriteOutput = True

        # List all the point and multipoint feature classes.
        # (This function does not have separate "Multipoint" option.)
        fc_list = arcpy.ListFeatureClasses(feature_type="Point")

        # Create another list with just "Multipoint" feature classes.
        mp_fc_list = []
        for fc in fc_list:
            desc = arcpy.da.Describe(fc)
            if desc["shapeType"] == "Multipoint":
                mp_fc_list.append(fc)

        for fc in mp_fc_list:
            out_name = "%s_singlepart" % fc
            arcpy.management.MultipartToSinglepart(fc, out_name)
    finally:
        # restore old workspace
        arcpy.env.workspace = old_workspace
        arcpy.env.overwriteOutput = old_overwrite




def main():
    """Console entry point
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("file_geodatabase", help="Path to file geodatabase")

    args = parser.parse_args()

    fgdb_path = args.file_geodatabase

    multipoint_to_point_fc(fgdb_path)

if __name__ == '__main__':
    main()
