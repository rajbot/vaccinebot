# Parse vaccination site locations for Tulare County

# Run manually: python3 -m location_parsers.tulare

import time

from . import County, Location
from . import driver_start, driver_stop
from . import debug_print, validate

county = County(
    name="Tulare",
    url="https://covid19.tularecounty.ca.gov/covid-19-vaccine/make-a-vaccination-appointment/covid-vaccination-sites-in-tulare-county/",
)


# Returns a list of Location objects
def run():
    driver, display = driver_start()
    driver.get(county.url)

    locations = []

    def get_locations_from_table():
        time.sleep(1)
        table_body = driver.find_element_by_xpath("//table[@id='listingofdata']//tbody")
        rows = table_body.find_elements_by_tag_name("tr")

        for row in rows:
            columns = row.find_elements_by_tag_name("td")
            name = columns[0].text
            link = columns[0].find_elements_by_tag_name("a")[0]
            url = link.get_attribute("href") or None
            address = columns[1].text.replace("\n", ", ").replace(" CA, ", " CA ")
            locations.append(
                Location(name=name, address=address, county=county.name, url=url)
            )

    while True:
        get_locations_from_table()
        next_button = driver.find_element_by_xpath(
            "//a[contains(@class, 'paginate_button next')]"
        )
        if "disabled" in next_button.get_attribute("class"):
            break
        else:
            next_button.click()

    driver_stop(driver, display)

    validate(locations)
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
