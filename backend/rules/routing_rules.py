import re


def check_routing(symptom: str = "", context: str = "", command_output: str = ""):
    """
    Deterministic routing checks.
    Never changes network configuration.
    """

    text = "\n".join([
        symptom or "",
        context or "",
        command_output or "",
    ]).lower()

    findings = []

    # Default gateway / route problems
    if any(word in text for word in [
        "default gateway",
        "gateway unreachable",
        "cannot reach gateway",
        "gateway fails",
    ]):
        findings.append({
            "rule": "default_gateway_reachability",
            "severity": "high",
            "finding": "Default gateway reachability is failing.",
            "evidence": "Incident contains gateway reachability symptoms.",
            "recommendation": [
                "Verify the VLAN gateway interface is up.",
                "Verify the host is assigned to the expected VLAN.",
                "Verify the gateway IP and subnet mask.",
            ],
        })

    # Missing route
    if "show ip route" in text:
        if "default" in text and (
            "0.0.0.0" not in text and
            "gateway of last resort" not in text
        ):
            findings.append({
                "rule": "missing_default_route",
                "severity": "medium",
                "finding": "No clear default route was observed.",
                "evidence": "Routing output does not show an obvious default route.",
                "recommendation": [
                    "Run `show ip route`.",
                    "Verify the default route or gateway of last resort.",
                ],
            })

    # Static route / destination mismatch
    if "network unreachable" in text or "no route" in text:
        findings.append({
            "rule": "route_missing",
            "severity": "high",
            "finding": "The destination may not have a valid route.",
            "evidence": "Incident or command output indicates a routing failure.",
            "recommendation": [
                "Run `show ip route <destination>`.",
                "Verify next-hop reachability.",
                "Verify the routing protocol or static route configuration.",
            ],
        })

    return findings