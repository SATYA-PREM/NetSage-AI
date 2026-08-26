import re


def check_vlans(symptom: str = "", context: str = "", command_output: str = ""):
    """
    Deterministic VLAN checks.
    """

    text = "\n".join([
        symptom or "",
        context or "",
        command_output or "",
    ])

    lower = text.lower()
    findings = []

    # VLAN explicitly mentioned
    vlan_numbers = re.findall(r"\bvlan\s*(\d+)\b", lower)

    if vlan_numbers:
        vlan = vlan_numbers[0]

        findings.append({
            "rule": "vlan_present",
            "severity": "info",
            "finding": f"Incident contains VLAN {vlan} information.",
            "evidence": f"VLAN {vlan} was detected in supplied evidence.",
            "recommendation": [
                f"Verify VLAN {vlan} exists.",
                f"Verify the affected access ports belong to VLAN {vlan}.",
                f"Verify VLAN {vlan} is permitted across required trunks.",
            ],
        })

    # Trunk allowed VLAN detection
    if "allowed on trunk" in lower or "allowed vlan" in lower:

        allowed_match = re.search(
            r"(?:allowed\s+(?:on\s+)?trunk|allowed\s+vlan).*?([\d,\s]+)",
            lower,
            re.IGNORECASE
        )

        if allowed_match:
            allowed = allowed_match.group(1).strip()

            findings.append({
                "rule": "trunk_allowed_vlan",
                "severity": "medium",
                "finding": "Trunk VLAN membership should be verified.",
                "evidence": f"Observed allowed VLAN information: {allowed}",
                "recommendation": [
                    "Verify the affected VLAN is allowed on the trunk.",
                    "Run `show interfaces trunk`.",
                    "Compare allowed VLANs on both ends of the trunk.",
                ],
            })

    # VLAN connectivity symptoms
    if any(word in lower for word in [
        "vlan connectivity",
        "vlan connectivity failure",
        "cannot reach gateway",
        "unable to reach gateway",
    ]):

        findings.append({
            "rule": "vlan_gateway_failure",
            "severity": "high",
            "finding": "VLAN gateway connectivity is failing.",
            "evidence": "The incident indicates hosts cannot reach their gateway.",
            "recommendation": [
                "Verify VLAN membership.",
                "Verify trunk VLAN allowance.",
                "Verify the gateway SVI is operational.",
                "Verify host IP addressing.",
            ],
        })

    return findings