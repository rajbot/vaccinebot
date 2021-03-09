from airtable import Airtable
import editdistance
import geocoder
import logging
import os
import re
import sys
import webhook

max_distance = 10
max_address_difference = 10

api_key = os.environ.get("AIRTABLE_API_KEY")
base_id = os.environ.get("AIRTABLE_BASE_ID")


# validate_env_vars()
# _________________________________________________________________________________________
def validate_env_vars():
    for var in ["AIRTABLE_API_KEY", "AIRTABLE_BASE_ID", "MAPQUEST_API_KEY"]:
        if os.environ.get(var) is None:
            sys.exit(f"Must set {var} env var!")


# get_lat_long()
# _________________________________________________________________________________________
def get_lat_long(a):
    g = geocoder.mapquest(a)
    return g.json["lat"], g.json["lng"]


# normalize()
# _________________________________________________________________________________________
def normalize(a):
    # requres libpostal c library to be installed
    from postal.parser import parse_address

    d = {k: v for (v, k) in parse_address(a)}
    return f"{d.get('house_number')} {d.get('road')}, {d.get('city')}, {d.get('state')} {d.get('postcode')}"


# canonicalize()
# _________________________________________________________________________________________
def canonicalize(a):
    """
    >>> canonicalize("460 W San Ysidro Blvd, San Ysidro, CA 92173, United States")
    '460 west san ysidro boulevard, san ysidro, ca 92173'

    >>> canonicalize("1208 WEST REDONDO BEACH BOULEVARD, GARDENA, CA 90247")
    '1208 west redondo beach boulevard, gardena, ca 90247'

    >>> canonicalize("1208 West Redondo Beach Blvd., Gardena, CA 90247")
    '1208 west redondo beach boulevard, gardena, ca 90247'

    >>> canonicalize("555 E. Valley Pkwy, Escondido, CA 92025")
    '555 east valley parkway, escondido, ca 92025'

    >>> canonicalize("500 OLD RIVER RD STE 125, BAKERSFIELD, CA 93311")
    '500 old river road suite 125, bakersfield, ca 93311'

    >>> canonicalize("2419 EAST AVENUE  SOUTH, PALMDALE, CA 93550")
    '2419 east avenue south, palmdale, ca 93550'

    >>> canonicalize("2419 East Avenue S, Palmdale, CA 93550")
    '2419 east avenue south, palmdale, ca 93550'

    >>> canonicalize("7239 WOODMAN AVENUE, VAN NUYS, CA 91405")
    '7239 woodman avenue, van nuys, ca 91405'

    >>> canonicalize("7239 Woodman Ave, Van Nuys, CA 91405")
    '7239 woodman avenue, van nuys, ca 91405'

    >>> canonicalize("10823 ZELZAH AVENUE BUILDING D, GRANADA HILLS, CA 91344")
    '10823 zelzah avenue building d, granada hills, ca 91344'

    >>> canonicalize("10823 Zelzah Avenue Bldg D, Granada Hills, CA 91344")
    '10823 zelzah avenue building d, granada hills, ca 91344'

    >>> canonicalize("23 PENINSULA CENTER, ROLLING HILLS ESTATES, CA 90274")
    '23 peninsula center, rolling hills estates, ca 90274'

    >>> canonicalize("23 Peninsula Center, Rolling Hills Ests, CA 90274")
    '23 peninsula center, rolling hills estates, ca 90274'

    >>> canonicalize("2352 Arrow Hwy (Gate 15) , Pomona, CA 91768")
    '2352 arrow hwy (gate 15), pomona, ca 91768'

    >>> canonicalize("11798 Foothill Blvd., , Lake View Terrace, CA 91342")
    '11798 foothill boulevard, lake view terrace, ca 91342'

    >>> canonicalize('808 W. 58th St. \\nLos Angeles, CA 90037')
    '808 west 58th street, los angeles, ca 90037'

    >>> canonicalize("45104 10th St W\\nLancaster, CA 93534")
    '45104 10th street west, lancaster, ca 93534'

    >>> canonicalize("133 W Rte 66, Glendora, CA 91740")
    '133 west route 66, glendora, ca 91740'

    >>> canonicalize("3410 W THIRD ST, LOS ANGELES, CA 90020")
    '3410 west 3rd street, los angeles, ca 90020'
    """

    # if a.startswith('45104 '):
    #    import pdb
    #    pdb.set_trace()

    a = a.lower().strip()
    if a.endswith(", united states"):
        a = a[: -len(", united states")]

    a = re.sub(r"([^,])\n+", r"\1, ", a)  # newline instead of comma
    a = re.sub(r",\s+,", ", ", a)  # repeated comma
    a = re.sub(r"\s+, ", ", ", a)  # extra space around comma

    a = re.sub(r" e\.?(\W)? ", r" east\1 ", a, re.I)
    a = re.sub(r" w\.?(\W)? ", r" west\1 ", a)
    a = re.sub(r" n\.?(\W)? ", r" north\1 ", a)
    a = re.sub(r" s\.?(\W)? ", r" south\1 ", a)

    a = re.sub(r" ave\.?(\W)", r" avenue\1", a)
    a = re.sub(r" blvd\.?(\W)", r" boulevard\1", a)
    a = re.sub(r" ctr\.?(\W)", r" center\1", a)
    a = re.sub(r" ests\.?(\W)", r" estates\1", a)
    a = re.sub(r" rd\.?(\W)", r" road\1", a)
    a = re.sub(r" pkwy\.?(\W)", r" parkway\1", a)
    a = re.sub(r" rte\.?(\W)", r" route\1", a)
    a = re.sub(r" ste\.?(\W)", r" suite\1", a)
    a = re.sub(r" st\.?(\W)", r" street\1", a)
    a = re.sub(r" wy\.?(\W)", r" way\1", a)

    a = re.sub(r"([a-z]) dr\.?(\W)", r"\1 drive\2", a)  # "drive" not "doctor"

    a = re.sub(r" bldg\.?(\W)", r" building\1", a)

    # Use numeric version of street names.
    # i.e. "1st" instead of "first"
    a = re.sub(r"(\W)first(\W)", r"\g<1>1st\g<2>", a)
    a = re.sub(r"(\W)second(\W)", r"\g<1>2nd\g<2>", a)
    a = re.sub(r"(\W)third(\W)", r"\g<1>3rd\g<2>", a)
    a = re.sub(r"(\W)fourth(\W)", r"\g<1>4th\g<2>", a)
    a = re.sub(r"(\W)fifth(\W)", r"\g<1>5th\g<2>", a)
    a = re.sub(r"(\W)sixth(\W)", r"\g<1>6th\g<2>", a)
    a = re.sub(r"(\W)seventh(\W)", r"\g<1>7th\g<2>", a)
    a = re.sub(r"(\W)eighth(\W)", r"\g<1>8th\g<2>", a)
    a = re.sub(r"(\W)ninth(\W)", r"\g<1>9th\g<2>", a)
    a = re.sub(r"(\W)tenth(\W)", r"\g<1>10th\g<2>", a)

    a = re.sub(r"\s+", " ", a)
    return a


