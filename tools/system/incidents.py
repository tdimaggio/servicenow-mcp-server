"""
Query incident records for context when investigating AI activity
"""

import os

import requests


def query_incidents(
    number: str = "",
    sys_id: str = "",
    limit: int = 10,
    minutes_ago: int = 1440,
) -> str:
    """
    Query incident records to get context about tickets involved in AI operations.

    Use this when you need to look up incident details by number or sys_id,
    especially when investigating AI Agent or Now Assist activity on specific incidents.

    Args:
        number: Incident number (e.g., INC0009005) - partial match supported
        sys_id: Incident sys_id for exact lookup
        limit: Maximum number of results (default 10)
        minutes_ago: Look back this many minutes (default 1440 = 24 hours)

    Returns:
        Formatted string with incident details
    """
    INSTANCE = os.getenv("SERVICENOW_INSTANCE")
    USERNAME = os.getenv("SERVICENOW_USERNAME")
    PASSWORD = os.getenv("SERVICENOW_PASSWORD")

    # Build query
    query_parts = []

    if sys_id:
        # Direct sys_id lookup
        url = f"{INSTANCE}/api/now/table/incident/{sys_id}"
        params = {
            "sysparm_display_value": "true",
            "sysparm_fields": "number,short_description,description,state,priority,urgency,impact,category,assigned_to,assignment_group,sys_created_on,sys_updated_on,work_notes,close_notes",
        }
    else:
        # Query-based lookup
        if number:
            query_parts.append(f"numberLIKE{number}")
        query_parts.append(f"sys_updated_onRELATIVEGT@minute@ago@{minutes_ago}")
        query = "^".join(query_parts)

        url = f"{INSTANCE}/api/now/table/incident"
        params = {
            "sysparm_query": f"{query}^ORDERBYDESCsys_updated_on",
            "sysparm_limit": limit,
            "sysparm_display_value": "true",
            "sysparm_fields": "number,short_description,description,state,priority,urgency,impact,category,assigned_to,assignment_group,sys_created_on,sys_updated_on,work_notes,close_notes",
        }

    response = requests.get(
        url,
        params=params,
        auth=(USERNAME, PASSWORD),
        headers={"Accept": "application/json"},
    )

    if response.status_code == 404:
        return f"Incident not found with sys_id: {sys_id}"

    if response.status_code == 403:
        return "Error: Permission denied. The mcp.syslog user may not have read access to the incident table. Please run the ACL permission script."

    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"

    # Handle both single record (sys_id lookup) and list responses
    if sys_id:
        result = response.json().get("result", {})
        if not result:
            return f"Incident not found with sys_id: {sys_id}"
        results = [result]
    else:
        results = response.json().get("result", [])
        if not results:
            return "No incidents found matching your criteria."

    output = []
    for entry in results:
        # Truncate long fields for readability
        description = entry.get("description", "N/A")
        if len(description) > 200:
            description = description[:200] + "..."

        work_notes = entry.get("work_notes", "")
        if work_notes and len(work_notes) > 200:
            work_notes = work_notes[:200] + "..."

        close_notes = entry.get("close_notes", "")
        if close_notes and len(close_notes) > 200:
            close_notes = close_notes[:200] + "..."

        output.append(
            f"[{entry.get('number', 'N/A')}] {entry.get('short_description', 'N/A')}\n"
            f"  State: {entry.get('state', 'N/A')}\n"
            f"  Priority: {entry.get('priority', 'N/A')} (Urgency: {entry.get('urgency', 'N/A')}, Impact: {entry.get('impact', 'N/A')})\n"
            f"  Category: {entry.get('category', 'N/A')}\n"
            f"  Assigned To: {entry.get('assigned_to', 'Unassigned')}\n"
            f"  Assignment Group: {entry.get('assignment_group', 'N/A')}\n"
            f"  Created: {entry.get('sys_created_on', 'N/A')}\n"
            f"  Updated: {entry.get('sys_updated_on', 'N/A')}\n"
            f"  Description: {description}\n"
            + (f"  Work Notes: {work_notes}\n" if work_notes else "")
            + (f"  Close Notes: {close_notes}\n" if close_notes else "")
            + f"  Sys ID: {entry.get('sys_id', 'N/A')}"
        )
    return "\n---\n".join(output)
