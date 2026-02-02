"""
Query ServiceNow application logs (syslog)
"""

import os

import requests


def query_syslog(
    message_contains: str = "",
    source: str = "",
    level: str = "",
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """
    Query the ServiceNow syslog table for application logs.

    Args:
        message_contains: Filter by message content (partial match)
        source: Filter by log source (partial match)
        level: Filter by log level (0=Error, 1=Warning, 2=Info, 3=Debug)
        limit: Maximum number of results (default 20)
        minutes_ago: Look back this many minutes (default 60)

    Returns:
        Formatted string with syslog entries
    """
    INSTANCE = os.getenv("SERVICENOW_INSTANCE")
    USERNAME = os.getenv("SERVICENOW_USERNAME")
    PASSWORD = os.getenv("SERVICENOW_PASSWORD")

    query_parts = []
    if message_contains:
        query_parts.append(f"messageLIKE{message_contains}")
    if source:
        query_parts.append(f"sourceLIKE{source}")
    if level:
        query_parts.append(f"level={level}")
    query_parts.append(f"sys_created_onRELATIVEGT@minute@ago@{minutes_ago}")
    query = "^".join(query_parts)

    url = f"{INSTANCE}/api/now/table/syslog"
    params = {
        "sysparm_query": f"{query}^ORDERBYDESCsys_created_on",
        "sysparm_limit": limit,
        "sysparm_fields": "sys_created_on,level,source,message",
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
        return "No syslog entries found matching your criteria."

    output = []
    for entry in results:
        output.append(
            f"[{entry.get('sys_created_on')}] "
            f"{entry.get('level', 'N/A').upper()} | "
            f"{entry.get('source', 'N/A')}\n"
            f"{entry.get('message', 'No message')}\n"
        )
    return "\n---\n".join(output)
