import unittest
import os
import json
import re
from wsdottraffic.classes import parse, TrafficJSONEncoder

class classtest(unittest.TestCase):

    def test_deserialize(self):

        # Read JSON files and deserialize
        jsondir = os.path.dirname(__file__)
        jsondir = os.path.join(jsondir, "testjson")
        output = {}
        regex = re.compile(r"(\w+)_raw.json")
        for dirpath, dirnames, filenames in os.walk(jsondir):
            del dirnames
            for filename in filenames:
                jsonpath = os.path.join(dirpath, filename)
                key = regex.match(filename).groups()[0]
                with open(jsonpath, "r", encoding="utf_8") as f:
                    val = json.load(f, object_hook=parse)
                    output[key] = val
                self.assertIsNotNone(val)

        # Write the objects to files
        outdir = os.path.join(os.path.dirname(__file__), "testdump")
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        for key, l in output.items():
            self.assertGreater(len(l), 0)
            outfn = os.path.join(outdir, key + ".json")
            with open(outfn, "w", encoding='utf_8') as f:
                # f.write("%s" % l)
                json.dump(l, f, cls=TrafficJSONEncoder)

if __name__ == '__main__':
    unittest.main()
