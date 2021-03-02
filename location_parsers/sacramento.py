# Parse vaccination site locations for Sacramento County

# Run manually: python3 -m location_parsers.sacramento

import csv
import os
import json
import re
import time
import urllib3

from . import County, Location
from . import header_dict, debug_print
from . import add_state, validate

county = County(
    name="Sacramento",
    url="https://www.arcgis.com/sharing/rest/content/items/70b3149c1b884173a4232c9a0c9aee10/data?f=json",
)


def address_fixup(a):
    return a


# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)  # set user-agent


    locations = []
    r = http.request("GET", county.url)
    obj = json.loads(r.data.decode("utf-8"))

    vaccination_sites = None
    for layer in obj["operationalLayers"]:
        if layer["title"] == "Community Vaccination Sites":
            vaccination_sites = layer
            break

    if vaccination_sites is None:
        raise Exception("Could not find Vaccination Sites layer")

    site_layer = None
    for layer in vaccination_sites["featureCollection"]["layers"]:
        if layer["layerDefinition"]["name"] == "community vaccine locations":
            site_layer = layer
            break

    if site_layer is None:
        raise Exception("Could not find Vaccination Locations layer")

    for s in site_layer["featureSet"]["features"]:
        site = s["attributes"]
        name = site["Location"]
        #if site["Community_Doses"] == "No":
        #    continue

        address = site["Address"]
        if site.get("Address2"):
            address += f", {site['Address2']}"
        address += f", {site['City']}, {site['State']}, {site['Zip']}"

        l = Location(
            name = name,
            address = address,
            county = county.name
        )

        if l not in locations:
            locations.append(l)

    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
