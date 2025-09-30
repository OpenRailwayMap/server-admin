#! /usr/bin/env python3

"""Check if Tirex is running and collect some stats.
"""

import argparse
from enum import Enum
import json
import subprocess
import sys


WARNING = 4000
CRITICAL = 20000
TIMEOUT = 10


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


def get_data(timeout):
    args = ["tirex-status", "--raw"]
    p = subprocess.run(args, capture_output=True, timeout=timeout, check=True)
    json_data = json.loads(p.stdout)
    return json_data


def format_measurement(k, v, warn=None, crit=None):
    if warn is not None and crit is not None:
        return "'{}'={};{};{}".format(k, v, warn, crit)
    return "'{}'={}".format(k, v)


def join_values(measurements, total_size, warn, crit):
    parts = [format_measurement("queue_length", total_size, warn, crit)]
    for m in measurements:
        parts.append(format_measurement(m[0], m[1]))
    return " ".join(parts)


def get_queue_sizes(data):
    buckets = data.get("rm", {}).get("buckets", {})
    prioqueues = data.get("queue", {}).get("prioqueues", {})
    if not buckets or not prioqueues:
        respond(ServiceStatus.UNKNOWN, "Failed to read list of buckets or priority queues from response of `tirex-status`")
    # Need to sort by both minprio and maxprio because otherwise the lowest bucket gets sorted before the highest bucket (the lowest has maxprio 0)
    buckets.sort(key=lambda b: (b.get("minprio"), b.get("maxprio")))
    for i in range(len(buckets)):
        buckets[i]["length"] = 0
    total_length = 0
    for q in prioqueues:
        for b in buckets:
            prio = q["prio"]
            if b["minprio"] <= prio and prio <= b["maxprio"]:
                size = q["size"]
                b["length"] += size
                total_length += size
    # Sort order of dictonaries is an implementation detail in Python. Thefore, we put values as tuples into a list.
    sizes = [(b["name"], b["length"]) for b in buckets]
    return sizes, total_length


parser = argparse.ArgumentParser(description="Monitoring plugin for Tirex queue length.")
parser.add_argument("-w", "--warning", type=int, default=WARNING, help="Warn if Tirex queue is larger than this value (default: {})".format(WARNING))
parser.add_argument("-c", "--critical", type=int, default=CRITICAL, help="Warn if Tirex queue is larger than this value (default: {})".format(CRITICAL))
parser.add_argument("-t", "--timeout", type=int, default=TIMEOUT, help="Timeout in seconds for calling tirex-status (default: {})".format(TIMEOUT))
args = parser.parse_args()

total_size = 0
queue_sizes = []
try:
    queue = get_data(args.timeout)
    queue_sizes, total_size = get_queue_sizes(queue)
except subprocess.TimeoutExpired as e:
    respond(ServiceStatus.UNKNOWN, "tirex-status failed due to timeout\nTimeout: {}s".format(e.timeout))
except subprocess.CalledProcessError as e:
    respond(ServiceStatus.UNKNOWN, "tirex-status returned failure\nReturn code: {}\nOutput:\n{}".format(e.returncode, e.output))
except Exception as e:
    respond(ServiceStatus.UNKNOWN, "Failed to parse JSON response by tirex-status\n{}".format(e))
if total_size is None:
    respond(ServiceStatus.UNKNOWN, "Failed to read total queue length from response by tirex-status")
values = join_values(queue_sizes, total_size, args.warning, args.critical)
if total_size > args.critical:
    respond(ServiceStatus.CRITICAL, "Tirex queue size is too long: {}".format(total_size), values)
elif total_size > args.warning:
    respond(ServiceStatus.WARNING, "Tirex queue size is too long: {}".format(total_size), values)
respond(ServiceStatus.OK, "Tirex queue size: {}".format(total_size), values)
