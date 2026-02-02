#!/usr/bin/env python3
"""
Compare admin vs mcp.syslog access to workflow-related tables
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

INSTANCE = os.getenv("SERVICENOW_INSTANCE")
MCP_USERNAME = os.getenv("SERVICENOW_USERNAME")
MCP_PASSWORD = os.getenv("SERVICENOW_PASSWORD")
ADMIN_USERNAME = os.getenv("SERVICENOW_ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("SERVICENOW_ADMIN_PASSWORD")

# Workflow-related tables to test
WORKFLOW_TABLES = [
    ("wf_context", "Workflow Context (classic workflows)"),
    ("wf_executing", "Currently Executing Workflows"),
    ("wf_history", "Workflow History"),
    ("wf_log", "Workflow Logs"),
    ("sys_trigger", "Triggered Events"),
]


def test_table(table_name, description, username, password, user_label):
    """Test access to a table"""
    url = f"{INSTANCE}/api/now/table/{table_name}"
    params = {
        "sysparm_limit": 5,
        "sysparm_display_value": "true",
    }

    try:
        response = requests.get(
            url,
            params=params,
            auth=(username, password),
            headers={"Accept": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            results = response.json().get("result", [])
            return {"status": "success", "count": len(results), "status_code": 200}
        else:
            return {
                "status": "error",
                "count": 0,
                "status_code": response.status_code,
                "error": response.text[:100],
            }
    except Exception as e:
        return {"status": "exception", "count": 0, "error": str(e)[:100]}


def main():
    print("\n" + "=" * 80)
    print("WORKFLOW TABLE ACCESS COMPARISON")
    print("=" * 80)
    print(f"\nInstance: {INSTANCE}")
    print(f"Admin User: {ADMIN_USERNAME}")
    print(f"MCP User: {MCP_USERNAME}")
    print("\n" + "=" * 80)

    results = []

    for table_name, description in WORKFLOW_TABLES:
        print(f"\nTesting: {table_name}")
        print(f"Description: {description}")
        print("-" * 80)

        # Test with admin
        admin_result = test_table(
            table_name, description, ADMIN_USERNAME, ADMIN_PASSWORD, "ADMIN"
        )
        print(f"  ADMIN:       ", end="")
        if admin_result["status"] == "success":
            print(f"✓ {admin_result['count']} records")
        else:
            print(
                f"✗ Status {admin_result.get('status_code', 'N/A')} - {admin_result.get('error', 'Unknown')}"
            )

        # Test with mcp.syslog
        mcp_result = test_table(
            table_name, description, MCP_USERNAME, MCP_PASSWORD, "MCP"
        )
        print(f"  MCP.SYSLOG:  ", end="")
        if mcp_result["status"] == "success":
            print(f"✓ {mcp_result['count']} records")
        else:
            print(
                f"✗ Status {mcp_result.get('status_code', 'N/A')} - {mcp_result.get('error', 'Unknown')}"
            )

        # Compare
        print(f"  COMPARISON:  ", end="")
        if admin_result["status"] == "success" and mcp_result["status"] == "success":
            if admin_result["count"] == mcp_result["count"]:
                print(f"✓ SAME ({admin_result['count']} records each)")
                status = "WORKING"
            else:
                print(
                    f"⚠ DIFFERENT (admin:{admin_result['count']} vs mcp:{mcp_result['count']})"
                )
                status = "PARTIAL"
        elif admin_result["status"] == "success" and mcp_result["status"] != "success":
            print(f"✗ BROKEN (admin works, mcp doesn't)")
            status = "BROKEN"
        elif admin_result["status"] != "success" and mcp_result["status"] != "success":
            print(f"✗ BOTH FAIL (no data or permission issue)")
            status = "NO_DATA"
        else:
            print(f"? UNKNOWN STATE")
            status = "UNKNOWN"

        results.append(
            {
                "table": table_name,
                "description": description,
                "admin_count": admin_result.get("count", 0),
                "mcp_count": mcp_result.get("count", 0),
                "status": status,
            }
        )

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    working = [r for r in results if r["status"] == "WORKING"]
    partial = [r for r in results if r["status"] == "PARTIAL"]
    broken = [r for r in results if r["status"] == "BROKEN"]
    no_data = [r for r in results if r["status"] == "NO_DATA"]

    print(f"\n✓ WORKING (same data for both users): {len(working)}")
    for r in working:
        print(f"    - {r['table']}: {r['mcp_count']} records")

    if partial:
        print(f"\n⚠ PARTIAL (different record counts): {len(partial)}")
        for r in partial:
            print(f"    - {r['table']}: admin={r['admin_count']}, mcp={r['mcp_count']}")

    if broken:
        print(f"\n✗ BROKEN (admin works, mcp doesn't): {len(broken)}")
        for r in broken:
            print(f"    - {r['table']}: admin={r['admin_count']}, mcp=0")

    if no_data:
        print(f"\n○ NO DATA (both users have no records): {len(no_data)}")
        for r in no_data:
            print(f"    - {r['table']}")

    print("\n" + "=" * 80)
    print("\nRecommendations:")
    print("-" * 80)

    if broken:
        print("\nBroken tables need ACL configuration:")
        for r in broken:
            print(f"  - {r['table']}: Add claude_mcp role to ACL")

    if partial:
        print(
            "\nPartial access tables may have admin_overrides or security constraints:"
        )
        for r in partial:
            print(f"  - {r['table']}: Review ACL for admin_overrides=true")

    if working:
        print("\nWorking tables are ready to use!")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
