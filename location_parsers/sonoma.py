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

    a = a.replace("501 Asti Road, Cloverdale", "501 Asti Road, Cloverdale, CA 95425")
    a = a.replace(
        "9291 Old Redwood Highway #200, Windsor",
        "9291 Old Redwood Highway #200, Windsor, CA 95492",
    )
    a = a.replace(
        "5401 Snyder Lane, Rohnert Park", "5401 Snyder Lane, Rohnert Park, CA 94928"
    )
    a = a.replace(
        "16405 River Road, Guerneville", "16405 River Road, Guerneville, CA 95446"
    )
    a = a.replace(
        "1115 Vine Street, Healdsburg", "1115 Vine Street, Healdsburg, CA 95448"
    )
    a = a.replace(
        "389 South McDowell Boulevard, Petaluma",
        "389 South McDowell Boulevard, Petaluma, CA 94954",
    )
    a = a.replace(
        "6340 Commerce Boulevard, Rohnert Park",
        "6340 Commerce Boulevard, Rohnert Park, CA 94928",
    )
    a = a.replace(
        "1350 Bennett Valley Road, Santa Rosa",
        "1350 Bennett Valley Road, Santa Rosa, CA 95404",
    )
    a = a.replace(
        "6633 Oakmont Drive, Santa Rosa", "6633 Oakmont Drive, Santa Rosa, CA 95409"
    )
    a = a.replace(
        "100 Calistoga Road, Santa Rosa", "100 Calistoga Road, Santa Rosa, CA 95409"
    )
    a = a.replace(
        "1799 Marlow Road, Santa Rosa", "1799 Marlow Road, Santa Rosa, CA 95401"
    )
    a = a.replace(
        "2300 Mendocino Avenue, Santa Rosa",
        "2300 Mendocino Avenue, Santa Rosa, CA 95403",
    )
    a = a.replace(
        "2785 Yulupa Avenue, Santa Rosa", "2785 Yulupa Avenue, Santa Rosa, CA 95405"
    )
    a = a.replace(
        "406 North Main Street, Sebastopol",
        "406 North Main Street, Sebastopol, CA 95472",
    )
    a = a.replace(
        "477 West Napa Street, Sonoma", "477 West Napa Street, Sonoma, CA 95476"
    )
    a = a.replace("9080 Brooks Road, Windsor", "9080 Brooks Road, Windsor, CA 95492")
    a = a.replace(
        "126 1st Street West, Sonoma", "126 1st Street West, Sonoma, CA 95476"
    )
    a = a.replace("20000 Broadway, Sonoma", "20000 Broadway, Sonoma, CA 95476")
    a = a.replace(
        "14630 Armstrong Woods Road, Guerneville",
        "14630 Armstrong Woods Road, Guerneville, CA 95446",
    )

    # For Petaluma Health Center, the county lists the address for Petaluma Fitness Center
    # However, our records have the health center's address.
    a = a.replace(
        "680 Sonoma Mountain Parkway, Building 800, Petaluma",
        "1179 N McDowell Blvd, Petaluma, CA 94954"
    )

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
