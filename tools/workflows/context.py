"""
Query workflow contexts to see workflow executions
"""

import os

import requests


def query_workflow_context(
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """
    Query classic workflow contexts to see workflow executions.

    Args:
        limit: Maximum number of results (default 20)
        minutes_ago: Look back this many minutes (default 60)

    Returns:
        Formatted string with workflow context details
    """
    INSTANCE = os.getenv("SERVICENOW_INSTANCE")
    USERNAME = os.getenv("SERVICENOW_USERNAME")
    PASSWORD = os.getenv("SERVICENOW_PASSWORD")

    query_parts = []
    query_parts.append(f"sys_created_onRELATIVEGT@minute@ago@{minutes_ago}")
    query = "^".join(query_parts)

    url = f"{INSTANCE}/api/now/table/wf_context"
    params = {
        "sysparm_query": f"{query}^ORDERBYDESCsys_created_on",
        "sysparm_limit": limit,
        "sysparm_display_value": "true",
    }

    response = requests.get(
        url,
        params=params,
        auth=(USERNAME, PASSWORD),
        headers={"Accept": "application/json"},
    )

    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"

    results = response.json().get("result", [])
    if not results:
        return "No workflow contexts found matching your criteria."

    output = []
    for entry in results:
        output.append(
            f"[{entry.get('sys_created_on')}]\n"
            f"  Workflow: {entry.get('workflow', 'N/A')}\n"
            f"  State: {entry.get('state', 'N/A')}\n"
            f"  Sys ID: {entry.get('sys_id', 'N/A')}"
        )
    return "\n---\n".join(output)
