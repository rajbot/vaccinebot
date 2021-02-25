# Parse vaccination site locations for an arcgis dump from CA on Jan 29

# Run manually: python3 -m state_parsers.california_jan29

import csv
import os
import json
import re
import time
import urllib3

from . import Parser, Location
from . import header_dict, debug_print
from . import add_state, validate

parser = Parser(name="California_Jan29", url=None)


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
    url_fmt = "https://services.arcgis.com/BLN4oKB0N1YSgvY8/arcgis/rest/services/CDPH_ApprovedVaccinationLocations_Final_20210129/FeatureServer/0/query?f=json&where=1%3D1&outFields=*&resultOffset={}&resultRecordCount=50"

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
            zip = str(a["USER_Zip"] or "99999")
            zip = zip_fixup(zip)
            if (
                a["USER_Street"] == None
                and a["USER_City"] == None
                and a["USER_State"] == None
            ):
                continue

            address = f"{a['USER_Street'].strip()}, {a['USER_City'].strip()}, {a['USER_State'].strip()} {zip}"
            address = address_fixup(address)

            if address in seen_addresses:
                continue

            seen_addresses.add(address)

            l = Location(
                name=a["USER_Location_Name"].strip(),
                address=address,
                county=a["USER_County"].strip(),
                zip=zip,
                org_name="",  # a["USER_Organization_Name"].strip(),
            )
            locations.append(l)

    validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
