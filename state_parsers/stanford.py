# Parse vaccination site locations in CA ArcGIS feed

# Run manually: python3 -m state_parsers.california

import csv
import os
import json
import re
import time
import urllib3
from bs4 import BeautifulSoup

from . import Parser, Location
from . import header_dict, debug_print
from . import add_state, validate

parser = Parser(name="Stanford", url="https://stanfordhealthcare.org/discover/covid-19-resource-center/patient-care/safety-health-vaccine-planning.html")


def address_fixup(a):

    d = {
        "2585 Samaritan Drive, Suite 303, San Jose": ("95124", "Santa Clara"),
        "5565 W. Las Positas Blvd, Suite 150, Pleasanton": ("94588", "Alameda"),
        "6121 Hollis St, Emeryville": ("94608", "Alameda"),
        "341 Galvez Street, Stanford": ("94305", "Santa Clara"),
        "505 Broadway, Redwood City": ("94063", "San Mateo"),
        "350 E Tasman Dr, San Jose": ("95134", "Santa Clara"),
        '4501 Pleasanton Ave, Pleasanton, CA 94566': ("94566", "Alameda"),
        "2190 Eastridge Loop #1402, San José, CA 95122": ("95122", "Santa Clara"),
    }
    zip, county = d[a]
    if not re.search(r'\d{5}$', a):
        a = a + ", CA " + zip

    return a, county


# Returns a list of Locations
def run():
    http = urllib3.PoolManager(headers=header_dict)  # set user-agent
    r = http.request("GET", parser.url)

    soup = BeautifulSoup(r.data, "lxml")
    locations = []

    p = soup.find('p', string="Vaccination Sites")
    container = p.find_next('div', class_="container")
    items = container.find_all('li')

    for li in items:
        parts = li.get_text().split('\n')
        if ' at ' in parts[0]:
            name, address = parts[0].split(' at ', 1)
            hours = '\n'.join(parts[1:])
        else:
            name = 'Clinic at ' + parts[0].split(',')[0].strip().strip('*')
            address = parts[0]
            hours = '\n'.join(parts[1:])
            if address.endswith('*'):
                address = parts[1]
                hours = '\n'.join(parts[2:-1])

        address, county = address_fixup(address)
        phone = "(650) 498-9000"

        l = Location(name=name, address=address, hours=hours, phone=phone, county=county)
        locations.append(l)

    validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
