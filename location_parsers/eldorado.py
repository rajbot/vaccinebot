# Parse vaccination site locations for El Dorado County
# TODO: parse Safeway Locations

# Run manually: python3 -m location_parsers.eldorado

import http
import re
import urllib3
from bs4 import BeautifulSoup

from . import header_dict
from . import County, Location

county = County(
    name = "El Dorado",
    url = "https://www.edcgov.us/Government/hhsa/edccovid-19-clinics"
)

# Returns a list of Location objects
def run():
    http = urllib3.PoolManager(headers=header_dict)
    r = http.request('GET', county.url)

    soup = BeautifulSoup(r.data, 'html.parser')

    span = soup.find('span', string="EL DORADO COUNTY PUBLIC HEALTH CLINICS")

    header_div = span.parent.parent
    locations_div = header_div.next_sibling
    locations_list = locations_div.find('ul')
    locations_items = locations_list.find_all('li')

    locations = []
    for item in locations_list.contents:
        if item.name == 'li':
            # Parse title, split across multiple spans
            title = ""
            title_spans = item.find_all(style=re.compile("font-weight:bold"))
            for t in title_spans:
                title += t.string

            if title == "":
                raise Exception("Could not parse location name")

            title = title.rstrip(':')
            # one title is missing whitespace around hyphen
            title = re.sub(r'(\S)-(\S)', r'\1 - \2', title)
            title = title.replace(u'\xa0', u' ')
            title = "El Dorado " + title

            # Parse address
            address = ""
            last_span = title_spans[-1].next_sibling
            while(last_span is not None):
                s = last_span.string
                if s is not None:
                    address += s
                last_span = last_span.next_sibling
            address = address.strip()

            if address == "":
                raise Exception("Could not parse location address")

            address +=", CA"

            location = Location(
                name = title,
                address = address,
                county = county.name,
                url = None
            )
            locations.append(location)

    return locations


if __name__ == "__main__":
    locations = run()
    print(locations)