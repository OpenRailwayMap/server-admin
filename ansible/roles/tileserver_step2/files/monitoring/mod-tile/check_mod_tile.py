#! /usr/bin/env python3

"""Check if mod-tile is enabled and collect some stats.
"""

import argparse
from enum import Enum
import urllib.request
import sys


class ServiceStatus(Enum):
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3


def respond(status, message, measurements):
    if not measurements:
        line = "{}: {}\n".format(status.name, message)
    else:
        line = "{}: {} | {}\n".format(status.name, message, measurements)
    print(line)
    sys.exit(status.value)


def get_url(url):
    user_agent = "check_mod_tile"
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(request) as response:
        return response.read().decode('iso-8859-1')


def parse_values(raw):
    rows = raw.split("\n")
    measurements = {}
    for row in rows:
        if len(row) == 0:
            continue
        parts = row.split(": ")
        if len(parts) != 2:
            respond(ServiceStatus.UNKNOWN, "Failed to parse row: {}".format(row))
        k = parts[0]
        v = None
        try:
            v = int(parts[1])
        except:
            respond(ServiceStatus.UNKNOWN, "Failed to parse value of {}".format(k))
        if k in measurements:
            respond(ServiceStatus.UNKNOWN, "Found measurement {} twice: {}: {}, {}: {}".format(parts[0]))
        measurements[k] = v
    return measurements


def join_values(measurements, keys):
    parts = []
    for key, unit in keys.items():
        if key in measurements:
            if unit is not None:
                parts.append("'{}'={}{}".format(key, measurements[key], unit))
            else:
                parts.append("'{}'={}".format(key, measurements[key]))
    return " ".join(parts)


parser = argparse.ArgumentParser(description="Monitoring plugin for mod-tile collecting some stats.")
parser.add_argument('-v', '--verbose', action='count', default=0)
args = parser.parse_args()

status = ServiceStatus.OK
data_url = 'http://localhost/mod_tile'
try:
    data = get_url(data_url)
except:
    respond(ServiceStatus.UNKNOWN, "Failed: HTTP GET {}".format(data_url))
values = parse_values(data)
selected_keys_and_units = {
    "NoResp200": None,
    "NoResp304": None,
    "NoResp404": None,
    "NoResp503": None,
    "NoResp5XX": None,
    "NoRespOther": None,
    "NoRespZoom00": None,
    "NoRespZoom01": None,
    "NoRespZoom02": None,
    "NoRespZoom03": None,
    "NoRespZoom04": None,
    "NoRespZoom05": None,
    "NoRespZoom06": None,
    "NoRespZoom07": None,
    "NoRespZoom08": None,
    "NoRespZoom09": None,
    "NoRespZoom10": None,
    "NoRespZoom11": None,
    "NoRespZoom12": None,
    "NoRespZoom13": None,
    "NoRespZoom14": None,
    "NoRespZoom15": None,
    "NoRespZoom16": None,
    "NoRespZoom17": None,
    "NoRespZoom18": None,
    "NoRespZoom19": None,
    "NoRespZoom20": None,
    "NoTileBufferReads": None,
    "DurationTileBufferReads": "us",
    "NoTileBufferReadZoom00": None,
    "DurationTileBufferReadZoom00": "us",
    "NoTileBufferReadZoom01": None,
    "DurationTileBufferReadZoom01": "us",
    "NoTileBufferReadZoom02": None,
    "DurationTileBufferReadZoom02": "us",
    "NoTileBufferReadZoom03": None,
    "DurationTileBufferReadZoom03": "us",
    "NoTileBufferReadZoom04": None,
    "DurationTileBufferReadZoom04": "us",
    "NoTileBufferReadZoom05": None,
    "DurationTileBufferReadZoom05": "us",
    "NoTileBufferReadZoom06": None,
    "DurationTileBufferReadZoom06": "us",
    "NoTileBufferReadZoom07": None,
    "DurationTileBufferReadZoom07": "us",
    "NoTileBufferReadZoom08": None,
    "DurationTileBufferReadZoom08": "us",
    "NoTileBufferReadZoom09": None,
    "DurationTileBufferReadZoom09": "us",
    "NoTileBufferReadZoom10": None,
    "DurationTileBufferReadZoom10": "us",
    "NoTileBufferReadZoom11": None,
    "DurationTileBufferReadZoom11": "us",
    "NoTileBufferReadZoom12": None,
    "DurationTileBufferReadZoom12": "us",
    "NoTileBufferReadZoom13": None,
    "DurationTileBufferReadZoom13": "us",
    "NoTileBufferReadZoom14": None,
    "DurationTileBufferReadZoom14": "us",
    "NoTileBufferReadZoom15": None,
    "DurationTileBufferReadZoom15": "us",
    "NoTileBufferReadZoom16": None,
    "DurationTileBufferReadZoom16": "us",
    "NoTileBufferReadZoom17": None,
    "DurationTileBufferReadZoom17": "us",
    "NoTileBufferReadZoom18": None,
    "DurationTileBufferReadZoom18": "us",
    "NoTileBufferReadZoom19": None,
    "DurationTileBufferReadZoom19": "us",
    "NoTileBufferReadZoom20": None,
    "DurationTileBufferReadZoom20": "us",
}
respond(ServiceStatus.OK, "working", join_values(values, selected_keys_and_units))
