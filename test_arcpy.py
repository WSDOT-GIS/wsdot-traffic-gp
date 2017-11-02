"""Test which require arcpy to be installed.
"""

from os.path import join, exists
import json
import re
import unittest

try:
    import arcpy
except ImportError:
    arcpy = None
else:
    from wsdottraffic.gp import __main__


class TestGeoprocessingFunctions(unittest.TestCase):
    def skip_if_no_arcpy(self):
        if not arcpy:
            self.skipTest("arcpy is not installed.")

    def test_tables(self):
        self.skip_if_no_arcpy()

        # Create the file geodatabase
        gdb_name = arcpy.CreateScratchName("Traffic", ".gdb", "File Geodatabase", ".")
        try:
            __main__.create_gdb(gdb_name, templates_gdb="Templates.gdb")

            # Import the table definition schema from JSON file
            schemas = None
            with open("wsdottraffic/gp/tabledefs.json") as json_file:
                schemas = json.load(json_file)

            def get_field_names_from_schema(table_prop_dict):
                """Generator function that iterates through the expected field names.
                """

                # Setup regex to match names we want to skip.
                # Latitude and Longitude fields were converted
                # into point geometry so are not included in the
                # feature classes.
                fields_to_skip_re = re.compile(
                    r"(?:(?:Latitude)|(?:Longitude))", re.IGNORECASE)

                # Fail if the dictionary doesn't contain "fields" key.
                if not "fields" in table_prop_dict:
                    raise KeyError("Expected 'fields' key in %s" % table_prop_dict)
                for name, data in table_prop_dict["fields"].items():
                    if not isinstance(data, str) and "field_name" in data:
                        out_name = data["field_name"]
                    else:
                        out_name = name
                    if not fields_to_skip_re.search(out_name):
                        yield out_name

            for table_name, schema_table_props in schemas.items():
                table_path = join(gdb_name, table_name)
                self.assertTrue(arcpy.Exists(table_path),
                                "'%s' must exist." % table_path)

                # Get list of field names in the current GIS table.
                fields = list(map(lambda field: field.name,
                                arcpy.ListFields(table_path)))

                for expected_name in get_field_names_from_schema(schema_table_props):
                    self.assertIn(expected_name, fields, "%s should include a field named %s." % (
                        table_name, expected_name))
        finally:
            if arcpy.Exists(gdb_name):
                arcpy.management.Delete(gdb_name)


if __name__ == '__main__':
    unittest.main()
