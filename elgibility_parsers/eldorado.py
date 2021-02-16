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

    age_element = soup.find("em", string=re.compile("We are currently in Phase 1A, all tiers and Phase1B tier 1"))
    if age_element is None:
        raise Exception(
            f"Could not parse elgibilty for El Dorado County. Elgiblity criteria might have changed!"
        )

    # TODO: parse kaiser and onemedical. Hardcoded for now
    return {
        "elgibility_age": 75,
        "location_overrides": {
            "rec1eeCGaqqSWzUTU": 65,
        }
    }


if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from counties import counties

    age = run(counties["eldorado"])
    print(age)
