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
import webhook

import location_parsers

parser = argparse.ArgumentParser(description="VaccinateCA crawler.")
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument(
    "-c", "--county", nargs=1, help="Run crawler only for the specified county"
)
parser.add_argument("-s", "--state-parser", nargs=1, help="Run a state-wide parser")
parser.add_argument(
    "--add-records", action="store_true", help="Add new locations found to Airtable"
)
parser.add_argument(
    "--update-external-ids", action="store_true", help="Add new external identifiers to Airtable"
)
parser.add_argument(
    "--print-tsv", action="store_true", help="Print results in TSV format"
)
parser.add_argument(
    "--webhook-notify",
    action="store_true",
    help="Notify via webhook if new locations are found",
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
state_parser = None
if args.state_parser is not None:
    state_parser = args.state_parser[0]
    logging.info(f"Running state parser for {state_parser}")
elif args.county is not None:
    county = args.county[0]
    logging.info(f"Running crawl only for {county.title()} County")

if args.add_records:
    locations.validate_env_vars()

if args.webhook_notify:
    if os.environ.get("WEBHOOK_NOTIFY_URL") is None:
        sys.exit("Must set WEBHOOK_NOTIFY_URL env var")


logging.info("Downloading known locations from vaccinateca")
with urllib.request.urlopen(
    "https://api.vaccinateca.com/v1/locations.json"
) as response:
    db = json.load(response)

logging.info(f'loaded {len(db["content"])} locations from vaccinateca')

# add canonicalized address to db dict
locations.cannonicalize_db(db)


if state_parser is not None:
    m = importlib.import_module(f".{state_parser}", "state_parsers")
    place_name = f"{m.parser.name}"
    locs = m.run()
    logging.info(f"\tParsed {len(locs)} locations from {state_parser}")
    locations.find_matches(locs, db, args, place_name)
    sys.exit(0)


# dynamically load each county module and parse location data
for modinfo in pkgutil.iter_modules(location_parsers.__path__):
    m = importlib.import_module(f".{modinfo.name}", "location_parsers")
    if county and m.county.name.lower() != county.lower():
        continue

    place_name = f"{m.county.name} County"
    logging.info(f"Parsing {place_name}")
    try:
        locs = m.run()
    except Exception as e:
        logging.error(
            f"\tParser for {place_name} failed! Please fix this parser. Err: {e}"
        )
        if args.webhook_notify:
            webhook.notify_broken(place_name)
        continue

    logging.info(f"\tParsed {len(locs)} locations")

    locations.find_matches(locs, db, args, place_name)
