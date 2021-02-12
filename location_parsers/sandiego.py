# Parse vaccination site locations for San Diego County

# Run manually: python3 -m location_parsers.sandiego

import csv
import os
import json
import re
import time
import urllib3

from . import County, Location
from . import header_dict, debug_print
from . import add_state, validate

county = County(
    name="San Diego",
    url="https://sdcounty.maps.arcgis.com/apps/Nearby/index.html?appid=7369c2080ccf447ab91610ae69d84c43",
)


# Returns a list of json objects
def run():
    http = urllib3.PoolManager(headers=header_dict)  # set user-agent

    # No longer need these urls which contain a geometry parameter
    geometry_urls = [
        "https://services1.arcgis.com/1vIhDJwtG5eNmiqX/arcgis/rest/services/COVID19_Vaccination_Locations_PUBLIC_VIEW/FeatureServer/0/query?f=JSON&geometry=%7B%22spatialReference%22%3A%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D%2C%22xmin%22%3A-13775786.985666996%2C%22ymin%22%3A2504688.542850986%2C%22xmax%22%3A-12523442.714242995%2C%22ymax%22%3A3757032.814274987%7D&maxRecordCountFactor=3&outFields=*&outSR=102100&quantizationParameters=%7B%22extent%22%3A%7B%22spatialReference%22%3A%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D%2C%22xmin%22%3A-13775786.985666996%2C%22ymin%22%3A2504688.542850986%2C%22xmax%22%3A-12523442.714242995%2C%22ymax%22%3A3757032.814274987%7D%2C%22mode%22%3A%22view%22%2C%22originPosition%22%3A%22upperLeft%22%2C%22tolerance%22%3A2445.984905125002%7D&resultType=tile&returnExceededLimitFeatures=false&spatialRel=esriSpatialRelIntersects&where=1%3D1&geometryType=esriGeometryEnvelope&inSR=102100",
        "https://services1.arcgis.com/1vIhDJwtG5eNmiqX/arcgis/rest/services/COVID19_Vaccination_Locations_PUBLIC_VIEW/FeatureServer/0/query?f=JSON&geometry=%7B%22spatialReference%22%3A%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D%2C%22xmin%22%3A-12523442.714242995%2C%22ymin%22%3A3757032.814274987%2C%22xmax%22%3A-11271098.442818994%2C%22ymax%22%3A5009377.085698988%7D&maxRecordCountFactor=3&outFields=*&outSR=102100&quantizationParameters=%7B%22extent%22%3A%7B%22spatialReference%22%3A%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D%2C%22xmin%22%3A-12523442.714242995%2C%22ymin%22%3A3757032.814274987%2C%22xmax%22%3A-11271098.442818994%2C%22ymax%22%3A5009377.085698988%7D%2C%22mode%22%3A%22view%22%2C%22originPosition%22%3A%22upperLeft%22%2C%22tolerance%22%3A2445.984905125002%7D&resultType=tile&returnExceededLimitFeatures=false&spatialRel=esriSpatialRelIntersects&where=1%3D1&geometryType=esriGeometryEnvelope&inSR=102100",
        "https://services1.arcgis.com/1vIhDJwtG5eNmiqX/arcgis/rest/services/COVID19_Vaccination_Locations_PUBLIC_VIEW/FeatureServer/0/query?f=JSON&geometry=%7B%22spatialReference%22%3A%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D%2C%22xmin%22%3A-13775786.985666996%2C%22ymin%22%3A3757032.814274987%2C%22xmax%22%3A-12523442.714242995%2C%22ymax%22%3A5009377.085698988%7D&maxRecordCountFactor=3&outFields=*&outSR=102100&quantizationParameters=%7B%22extent%22%3A%7B%22spatialReference%22%3A%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D%2C%22xmin%22%3A-13775786.985666996%2C%22ymin%22%3A3757032.814274987%2C%22xmax%22%3A-12523442.714242995%2C%22ymax%22%3A5009377.085698988%7D%2C%22mode%22%3A%22view%22%2C%22originPosition%22%3A%22upperLeft%22%2C%22tolerance%22%3A2445.984905125002%7D&resultType=tile&returnExceededLimitFeatures=false&spatialRel=esriSpatialRelIntersects&where=1%3D1&geometryType=esriGeometryEnvelope&inSR=102100",
        "https://services1.arcgis.com/1vIhDJwtG5eNmiqX/arcgis/rest/services/COVID19_Vaccination_Locations_PUBLIC_VIEW/FeatureServer/0/query?f=JSON&geometry=%7B%22spatialReference%22%3A%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D%2C%22xmin%22%3A-15028131.257090997%2C%22ymin%22%3A2504688.542850986%2C%22xmax%22%3A-13775786.985666996%2C%22ymax%22%3A3757032.814274987%7D&maxRecordCountFactor=3&outFields=*&outSR=102100&quantizationParameters=%7B%22extent%22%3A%7B%22spatialReference%22%3A%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D%2C%22xmin%22%3A-15028131.257090997%2C%22ymin%22%3A2504688.542850986%2C%22xmax%22%3A-13775786.985666996%2C%22ymax%22%3A3757032.814274987%7D%2C%22mode%22%3A%22view%22%2C%22originPosition%22%3A%22upperLeft%22%2C%22tolerance%22%3A2445.984905125002%7D&resultType=tile&returnExceededLimitFeatures=false&spatialRel=esriSpatialRelIntersects&where=1%3D1&geometryType=esriGeometryEnvelope&inSR=102100",
        "https://services1.arcgis.com/1vIhDJwtG5eNmiqX/arcgis/rest/services/COVID19_Vaccination_Locations_PUBLIC_VIEW/FeatureServer/0/query?f=JSON&geometry=%7B%22spatialReference%22%3A%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D%2C%22xmin%22%3A-15028131.257090997%2C%22ymin%22%3A3757032.814274987%2C%22xmax%22%3A-13775786.985666996%2C%22ymax%22%3A5009377.085698988%7D&maxRecordCountFactor=3&outFields=*&outSR=102100&quantizationParameters=%7B%22extent%22%3A%7B%22spatialReference%22%3A%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D%2C%22xmin%22%3A-15028131.257090997%2C%22ymin%22%3A3757032.814274987%2C%22xmax%22%3A-13775786.985666996%2C%22ymax%22%3A5009377.085698988%7D%2C%22mode%22%3A%22view%22%2C%22originPosition%22%3A%22upperLeft%22%2C%22tolerance%22%3A2445.984905125002%7D&resultType=tile&returnExceededLimitFeatures=false&spatialRel=esriSpatialRelIntersects&where=1%3D1&geometryType=esriGeometryEnvelope&inSR=102100",
    ]

    urls = [
        "https://services1.arcgis.com/1vIhDJwtG5eNmiqX/arcgis/rest/services/COVID19_Vaccination_Locations_PUBLIC_VIEW/FeatureServer/0/query?f=JSON&where=1%3D1&outFields=*"
    ]

    locations = []
    for url in urls:
        r = http.request("GET", url)
        obj = json.loads(r.data.decode("utf-8"))

        for feature in obj["features"]:
            attributes = feature["attributes"]
            l = Location(
                name=attributes["name"].strip(),
                address=add_state(attributes["fulladdr"]),
                url=attributes.get("url_scheduling").strip(),
                phone=attributes.get("phone"),
                hours=attributes.get("operhours"),
                county=county.name,
            )
            locations.append(l)

    validate(locations)
    return locations


