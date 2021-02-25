# Parse vaccination site locations in CA ArcGIS feed

# Run manually: python3 -m state_parsers.california

import csv
import os
import json
import re
import time
import urllib3

from . import Parser, Location
from . import header_dict, debug_print
from . import add_state, validate

parser = Parser(name="California", url=None)


def address_fixup(a):
    """ Some San Diego addresses aren't fixed up by the canonicalizer. """
    a = re.sub(r"(\d{5})-\d{4}", r"\1", a)
    return a


def zip_fixup(z):
    z = re.sub(r"(\d{5})-\d{4}", r"\1", z)
    return z


# Returns a list of json objects
def run():
    http = urllib3.PoolManager(headers=header_dict)  # set user-agent

    url_fmt = "https://services.arcgis.com/BLN4oKB0N1YSgvY8/arcgis/rest/services/CDPH_Vaccination_Locations_20210210/FeatureServer/0/query?f=json&where=1%3D1&outFields=*&resultOffset={}&resultRecordCount=50"

    counts_url = url_fmt.format(0) + "&returnCountOnly=true"
    r = http.request("GET", counts_url)
    obj = json.loads(r.data.decode("utf-8"))
    num_features = obj["count"]

    locations = []
    seen_addresses = set()

    # for i in range(0, 50, 50):
    for i in range(0, num_features, 50):
        url = url_fmt.format(i)
        r = http.request("GET", url)
        obj = json.loads(r.data.decode("utf-8"))

        for feature in obj["features"]:
            a = feature["attributes"]
            address = f"{a['Street'].strip()}, {a['City'].strip()}, {a['State'].strip()} {a['Zip'].strip()}"
            address = address_fixup(address)
            zip = zip_fixup(a["Zip"].strip())

            if address in seen_addresses:
                continue

            seen_addresses.add(address)

            l = Location(
                name=a["Location_Name"].strip(),
                address=address,
                county=a["County"].strip(),
                zip=zip,
                org_name=a["Organization_Name"].strip(),
            )
            locations.append(l)

    validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
