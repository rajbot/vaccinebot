import os
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

headless_mode = False
if os.getenv("HEADLESS") == "1" or os.getenv("HEADLESS") == "true":
    from pyvirtualdisplay import Display
    headless_mode = True

agent_string = "Vaccinebot (+https://bitstream.io/vaccinebot)"
chrome_opts = Options()
chrome_opts.add_argument(f"user-agent={agent_string}") # for selenium
header_dict = {'user-agent': agent_string}             # for urllib3

chromedriver_path =  os.environ.get("CHROMEDRIVER_PATH")

County = namedtuple('County', ['name', 'url'])
Location = namedtuple('Location', ['name', 'address', 'county', 'url'])


def driver_start():
    display = None
    if headless_mode:
        display = Display(visible=0, size=(800, 600))
        display.start()

    driver = webdriver.Chrome(chromedriver_path, options=chrome_opts)
    return driver, display

def driver_stop(driver, display):
    driver.close()

    if headless_mode:
        display.stop()
