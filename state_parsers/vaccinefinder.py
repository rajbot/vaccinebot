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


def run():
    raw_feed_data = (
        os.getenv("RAW_FEED_DATA")
        or os.path.expanduser("~/dev/raw-feed-data"))
    if not os.path.exists(raw_feed_data):
        raise FileNotFoundError(raw_feed_data)
    path = os.path.join(raw_feed_data, "vaccine-finder/providers/*.json")

    locations = []
    for provider_path in glob.iglob(path):
        fh = open(provider_path)
        try:
            provider = json.load(fh)
        except json.decoder.JSONDecodeError:
            logging.error("Could not parse " + provider_path)
            continue
        fh.close()

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

        county = None
        region = zipcodes.matching(zip_code)
        if len(region) > 0:
            county = region[0].get("county")

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
