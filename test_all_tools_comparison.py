#!/usr/bin/env python3
"""
Comprehensive test comparing admin vs mcp.syslog access to all 9 tools
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

# All 11 tools to test
TOOLS = [
    ("syslog", "Application Logs"),
    ("sn_aia_execution_plan", "AI Execution Plans"),
    ("sys_generative_ai_metric", "GenAI Metrics"),
    ("sys_gen_ai_log_metadata", "GenAI Metadata"),
    ("sys_rest_message", "REST Messages"),
    ("wf_context", "Workflow Context"),
    ("wf_executing", "Currently Executing Workflows"),
    ("wf_history", "Workflow History"),
    ("wf_log", "Workflow Logs"),
    ("incident", "Incidents (for AI context)"),
    ("change_request", "Change Requests (for AI ROI)"),
]


def test_table(table_name, username, password, user_label):
    """Test access to a table"""
    url = f"{INSTANCE}/api/now/table/{table_name}"
    params = {
        "sysparm_limit": 10,
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
        elif response.status_code == 403:
            return {
                "status": "forbidden",
                "count": 0,
                "status_code": 403,
                "error": "Permission denied",
            }
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
    print("COMPREHENSIVE ACCESS COMPARISON: ADMIN vs MCP.SYSLOG")
    print("=" * 80)
    print(f"\nInstance: {INSTANCE}")
    print(f"Admin User: {ADMIN_USERNAME}")
    print(f"MCP User: {MCP_USERNAME}")
    print("\n" + "=" * 80)

    results = []

    for table_name, description in TOOLS:
        print(f"\n{'=' * 80}")
        print(f"Testing: {table_name}")
        print(f"Description: {description}")
        print("-" * 80)

        # Test with admin
        admin_result = test_table(table_name, ADMIN_USERNAME, ADMIN_PASSWORD, "ADMIN")
        print(f"  ADMIN:       ", end="")
        if admin_result["status"] == "success":
            print(f"✓ {admin_result['count']} records")
        else:
            print(
                f"✗ Status {admin_result.get('status_code', 'N/A')} - {admin_result.get('error', 'Unknown')}"
            )

        # Test with mcp.syslog
        mcp_result = test_table(table_name, MCP_USERNAME, MCP_PASSWORD, "MCP")
        print(f"  MCP.SYSLOG:  ", end="")
        if mcp_result["status"] == "success":
            print(f"✓ {mcp_result['count']} records")
        else:
            print(
                f"✗ Status {mcp_result.get('status_code', 'N/A')} - {mcp_result.get('error', 'Unknown')}"
            )

        # Compare and analyze
        print(f"  COMPARISON:  ", end="")
        if admin_result["status"] == "success" and mcp_result["status"] == "success":
            if admin_result["count"] == mcp_result["count"]:
                if admin_result["count"] == 0:
                    print(f"○ BOTH EMPTY (no data in table)")
                    status = "NO_DATA"
                else:
                    print(f"✓ SAME ({admin_result['count']} records each)")
                    status = "WORKING"
            else:
                print(
                    f"⚠ DIFFERENT (admin:{admin_result['count']} vs mcp:{mcp_result['count']})"
                )
                print(
                    f"  WARNING:     Possible admin_overrides or security constraint issue!"
                )
                status = "PARTIAL"
        elif admin_result["status"] == "success" and mcp_result["status"] != "success":
            print(f"✗ BROKEN (admin works, mcp doesn't)")
            print(f"  ERROR:       {mcp_result.get('error', 'Unknown')}")
            status = "BROKEN"
        elif admin_result["status"] != "success" and mcp_result["status"] != "success":
            print(f"✗ BOTH FAIL (permission or connectivity issue)")
            status = "BOTH_FAIL"
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
    no_data = [r for r in results if r["status"] == "NO_DATA"]
    partial = [r for r in results if r["status"] == "PARTIAL"]
    broken = [r for r in results if r["status"] == "BROKEN"]

    print(f"\n✓ WORKING (same non-zero data): {len(working)}")
    for r in working:
        print(f"    - {r['table']}: {r['mcp_count']} records")

    if no_data:
        print(f"\n○ NO DATA (both users see 0 records): {len(no_data)}")
        for r in no_data:
            print(f"    - {r['table']}: Normal if table hasn't been used yet")

    if partial:
        print(f"\n⚠ PARTIAL ACCESS (different counts): {len(partial)}")
        for r in partial:
            print(f"    - {r['table']}: admin={r['admin_count']}, mcp={r['mcp_count']}")
            print(f"      ACTION: Check ACL for admin_overrides=true")

    if broken:
        print(f"\n✗ BROKEN (admin works, mcp doesn't): {len(broken)}")
        for r in broken:
            print(f"    - {r['table']}: admin={r['admin_count']}, mcp=0 (403 or error)")
            print(f"      ACTION: Check ACL configuration and role assignment")

    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)

    total_usable = len(working) + len(no_data)
    total_issues = len(partial) + len(broken)

    if total_issues == 0:
        print(
            "\n🎉 PERFECT! All tools are working correctly with least privilege access!"
        )
        print(f"\n  - {len(working)} tools have data and are accessible")
        print(f"  - {len(no_data)} tools have no data yet (normal)")
        print(f"  - 0 permission issues")
        print("\nYou're ready to use all 11 tools in Claude Desktop!")
    else:
        print(f"\n⚠ ISSUES FOUND: {total_issues} tools have permission problems")
        print(f"\n  - {len(working)} tools working correctly")
        print(f"  - {len(no_data)} tools with no data (normal)")
        print(f"  - {len(partial)} tools with partial access (admin_overrides issue)")
        print(f"  - {len(broken)} tools completely broken for mcp.syslog")
        print("\nReview the issues above and fix ACL configurations.")

    print("\n" + "=" * 80 + "\n")

    return total_issues


if __name__ == "__main__":
    issues = main()
    exit(0 if issues == 0 else 1)
