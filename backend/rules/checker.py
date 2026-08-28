from backend.rules.ip_rules import check_ip
from backend.rules.vlan_rules import check_vlans
from backend.rules.routing_rules import check_routing
from backend.rules.interface_rules import check_interfaces


def run_all_checks(
    symptom: str = "",
    context: str = "",
    command_output: str = "",
):
    """
    Execute all deterministic network checks.

    The rule engine runs BEFORE Gemini.
    Gemini receives these findings as evidence.
    """

    all_findings = []

    rule_functions = [
        ("ip", check_ip),
        ("vlan", check_vlans),
        ("routing", check_routing),
        ("interface", check_interfaces),
    ]

    for category, rule_function in rule_functions:

        try:
            findings = rule_function(
                symptom=symptom,
                context=context,
                command_output=command_output,
            )

            if findings:
                for finding in findings:
                    finding["category"] = category
                    all_findings.append(finding)

        except Exception as exc:
            all_findings.append({
                "category": category,
                "rule": "rule_execution_error",
                "severity": "error",
                "finding": f"{category} rule execution failed.",
                "evidence": str(exc),
                "recommendation": [],
            })

    # Highest severity first
    severity_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
        "info": 4,
        "error": 5,
    }

    all_findings.sort(
        key=lambda item: severity_order.get(
            item.get("severity", "info"),
            99
        )
    )

    return all_findings


# ============================================================
# DEMO / TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("NetSage AI - Deterministic Rule Checker")
    print("=" * 70)

    symptom = """
    PC gets an IP address but cannot reach the server.
    The server is located in VLAN 30.
    """

    context = """
    PC -> SW1 -> R1 -> Server
    """

    command_output = """
    show ip interface brief
    G0/0  192.168.30.1  up  up

    show ip route
    C 192.168.30.0/24 is directly connected
    """

    print("\n[INPUT]")
    print("-" * 70)
    print("Symptom:")
    print(symptom.strip())

    print("\nTopology:")
    print(context.strip())

    print("\nCommand Output:")
    print(command_output.strip())

    print("\n[RUNNING RULES]")
    print("-" * 70)

    findings = run_all_checks(
        symptom=symptom,
        context=context,
        command_output=command_output,
    )

    if not findings:
        print("No deterministic rule findings detected.")

    else:

        for index, finding in enumerate(findings, start=1):

            print(f"\nFinding #{index}")
            print("-" * 50)

            print(
                f"Category      : "
                f"{finding.get('category', 'unknown')}"
            )

            print(
                f"Rule          : "
                f"{finding.get('rule', 'unknown')}"
            )

            print(
                f"Severity      : "
                f"{finding.get('severity', 'unknown')}"
            )

            print(
                f"Finding       : "
                f"{finding.get('finding', 'unknown')}"
            )

            print(
                f"Evidence      : "
                f"{finding.get('evidence', 'N/A')}"
            )

            recommendations = finding.get(
                "recommendation",
                []
            )

            if recommendations:

                print("Recommendation:")

                for recommendation in recommendations:
                    print(f"  - {recommendation}")

    print("\n" + "=" * 70)
    print("RULE CHECK COMPLETE")
    print("=" * 70)