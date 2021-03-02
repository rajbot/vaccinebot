# Parse vaccination site locations for Santa Barbara County

# Run manually: python3 -m location_parsers.santabarbara

import os
import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict
from . import County, Location
from . import debug_print, validate, add_comma


county = County(
    name="San Bernardino",
    url="https://sbcovid19.com/vaccine/locations/",
)


def address_fixup(address):
    if address == "10801 Sixth St., Rancho Cucamonga":
        address = "10801 Sixth St, Rancho Cucamonga, CA 91730"
    elif address == "15970 Los Serranos City Club D, Chino Hills, CA 91709":
        address = "15970 Los Serranos City Club Dr, Chino Hills, CA 91709"
    elif address == "12202 1st St., Yucaipa":
        address = "12202 1st St., Yucaipa, CA 92399"
    elif address == "660 Colton Ave, Colton, CA 923246":
        address = "660 Colton Ave, Colton, CA 92324"

    # If the address doesn't have "," between the City and CA, add the comma
    address = add_comma(address)

    # Strip leading/trailing "." and whitespaces
    return address.strip(". ")


# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request("GET", county.url)

    soup = BeautifulSoup(r.data, "lxml")
    divs = soup.find_all("div", class_="wp-block-isd-column")

    locations = []

    for div in divs:
        name_spans = div.find_all("span", class_="lead")
        if len(name_spans) == 0:
            continue

        for name_span in name_spans:
            # We use contents[0] instead of name.string directly as <b>/<strong> formatting results in .string directly returning None
            name = name_span.contents[0].string.strip()

            # The address is within an anchor, two siblings down
            address_anchor = name_span.find_next_sibling().find_next_sibling().find("a")
            if address_anchor is None:
                continue

            address = address_anchor.string

            # If the address doesn't exist, or it's a URL/other link, skip it
            if address == "" or address is None or re.match(r"^[^0-9]", address):
                continue

            address = address_fixup(address)
            l = Location(name=name, address=address, county=county.name)
            if l not in locations:
                locations.append(l)

        p_spans = div.find_all("p", class_="has-black-color")

        for p_span in p_spans:
            name_strong = p_span.find("strong")
            if name_strong is None:
                continue
            name = name_strong.string
            if name is None:
                continue

            address = p_span.contents[2].string

            # If the address doesn't exist, or it's a URL/other link, skip it
            if address == "" or address is None or re.match(r"^[^0-9]", address):
                continue

            address = address_fixup(address)
            l = Location(name=name, address=address, county=county.name)
            if l not in locations:
                locations.append(l)

    validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
