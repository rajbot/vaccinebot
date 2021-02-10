# Parse vaccination site locations for Imperial County

# Run manually: python3 -m location_parsers.imperial

import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict
from . import County, Location

county = County(
    name="Imperial",
    url="http://www.icphd.org/health-information-and-resources/healthy-facts/covid-19/covid-19-vaccine/vaccination-clinics/65-years-of-age-and-older/",
)

# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request("GET", county.url)

    soup = BeautifulSoup(r.data, "lxml")

    locations = []
    headers = soup.find_all("b", string=re.compile("Vaccine Provider:"))

    if len(headers) == 0:
        raise Exception("Could not parse headers")

    for h in headers:
        # Parse location name
        n = h.next_sibling
        if n.name is not None:
            # this should have been an unwrapped text string
            raise Exception("Could not parse location name")

        name = n.string.strip()
        if name == "":
            raise Exception("Could not parse location name (got empty string)")

        # Parse location address
        address_header = h.parent.find("b", string=re.compile("Address:"))

        # There could be a misplaced </b> tag, grab trailing text for the start of the address
        address = address_header.string.lstrip("Address:")

        a = address_header.next_sibling
        if a.name is not None:
            # this should have been an unwrapped text string
            raise Exception("Could not parse location address")

        address = address + a.string
        address = address.strip()
        address = re.sub(r"St\.,", "Street,", address)  # Canonicalize
        address = re.sub(r"St\. ([A-Z])", r"Street, \1", address)  # missing comma
        address = re.sub(r"\s+", " ", address)  # repeated whitespace

        if address == "":
            raise Exception("Could not parse location address (got empty string)")

        # Parse url
        a = h.parent.find("a")
        url = a.get("href")

        locations.append(
            Location(name=name, address=address, county=county.name, url=url)
        )

    return locations


if __name__ == "__main__":
    locations = run()
    print(locations)
