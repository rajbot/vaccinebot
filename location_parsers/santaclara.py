# Parse vaccination site locations for Santa Clara County

# Run manually: python3 -m location_parsers.santaclara

import os
import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict
from . import County, Location
from . import debug_print, validate


county = County(
    name="Santa Clara",
    url="https://vax.sccgov.org/home",
)


def address_fixup(a):
    """ Add missing zip codes """

    a = a.replace(
        "2542 Monterey Highway, Gate D, San Jose, CA",
        "2542 Monterey Highway, Gate D, San Jose, CA 95111",
    )
    return a


# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request("GET", county.url)

    soup = BeautifulSoup(r.data, "lxml")

    span = soup.find("span", string="Where would you like to be vaccinated?")
    fieldset = span.find_parent("fieldset")
    inputs = fieldset.find_all("input")

    locations = []
    for i in inputs:
        label = i.parent.find("label")
        name = label.string

        div = i.parent.find("div")
        address = div.string
        address = address_fixup(address)

        if ", CA" not in address:
            continue

        l = Location(name=name, address=address, county=county.name)
        locations.append(l)

    options = fieldset.find_all_next("option")
    for o in options:
        if ", CA" in o.string:
            name, address, extra = re.split("[\(\)]", o.string)
            l = Location(name=name.strip(), address=address, county=county.name)
            locations.append(l)

    validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
