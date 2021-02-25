# Parse vaccination site locations in curative feed

# Run manually: python3 -m state_parsers.curative

import glob
import os
import json
import re

from . import Parser, Location
from . import header_dict, debug_print
from . import add_state, validate

parser = Parser(name="Curative", url=None)

def run():
    path = os.path.expanduser("~/dev/feed-recordings/curative/*.json")

    locations = []
    for file in glob.iglob(path):
        fh = open(file)
        obj = json.load(fh)
        fh.close()

        if "error_code" in obj:
            continue

        facility = obj.get("facility")
        if facility is None:
            continue

        vaccines_enabled = obj["facility"]["vaccines_enabled"]
        if vaccines_enabled is True:
            if obj['state'] != "CA":
                continue
            address = obj["street_address_1"].strip()
            if obj["street_address_2"] is not None and obj["street_address_2"].strip() != "":
                address += f", {obj['street_address_2'].strip()}"
            address += f", {obj['city']}, {obj['state']} {obj['postal_code']}"

            l = Location(
                name=obj["name"],
                address=address,
                zip=obj['postal_code'],
                county=obj.get("county"),
                org_name="",
            )
            locations.append(l)

    #validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
