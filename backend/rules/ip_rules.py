import ipaddress
import re


def check_ip(symptom: str = "", context: str = "", command_output: str = ""):
    """
    Deterministic IP addressing checks.
    """

    text = "\n".join([
        symptom or "",
        context or "",
        command_output or "",
    ])

    lower = text.lower()
    findings = []

    ips = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        text
    )

    valid_ips = []

    for ip in ips:
        try:
            ipaddress.ip_address(ip)
            valid_ips.append(ip)
        except ValueError:
            pass

    if valid_ips:
        findings.append({
            "rule": "ip_addresses_detected",
            "severity": "info",
            "finding": "IP addressing information was detected.",
            "evidence": ", ".join(dict.fromkeys(valid_ips)),
            "recommendation": [
                "Verify the host IP, subnet mask and default gateway.",
                "Check for duplicate or incorrect addressing.",
            ],
        })

    if "wrong subnet" in lower or "incorrect subnet" in lower:
        findings.append({
            "rule": "subnet_mismatch",
            "severity": "high",
            "finding": "Possible subnet mismatch detected.",
            "evidence": "Supplied incident information indicates an addressing mismatch.",
            "recommendation": [
                "Verify the host subnet mask.",
                "Verify the gateway belongs to the same subnet.",
            ],
        })

    if "duplicate ip" in lower or "ip conflict" in lower:
        findings.append({
            "rule": "duplicate_ip",
            "severity": "critical",
            "finding": "Possible duplicate IP address detected.",
            "evidence": "Incident contains duplicate-IP indicators.",
            "recommendation": [
                "Check ARP tables.",
                "Identify the device using the conflicting address.",
                "Correct the duplicate address assignment.",
            ],
        })

    return findings