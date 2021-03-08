# Parse vaccination site locations for Ventura County

# Run manually: python3 -m location_parsers.ventura

import os
import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict
from . import County, Location


county = County(
    name="Ventura",
    url="https://www.venturacountyrecovers.org/vaccine-information/portal/",
)


def address_fixup(address):
    if address == "Vons 2825 1291 S Victoria Ave, Oxnard, 93035":
        return "Vons 2825 – 1291 S Victoria Ave, Oxnard, CA 93035"
    elif address == "Vons 1913 – 450 S Ventura Rd, Oxnard, CA 93030-6557":
        return "Vons 1913 – 450 S Ventura Rd, Oxnard, CA 93030"

    return address


# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request("GET", county.url)

    soup = BeautifulSoup(r.data, "lxml")
    locations = []

    tables = soup.find_all("div", class_="vc_col-sm-6")

    for table in tables:
        sites = table.find_all("a", href=True)

        for site in sites:
            url = site["href"]

            contents = site.contents
            if len(contents) < 1:
                continue

            info = contents[0]
            info = address_fixup(info)

            # m dash
            strings = info.split("–")

            if len(strings) < 2:
                continue

            name = strings[0].strip()
            address = strings[1].strip()

            locations.append(
                Location(name=name, address=address, county=county.name, url=url)
            )

    return locations


if __name__ == "__main__":
    locations = run()
    print(locations)
