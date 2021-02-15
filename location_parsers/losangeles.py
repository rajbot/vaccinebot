# Parse vaccination site locations for Los Angeles County

# Run manually: python3 -m location_parsers.losangeles

import csv
import json
import logging
import os
import re
import time
import urllib3

from . import County, Location
from . import header_dict, debug_print
from . import add_state, validate


county = County(
    name="Los Angeles",
    url="https://www.google.com/maps/d/viewer?mid=1AdIIUb669F7mV6J5A6McJo7eC5X67dfG&ll=34.21430603614488%2C-118.28563654999999&z=9",
)


def address_fixup(a):
    """ Some LA addresses in the feed are incorrect and need fixing. """

    # missing comma
    a = re.sub(r"([^,])\s+Los Angeles, CA", r"\1, Los Angeles, CA", a)

    # wrong city
    a = a.replace(
        "23850 Copper Hill Dr, Santa Clarita, CA 91354",
        "23850 Copper Hill Dr, Valencia, CA 91354",
    )
    a = a.replace(
        "7257 W Sunset Blvd, Los Angeles, CA 90046",
        "7257 W Sunset Blvd, West Hollywood, CA 90046",
    )
    a = a.replace(
        "19781 Rinaldi St, Porter Ranch, CA 91326",
        "19781 Rinaldi St, Northridge, CA 91326",
    )
    a = a.replace(
        "645 W 9th St, Los Angeles, CA 90015", "645 W 9th St, Los Angeles, CA 90017"
    )
    a = a.replace(
        "500 N Pacific Coast Hwy, El Segundo, CA 90245",
        "500 N Sepulveda Blvd, El Segundo, CA 90245",
    )
    a = a.replace(
        "7789 Foothill Blvd, Los Angeles, CA 91042",
        "7789 Foothill Blvd, Tujunga, CA 91042",
    )
    a = a.replace(
        "16830 San Fernando Mission Blvd, Los Angeles, CA 91344",
        "16830 San Fernando Mission Blvd, Granada Hills, CA 91344",
    )
    return a


def parse_location(l):
    info = l[5][0]

    if not (info[0].startswith("Location") or info[0] == "name"):
        raise Exception("Could not parse location name")
    name = " ".join(info[1])
    name = name.encode("latin-1").decode("utf-8").strip()

    latlong = l[1][0][0]
    details = l[5][3]

    address = None
    reservation_url = None
    hours = None
    for kv in details:
        # Note: there is a Spanish version separated by six or more hypthens
        # Uncomment the code below to strip out translations, once we get a
        # translation layer built. In the mean time, keep it to help people.
        # s = re.split(r'-----+', kv[1][0])[0]
        s = kv[1][0]

        # encode spanish characters properly
        s = s.encode("latin-1").decode("utf-8")
        s = s.expandtabs(1)
        s = s.strip()

        if kv[0].startswith("Address"):
            address = address_fixup(s)
        elif kv[0].startswith("Appointments"):
            reservation_url = s
        elif kv[0].startswith("Hours"):
            hours = s

    location = Location(
        name=name,
        lat=latlong[0],
        long=latlong[1],
        address=address,
        reservation_url=reservation_url,
        hours=hours,
        county=county.name,
    )

    return location


def parse_locations(group):
    """Parse out locations from a group object. Return an array of locations"""
    subgroup = group[12]

    locations = []
    for sub in subgroup:
        locs = sub[13]

        for loc in locs[0]:
            l = parse_location(loc)
            locations.append(l)

    validate(locations)
    return locations


# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)  # set user-agent

    locations = []
    r = http.request("GET", county.url)
    c = r.data.decode("utf-8")

    m = re.search(r'var _pageData = "(.+)";<\/script>', c)
    c1 = m.group(1)
    obj = json.loads(c1.encode().decode("unicode-escape"))

    # get the mf'n map
    mf_map = obj[1]
    if mf_map[0] != "mf.map":
        raise Exception("Could not parse mf.map")

    groups = mf_map[6]
    locations = []
    for group in groups:
        print(f"Parsing {group[2]}")
        locations += parse_locations(group)

    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
