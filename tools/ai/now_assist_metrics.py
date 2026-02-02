"""
Query Now Assist usage metrics and GenAI activity
"""

import os

import requests


def query_now_assist_metrics(
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """
    Query Now Assist usage metrics including privacy operations and GenAI activity.

    This tracks Now Assist Skills (summarization, resolution notes, text generation),
    NOT AI Agents. For AI Agent activity, use query_ai_agent_executions.

    Captures:
    - Now Assist skill usage (summarize, resolve, generate)
    - Data privacy anonymization/de-anonymization
    - GenAI offensiveness scores
    - Model performance metrics

    Args:
        limit: Maximum number of results (default 20)
        minutes_ago: Look back this many minutes (default 60)

    Returns:
        Formatted string with Now Assist metrics
    """
    INSTANCE = os.getenv("SERVICENOW_INSTANCE")
    USERNAME = os.getenv("SERVICENOW_USERNAME")
    PASSWORD = os.getenv("SERVICENOW_PASSWORD")

    query_parts = []
    query_parts.append(f"sys_created_onRELATIVEGT@minute@ago@{minutes_ago}")
    query = "^".join(query_parts)

    url = f"{INSTANCE}/api/now/table/sys_generative_ai_metric"
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
        return "No Now Assist metrics found matching your criteria."

    output = []
    for entry in results:
        output.append(
            f"[{entry.get('sys_created_on')}]\n"
            f"  Metric: {entry.get('metric', 'N/A')}\n"
            f"  Sys ID: {entry.get('sys_id', 'N/A')}"
        )
    return "\n---\n".join(output)
