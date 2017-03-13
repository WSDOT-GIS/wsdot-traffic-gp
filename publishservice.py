"""Publishes an ArcGIS Pro project's map to ArcGIS Online.
"""

import re
from os.path import abspath, exists
from arcpy import AddMessage, AddError
from arcpy.mp import ArcGISProject, CreateWebLayerSDDraft


def main(project_path='traffic-map.aprx',
         service_name="Traveler_Info",
         folder_name="Traveler_Info"):
    """Publishes a project map to a service
    """
    project_path = abspath(project_path)
    if not exists(project_path):
        raise FileNotFoundError("File not found: %s" % project_path)
    # Open the project
    AddMessage("Opening %s" % project_path)
    aprx = ArcGISProject(project_path)
    # Get the first map
    the_map = aprx.listMaps()[0]

    # Create the output path string by replacing the file extension.
    draft_path = re.sub(r"\.aprx$", ".sddraft", project_path)
    AddMessage("Creating %s from %s..." % (project_path, draft_path))
    # Create the web layer SDDraft file.
    try:
        # TODO: Fails here with a RuntimeError that has no message.
        CreateWebLayerSDDraft(
            the_map, draft_path, service_name, folder_name=folder_name,
            copy_data_to_server=True, summary="Test service",
            tags="test,traffic,traveler", description="Test Service",
            use_limitations="For testing only")
    except RuntimeError as ex:
        if len(ex.args) > 0:
            AddError("Error creating %s. %s" % (draft_path, ex.args))
        else:
            AddError(
                "Error creating %s. No further info provided." % draft_path)

if __name__ == '__main__':
    main()
