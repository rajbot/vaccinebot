import os
import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict

# returns an minimum age
def run(county):
    # TODO: actually parse this info
    return {
        "elgibility_age": 65,
    }

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from counties import counties
    age = run(counties["contracosta"])
    print(age)
