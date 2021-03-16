# Parse Vaccine Spotter site locations

# Run manually: python3 -m state_parsers.vaccinespotter

import glob
import logging
import os
import json
import re
import urllib3

from . import Parser, Location
from . import header_dict, debug_print
from . import add_state, validate, trim_zip_code

parser = Parser(name="Vaccine Spotter", url='https://www.vaccinespotter.org/api/v0/states/CA.json')


# Returns a list of Locations
def run():
    http = urllib3.PoolManager(headers=header_dict)  # set user-agent
    r = http.request("GET", parser.url)
    obj = json.loads(r.data.decode("utf-8"))

    locations = []
    for feature in obj["features"]:
        props = feature["properties"]
        if props["address"] is None:
            continue

        id = props["id"]
        store_id = props["provider_location_id"]

        street = props["address"]
        city = props["city"]
        state = props["state"]
        zipcode = props["postal_code"]
        address = f"{street}, {city}, {state} {zipcode}"

        long, lat = feature["geometry"]["coordinates"]

        brand = props["provider_brand"]
        if brand == "safeway":
            name = props["name"]
            m = re.search(r'Safeway (\d+)', props["name"], re.I)
            provider_id = f"safeway:{int(m.group(1))}"
        elif brand == "vons":
            name = props["name"]
            m = re.search(r'Vons (\d+)', props["name"], re.I)
            provider_id = f"vons:{int(m.group(1))}"
        elif brand == "rite_aid":
            name = f"{props['name']} #{store_id}"
            provider_id = f"riteaid:{props['provider_location_id']}"
        elif props["provider"] == "walgreens":
            name = f"{props['name']} #{store_id}"
            provider_id = f"walgreens:{props['provider_location_id']}"
        elif brand == "sams_club":
            name = f"{props['name']} #{store_id}"
            provider_id = f"sams:{props['provider_location_id']}"
        elif brand == "albertsons":
            name = props["name"]
            m = re.search(r'Albertsons (\d+)', props["name"], re.I)
            provider_id = f"albertsons:{int(m.group(1))}"
        elif brand == "pavilions":
            name = props["name"]
            m = re.search(r'Pavilions (\d+)', props["name"], re.I)
            provider_id = f"pavilions:{int(m.group(1))}"
        elif brand == "walmart":
            name = f"{props['name']} #{store_id}"
            provider_id = f"walmart:{props['provider_location_id']}"
        else:
            name = f"{props['name']} #{store_id}"
            provider_id = None

        l = Location(
            id = id,
            name = name,
            address = address,
            zip = zipcode,
            url = props["url"],
            lat = lat,
            long = long,
            provider_id = provider_id
        )
        locations.append(l)

    #validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
