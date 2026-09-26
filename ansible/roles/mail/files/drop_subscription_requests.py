#! /usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
import requests
import sys
import configparser


user_agent = "drop_subscription_requests"

parser = argparse.ArgumentParser(description="Drop all subscription requests of a Mailman3 mailing list. To be run on the same host as Mailman is running on.")
parser.add_argument("-c", "--config", type=str, default="/etc/mailman3/mailman.cfg", help="Mailman configuration file")
parser.add_argument("-l", "--list", type=str, default="mailman3-sandbox.openrailwaymap.org", help="Mailing list")
parser.add_argument("-p", "--port", type=int, default=8001, help="port the REST API listens to")
args = parser.parse_args()

api_path = "/lists/mailman3-sandbox.openrailwaymap.org/requests"

# Read configuration file for username, password and API version
config = configparser.ConfigParser()
config.read(args.config)
try:
    username = config["webservice"]["admin_user"]
    password = config["webservice"]["admin_pass"]
    version = config["webservice"]["api_version"]
except KeyError as e:
    sys.stderr.write("ERROR: Could not parse configuration file at {}\nFailed to read key: {}\n".format(args.config, e))
    sys.exit(1)

url = "http://127.0.0.1:{}/{}{}".format(args.port, version, api_path)
auth = (username, password)
r = requests.get(url, auth=auth, headers={"User-agent": user_agent})
if r.status_code < 200 or r.status_code >= 300:
    sys.stderr.write("ERROR: {} HTTP {}\n".format(url, r.status_code))
    sys.exit(1)
entries = r.json().get("entries", [])
for entry in entries:
    data = {"action": "discard"}
    remove_url = url + "/{}".format(entry["token"])
    r = requests.post(remove_url, json=data, auth=auth)
    if r.status_code != 204:
        sys.stderr.write("ERROR: {} HTTP {}\n".format(remove_url, r.status_code))
        sys.exit(1)
    sys.stderr.write("Removed subscription requests for {}\n".format(entry["email"]))
