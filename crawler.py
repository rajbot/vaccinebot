#!/usr/bin/env python3

import importlib
import json
import logging
import pkgutil
import urllib.request

import location_parsers


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

logging.info("Downloading known locations")
with urllib.request.urlopen("https://api.vaccinateca.com/v1/locations.json") as response:
    db = json.load(response)

logging.info(f'loaded {len(db["content"])} locations')


# dynamically load each county module and parse location data
for modinfo in pkgutil.iter_modules(location_parsers.__path__):
    m = importlib.import_module(f'.{modinfo.name}', 'location_parsers')
    logging.info(f'Parsing {m.county.name} County')
    locations = m.run()
    logging.info(f'\tFound {len(locations)} locations')

    # check to see if these locations are already in the database
    num_found = 0
    for location in locations:
        found = False
        for db_loc in db["content"]:
            # match on address field, which should be sufficient
            if location.address == db_loc.get("Address", ""):
                found = True
                break
        if not found:
            logging.warning(f'\t{location.name}, {location.address} was not found in database! Please add it manually.')
        else:
            num_found += 1

    logging.info(f'\t{num_found} locations already in database')
