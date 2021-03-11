# Parse vaccination site locations in from the vaccinefinder JSONs

# Run manually: python3 -m state_parsers.vaccinefinder

import glob
import logging
import os
import json
import re
import zipcodes

from . import Parser, Location
from . import header_dict, debug_print
from . import add_state, validate, trim_zip_code

parser = Parser(name="Vaccine Finder", url=None)

days = {
    "mon": "Monday",
    "tue": "Tuesday",
    "wed": "Wednesday",
    "thur": "Thursday",
    "fri": "Friday",
    "sat": "Saturday",
    "sun": "Sunday",
}

# Prefer the records that are newer or that have more information
duplicates = set([
    "b6013918-8aa7-4835-b4b7-6873fdd4b784", # dupe of 8fa1a834-6659-4117-955e-3b36578ef74e
    "0cb131ed-3bf6-43f0-b077-cbab62111563", # dupe of 1a9a70a7-c99c-43a7-aa43-f9a148eea1c7
    "d1eb38a0-6a93-4520-a396-d223e748a08a", # dupe of c1da01e5-bb53-4942-998c-d10596ae5db7
    "c8ba0064-cfac-412b-a9fc-0f469f48a088", # dupe of 0dcd7db3-808a-4f8f-a61b-df5e30108e16
    "496322cd-11fd-44f4-921b-1dbeeb26dc61", # dupe of 805e8b71-078b-4713-a6c3-102ba12c7801
    "b2136855-80c3-451f-ae03-13e83f4139ab", # dupe of 1c33f721-95c7-4f6e-a713-0acefb77091e
    "7fdcc142-2baf-4e89-bb46-c7e4c4328daf", # dupe of 9e353e7c-6a6e-4694-a3a8-8330867fb742
    "02db7295-2663-4bfb-9cb2-d614b57a4d8b", # dupe of 4ce3999b-241f-4629-bd22-9e726c1614e9
    "f46b5dd7-b01e-45f8-8f58-9ba17e0548c6", # dupe of f99bef37-1c96-4673-8f3a-0600c0fa3c41
    "33017e63-e043-467c-826d-8f4f0a71025f", # dupe of bbcbfe7f-ff4d-4454-8069-9277968e4a28
    "96eecc07-eccb-4ad7-a6b9-75bae861c718", # dupe of f9ba55d9-7827-4895-86fb-651960dee1f8
    "12a2119a-30c3-4b8f-a911-cff6ffdea9fe", # dupe of 851662aa-e044-4896-9088-2e7cf3c559e4
    "f7984f64-e9cf-4f97-ae75-7d1eb6606127", # dupe of c5ef8950-68a0-4d39-8618-f9da29c397d5
    "4a84545b-f789-44a2-b307-0b1189bf34e3", # dupe of d89bd933-86d4-46ed-99d2-aae126485951
    "47ba8bbe-a5a1-4e6a-a980-5023c580e4e8", # dupe of eab4b8d4-c345-49be-b68d-fef9b0f85308
    "58670db0-ca74-419a-8785-85d34c63c078", # dupe of 2fdc930e-c63c-42b0-86db-d495830375b2
    "836906a2-011e-4e2b-a734-eeb2a22c1e14", # dupe of 1f75e5f4-5e67-4237-928f-484fd4961e7c
])


# Hours comes in a format like:
#   "hours_mon" : "09:00AM-08:00PM",
#   "hours_tue" : ...,
# We'll just format it as "Monday: 09:00AM-08:00PM\nTuesday ..."
def format_hours(provider):
    hours = ""

    for short_date, date in days.items():
        key = f"hours_{short_date}"

        if provider.get(key) is not None:
            hours += f"{date}: {provider.get(key)}\n"

    return hours.strip()


def name_fixup(id, name):
    if id == "069a9923-5e49-48be-9200-f6f08d367f9e":
        return "Bartz Altadonna CHC - E Palmdale Blvd"
    return name


def run():
    raw_feed_data = (
        os.getenv("RAW_FEED_DATA")
        or os.path.expanduser("~/dev/raw-feed-data"))
    if not os.path.exists(raw_feed_data):
        raise FileNotFoundError(raw_feed_data)
    path = os.path.join(raw_feed_data, "vaccine-finder/CA/providers/*.json")

    locations = []
    for provider_path in glob.iglob(path):
        fh = open(provider_path)
        try:
            provider = json.load(fh)
        except json.decoder.JSONDecodeError:
            logging.error("Could not parse " + provider_path)
            continue
        fh.close()

        if provider["guid"] in duplicates:
            continue

        name = provider.get("name")
        name = name_fixup(provider["guid"], name)
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

        county = None
        region = zipcodes.matching(zip_code)
        if len(region) > 0:
            county = region[0].get("county")
            county = county[:-len(" County")]

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
            county=county,
            # Fields from the higher fidelity data
            url=provider.get("website"),
            reservation_url=provider.get("prescreening_site"),
            hours=format_hours(provider),
            id = provider["guid"]
        )

        if l not in locations:
            locations.append(l)

    # Can't validate at the moment since we don't have counties from our scrapes
    # validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
