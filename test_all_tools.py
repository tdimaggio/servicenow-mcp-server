#!/usr/bin/env python3
"""
Test script to verify all MCP server tools work correctly
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

INSTANCE = os.getenv("SERVICENOW_INSTANCE")
USERNAME = os.getenv("SERVICENOW_USERNAME")
PASSWORD = os.getenv("SERVICENOW_PASSWORD")

# Define all tools to test (only the 9 working tools)
TOOLS = [
    {
        "name": "query_syslog",
        "table": "syslog",
        "params": {
            "sysparm_limit": 2,
            "sysparm_query": "sys_created_onRELATIVEGT@minute@ago@60^ORDERBYDESCsys_created_on",
            "sysparm_fields": "sys_created_on,level,source,message",
        },
    },
    {
        "name": "query_ai_execution_plans",
        "table": "sn_aia_execution_plan",
        "params": {
            "sysparm_limit": 2,
            "sysparm_query": "sys_created_onRELATIVEGT@minute@ago@60^ORDERBYDESCsys_created_on",
            "sysparm_display_value": "true",
        },
    },
    {
        "name": "query_gen_ai_metrics",
        "table": "sys_generative_ai_metric",
        "params": {
            "sysparm_limit": 2,
            "sysparm_query": "sys_created_onRELATIVEGT@minute@ago@60^ORDERBYDESCsys_created_on",
            "sysparm_display_value": "true",
        },
    },
    {
        "name": "query_gen_ai_metadata",
        "table": "sys_gen_ai_log_metadata",
        "params": {
            "sysparm_limit": 2,
            "sysparm_query": "sys_created_onRELATIVEGT@minute@ago@60^ORDERBYDESCsys_created_on",
            "sysparm_display_value": "true",
        },
    },
    {
        "name": "query_flow_executions",
        "table": "sys_flow_context",
        "params": {
            "sysparm_limit": 2,
            "sysparm_query": "sys_created_onRELATIVEGT@minute@ago@60^ORDERBYDESCsys_created_on",
            "sysparm_fields": "sys_created_on,sys_updated_on,state,workflow_version.workflow,trigger_name,error_text",
            "sysparm_display_value": "true",
        },
    },
    {
        "name": "query_rest_messages",
        "table": "sys_rest_message",
        "params": {
            "sysparm_limit": 2,
            "sysparm_query": "sys_created_onRELATIVEGT@minute@ago@60^ORDERBYDESCsys_created_on",
            "sysparm_display_value": "true",
        },
    },
    {
        "name": "query_scheduled_jobs",
        "table": "sysauto",
        "params": {
            "sysparm_limit": 2,
            "sysparm_query": "ORDERBYDESCsys_updated_on",
            "sysparm_fields": "name,state,next_action,last_run,last_run_duration,run_count,error_description",
            "sysparm_display_value": "true",
        },
    },
    {
        "name": "query_execution_tracker",
        "table": "sys_execution_tracker",
        "params": {
            "sysparm_limit": 2,
            "sysparm_query": "sys_created_onRELATIVEGT@minute@ago@60^ORDERBYDESCsys_created_on",
            "sysparm_display_value": "true",
        },
    },
    {
        "name": "query_workflow_context",
        "table": "wf_context",
        "params": {
            "sysparm_limit": 2,
            "sysparm_query": "sys_created_onRELATIVEGT@minute@ago@60^ORDERBYDESCsys_created_on",
            "sysparm_display_value": "true",
        },
    },
]


def test_tool(tool):
    """Test a single tool by querying its table"""
    url = f"{INSTANCE}/api/now/table/{tool['table']}"

    try:
        response = requests.get(
            url,
            params=tool["params"],
            auth=(USERNAME, PASSWORD),
            headers={"Accept": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            results = response.json().get("result", [])
            return {
                "status": "✓ SUCCESS",
                "code": 200,
                "records": len(results),
                "fields": list(results[0].keys())[:8] if results else [],
            }
        elif response.status_code == 403:
            return {
                "status": "✗ FORBIDDEN",
                "code": 403,
                "error": "User not authorized to access this table",
            }
        elif response.status_code == 400:
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            return {"status": "✗ BAD REQUEST", "code": 400, "error": error_msg}
        else:
            return {
                "status": f"? UNKNOWN ({response.status_code})",
                "code": response.status_code,
                "error": response.text[:100],
            }
    except Exception as e:
        return {"status": "✗ EXCEPTION", "error": str(e)[:100]}


def main():
    print("=" * 80)
    print("ServiceNow MCP Server Tool Test")
    print("=" * 80)
    print(f"Instance: {INSTANCE}")
    print(f"Username: {USERNAME}")
    print("=" * 80)
    print()

    results = {}
    success_count = 0
    error_count = 0

    for tool in TOOLS:
        print(f"Testing: {tool['name']} ({tool['table']})")
        result = test_tool(tool)
        results[tool["name"]] = result

        if result["status"].startswith("✓"):
            success_count += 1
            print(f"  {result['status']} - {result['records']} records found")
            if result.get("fields"):
                print(f"  Available fields: {', '.join(result['fields'][:5])}...")
        else:
            error_count += 1
            print(f"  {result['status']}")
            if result.get("error"):
                print(f"  Error: {result['error']}")
        print()

    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total tools tested: {len(TOOLS)}")
    print(f"✓ Successful: {success_count}")
    print(f"✗ Failed: {error_count}")
    print()

    if error_count > 0:
        print("Failed Tools:")
        for name, result in results.items():
            if not result["status"].startswith("✓"):
                print(f"  - {name}: {result['status']}")
                if result.get("error"):
                    print(f"    {result['error']}")

    print()
    print("=" * 80)

    return success_count, error_count


if __name__ == "__main__":
    success, errors = main()
    exit(0 if errors == 0 else 1)
