# Parse vaccination site locations for Kern County

# Run manually: python3 -m location_parsers.kern

import csv
import os
import re
import tempfile
import time

from . import County, Location
from . import driver_start, driver_stop

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

county = County(
    name = "Kern",
    url = "https://phweb.kerncounty.com/Html5Viewer/index.html?viewer=COVID19Vaccination#"
)


# Returns a list of Location objects
def run():
    dir = tempfile.TemporaryDirectory()
    driver, display = driver_start(download_dir=dir.name)
    driver.get(county.url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(.,'OK')]")))
    time.sleep(2)


    # We wait for an OK button to get past the splash screen, but we actually
    # need to click the offscreen submit input instead..
    driver.execute_script("(function() {var i = document.getElementsByTagName('input'); i.item(i.length-1).click();})();");
    time.sleep(1)

    # Open the toolbar
    driver.execute_script("$('.flyout-menu-active-tool').click();")
    time.sleep(1)

    # Click the button to open the table view
    driver.execute_script("$('button.toolbar-item')[0].click();")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//strong[contains(.,'Vaccination Locations')]")))

    # Open the options menu
    driver.execute_script("$('button[data-tab-context-menu-button]')[0].click()")
    time.sleep(1)

    # Click the export to CSV button
    e = driver.find_element_by_xpath("//strong[contains(., 'Export to CSV')]")
    button = e.find_element_by_xpath('..')
    driver.execute_script("arguments[0].click();", button)
    time.sleep(1)

    # Click the OK button to download CSV to `dir/Export.csv`
    p = driver.find_element_by_xpath("//p[contains(., 'Confirm?')]")
    driver.execute_script("console.log(arguments[0]);", p)

    div = p.find_element_by_xpath(".//following-sibling::div")
    driver.execute_script("console.log(arguments[0]);", div)

    button = div.find_element_by_xpath(".//button[contains(.,'OK')]");
    driver.execute_script("console.log(arguments[0]);", button)
    driver.execute_script("arguments[0].click();", button)

    time.sleep(5) # How do we know if the download is done?

    csv_path = os.path.join(dir.name, 'Export.csv')

    locations = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = None
            if row['Online Registration'] != '':
                url = row['Online Registration']
            locations.append(Location(
                name = row['Facility Name'].strip(),
                address = f'{row["Address"].strip()}, {row["City"].strip()}, CA {row["Zip Code"].strip()}',
                url = url,
                county = county.name
            ))
    return locations

if __name__ == "__main__":
    locations = run()
    print(locations)