# address_line1()
# ________________________________________________________________________________________
def address_line1(a):
    """Return only the main part of a multipart address

    Warnings:
    - Only works on canonicalized addresses. Call canonicalize() first.
    - Returns addresses that are incorrect!
    - Only use the output of this function for fuzzy matching.

    >>> address_line1('1910 south magnolia avenue suite 101, los angeles, ca 90007')
    '1910 magnolia, los angeles, ca 90007'

    >>> a = '9201 W. Sunset Blvd., Suite 812\\nWest Hollywood, Ca. 90069'
    >>> address_line1(canonicalize(a))
    '9201 sunset, west hollywood, ca. 90069'

    >>> a = '45104 10th St W Ste A, Lancaster, CA 93534'
    >>> address_line1(canonicalize(a))
    '45104 10th, lancaster, ca 93534'
    """

    a = re.sub(r",? suite [0-9a-z]+,", ",", a)

    s = a.split(", ", 1)
    if len(s) == 2:
        address = s[0]
        address = re.sub(r" east$", r"", address)
        address = re.sub(r"^east ", r"", address)
        address = re.sub(r" east ", r" ", address)

        address = re.sub(r" west$", r"", address)
        address = re.sub(r"^west ", r"", address)
        address = re.sub(r" west ", r" ", address)

        address = re.sub(r" north$", r"", address)
        address = re.sub(r"^north ", r"", address)
        address = re.sub(r" north ", r" ", address)

        address = re.sub(r" south$", r"", address)
        address = re.sub(r"^south ", r"", address)
        address = re.sub(r" south ", r" ", address)

        a = f"{address}, {s[1]}"

    a = a.replace(" avenue,", ",")
    a = a.replace(" boulevard,", ",")
    a = a.replace(" center,", ",")
    a = a.replace(" estates,", ",")
    a = a.replace(" parkway,", ",")
    a = a.replace(" road,", ",")
    a = a.replace(" route,", ",")
    a = a.replace(" suite,", ",")
    a = a.replace(" street,", ",")
    a = a.replace(" way,", ",")

    return a


