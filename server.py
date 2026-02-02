import os

from dotenv import load_dotenv

load_dotenv()

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("servicenow-debug")

INSTANCE = os.getenv("SERVICENOW_INSTANCE")
USERNAME = os.getenv("SERVICENOW_USERNAME")
PASSWORD = os.getenv("SERVICENOW_PASSWORD")


@mcp.tool()
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
    """
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


@mcp.tool()
def query_ai_execution_plans(
    status: str = "",
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """
    Query AI execution plans to see AI agent activity and conversations.

    Args:
        status: Filter by status (partial match)
        limit: Maximum number of results (default 20)
        minutes_ago: Look back this many minutes (default 60)
    """
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
        return "No AI execution plans found matching your criteria."

    output = []
    for entry in results:
        output.append(
            f"[{entry.get('sys_created_on')}] Status: {entry.get('status', 'N/A')}\n"
            f"  Sys ID: {entry.get('sys_id', 'N/A')}\n"
            f"  Updated: {entry.get('sys_updated_on', 'N/A')}"
        )
    return "\n---\n".join(output)


@mcp.tool()
def query_gen_ai_metrics(
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """
    Query GenAI metrics including offensiveness scores.

    Args:
        limit: Maximum number of results (default 20)
        minutes_ago: Look back this many minutes (default 60)
    """
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
        return "No GenAI metrics found matching your criteria."

    output = []
    for entry in results:
        output.append(
            f"[{entry.get('sys_created_on')}]\n"
            f"  Metric: {entry.get('metric', 'N/A')}\n"
            f"  Sys ID: {entry.get('sys_id', 'N/A')}"
        )
    return "\n---\n".join(output)


@mcp.tool()
def query_gen_ai_metadata(
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """
    Query GenAI metadata with user feedback.

    Args:
        limit: Maximum number of results (default 20)
        minutes_ago: Look back this many minutes (default 60)
    """
    query_parts = []
    query_parts.append(f"sys_created_onRELATIVEGT@minute@ago@{minutes_ago}")
    query = "^".join(query_parts)

    url = f"{INSTANCE}/api/now/table/sys_gen_ai_log_metadata"
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
        return "No GenAI metadata found matching your criteria."

    output = []
    for entry in results:
        output.append(
            f"[{entry.get('sys_created_on')}]\n"
            f"  Feedback: {entry.get('feedback', 'N/A')}\n"
            f"  Sys ID: {entry.get('sys_id', 'N/A')}"
        )
    return "\n---\n".join(output)


@mcp.tool()
def query_rest_messages(
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """
    Query REST messages to see outbound API call configurations.

    Args:
        limit: Maximum number of results (default 20)
        minutes_ago: Look back this many minutes (default 60)
    """
    query_parts = []
    query_parts.append(f"sys_created_onRELATIVEGT@minute@ago@{minutes_ago}")
    query = "^".join(query_parts)

    url = f"{INSTANCE}/api/now/table/sys_rest_message"
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
        return "No REST messages found matching your criteria."

    output = []
    for entry in results:
        output.append(
            f"[{entry.get('sys_created_on')}]\n"
            f"  Name: {entry.get('name', 'N/A')}\n"
            f"  Endpoint: {entry.get('endpoint', 'N/A')}\n"
            f"  Sys ID: {entry.get('sys_id', 'N/A')}"
        )
    return "\n---\n".join(output)


@mcp.tool()
def query_scheduled_jobs(
    job_name: str = "",
    state: str = "",
    limit: int = 20,
) -> str:
    """
    Query scheduled jobs (sysauto) to see job status and execution history.

    Args:
        job_name: Filter by job name (partial match)
        state: Filter by state (ready, running, queued, error)
        limit: Maximum number of results (default 20)
    """
    query_parts = []
    if job_name:
        query_parts.append(f"nameLIKE{job_name}")
    if state:
        query_parts.append(f"state={state}")

    query = "^".join(query_parts) if query_parts else ""

    url = f"{INSTANCE}/api/now/table/sysauto"
    params = {
        "sysparm_query": f"{query}^ORDERBYDESCsys_updated_on"
        if query
        else "ORDERBYDESCsys_updated_on",
        "sysparm_limit": limit,
        "sysparm_fields": "name,state,next_action,last_run,last_run_duration,run_count,error_description",
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
        return "No scheduled jobs found matching your criteria."

    output = []
    for entry in results:
        error = entry.get("error_description", "")
        error_text = f"\n  Error: {error}" if error else ""
        output.append(
            f"Job: {entry.get('name', 'N/A')}\n"
            f"  State: {entry.get('state', 'N/A')}\n"
            f"  Last Run: {entry.get('last_run', 'Never')}\n"
            f"  Duration: {entry.get('last_run_duration', 'N/A')}\n"
            f"  Run Count: {entry.get('run_count', '0')}\n"
            f"  Next Action: {entry.get('next_action', 'N/A')}{error_text}"
        )
    return "\n---\n".join(output)


@mcp.tool()
def query_workflow_context(
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """
    Query classic workflow contexts to see workflow executions.

    Args:
        limit: Maximum number of results (default 20)
        minutes_ago: Look back this many minutes (default 60)
    """
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


if __name__ == "__main__":
    mcp.run()
