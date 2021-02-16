import os
import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict

# returns an minimum age
def run(county):
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request("GET", county.url)

    soup = BeautifulSoup(r.data, "lxml")
    locations = []

    age_li = soup.find("li", string="65 years and older")
    if age_li is None:
        raise Exception("Could not parse elgibilty for San Francisco County. Elgiblity criteria might have changed!")

    # TODO: parse kaiser and onemedical. Hardcoded for now
    return {
        "elgibility_age": 65,
        "overrides" : {
            "kaiser": 75,
            "onemedical": 75,
        }
    }