# address_line1_min()
# ________________________________________________________________________________________
def address_line1_min(a):
    """Return only a minimal version of an address

    >>> address_line1_min('1001 Potrero Ave GR-1, San Francisco, CA 94110')
    '1001 potrero san francisco ca 94110'

    """
    line1 = address_line1(canonicalize(a))
    m = re.match(".*?(\d+\s+\w+?)\s.*?((?:san |santa |los )\w+, ca \d{5})", line1)

    if m is not None:
        line1 = f"{m.group(1)} {m.group(2)}"

    line1 = line1.replace(', ', ' ')
    line1 = line1.replace('. ', ' ')

    return line1


# in_db()
# ________________________________________________________________________________________
def in_db(location, db, address_match, external_id_field):
    """Return True if location is already in airtable"""

    if address_match == "strict":
        loc_address = canonicalize(location.address)
    elif address_match == "close":
        # loc_address = address_line1(canonicalize(location.address))
        loc_address = address_line1_min(canonicalize(location.address))
    else:
        raise Exception("Invalid address_match option")

    for db_loc in db["content"]:
        if external_id_field is not None and location.id is not None:
            if db_loc.get(external_id_field) == location.id:
                return True, db_loc["id"], db_loc

        # match on canonicalized address field
        db_address = db_loc["address_line1"]
        if db_address == loc_address:
            return True, db_loc["id"], db_loc

    return False, None, None


# cannonicalize_db()
# ________________________________________________________________________________________
def cannonicalize_db(db, address_match):
    for db_loc in db["content"]:
        db_address = db_loc.get("Address", "")
        if address_match == "strict":
            a = canonicalize(db_address)
        elif address_match == "close":
            # a = address_line1(canonicalize(db_address))
            a = address_line1_min(canonicalize(db_address))
        else:
            raise Exception("Invalid address_match option")

        db_loc["address_line1"] = a


# get_fuzzy_matches()
# ________________________________________________________________________________________
def get_fuzzy_matches(location, table):
    matches = []
    for db_loc in table:
        address = location.address.lower()
        db_address = db_loc.get("Address", "").lower()
        if db_address == "":
            continue
        if editdistance.eval(address, db_address) < max_distance:
            num1 = address.split()[0]
            num2 = db_address.split()[0]
            try:
                num1 = int(re.sub("[^0-9]", "", num1))
                num2 = int(re.sub("[^0-9]", "", num2))
            except ValueError:
                continue
            if abs(num1 - num2) < max_address_difference:
                matches.append(db_loc)

    return matches


# print_fuzzy_matches()
# ________________________________________________________________________________________
def print_fuzzy_matches(location, table):
    print("New location found:")
    print(f"\t{location.name}")
    print(f"\t{location.address}")
    print(f"\t{location.phone}, {location.id}")
    print("-" * 80)

    matches = get_fuzzy_matches(location, table)

    if len(matches) > 0:
        print("Possible matches for new location:")
        for i, m in enumerate(matches):
            print(f"{i+1:<5} {m['Name']}")
            print(f"      {m['Address']}")
            print()
    else:
        print("No existing locations found for this location")

    return matches


# print_fuzzy_tsv()
# ________________________________________________________________________________________
def print_fuzzy_tsv(location, table, match_id):
    # Extract fields of interest.  Remove tabs and newlines that will make a
    # tsv very unhappy.
    name = location.name.replace("\t", " ").replace("\n", " ")
    address = location.address.replace("\t", " ").replace("\n", ", ")
    org_name = location.org_name or ""
    org_name = org_name.replace("\t", " ").replace("\n", " ")
    zip = location.zip
    county = location.county
    url = location.url
    phone = location.phone
    id = location.id or ""
    if url is None:
        url = ""

    fuzzy_match_ids = ""
    fuzzy_match_addresses = ""
    if match_id is None:
        fuzzy_matches = get_fuzzy_matches(location, table)
        if len(fuzzy_matches) > 0:
            fuzzy_match_ids = ",".join([m["id"] for m in fuzzy_matches])
            fuzzy_match_addresses = "\t".join([f"{m['Name'], m['Address'], m.get('Phone number', '')}" for m in fuzzy_matches])

    cols = [url, org_name, name, address, zip, county, match_id or "", fuzzy_match_ids]
    #cols = [url, id, name, address, zip, phone, match_id or "", fuzzy_match_addresses]

    print("\t".join(cols))


