"""Built-in Cisco troubleshooting cases used as the local RAG corpus."""

CASE_SEEDS = [
    ("Routing", "Layer 3", "show ip route", "Missing route to remote network", "PC reaches gateway but cannot reach a remote subnet.", "Destination network is absent from the routing table.", "Add and verify the appropriate route after human approval."),
    ("Routing", "Layer 3", "show ip route", "Missing default route", "Branch users cannot reach the Internet.", "No default route is present on the branch router.", "Configure the correct default route after review."),
    ("Routing", "Layer 3", "show ip ospf neighbor", "OSPF neighbor stuck in EXSTART", "OSPF adjacency never reaches FULL.", "An MTU mismatch prevents adjacency completion.", "Match MTU values on both interfaces."),
    ("VLAN", "Layer 2", "show vlan brief", "Access port on wrong VLAN", "A PC gets no DHCP address on a switch port.", "The access port is assigned to the wrong VLAN.", "Correct the access VLAN after human approval."),
    ("VLAN", "Layer 2", "show vlan brief", "VLAN missing from database", "One VLAN stops working after a switch reboot.", "The VLAN is absent from the VLAN database.", "Recreate or restore the VLAN after review."),
    ("Trunk", "Layer 2", "show interfaces trunk", "Required VLAN missing from trunk", "Only some VLANs cross the switch uplink.", "The required VLAN is not in the allowed list.", "Update the allowed VLAN list after review."),
    ("Trunk", "Layer 2", "show interfaces trunk", "Native VLAN mismatch", "CDP reports a native VLAN mismatch.", "Trunk ends use different native VLANs.", "Align the native VLAN on both ends."),
    ("DHCP", "Layer 3", "show ip dhcp binding", "Missing DHCP relay", "Clients in a remote VLAN receive no address.", "The client SVI has no helper address.", "Configure the correct DHCP relay after review."),
    ("DHCP", "Layer 3", "show ip dhcp pool", "DHCP scope exhausted", "New clients receive APIPA addresses.", "No free addresses remain in the DHCP pool.", "Expand or clean the pool after approval."),
    ("DNS", "Layer 7", "nslookup <host>", "Wrong client DNS server", "IP access works but hostnames do not resolve.", "The client DNS server is wrong or unreachable.", "Correct DNS assignment after review."),
    ("DNS", "Layer 7", "nslookup <host>", "DNS record missing", "One hostname fails while others resolve.", "The requested record is missing from the zone.", "Add or correct the record after approval."),
    ("ACL", "Layer 3/4", "show access-lists", "ACL blocks return traffic", "The client sends traffic but receives no replies.", "An ACL denies the return path or uses an implicit deny.", "Add the narrowly scoped permit after review."),
    ("ACL", "Layer 3/4", "show access-lists", "ACL applied in wrong direction", "An ACL blocks too much traffic or has no effect.", "The ACL direction does not match the intended interface path.", "Correct the direction after human approval."),
    ("NAT", "Layer 3", "show ip nat translations", "NAT inside/outside missing", "Internal hosts cannot reach external services.", "Interfaces are not marked inside and outside correctly.", "Correct NAT interface roles after review."),
    ("Gateway", "Layer 3", "show run interface", "Gateway outside client subnet", "A host cannot ARP for its default gateway.", "The gateway is outside the host subnet.", "Correct the gateway or mask after approval."),
    ("Gateway", "Layer 3", "show ip interface brief", "Gateway interface shutdown", "An entire LAN loses router connectivity.", "The router LAN interface is administratively down.", "Bring the interface up only after review."),
    ("Wireless", "Layer 1/2", "show wlan summary", "Guest isolation misconfigured", "Guest clients can reach internal servers.", "Guest-to-corporate isolation policy is missing or incorrect.", "Correct guest isolation after review."),
    ("Interface", "Layer 1", "show interfaces", "Interface administratively shutdown", "A connected link passes no traffic.", "The interface has shutdown configured.", "Restore the interface after human approval."),
    ("Interface", "Layer 1", "show interfaces", "Duplex mismatch", "A link is slow and reports CRC errors.", "The two ends negotiate different duplex settings.", "Align speed and duplex after review."),
    ("IP addressing", "Layer 3", "ipconfig /all", "Wrong host subnet mask", "Some local hosts cannot reach the gateway.", "The host mask excludes the intended local network.", "Correct the host addressing after approval."),
]


def build_cases(total=100):
    cases = []
    for index in range(total):
        category, layer, command, title, symptom, fault, solution = CASE_SEEDS[index % len(CASE_SEEDS)]
        variant = index // len(CASE_SEEDS)
        suffix = f" (variant {variant + 1})" if variant else ""
        cases.append({
            "case_id": f"TC-{index + 1:03d}",
            "title": title + suffix,
            "category": category,
            "osi_layer": layer,
            "severity": "High" if category in {"Routing", "ACL", "NAT", "Gateway"} else "Medium",
            "symptom": symptom,
            "expected_fault": fault,
            "evidence_command": command,
            "next_command": command,
            "solution": solution,
            "verification": f"Re-run `{command}` and verify the affected path.",
            "keywords": [category.lower(), layer.lower(), *title.lower().split()],
        })
    return cases


CASES = build_cases()
