from collections import namedtuple
import ndjson
import os

Address = namedtuple(
    "Address",
    [
        "street1",
        "street2",
        "city",
        "state",
        "zip",
    ],
    defaults=[""] * 5,
)

ParentOrganization = namedtuple(
    "ParentOrganization",
    [
        "id",
        "name",
    ],
    defaults=[""] * 2,
)

# Format from:
# https://docs.google.com/document/d/1qxABDlRep76llrXhgwdwA6Ji3Jub-MftRvustk12XHc/edit#
OutputSchema = namedtuple(
    "OutputSchema",
    [
        "id",
        "name",
        "address",
        "location",
        "census",
        "contact",
        "booking",
        "languages",
        "open_dates",
        "hours",
        "availability",
        "inventory",
        "access",
        "parent_organization",
        "links",
        "notes",
        "active",
        "fetched_at",
        "published_at",
        "sources",
    ],
    defaults=["", "", {}, {}, {}, {}, [], [], [], {}, [], {}, {}, [], [], False, "", "", []], # Try and put the defaults in the correct type
)

# Expects a Location
# Returns an OutputSchema
def location_to_output_schema(location):
    o = OutputSchema(
        id = location.id,
        name = location.name,
        address = Address(
            street1 = location.address,
            zip = location.zip,
        )._asdict(), # so it gets outputted as a dict instead of a tuple, since calling ._asdict() on the parent namedtuple doesn't recursively do it
        parent_organization = ParentOrganization(
            id = location.provider_id,
        )._asdict(),
    )

    return o

# Outputs a list of Locations to data/ as ndjson
def output_ndjson(locations, file_name_prefix="vaccinebot"):
    schemas = []
    for loc in locations:
        schemas.append(location_to_output_schema(loc)._asdict())
    
    os.makedirs("data", exist_ok=True)

    with open(f"data/{file_name_prefix}.ndjson", "w") as f:
        ndjson.dump(schemas, f)