# print_match_tsv()
# ________________________________________________________________________________________
def print_match_tsv(location, match_row, found):
    if not found:
        return
    name = location.name.replace("\t", " ").replace("\n", " ")
    address = location.address.replace("\t", " ").replace("\n", ", ")
    id = location.id

    match_name = match_row["Name"]
    match_address = match_row["Address"]
    match_id = match_row["id"]

    print(f'"{name}", {address}, "{match_name}", {match_address}')


# airtable_insert()
# ________________________________________________________________________________________
def airtable_insert(location, external_id):
    lat = location.lat
    long = location.long
    if lat is None or long is None:
        lat, long = get_lat_long(location.address)
        print(f"Found lat/long: {lat}, {long}")

    airtable = Airtable(base_id, "Locations", api_key)
    url = location.url
    if location.reservation_url is not None:
        url = location.reservation_url

    county = location.county
    if not county.endswith(" County") and county != "San Francisco":
        county += " County"

    fields = {
        "Name": location.name,
        "Address": location.address,
        "Website": location.url,
        "Phone number": location.phone,
        "Hours": location.hours,
        "County": county,
        "Latitude": lat,
        "Longitude": long,
    }

    if external_id is not None:
        fields[external_id] = location.id

    airtable.insert(fields)


# airtable_update_id()
# ________________________________________________________________________________________
def airtable_update_id(location, match_id, place_name):
    if match_id is None:
        raise Exception("Match id is None!")

    if location.id is None:
        raise Exception("location.id is None!")

    if place_name == "Vaccine Finder":
        id_field = "vaccinefinder_location_id"
    else:
        raise Exception("Do not know how to update external id for " + place_name)

    logging.info(f"Updating {id_field} for {location.name}")
    airtable = Airtable(base_id, "Locations", api_key)
    record = airtable.match("Location ID", match_id)

    fields = {id_field: location.id}
    airtable.update(record["id"], fields)


# find_matches()
# ________________________________________________________________________________________
def find_matches(locs, db, args, place_name, address_match):
    # check to see if these locations are already in the database

    external_id = None
    if place_name == "Vaccine Finder":
        external_id = "vaccinefinder_location_id"

    num_found = 0
    for location in locs:
        found, match_id, match_row = in_db(location, db, address_match, external_id)

        if found:
            num_found += 1

        if args.print_tsv:
            if not found:
                print_fuzzy_tsv(location, db["content"], match_id)
        elif args.update_external_ids:
            if found:
                airtable_update_id(location, match_id, place_name)
        elif not found:
            if args.add_records:
                print_fuzzy_matches(location, db["content"])
                response = input("Add this record to Airtable? (y/n):")
                if response == "y":
                    airtable_insert(location, external_id)
            elif args.update_external_ids_fuzzy:
                matches = print_fuzzy_matches(location, db["content"])
                if len(matches) > 0:
                    response = input(f"Add {external_id}? (Enter N to skip, or 1-9 to update: ")
                    if re.match(r'\d+', response):
                        update_num = int(response)
                        if update_num <1 or update_num > len(matches):
                            raise Exception("Invalid record number")
                        match_id = matches[update_num-1]['id']
                        airtable_update_id(location, match_id, place_name)
            else:
                logging.warning(
                    f"\t{location.name}, {location.address} was not found in database! Please add it manually."
                )
                if external_id is not None:
                    logging.warning(
                        f"\t  {external_id}: {location.id}"
                    )

                fuzzy_matches = get_fuzzy_matches(location, db["content"])
                if len(fuzzy_matches) > 0:
                    logging.warning("\t  Possible matches for new location:")
                    for i, m in enumerate(fuzzy_matches):
                        logging.warning(f"\t  #{i+1:<5} {m['Name']}, {m['Address']}")
                    logging.warning("")

                if args.webhook_notify:
                    webhook.notify(
                        place_name, location.name, location.address, fuzzy_matches
                    )

    logging.info(f"\t{num_found} locations already in database")
