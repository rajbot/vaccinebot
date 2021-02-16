import importlib
import logging
import pkgutil

import elgibility_parsers
from counties import counties


def verify_locations(db, name, info):

    for db_loc in db["content"]:
        if not db_loc.get("County", "").startswith(name):
            continue

        age = info["elgibility_age"]

        # look for overrides (eg kaiser, onemedical)
        system_name = db_loc["Name"].lower().split()[0]
        if system_name in info.get("overrides", []):
            age = info["overrides"][system_name]

        availability_str = f"Yes: vaccinating {age}+"

        has_vaccine = False
        for string in db_loc.get("Availability Info", []):
            if string.startswith("Yes: vaccinating"):
                has_vaccine = True

        if has_vaccine and availability_str not in db_loc.get("Availability Info", []):
            logging.error("\t---------------------")
            logging.error(
                f"\tWrong elgibility listed for {db_loc['Name']}({db_loc.get('Address', '')})"
            )
            logging.error(f"\tInfo in db: {db_loc['Availability Info']}")
            logging.error(f"\tShould include {availability_str}")
            logging.error(f"\tLocation id: {db_loc['id']}")


def run(db, county_filter):
    logging.info("Checking elgibility criteria")

    for modinfo in pkgutil.iter_modules(elgibility_parsers.__path__):
        county = counties[modinfo.name]
        m = importlib.import_module(f".{modinfo.name}", "elgibility_parsers")
        if county_filter and county.name.lower() != county_filter.lower():
            continue

        logging.info(f"Parsing elgibility criteria for {county.name} County")
        try:
            elgibility_age = m.run(county)
            logging.info(f"\tMinimium age is {elgibility_age}")
        except Exception as e:
            logging.error(
                f"\tElgibility parser for {county.name} County failed! Please fix this parser. Err: {e}"
            )
            continue

        verify_locations(db, county.name, elgibility_age)
