"""
Query AI Agent execution plans and activity
"""

import os

import requests


def query_ai_agent_executions(
    status: str = "",
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """
    Query AI Agent execution plans to see agentic AI activity (multi-step AI actions).

    This tracks AI Agents (the agentic AI that performs multi-step actions autonomously),
    NOT Now Assist Skills. For Now Assist activity, use query_now_assist_metrics.

    Args:
        status: Filter by status (partial match)
        limit: Maximum number of results (default 20)
        minutes_ago: Look back this many minutes (default 60)

    Returns:
        Formatted string with AI Agent execution details
    """
    INSTANCE = os.getenv("SERVICENOW_INSTANCE")
    USERNAME = os.getenv("SERVICENOW_USERNAME")
    PASSWORD = os.getenv("SERVICENOW_PASSWORD")

    query_parts = []
    if status:
        query_parts.append(f"statusLIKE{status}")
    query_parts.append(f"sys_created_onRELATIVEGT@minute@ago@{minutes_ago}")
    query = "^".join(query_parts)

    url = f"{INSTANCE}/api/now/table/sn_aia_execution_plan"
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
        return "No AI Agent execution plans found matching your criteria."

    output = []
    for entry in results:
        output.append(
            f"[{entry.get('sys_created_on')}] Status: {entry.get('status', 'N/A')}\n"
            f"  Sys ID: {entry.get('sys_id', 'N/A')}\n"
            f"  Updated: {entry.get('sys_updated_on', 'N/A')}"
        )
    return "\n---\n".join(output)
