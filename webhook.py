import json
import os
import urllib3


def notify(county, name, address):
    http = urllib3.PoolManager()
    url = os.environ["WEBHOOK_NOTIFY_URL"]

    data = {
        "username": "VaccineBot",
        "content": f"New Site Found in {county} county!",
        "embeds": [{"title": name, "description": address}],
    }

    encoded_data = json.dumps(data).encode("utf-8")

    r = http.request(
        "POST", url, body=encoded_data, headers={"Content-Type": "application/json"}
    )
