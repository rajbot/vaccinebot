import os
import re
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

headless_mode = False
if os.getenv("HEADLESS") == "1" or os.getenv("HEADLESS") == "true":
    from pyvirtualdisplay import Display

    headless_mode = True

agent_string = "Vaccinebot (+https://bitstream.io/vaccinebot)"
header_dict = {"user-agent": agent_string}  # for urllib3

County = namedtuple("County", ["name", "url"])
Location = namedtuple(
    "Location",
    [
        "name",
        "address",
        "county",
        "url",
        "reservation_url",
        "phone",
        "hours",
        "lat",
        "long",
        "zip",
        "org_name",
        "id",
    ],
    defaults=[None] * 12,
)


def driver_start(download_dir=None):
    chrome_opts = Options()
    chrome_opts.add_argument(f"user-agent={agent_string}")  # for selenium
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")

    display = None
    if headless_mode:
        display = Display(visible=0, size=(800, 600))
        display.start()

    if download_dir is not None:
        chrome_opts.add_experimental_option(
            "prefs",
            {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing_for_trusted_sources_enabled": False,
                "safebrowsing.enabled": False,
            },
        )

    driver = webdriver.Chrome(chromedriver_path, options=chrome_opts)
    return driver, display


def driver_stop(driver, display):
    driver.close()

    if headless_mode:
        display.stop()

def add_comma(address):
    """fix any addresses that are missing a comma between the city and state"""
    return re.sub(r"(\w) CA", r"\1, CA", address)

def add_state(address):
    """fix any addresses with missing state"""
    return re.sub(r", (9\d{4})$", r", CA \1", address.strip())


def validate(locations):
    for l in locations:
        if l.name is None or l.name.strip() == "":
            raise Exception("Could not parse name")
        if l.address is None or l.address.strip() == "":
            raise Exception(f"Could not parse address: {l.address}")
        if not re.search(r", CA 9\d{4}$", l.address):
            raise Exception(f"Couldn't parse zip code: {l.address}")
        if l.county is None or l.county.strip() == "":
            raise Exception("Could not parse county")


def debug_print(locations):
    for l in locations:
        for key in l._fields:
            print(f"{key:20} {getattr(l, key)}")
        print()
