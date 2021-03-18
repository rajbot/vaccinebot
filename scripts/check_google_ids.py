#!/usr/bin/env python3

import csv
import json
import os
import sys
import urllib3


url = "https://api.vaccinateca.com/v1/locations.json"
http = urllib3.PoolManager()
r = http.request("GET", url)
db = json.loads(r.data.decode("utf-8"))

print(f'loaded {len(db["content"])} locations from vaccinateca')

place_ids = {}
for row in db["content"]:
    vacca_id = row["id"]
    place_id = row.get("google_places_id")
    if place_id is not None:
        place_ids[place_id] = vacca_id

path = sys.argv[1]
with open(path) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        place_id = row['google_place_id']
        vacca_id = place_ids.get(place_id)
        if vacca_id is not None:
            print("Match:", place_id, "\n", vacca_id, "\n", row, "\n\n")

