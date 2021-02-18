#!/usr/bin/env python3

import locations
import argparse
import importlib
import json
import logging
import os
import pkgutil
import sys
import urllib.request

import location_parsers

parser = argparse.ArgumentParser(description="VaccinateCA crawler.")
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument(
    "-c", "--county", nargs=1, help="Run crawler only for the specified county"
)
parser.add_argument(
    "--add-records", action="store_true", help="Add new locations found to Airtable"
)
parser.add_argument(
    "--print-tsv", action="store_true", help="Print fuzzy matches in TSV format"
)
args = parser.parse_args()

level = logging.INFO
if args.verbose:
    level = logging.INFO


logging.basicConfig(
    level=level,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)

county = None
if args.county is not None:
    county = args.county[0]
    logging.info(f"Running crawl only for {county.title()} County")

if args.add_records:
    locations.validate_env_vars()


logging.info("Downloading known locations")
with urllib.request.urlopen(
    "https://api.vaccinateca.com/v1/locations.json"
) as response:
    db = json.load(response)

logging.info(f'loaded {len(db["content"])} locations')

# add canonicalized address to db dict
locations.cannonicalize_db(db)


# dynamically load each county module and parse location data
for modinfo in pkgutil.iter_modules(location_parsers.__path__):
    m = importlib.import_module(f".{modinfo.name}", "location_parsers")
    if county and m.county.name.lower() != county.lower():
        continue

    logging.info(f"Parsing {m.county.name} County")
    try:
        locs = m.run()
    except Exception as e:
        logging.error(
            f"\tParser for {m.county.name} County failed! Please fix this parser. Err: {e}"
        )
        continue

    logging.info(f"\tParsed {len(locs)} locations")

    # check to see if these locations are already in the database
    num_found = 0
    for location in locs:
        found, match_id = locations.in_db(location, db)

        if found:
            num_found += 1

        if args.print_tsv:
            locations.print_fuzzy_tsv(location, db["content"], match_id)
        elif not found:
            if args.add_records:
                locations.print_fuzzy_matches(location, db["content"])
                response = input("Add this record to Airtable? (y/n):")
                if response == "y":
                    locations.airtable_insert(location)
            else:
                logging.warning(
                    f"\t{location.name}, {location.address} was not found in database! Please add it manually."
                )

    logging.info(f"\t{num_found} locations already in database")
