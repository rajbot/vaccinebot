#!/usr/bin/env python3

import importlib
import json
import logging
import pkgutil
import sys
import urllib.request

import location_parsers


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

logging.info("Downloading known locations")
with urllib.request.urlopen("https://api.vaccinateca.com/v1/locations.json") as response:
    db = json.load(response)

logging.info(f'loaded {len(db["content"])} locations')

if len(sys.argv) == 2:
    county = sys.argv[1]
    logging.info(f'Running crawl only for {county.title()} County')

# dynamically load each county module and parse location data
for modinfo in pkgutil.iter_modules(location_parsers.__path__):
    m = importlib.import_module(f'.{modinfo.name}', 'location_parsers')
    if m.county.name.lower() != county.lower():
        continue

    logging.info(f'Parsing {m.county.name} County')
    try:
        locations = m.run()
    except Exception as e:
        logging.error(f'\tParser for {m.county.name} County failed! Please fix this parser. Err: {e}')
        continue

    logging.info(f'\tParsed {len(locations)} locations')
    # check to see if these locations are already in the database
    num_found = 0
    for location in locations:
        found = False
        for db_loc in db["content"]:
            # match on address field, which should be sufficient
            if db_loc.get("Address", "").lower().startswith(location.address.lower()):
                found = True
                break
        if not found:
            logging.warning(f'\t{location.name}, {location.address} was not found in database! Please add it manually.')
        else:
            num_found += 1

    logging.info(f'\t{num_found} locations already in database')
