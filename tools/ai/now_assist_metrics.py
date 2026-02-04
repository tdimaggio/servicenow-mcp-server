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
        # Parse the value field if it exists (contains request/response details)
        value_data = entry.get("value", "")
        error_msg = ""
        activity_type = ""

        # Try to extract useful info from value field
        if "error" in value_data.lower():
            # Extract error message
            if '"error":' in value_data:
                try:
                    import json

                    value_json = json.loads(value_data)
                    error_msg = value_json.get(
                        "error", value_json.get("response", {}).get("error", "")
                    )
                except:
                    error_msg = "Error present (see details)"

        if '"type":' in value_data:
            try:
                import json

                value_json = json.loads(value_data)
                activity_type = value_json.get("type", "")
            except:
                pass

        output.append(
            f"[{entry.get('sys_created_on')}]\n"
            f"  Name: {entry.get('name', 'N/A')}\n"
            f"  Type: {entry.get('type', 'N/A')}\n"
            f"  Source: {entry.get('source', 'N/A')}\n"
            + (f"  Activity: {activity_type}\n" if activity_type else "")
            + (f"  ⚠️ Error: {error_msg}\n" if error_msg else "")
            + f"  Sys ID: {entry.get('sys_id', 'N/A')}"
        )
    return "\n---\n".join(output)
