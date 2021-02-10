# Parse vaccination site locations for Placer County

# Run manually: python3 -m location_parsers.placer

import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict, validate
from . import County, Location

county = County(
    name = "Placer",
    url = "https://www.placer.ca.gov/vaccineclinics"
)


# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request('GET', county.url)

    soup = BeautifulSoup(r.data, 'lxml')

    header = soup.find('strong', string='Location')
    table = header.find_parent('table')
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')

    locations = []

    for row in rows:
        name = row.find('strong')

        address1 = name.next_sibling.next_sibling
        address2 = address1.next_sibling.next_sibling

        address = f'{address1}, {address2}'

        # fix any addresses with missing state
        address = re.sub(r', (9\d{4})$', r', CA \1', address)

        locations.append(Location(
            name = name.text,
            address = address,
            county = county.name
        ))

    validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    print(locations)
