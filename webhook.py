import json
import os
import urllib3


def notify(place_name, name, address, fuzzy_matches):
    http = urllib3.PoolManager()
    url = os.environ["WEBHOOK_NOTIFY_URL"]

    data = {
        "username": "VaccineBot",
        "content": f"New Site Found in {place_name}!",
        "embeds": [{"title": name, "description": address}],
    }

    for i, m in enumerate(fuzzy_matches):
        loc = {
            "title": f"Possible match #{i+1}",
            "description": f"{m['Name']}, {m['Address']}",
        }
        data["embeds"].append(loc)

    encoded_data = json.dumps(data).encode("utf-8")

    r = http.request(
        "POST", url, body=encoded_data, headers={"Content-Type": "application/json"}
    )


def notify_broken(place_name):
    http = urllib3.PoolManager()
    url = os.environ["WEBHOOK_NOTIFY_URL"]

    data = {
        "username": "VaccineBot",
        "content": f"The parser for {place_name} is broken! Please fix it.",
    }

    encoded_data = json.dumps(data).encode("utf-8")

    r = http.request(
        "POST", url, body=encoded_data, headers={"Content-Type": "application/json"}
    )
