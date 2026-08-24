import ipaddress
import re
from collections import Counter

IP_PATTERN = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?(?![\d/])")
VLAN_PATTERN = re.compile(r"\b(?:vlan|vlan id)\s*(\d{1,4})\b", re.I)


def extract_network_data(text):
    addresses = [match.group(0) for match in IP_PATTERN.finditer(text)]
    interfaces = re.findall(r"\b(?:GigabitEthernet|FastEthernet|Ethernet|Serial)\S*", text, re.I)
    return {"ip_addresses": addresses, "interfaces": interfaces}


def check_ip_address(value):
    try:
        ipaddress.ip_interface(value)
        return None
    except ValueError:
        return {"type": "invalid_ip", "status": "FAIL", "evidence": f"Invalid IP address or interface: {value}"}


def check_gateway_in_subnet(text):
    interfaces = IP_PATTERN.findall(text)
    cidr = next((value for value in interfaces if "/" in value), None)
    gateway_match = re.search(r"(?:default gateway|gateway)\s*[:=]?\s*(\d{1,3}(?:\.\d{1,3}){3})", text, re.I)
    if not cidr or not gateway_match:
        return None
    try:
        network = ipaddress.ip_interface(cidr).network
        gateway = ipaddress.ip_address(gateway_match.group(1))
        if gateway not in network:
            return {"type": "gateway_mismatch", "status": "FAIL", "evidence": f"Gateway {gateway} is outside subnet {network}"}
    except ValueError:
        return None
    return {"type": "gateway_check", "status": "PASS", "evidence": f"Gateway {gateway_match.group(1)} is inside subnet {network}"}


def check_duplicate_ips(text):
    addresses = [value.split("/")[0] for value in IP_PATTERN.findall(text)]
    duplicate = [address for address, count in Counter(addresses).items() if count > 1]
    if duplicate:
        return {"type": "duplicate_ip", "status": "FAIL", "evidence": f"Duplicate IP address detected: {', '.join(duplicate)}"}
    return None


def check_interface_status(text):
    if re.search(r"(?:administratively down|interface .* shutdown|\bshutdown\b)", text, re.I):
        return {"type": "interface_status", "status": "FAIL", "evidence": "An interface is reported as shutdown or administratively down."}
    return None


def check_vlan(text):
    vlan_ids = [int(value) for value in VLAN_PATTERN.findall(text)]
    invalid = [value for value in vlan_ids if value < 1 or value > 4094]
    if invalid:
        return {"type": "vlan", "status": "FAIL", "evidence": f"Invalid VLAN ID: {invalid[0]}"}
    if re.search(r"vlan\s+\d+", text, re.I) and re.search(r"not found|missing|does not exist", text, re.I):
        return {"type": "vlan_missing", "status": "FAIL", "evidence": "The supplied output indicates a referenced VLAN is missing."}
    return None


def check_route(text):
    if re.search(r"(?:no route|network unreachable|destination host unreachable)", text, re.I):
        return {"type": "route", "status": "FAIL", "evidence": "The supplied output reports unreachable routing or a missing route."}
    return None


def run_checks(text):
    checks = []
    for address in extract_network_data(text)["ip_addresses"]:
        invalid = check_ip_address(address)
        if invalid:
            checks.append(invalid)
    for check in (check_gateway_in_subnet(text), check_duplicate_ips(text), check_interface_status(text), check_vlan(text), check_route(text)):
        if check:
            checks.append(check)
    return {"checks": checks}
