#!/usr/bin/env python

from airtable import Airtable
import csv
import os

for var in ["AIRTABLE_API_KEY", "AIRTABLE_BASE_ID"]:
    if os.environ.get(var) is None:
        sys.exit(f"Must set {var} env var!")

api_key = os.environ.get("AIRTABLE_API_KEY")
base_id = os.environ.get("AIRTABLE_BASE_ID")

airtable = Airtable(base_id, "Locations", api_key)

path = sys.argv[1]
with open(path) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print("adding", row)
        fields = {"vaccinefinder_location_id": row["vaccinefinder_id"]}
        airtable.update(row["id"], fields)
