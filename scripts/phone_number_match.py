#!/usr/bin/env python3

# usage: ./phone_number_match.py  Airtable_Locations.csv fuzzy-match.tsv

from airtable import Airtable
import csv
import re
import os
import sys

for var in ["AIRTABLE_API_KEY", "AIRTABLE_BASE_ID"]:
    if os.environ.get(var) is None:
        sys.exit(f"Must set {var} env var!")

api_key = os.environ.get("AIRTABLE_API_KEY")
base_id = os.environ.get("AIRTABLE_BASE_ID")
airtable = Airtable(base_id, "Locations", api_key)

phone_map = {}

path = sys.argv[1]
with open(path) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        phone = row['Phone number']
        phone = re.sub(r'[^\d]', '', phone)
        phone_map[phone] = row


#print(phone_map)

path = sys.argv[2]
with open(path) as fh:
    for line in fh.readlines():
        fields = line.split('\t')
        phone = fields[5]
        phone = re.sub(r'[^\d]', '', phone)

        if phone in phone_map:
            p = phone_map[phone]
            print(f"MATCH: {fields[5]}")
            name = p['\ufeffName']
            print(f"{fields[2]:60} | {name:60}")
            print(f"{fields[3]:60} | {p['Address']:60}")
            print(f"{fields[1]:60} | {p['Location ID']:60}")
            print()

            response = input("Add this vaccinefinder id to Airtable? (y/n):")
            if response == "y":
                print("adding")
                updates = {"vaccinefinder_location_id": fields[1]}
                airtable.update(p['Location ID'], updates)
