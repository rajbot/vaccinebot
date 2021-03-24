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
    "f56e92f8-29b5-45f5-a6e7-3477459ddf43", # dupe of a2c5b40d-d610-4313-8c12-7fd23be39f90
    "5df170f8-7c55-494b-a0c6-3b82203a125d", # dupe of 0005060d-087f-4529-ab56-d138e0d74686
    "d9896b38-cf56-4a37-9b94-8723ec420dc5", # dupe of af69fc64-7d4f-4fde-bef2-4a5ae7a285f4
    "971f0373-02a8-43b1-aa11-2e40b29ea8d3", # dupe of 4a3e2ec0-64d3-4fba-902f-0447aea9d148
    "0401f4d1-e8ec-4ff4-81a3-9afd663ac24c", # dupe of d7c23c3d-1c52-4476-808b-4635721a72db
])

# People or non-public locations
skips = set([
    "4d9c9ddb-5b22-4cb7-903c-05f011bb23f1", # Lake County Jail
    "aae96c22-53e4-4c8c-afd6-58e7c969af15", # Person
    "ba3c1342-ff9f-4d39-a89a-0dbd8ea6332d", # Person
    "2640cff4-ebdd-4147-bf31-6e632b5b58bb", # Person
    "06b55882-185f-4ff6-bcb5-684d169c5c5b", # Person
    "3e985d94-3e9e-4f3a-b3af-bc13bb45c0ef", # Person
    "b4b50351-8457-4692-a301-cd1c8c104db7", # Same person as above
    "9a5f7e91-9323-4bdf-92d4-2b165862c87b", # Mask manufacturer
    "256805ae-99c5-42ac-8dd7-7113d90262a3", # Person
    "2074dbd3-47a5-473e-938e-9f3bf16d51ee", # Shopping mall?
    "203a1780-ce20-4d53-a486-bd69cbf75d00", # Person
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


def address_fixup(id, a):

    d = {
        "84bb398b-965a-4fea-a51b-41746c7a64c2": "861 North Vine Street, Hollywood, CA 90038",
        "d0db520-f047-4b23-a002-a515274988a8": "2101 W. Imperial Highway #c, La Habra, CA 90631",
        "9d3474f8-fbcc-4163-b442-45123673f07e": "9725 Laurel Canyon Blvd, Arleta CA, 91331",
        "720a49a3-1c20-480a-ba23-d8121daf0ea1": "345 Town Center West Santa Maria, CA 93458",
    }

    return d.get(id, a)


def run():
    raw_feed_data = (
        os.getenv("RAW_FEED_DATA")
        or os.path.expanduser("~/dev/raw-feed-data/vaccine-finder"))
    if not os.path.exists(raw_feed_data):
        raise FileNotFoundError(raw_feed_data)
    path = os.path.join(raw_feed_data, "CA/providers/*.json")

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

        if provider["guid"] in skips:
            continue

        guid = provider["guid"]
        name = provider.get("name")
        name = name_fixup(guid, name)
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
        address = address_fixup(guid, address)

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
