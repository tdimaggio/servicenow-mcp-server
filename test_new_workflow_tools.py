#!/usr/bin/env python3
"""
Test the new workflow debugging tools after adding permissions
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

INSTANCE = os.getenv("SERVICENOW_INSTANCE")
MCP_USERNAME = os.getenv("SERVICENOW_USERNAME")
MCP_PASSWORD = os.getenv("SERVICENOW_PASSWORD")

# New workflow tools to test
NEW_WORKFLOW_TOOLS = [
    ("wf_executing", "Currently Executing Workflows"),
    ("wf_history", "Workflow Execution History"),
    ("wf_log", "Workflow Detailed Logs"),
]


def test_table_access(table_name, description):
    """Test access to a table with mcp.syslog credentials"""
    url = f"{INSTANCE}/api/now/table/{table_name}"
    params = {
        "sysparm_limit": 5,
        "sysparm_display_value": "true",
    }

    try:
        response = requests.get(
            url,
            params=params,
            auth=(MCP_USERNAME, MCP_PASSWORD),
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
                "error": "Permission denied - ACL may not be configured",
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
    print("NEW WORKFLOW TOOLS ACCESS TEST")
    print("=" * 80)
    print(f"\nInstance: {INSTANCE}")
    print(f"Testing as: {MCP_USERNAME}")
    print("\n" + "=" * 80)

    results = []

    for table_name, description in NEW_WORKFLOW_TOOLS:
        print(f"\nTesting: {table_name}")
        print(f"Description: {description}")
        print("-" * 80)

        result = test_table_access(table_name, description)

        if result["status"] == "success":
            print(f"  Status:  ✓ SUCCESS")
            print(f"  Records: {result['count']}")
            if result["count"] == 0:
                print(
                    f"  Note:    No data in table (normal if workflows haven't run recently)"
                )
            status = "WORKING"
        elif result["status"] == "forbidden":
            print(f"  Status:  ✗ FORBIDDEN (403)")
            print(f"  Error:   {result['error']}")
            print(f"  Action:  Run add_workflow_permissions.js in ServiceNow")
            status = "BROKEN"
        else:
            print(f"  Status:  ✗ ERROR ({result.get('status_code', 'N/A')})")
            print(f"  Error:   {result.get('error', 'Unknown')}")
            status = "ERROR"

        results.append(
            {
                "table": table_name,
                "description": description,
                "status": status,
                "count": result.get("count", 0),
            }
        )

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    working = [r for r in results if r["status"] == "WORKING"]
    broken = [r for r in results if r["status"] == "BROKEN"]
    error = [r for r in results if r["status"] == "ERROR"]

    print(f"\n✓ WORKING: {len(working)}/{len(results)}")
    for r in working:
        print(f"    - {r['table']}: {r['count']} records")

    if broken:
        print(f"\n✗ BROKEN (403 Forbidden): {len(broken)}")
        for r in broken:
            print(f"    - {r['table']}: Permission denied")

    if error:
        print(f"\n✗ ERROR: {len(error)}")
        for r in error:
            print(f"    - {r['table']}: Unexpected error")

    print("\n" + "=" * 80)

    if len(working) == len(results):
        print("\n🎉 SUCCESS! All workflow tools are working!")
        print("\nNext steps:")
        print("  1. Update test_all_tools.py to include these tools")
        print("  2. Update README.md documentation")
        print("  3. Restart Claude Desktop to use the new tools")
        print("  4. Test queries like: 'Show me workflow logs from the last hour'")
    elif broken:
        print("\n⚠ PERMISSIONS NEEDED")
        print("\nTo fix:")
        print("  1. Navigate to ServiceNow: System Definition > Scripts - Background")
        print("  2. Copy and run: add_workflow_permissions.js")
        print("  3. Verify output shows successful ACL configuration")
        print("  4. Re-run this test script")
    else:
        print("\n⚠ UNEXPECTED ERRORS")
        print("\nReview the errors above and troubleshoot as needed")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
