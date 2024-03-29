import os
import re
from collections import namedtuple

agent_string = "Vaccinebot (+https://bitstream.io/vaccinebot)"
header_dict = {"user-agent": agent_string}  # for urllib3

Parser = namedtuple("Parser", ["name", "url"])
Location = namedtuple(
    "Location",
    [
        "name",
        "address",
        "county",
        "url",
        "reservation_url",
        "phone",
        "hours",
        "lat",
        "long",
        "zip",
        "org_name",
        "id",
        "provider_id",
    ],
    defaults=[None] * 12,
)


def add_state(address):
    """fix any addresses with missing state"""
    return re.sub(r", (9\d{4})$", r", CA \1", address.strip())

# Given a 9 digit zipcode, returns the first 5 digits
# Will be a no-op for 5 digit zips
def trim_zip_code(zip_code):
    zip_code = zip_code.strip()
    return zip_code.split("-")[0]

def validate(locations):
    for l in locations:
        if l.name is None or l.name.strip() == "":
            raise Exception("Could not parse name")
        if l.address is None or l.address.strip() == "":
            raise Exception(f"Could not parse address: {l.address}")
        if not re.search(r", CA 9\d{4}$", l.address):
            raise Exception(f"Couldn't parse zip code: {l.address}")
        if l.county is None or l.county.strip() == "":
            raise Exception(f"Could not parse county: {l.address}")


def debug_print(locations):
    for l in locations:
        for key in l._fields:
            print(f"{key:20} {getattr(l, key)}")
        print()
