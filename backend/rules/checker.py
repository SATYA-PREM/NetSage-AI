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