from airtable import Airtable
import editdistance
import geocoder
import os
import re

max_distance = 10
max_address_difference = 50

api_key = os.environ.get("AIRTABLE_API_KEY")
base_id = os.environ.get("AIRTABLE_BASE_ID")


# validate_env_vars()
#_________________________________________________________________________________________
def validate_env_vars():
    for var in ["AIRTABLE_API_KEY", "AIRTABLE_BASE_ID", "MAPQUEST_API_KEY"]:
        if os.environ.get(var) is None:
            sys.exit(f"Must set {var} env var!")


# get_lat_long()
#_________________________________________________________________________________________
def get_lat_long(a):
    g = geocoder.mapquest(a)
    return g.json['lat'], g.json['lng']


# canonicalize()
#_________________________________________________________________________________________
def canonicalize(a):
    """
    >>> canonicalize("460 W San Ysidro Blvd, San Ysidro, CA 92173, United States")
    '460 west san ysidro blvd, san ysidro, ca 92173'

    >>> canonicalize("555 E. Valley Pkwy, Escondido, CA 92025")
    '555 east valley parkway, escondido, ca 92025'
    """

    a = a.lower()
    if a.endswith(", united states"):
        a = a[:-len(", united states")]

    a = re.sub(r" e\.? ", " east ", a)
    a = re.sub(r" w\.? ", " west ", a)
    a = re.sub(r" n\.? ", " north ", a)
    a = re.sub(r" s\.? ", " south ", a)

    a = re.sub(r" pkwy(\W)", r" parkway\1", a)

    return a


# in_db()
#_________________________________________________________________________________________
def in_db(location, db):
    """Return True if location is already in airtable"""

    for db_loc in db["content"]:
        # match on address field,
        db_address = canonicalize(db_loc.get("Address", ""))
        loc_address = canonicalize(location.address)
        if db_address == loc_address:
            return True

    return False


# print_fuzzy_matches()
#_________________________________________________________________________________________
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


# airtable_insert()
#_________________________________________________________________________________________
def airtable_insert(location, latlong):
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
            "Latitude": latlong[0],
            "Longitude": latlong[1],
        }
    )
