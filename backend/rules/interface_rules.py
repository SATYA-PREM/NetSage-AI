import re


def check_interfaces(symptom: str = "", context: str = "", command_output: str = ""):
    """
    Deterministic interface checks.
    """

    text = "\n".join([
        symptom or "",
        context or "",
        command_output or "",
    ])

    lower = text.lower()
    findings = []

    interface_down = re.search(
        r"(?:interface|link|port)(?:\s+\S+){0,4}\s+down\b",
        lower
    )

    if interface_down or any(x in lower for x in [
        "administratively down",
        "protocol down",
    ]):

        findings.append({
            "rule": "interface_down",
            "severity": "critical",
            "finding": "An interface appears to be down.",
            "evidence": "Supplied evidence contains interface-down indicators.",
            "recommendation": [
                "Run `show ip interface brief`.",
                "Verify physical link status.",
                "Verify the interface is not administratively shut down.",
            ],
        })

    if "err-disabled" in lower:
        findings.append({
            "rule": "err_disabled",
            "severity": "critical",
            "finding": "An interface appears to be err-disabled.",
            "evidence": "Command output contains `err-disabled`.",
            "recommendation": [
                "Identify the err-disable cause.",
                "Inspect switch logs.",
                "Do not automatically re-enable the interface.",
            ],
        })

    if "trunking" in lower:
        findings.append({
            "rule": "trunk_detected",
            "severity": "info",
            "finding": "A trunk interface was detected.",
            "evidence": "Command output indicates trunking.",
            "recommendation": [
                "Verify trunk encapsulation.",
                "Verify allowed VLANs.",
                "Verify both ends agree on trunk configuration.",
            ],
        })

    return findings