# No longer used because json feeds are available
def run_selenium():
    import tempfile
    from . import driver_start, driver_stop
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    from selenium.webdriver import ActionChains
    from selenium.webdriver.common.keys import Keys

    dir = tempfile.TemporaryDirectory()
    driver, display = driver_start(download_dir=dir.name)
    driver.get(county.url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//span[@class='esri-slider__thumb']")
        )
    )
    time.sleep(2)

    e = driver.find_element_by_xpath("//span[@class='esri-slider__thumb']")

    move = ActionChains(driver)
    move.click_and_hold(e).move_by_offset(300, 0).release().perform()

    input = driver.find_element_by_xpath(
        "//input[@title='Search by address, city, or ZIP code']"
    )
    print(input)
    input.send_keys("San Diego, CA, USA", Keys.ENTER)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//ul[@role='group']"))
    )
    time.sleep(2)
    ul = driver.find_element_by_xpath("//ul[@role='group']")
    print(ul)

    items = ul.find_elements_by_tag_name("li")
    print(items)

    time.sleep(60)
    return []

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(.,'OK')]"))
    )
    time.sleep(2)

    # We wait for an OK button to get past the splash screen, but we actually
    # need to click the offscreen submit input instead..
    driver.execute_script(
        "(function() {var i = document.getElementsByTagName('input'); i.item(i.length-1).click();})();"
    )
    time.sleep(1)

    # Open the toolbar
    driver.execute_script("$('.flyout-menu-active-tool').click();")
    time.sleep(1)

    # Click the button to open the table view
    driver.execute_script("$('button.toolbar-item')[0].click();")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//strong[contains(.,'Vaccination Locations')]")
        )
    )

    # Open the options menu
    driver.execute_script("$('button[data-tab-context-menu-button]')[0].click()")
    time.sleep(1)

    # Click the export to CSV button
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//strong[contains(., 'Export to CSV')]")
        )
    )
    e = driver.find_element_by_xpath("//strong[contains(., 'Export to CSV')]")
    button = e.find_element_by_xpath("..")
    driver.execute_script("arguments[0].click();", button)
    time.sleep(1)

    # Click the OK button to download CSV to `dir/Export.csv`
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//p[contains(., 'Confirm?')]"))
    )
    p = driver.find_element_by_xpath("//p[contains(., 'Confirm?')]")
    driver.execute_script("console.log(arguments[0]);", p)

    div = p.find_element_by_xpath(".//following-sibling::div")
    driver.execute_script("console.log(arguments[0]);", div)

    button = div.find_element_by_xpath(".//button[contains(.,'OK')]")
    driver.execute_script("console.log(arguments[0]);", button)
    driver.execute_script("arguments[0].click();", button)

    time.sleep(5)  # How do we know if the download is done?

    csv_path = os.path.join(dir.name, "Export.csv")

    locations = []
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = None
            if row["Online Registration"] != "":
                url = row["Online Registration"]
            locations.append(
                Location(
                    name=row["Facility Name"].strip(),
                    address=f'{row["Address"].strip()}, {row["City"].strip()}, CA {row["Zip Code"].strip()}',
                    url=url,
                    county=county.name,
                )
            )
    return locations


if __name__ == "__main__":
    locations = run()
    debug_print(locations)
