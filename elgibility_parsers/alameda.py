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

    age_element = soup.find("h4", string=re.compile("Phase 1b: 65\+"))
    if age_element is None:
        raise Exception(
            f"Could not parse elgibilty for Alameda County. Elgiblity criteria might have changed!"
        )

    # TODO: parse kaiser and onemedical. Hardcoded for now
    return {
        "elgibility_age": 65,
        "overrides": {
            "kaiser": 75,
            "onemedical": 75,
        },
    }
