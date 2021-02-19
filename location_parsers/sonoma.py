# Parse vaccination site locations for Sonoma County

# Run manually: python3 -m location_parsers.sonoma

import os
import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict
from . import County, Location
from . import debug_print, validate


county = County(
    name="Sonoma",
    url="https://socoemergency.org/emergency/novel-coronavirus/vaccine-information/clinics/",
)


def address_fixup(a):
    """Add missing zip codes. These are from geocoder lookups, but
    hardcoded here so you don't need a mapquest api key to run this module"""

    d = {
        "501 Asti Road, Cloverdale": "95425",
        "9291 Old Redwood Highway #200, Windsor": "95492",
        "5401 Snyder Lane, Rohnert Park": "94928",
        "16405 River Road, Guerneville": "95446",
        "1115 Vine Street, Healdsburg": "95448",
        "389 South McDowell Boulevard, Petaluma": "94954",
        "6340 Commerce Boulevard, Rohnert Park": "94928",
        "1350 Bennett Valley Road, Santa Rosa": "95404",
        "6633 Oakmont Drive, Santa Rosa": "95409",
        "100 Calistoga Road, Santa Rosa": "95409",
        "1799 Marlow Road, Santa Rosa": "95401",
        "2300 Mendocino Avenue, Santa Rosa": "95403",
        "2785 Yulupa Avenue, Santa Rosa": "95405",
        "406 North Main Street, Sebastopol": "95472",
        "477 West Napa Street, Sonoma": "95476",
        "9080 Brooks Road, Windsor": "95492",
        "126 1st Street West, Sonoma": "95476",
        "20000 Broadway, Sonoma": "95476",
        "14630 Armstrong Woods Road, Guerneville": "95446",
        "1024 Prince Avenue, Healdsburg": "95448",
    }

    if a in d:
        zip = d[a]
        a = f"{a}, CA {zip}"

    # For Petaluma Health Center, the county lists the address for Petaluma Fitness Center
    # However, our records have the health center's address.
    if a == "680 Sonoma Mountain Parkway, Building 800, Petaluma":
        a = "1179 N McDowell Blvd, Petaluma, CA 94954"

    return a


# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request("GET", county.url)

    soup = BeautifulSoup(r.data, "lxml")

    table = soup.find("table", class_="vaccineFilterTable")
    rows = table.find_all("tr")

    locations = []

    for row in rows:
        tds = row.find_all("td")
        if len(tds) == 0:
            continue

        # print(tds[2])
        strong = tds[2].find("strong")
        if strong == None:
            continue

        name = strong.get_text()
        if name == "Safeway":
            name = tds[0].get_text()
        name = name.strip()

        next = strong.next_sibling
        if next.name == "br":
            next = next.next_sibling
        address = next.string.strip()
        address = address_fixup(address)

        l = Location(name=name, address=address, county=county.name)
        locations.append(l)

    validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
