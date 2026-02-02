"""
Query workflow logs to see detailed workflow execution logs and errors
"""

import os

import requests


def query_workflow_log(
    workflow_name: str = "",
    level: str = "",
    limit: int = 20,
    minutes_ago: int = 1440,
) -> str:
    """
    Query workflow logs to see detailed workflow execution logs and errors.

    Args:
        workflow_name: Filter by workflow name (partial match)
        level: Filter by log level (error, warn, info, debug)
        limit: Maximum number of results (default 20)
        minutes_ago: Look back this many minutes (default 1440 = 24 hours)

    Returns:
        Formatted string with workflow logs
    """
    INSTANCE = os.getenv("SERVICENOW_INSTANCE")
    USERNAME = os.getenv("SERVICENOW_USERNAME")
    PASSWORD = os.getenv("SERVICENOW_PASSWORD")

    query_parts = []
    if workflow_name:
        query_parts.append(f"workflow_versionLIKE{workflow_name}")
    if level:
        query_parts.append(f"level={level}")
    query_parts.append(f"sys_created_onRELATIVEGT@minute@ago@{minutes_ago}")
    query = "^".join(query_parts)

    url = f"{INSTANCE}/api/now/table/wf_log"
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
        return "No workflow logs found matching your criteria."

    output = []
    for entry in results:
        output.append(
            f"[{entry.get('sys_created_on')}] {entry.get('level', 'INFO').upper()}\n"
            f"  Workflow: {entry.get('workflow_version', 'N/A')}\n"
            f"  Activity: {entry.get('activity', 'N/A')}\n"
            f"  Message: {entry.get('message', 'N/A')}"
        )
    return "\n---\n".join(output)
