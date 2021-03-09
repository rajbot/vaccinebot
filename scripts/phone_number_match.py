#!/usr/bin/env python3

import csv
import re
import os
import sys


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
            print("MATCH:")
            name = p['\ufeffName']
            print(f"{fields[2]:60} | {name:60}")
            print(f"{fields[3]:60} | {p['Address']:60}")
            print(f"{fields[1]:60} | {p['Location ID']:60}")
            print()