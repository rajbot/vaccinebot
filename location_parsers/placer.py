# Parse vaccination site locations for Placer County

# Run manually: python3 -m location_parsers.placer

import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict, validate
from . import County, Location

county = County(name="Placer", url="https://www.placer.ca.gov/vaccineclinics")


# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request("GET", county.url)

    soup = BeautifulSoup(r.data, "lxml")

    locations = []

    # Parse clinic locations. Look for all h2 headers
    # between "Available Clinics" and "Second Dose Appointments"
    h2 = soup.find("h2", string="Available Clinics")
    h2 = h2.find_next("h2", class_="subhead1")

    while h2.text != "Second Dose Appointments":
        name = h2.text

        p = h2.find_next("p")
        address = f"{p.contents[0]}, {p.contents[2]}"

        l = Location(name=name, address=address, county=county.name)
        locations.append(l)
        h2 = h2.find_next("h2", class_="subhead1")

    # Parse safeway locations
    header = soup.find("strong", string="Location")
    table = header.find_parent("table")
    tbody = table.find("tbody")
    rows = tbody.find_all("tr")

    for row in rows:
        name = row.find("strong")

        address1 = name.next_sibling.next_sibling
        address2 = address1.next_sibling.next_sibling

        address = f"{address1}, {address2}"

        # fix any addresses with missing state
        address = re.sub(r", (9\d{4})$", r", CA \1", address)

        td = row.find_all("td")[1]
        url = td.find("a").get("href")

        l = Location(
            name=name.text, address=address, county=county.name, reservation_url=url
        )
        locations.append(l)

    validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    print(locations)
