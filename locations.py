from airtable import Airtable
import editdistance
import os
import re

max_distance = 10
max_address_difference = 50

api_key = os.environ.get("AIRTABLE_API_KEY")
base_id = os.environ.get("AIRTABLE_BASE_ID")


def print_fuzzy_matches(location, table):
    print("New location found:")
    print(f"\t{location.name}")
    print(f"\t{location.address}")
    print("-" * 80)

    matches = []
    for db_loc in table:
        address = location.address.lower()
        db_address = db_loc.get("Address", "").lower()
        if db_address == "":
            continue
        if editdistance.eval(address, db_address) < max_distance:
            num1 = address.split()[0]
            num2 = db_address.split()[0]
            num1 = int(re.sub("[^0-9]", "", num1))
            try:
                num2 = int(re.sub("[^0-9]", "", num2))
            except ValueError:
                continue
            if abs(num1 - num2) < max_address_difference:
                matches.append(db_loc)

    if len(matches) > 0:
        print("Possible matches for new location:")
        for i, m in enumerate(matches):
            print(f"{i+1:<5} {m['Name']}")
            print(f"      {m['Address']}")
            print()
    else:
        print("No existing locations found for this location")


def airtable_insert(location):
    airtable = Airtable(base_id, "Locations", api_key)
    url = location.url
    if location.reservation_url is not None:
        url = location.reservation_url

    airtable.insert(
        {
            "Name": location.name,
            "Address": location.address,
            "Website": location.url,
            "Phone number": location.phone,
            "Hours": location.hours,
            "County": f"{location.county} County",
        }
    )
