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

    age_element = soup.find("span", string=re.compile("Persons 65 and older interested in getting the COVID-19 vaccine"))
    if age_element is None:
        raise Exception(f"Could not parse elgibilty for Butte County. Elgiblity criteria might have changed!")

    # TODO: parse kaiser and onemedical. Hardcoded for now
    return {
        "elgibility_age": 65,
    }

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from counties import counties
    age = run(counties["calaveras"])
    print(age)
