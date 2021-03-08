# Parse vaccination site locations for Fresno County

# Run manually: python3 -m location_parsers.fresno

import os
import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict
from . import County, Location


county = County(
    name="Fresno",
    url="https://www.co.fresno.ca.us/departments/public-health/covid-19/covid-19-vaccine-information",
)

# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request("GET", county.url)

    soup = BeautifulSoup(r.data, "lxml")
    locations = []

    table = soup.find("table")
    sites = table.find_all("p")

    for site in sites:
        strong = site.find("strong")
        if strong is None:
            continue

        if len(strong.contents) == 0:
            continue

        # There's whitespace around a "-", with more whitespace
        name = strong.contents[0].strip().strip("-").strip()
        a = site.find("a")

        address = a.string

        locations.append(
            Location(name=name, address=address, county=county.name, url=None)
        )

    return locations


if __name__ == "__main__":
    locations = run()
    print(locations)
