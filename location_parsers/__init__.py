import os
from collections import namedtuple
from selenium.webdriver.chrome.options import Options

chrome_opts = Options()
chrome_opts.add_argument("user-agent=Vaccinebot (+https://bitstream.io/vaccinebot)")

chromedriver_path =  os.environ.get("CHROMEDRIVER_PATH")

County = namedtuple('County', ['name', 'url'])
Location = namedtuple('Location', ['name', 'address', 'county'])
