# Parse vaccination site locations for San Francisco County
# TODO: parse nonstandard City Collage location

# Run manually: python3 -m location_parsers.sanfrancisco

import os
import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict
from . import County, Location


county = County(name="San Francisco", url="https://sf.gov/vaccine-sites")

address_to_zip = {
    "1001 Potrero Ave, Building 30, San Francisco": "94110",
    "755 Font Blvd, San Francisco": "94132",
    "1181 Golden Gate Ave, San Francisco": "94115",
    "2401 Keith St, San Francisco": "94124",
    "1490 Mason St, San Francisco": "94133",
    "1351 24th Ave, San Francisco": "94122",
    "55 Frida Kahlo Way, San Francisco": "94112",
    "333 Turk St, San Francisco": "94102",
    "7000 Coliseum Way, Oakland": "94621",
    "747 Howard Street, San Francisco": "94103",
    "901 Rankin Street, San Francisco": "94124",
}


def address_fixup(address):
    if address in address_to_zip:
        zip = address_to_zip[address]

    return f"{address}, CA {zip}"


# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request("GET", county.url)

    soup = BeautifulSoup(r.data, "lxml")
    locations = []

    sites = soup.find_all("div", class_="sfgov-service-card vaccine-site")

    for site in sites:
        title = site.find(class_="vaccine-site__title")
        name = title.string.strip()

        title2 = site.find(class_="sfgov-address__location-name")
        if title2 is not None:
            name += f" - {title2.string}"

        if name == "":
            raise Exception("Could not parse location name")

        address = site.find(class_="vaccine-site__address").find("a").string

        if address == "":
            raise Exception("Could not parse location address")

        address = address_fixup(address)

        locations.append(
            Location(name=name, address=address, county=county.name, url=None)
        )

    return locations


# Not used for now
def run_selenium():
    from pyvirtualdisplay import Display
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException

    driver, display = driver_start()
    driver.get(county.url)

    locations = []
    sites = driver.find_elements_by_class_name("sfgov-address")

    for site in sites:
        title = site.find_element_by_class_name("sfgov-address__title")
        name = title.text

        try:
            name2 = site.find_element_by_class_name("sfgov-address__location-name")
            name += f"- {name2.text}"
        except NoSuchElementException:
            pass

        if name == "":
            raise Exception("Could not parse location name")

        address1 = site.find_element_by_class_name("sfgov-address__line1")
        address2 = site.find_element_by_class_name("sfgov-address__city-state-zip")
        address = ", ".join([address1.text, address2.text])

        if address == "":
            raise Exception("Could not parse location address")

        location = Location(name=name, address=address, county=county.name, url=None)
        locations.append(location)

    driver_stop(driver, display)
    return locations


if __name__ == "__main__":
    locations = run()
    print(locations)
