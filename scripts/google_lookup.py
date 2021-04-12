#!/usr/bin/env python3

# google_lookup.py performs lookups against the Google Places
# API.ArithmeticError(
#
# Usage: google_lookup.py <place> google_lookup.py < input.txt input.txt should
#   have one line per input.
#
#   You must set the GOOGLE_API_KEY to the Google API token you want to use.  It
#   must be from a project that has the Places API enabled:
#   https://console.cloud.google.com/marketplace/product/google/places-backend.googleapis.com?
#
# Output is tab seperated data (for easy pasting into Google Sheets.)
#
# This script uses percache to cache API results.  This means you can run it
# over and over on the same data and not run up the Google bill.   Cached data
# is stored in `places.percache` in the current directory.

import os
import csv
import logging
import json
import urllib
import sys

import percache
import googlemaps

cache = percache.Cache("places.percache")

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logging.fatal("GOOGLE_API_KEY not set.")
gmaps = googlemaps.Client(key=api_key)


@cache
def get_google_place(address):
    fields = ["business_status", "formatted_address", "name",
              "permanently_closed", "place_id"]
    return gmaps.find_place(address, "textquery", fields=fields)

# Clean a string to make it safe for use in TSV output.


def clean(a):
    return a.replace("\t", " ").replace("\n", " ")


def output(input, can, error):
    out = []
    if can:
        out = [
            input,
            can['place_id'],
            can['name'],
            can['formatted_address'],
            json.dumps(can),
        ]
    else:
        out = [
            input,
            "",
            "",
            "",
            "# " + error,
        ]
    out = [clean(x) for x in out]
    print("\t".join(out))

addrs = []
if sys.stdin.isatty() and len(sys.argv) > 1: 
    addrs = [" ".join(sys.argv[1:])]
else:
    addrs = sys.stdin.readlines()

for a in addrs:
    p = get_google_place(a)
    if len(p['candidates']) == 0:
        output(a, None, "No Google Place candidates found")
        continue

    if len(p['candidates']) > 1:
        output(a, None, "Multiple Google Place candidates found")
        continue

    can = p['candidates'][0]
    output(a, p['candidates'][0], None)
