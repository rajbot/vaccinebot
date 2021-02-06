# Parse vaccination site locations for San Francisco County
# TODO: parse nonstandard City Collage location

import os

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from . import chrome_opts, chromedriver_path
from . import County, Location

county = County(
    name = "San Francisco",
    url = "https://sf.gov/get-vaccinated-against-covid-19"
)

def run():
    display = Display(visible=0, size=(800, 600))
    display.start()

    driver = webdriver.Chrome(chromedriver_path, chrome_options=chrome_opts)
    driver.get(county.url)

    locations = []
    sites = driver.find_elements_by_class_name("sfgov-address")

    for site in sites:
        title = site.find_element_by_class_name("sfgov-address__title")
        name = title.text

        try:
            name2 = site.find_element_by_class_name("sfgov-address__location-name")
            name += f'- {name2.text}'
        except NoSuchElementException:
            pass

        address1 = site.find_element_by_class_name("sfgov-address__line1")
        address2 = site.find_element_by_class_name("sfgov-address__city-state-zip")
        address = ', '.join([address1.text, address2.text])

        location = Location(
            name = title.text,
            address = address,
            county = county.name
        )
        locations.append(location)

    driver.close()
    display.stop()
    return locations