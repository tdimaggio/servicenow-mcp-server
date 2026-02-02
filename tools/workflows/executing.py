"""
Query currently executing workflows in real-time
"""

import os

import requests


def query_workflow_executing(
    workflow_name: str = "",
    limit: int = 20,
) -> str:
    """
    Query currently executing workflows to see real-time workflow activity.

    Args:
        workflow_name: Filter by workflow name (partial match)
        limit: Maximum number of results (default 20)

    Returns:
        Formatted string with currently executing workflows
    """
    INSTANCE = os.getenv("SERVICENOW_INSTANCE")
    USERNAME = os.getenv("SERVICENOW_USERNAME")
    PASSWORD = os.getenv("SERVICENOW_PASSWORD")

    query_parts = []
    if workflow_name:
        query_parts.append(f"nameLIKE{workflow_name}")

    query = "^".join(query_parts) if query_parts else ""

    url = f"{INSTANCE}/api/now/table/wf_executing"
    params = {
        "sysparm_query": f"{query}^ORDERBYDESCsys_created_on"
        if query
        else "ORDERBYDESCsys_created_on",
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
        return "No currently executing workflows found."

    output = []
    for entry in results:
        output.append(
            f"[{entry.get('sys_created_on')}]\n"
            f"  Workflow: {entry.get('name', 'N/A')}\n"
            f"  Context: {entry.get('context', 'N/A')}\n"
            f"  Activity: {entry.get('activity', 'N/A')}\n"
            f"  State: {entry.get('state', 'N/A')}"
        )
    return "\n---\n".join(output)
