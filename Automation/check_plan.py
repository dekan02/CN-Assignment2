import ipaddress
import sys
from itertools import combinations
from pathlib import Path

import yaml

PLAN = Path(__file__).resolve().parent / "ip-plan.yml"


def load(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def find_overlaps(entries, key):
    problems = []
    parsed = [(item, ipaddress.ip_network(item[key])) for item in entries if item.get(key)]
    for (a, net_a), (b, net_b) in combinations(parsed, 2):
        if net_a.version == net_b.version and net_a.overlaps(net_b):
            problems.append(f"{key} overlap: {a['name']} {net_a} and {b['name']} {net_b}")
    return problems


def check_gateways(entries):
    problems = []
    for item in entries:
        gateway = item.get("gateway")
        if not gateway:
            continue
        net = ipaddress.ip_network(item["cidr"])
        address = ipaddress.ip_address(gateway)
        if address not in net or address in (net.network_address, net.broadcast_address):
            problems.append(f"gateway {gateway} is not a usable host of {net} ({item['name']})")
    return problems


def check_ipv6(plan):
    problems = []
    prefixes = {site: ipaddress.ip_network(value) for site, value in plan["ipv6_site_prefixes"].items()}
    for item in plan["subnets"]:
        value = item.get("ipv6")
        if not value:
            continue
        net = ipaddress.ip_network(value)
        site_net = prefixes.get(item["site"])
        if site_net is None or not net.subnet_of(site_net):
            problems.append(f"ipv6 {net} is outside the site prefix of {item['site']}")
        if net.prefixlen != 64:
            problems.append(f"ipv6 {net} is not a /64")
    return problems


def check_capacity(entries, needs):
    problems = []
    for item in entries:
        need = needs.get((item["site"], item["name"]))
        if not need:
            continue
        capacity = ipaddress.ip_network(item["cidr"]).num_addresses - 2
        if capacity < need:
            problems.append(f"{item['site']} {item['name']} holds {capacity} hosts, needs {need}")
    return problems


def main():
    plan = load(PLAN)
    entries = plan["subnets"]
    vlans = [item for item in entries if item["kind"] == "vlan"]
    problems = []
    problems += find_overlaps(entries, "cidr")
    problems += find_overlaps(vlans, "ipv6")
    problems += check_gateways(entries)
    problems += check_ipv6(plan)
    problems += check_capacity(entries, {("HCM", "Staff A"): 1000, ("HCM", "Staff B"): 1000, ("HN", "RD A"): 750, ("HN", "RD B"): 750, ("DN", "IoT"): 500, ("DN", "Staff"): 250})
    summary = f"{len(entries)} subnets checked"
    if problems:
        print(summary)
        for line in problems:
            print("FAIL", line)
        return 1
    print(summary + ", no problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
