from backend.rules.checker import (
    run_rule_checker
)


def verify_evidence(
    show_outputs: str
) -> dict:

    rule_results = run_rule_checker(
        show_outputs
    )

    return {
        "verified": (
            rule_results["failures"] == 0
        ),
        "rule_results": rule_results
    }