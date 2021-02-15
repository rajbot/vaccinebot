# Parse vaccination site locations for San Francisco County
# TODO: parse nonstandard City Collage location

# Run manually: python3 -m location_parsers.santabarbara

import os
import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict
from . import County, Location
from . import debug_print, validate


county = County(
    name="Santa Barbara",
    url="https://publichealthsbc.org/covid-19-vaccine-appointment-registration/",
)


def address_fixup(a):
    # correct zip codes / add missing zips
    if a == "1400 East Church Street, Santa Maria, CA":
        a += " 93454"
    elif a == "2320 South Broadway, Santa Maria, CA 93455":
        a = a.replace("93455", "93454")

    return a


# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request("GET", county.url)

    soup = BeautifulSoup(r.data, "lxml")
    sites = soup.find("h2", string="Location")
    section = sites.find_parent("section")

    locations = []
    for s in section.next_siblings:
        if s.name is None:
            continue
        if s.name == "div":
            break
        # print(s)

        strong = s.find("strong")
        name = strong.string

        address = strong.parent.get_text()
        address = address[len(name) :].strip()
        address = address.replace("at ", "")
        address = re.sub(r"(, CA( \d{5})?).*", r"\1", address)
        address = address_fixup(address)

        # Some listings aren't for individual sites and don't have addresses
        if ", CA" not in address:
            continue

        l = Location(name=name, address=address)
        locations.append(l)

    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
