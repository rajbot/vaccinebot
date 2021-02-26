# Parse vaccination site locations in from the vaccinefinder JSONs

# Run manually: python3 -m state_parsers.vaccinefinder

import glob
import os
import json
import re

from . import Parser, Location
from . import header_dict, debug_print
from . import add_state, validate, trim_zip_code

parser = Parser(name="Vaccine Finder", url=None)

def run():
    path = os.path.expanduser("~/dev/feed-recordings/vaccine-finder/*.json")

    locations = []
    for file in glob.iglob(path):
        fh = open(file)
        obj = json.load(fh)
        fh.close()

        providers = obj.get("providers")
        for provider in providers:
            name = provider.get("name")
            if name is None:
                continue

            address = provider.get("address1")
            if address is None:
                continue

            address = address.strip(" .-")

            address2 = provider.get("address2")
            if address2 is not None:
                address2 = address2.strip(" .-")

            if address2 != "":
                address = f"{address} {address2}"

            city = provider.get("city")
            if city is None:
                continue
            city = city.strip()
            
            zip_code = provider.get("zip")
            if zip_code is None:
                continue

            zip_code = trim_zip_code(zip_code)

            state = provider.get("state")
            if state is None or state != "CA":
                continue

            address = f"{address}, {city}, CA {zip_code}"

            l = Location(
                name=name,
                address=address,
                zip=zip_code,
                phone=provider.get("phone"),
                lat=provider.get("lat"),
                long=provider.get("long"),
            )
            
            if l not in locations:
                locations.append(l)

    # Can't validate at the moment since we don't have counties from our scrapes
    # validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
