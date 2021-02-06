import os
from collections import namedtuple
from selenium.webdriver.chrome.options import Options

agent_string = "Vaccinebot (+https://bitstream.io/vaccinebot)"
chrome_opts = Options()
chrome_opts.add_argument(f"user-agent={agent_string}") # for selenium
header_dict = {'user-agent': agent_string}             # for urllib3

chromedriver_path =  os.environ.get("CHROMEDRIVER_PATH")

County = namedtuple('County', ['name', 'url'])
Location = namedtuple('Location', ['name', 'address', 'county'])
