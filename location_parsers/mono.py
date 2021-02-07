# Parse vaccination site locations for Mono County

# Run manually: python3 -m location_parsers.mono

import re
import time

from . import chrome_opts, chromedriver_path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from . import header_dict
from . import County, Location


county = County(
    name = "Mono",
    url = "https://coronavirus.monocounty.ca.gov/pages/vaccinations"
)


# Returns a list of Location objects
def run():
    driver = webdriver.Chrome(chromedriver_path, options=chrome_opts)
    driver.get(county.url)

    # Wait for ember.js
    time.sleep(5);

    e = driver.find_element_by_xpath("//strong[contains(., 'Vaccination Locations')]")

    h5 = e.find_element_by_xpath('../..')
    next_h5 = h5.find_element_by_xpath(".//following-sibling::h5")

    ul = next_h5.find_element_by_tag_name('ul')
    ul2 = ul.find_element_by_tag_name('ul')
    items = ul2.find_elements_by_tag_name('li')

    locations = []
    for li in items:
        # split name and address
        m = re.match(r'(.+) \((.+)\)', li.text)
        name = m.group(1)

        address = m.group(2)
        if ',' not in address:
            # add town name
            town = name.split()[0]
            address += ", " + town
        address += ", CA"

        locations.append(Location(
            name = name,
            address = address,
            county = county.name,
            url = None
        ))

    driver.close()

    return locations


if __name__ == "__main__":
    locations = run()
    print(locations)
