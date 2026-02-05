"""
AI ROI Analysis - Measure business impact of AI on task resolution times

Compares resolution times for AI-assisted vs non-AI records across:
- Incidents (MTTR)
- Change Requests (Time to Implementation)
- Problems (Time to Root Cause)
- Cases (Time to Closure)
"""

import os
import re
from collections import defaultdict
from datetime import datetime

import requests

INSTANCE = os.getenv("SERVICENOW_INSTANCE")
USERNAME = os.getenv("SERVICENOW_USERNAME")
PASSWORD = os.getenv("SERVICENOW_PASSWORD")

# Table configuration - maps table name to relevant fields
TABLE_CONFIG = {
    "incident": {
        "number_prefix": "INC",
        "created_field": "sys_created_on",
        "resolved_field": "resolved_at",
        "metric_name": "Mean Time to Resolution (MTTR)",
        "state_field": "state",
        "priority_field": "priority",
        "category_field": "category",
        "group_field": "assignment_group",
    },
    "change_request": {
        "number_prefix": "CHG",
        "created_field": "sys_created_on",
        "resolved_field": "closed_at",
        "metric_name": "Mean Time to Implementation",
        "state_field": "state",
        "priority_field": "priority",
        "category_field": "category",
        "group_field": "assignment_group",
    },
    "problem": {
        "number_prefix": "PRB",
        "created_field": "sys_created_on",
        "resolved_field": "resolved_at",
        "metric_name": "Mean Time to Root Cause",
        "state_field": "state",
        "priority_field": "priority",
        "category_field": "category",
        "group_field": "assignment_group",
    },
    "sn_customerservice_case": {
        "number_prefix": "CS",
        "created_field": "sys_created_on",
        "resolved_field": "closed_at",
        "metric_name": "Mean Time to Closure",
        "state_field": "state",
        "priority_field": "priority",
        "category_field": "category",
        "group_field": "assignment_group",
    },
}


def get_ai_assisted_records():
    """
    Get all records that used AI agents

    Returns:
        dict: {table_name: {record_number: [ai_execution_data]}}
    """
    url = f"{INSTANCE}/api/now/table/sn_aia_execution_plan"

    # Get ALL AI executions to find records that used AI
    params = {
        "sysparm_query": "ORDERBYDESCsys_created_on",
        "sysparm_fields": "sys_id,sys_created_on,agent,objective,state,execution_time_sec",
        "sysparm_display_value": "true",
        "sysparm_limit": 1000,
    }

    response = requests.get(
        url,
        auth=(USERNAME, PASSWORD),
        params=params,
        headers={"Accept": "application/json"},
    )

    if response.status_code != 200:
        return {}

    ai_records = defaultdict(lambda: defaultdict(list))

    records = response.json().get("result", [])

    for record in records:
        objective = record.get("objective", "")

        # Try to match different record types
        for table_name, config in TABLE_CONFIG.items():
            prefix = config["number_prefix"]
            match = re.search(f"{prefix}\\d+", objective, re.IGNORECASE)

            if match:
                record_number = match.group(0).upper()
                ai_records[table_name][record_number].append(
                    {
                        "time": record.get("sys_created_on"),
                        "agent": record.get("agent"),
                        "state": record.get("state"),
                        "execution_time": record.get("execution_time_sec"),
                        "objective": objective,
                    }
                )
                break

    return ai_records


def get_task_records(table_name):
    """
    Get all records from a task table with resolution times

    Args:
        table_name: incident, change_request, problem, etc.

    Returns:
        list: Records with resolution time calculated
    """
    config = TABLE_CONFIG.get(table_name)
    if not config:
        return []

    url = f"{INSTANCE}/api/now/table/{table_name}"

    fields = [
        "number",
        "sys_id",
        config["created_field"],
        config["resolved_field"],
        config["state_field"],
        config["priority_field"],
        config["category_field"],
        config["group_field"],
    ]

    # Get ALL records to analyze
    params = {
        "sysparm_query": "ORDERBYDESCsys_created_on",
        "sysparm_fields": ",".join(fields),
        "sysparm_display_value": "true",
        "sysparm_limit": 1000,
    }

    response = requests.get(
        url,
        auth=(USERNAME, PASSWORD),
        params=params,
        headers={"Accept": "application/json"},
    )

    if response.status_code != 200:
        return []

    records = response.json().get("result", [])
    processed = []

    for rec in records:
        created = rec.get(config["created_field"], "")
        resolved = rec.get(config["resolved_field"], "")

        # Calculate resolution time if resolved
        resolution_hours = None
        if created and resolved:
            try:
                created_dt = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
                resolved_dt = datetime.strptime(resolved, "%Y-%m-%d %H:%M:%S")
                resolution_hours = (resolved_dt - created_dt).total_seconds() / 3600
            except:
                pass

        processed.append(
            {
                "number": rec.get("number", ""),
                "created": created,
                "resolved": resolved,
                "resolution_hours": resolution_hours,
                "state": rec.get(config["state_field"], ""),
                "priority": rec.get(config["priority_field"], ""),
                "category": rec.get(config["category_field"], ""),
                "group": rec.get(config["group_field"], ""),
            }
        )

    return processed


def query_ai_roi_analysis(table_name="incident", breakdown_by="priority"):
    """
    Analyze AI ROI for a specific task table

    Args:
        table_name: incident, change_request, problem, sn_customerservice_case
        breakdown_by: priority, category, group, or none

    Returns:
        Formatted analysis string
    """
    config = TABLE_CONFIG.get(table_name)
    if not config:
        return f"Error: Unknown table {table_name}. Supported: incident, change_request, problem, sn_customerservice_case"

    # Get AI-assisted records
    ai_records = get_ai_assisted_records()
    ai_numbers = set(ai_records.get(table_name, {}).keys())

    # Get all task records
    all_records = get_task_records(table_name)

    # Split into AI vs non-AI, only include resolved records
    with_ai = [
        r
        for r in all_records
        if r["number"] in ai_numbers and r["resolution_hours"] is not None
    ]
    without_ai = [
        r
        for r in all_records
        if r["number"] not in ai_numbers and r["resolution_hours"] is not None
    ]

    # Build output
    output = []
    output.append(f"AI ROI ANALYSIS - {table_name.upper().replace('_', ' ')}")
    output.append("=" * 80)
    output.append(f"Metric: {config['metric_name']}")
    output.append(f"Total records: {len(all_records)}")
    output.append(f"  - Resolved: {len(with_ai) + len(without_ai)}")
    output.append(
        f"  - With AI: {len(with_ai)} resolved ({len(ai_numbers)} total AI activity)"
    )
    output.append(f"  - Without AI: {len(without_ai)} resolved")
    output.append("")

    # Overall comparison
    if with_ai and without_ai:
        avg_with_ai = sum(r["resolution_hours"] for r in with_ai) / len(with_ai)
        avg_without_ai = sum(r["resolution_hours"] for r in without_ai) / len(
            without_ai
        )
        improvement = ((avg_without_ai - avg_with_ai) / avg_without_ai) * 100
        time_saved = avg_without_ai - avg_with_ai

        output.append(f"OVERALL {config['metric_name'].upper()}:")
        output.append("-" * 80)
        output.append(f"  With AI:     {avg_with_ai:.1f} hours (n={len(with_ai)})")
        output.append(
            f"  Without AI:  {avg_without_ai:.1f} hours (n={len(without_ai)})"
        )
        output.append(
            f"  Improvement: {improvement:.1f}% {'faster' if improvement > 0 else 'slower'}"
        )
        output.append(f"  Time saved:  {time_saved:.1f} hours per record")
        output.append("")

        # Breakdown analysis
        if breakdown_by and breakdown_by != "none":
            output.append(f"BREAKDOWN BY {breakdown_by.upper()}:")
            output.append("-" * 80)

            # Group by breakdown field
            with_ai_groups = defaultdict(list)
            without_ai_groups = defaultdict(list)

            for r in with_ai:
                with_ai_groups[r[breakdown_by]].append(r["resolution_hours"])

            for r in without_ai:
                without_ai_groups[r[breakdown_by]].append(r["resolution_hours"])

            # Get all unique groups
            all_groups = set(
                list(with_ai_groups.keys()) + list(without_ai_groups.keys())
            )

            for group in sorted(all_groups):
                ai_times = with_ai_groups.get(group, [])
                non_ai_times = without_ai_groups.get(group, [])

                if ai_times and non_ai_times:
                    avg_ai = sum(ai_times) / len(ai_times)
                    avg_non_ai = sum(non_ai_times) / len(non_ai_times)
                    improvement = ((avg_non_ai - avg_ai) / avg_non_ai) * 100

                    output.append(f"  {group}:")
                    output.append(
                        f"    With AI:    {avg_ai:.1f} hours (n={len(ai_times)})"
                    )
                    output.append(
                        f"    Without AI: {avg_non_ai:.1f} hours (n={len(non_ai_times)})"
                    )
                    output.append(f"    Improvement: {improvement:.1f}%")
                elif ai_times:
                    avg_ai = sum(ai_times) / len(ai_times)
                    output.append(f"  {group}:")
                    output.append(
                        f"    With AI:    {avg_ai:.1f} hours (n={len(ai_times)})"
                    )
                    output.append(f"    Without AI: No data")
                elif non_ai_times:
                    avg_non_ai = sum(non_ai_times) / len(non_ai_times)
                    output.append(f"  {group}:")
                    output.append(f"    With AI:    No data")
                    output.append(
                        f"    Without AI: {avg_non_ai:.1f} hours (n={len(non_ai_times)})"
                    )
                output.append("")

        # AI activity details
        if ai_numbers:
            output.append("AI ACTIVITY DETAILS:")
            output.append("-" * 80)
            for number in sorted(ai_numbers):
                executions = ai_records[table_name][number]
                output.append(f"  {number}: {len(executions)} AI execution(s)")
                for exec in executions[:3]:  # Limit to first 3 to avoid clutter
                    agent_name = (
                        exec["agent"].get("display_value", "Unknown")
                        if isinstance(exec["agent"], dict)
                        else exec["agent"]
                    )
                    output.append(f"    - {exec['time']}: {agent_name}")
                if len(executions) > 3:
                    output.append(f"    ... and {len(executions) - 3} more")

    elif not with_ai and not without_ai:
        output.append("INSUFFICIENT DATA:")
        output.append("-" * 80)
        output.append(f"  No resolved records found")
        output.append(f"  Total records with AI activity: {len(ai_numbers)}")
        output.append("")
        if ai_numbers:
            output.append("Records with AI activity (not yet resolved):")
            for number in sorted(ai_numbers):
                executions = ai_records[table_name][number]
                output.append(f"  {number}: {len(executions)} AI execution(s)")
    else:
        output.append("INSUFFICIENT DATA FOR COMPARISON:")
        output.append("-" * 80)
        output.append(f"  Resolved with AI: {len(with_ai)}")
        output.append(f"  Resolved without AI: {len(without_ai)}")
        output.append("")
        output.append("Need at least 1 resolved record in each category for comparison")
        output.append("")
        if ai_numbers:
            output.append("Records with AI activity:")
            for number in sorted(ai_numbers):
                rec = next((r for r in all_records if r["number"] == number), None)
                if rec:
                    status = (
                        f"Resolved in {rec['resolution_hours']:.1f} hours"
                        if rec["resolution_hours"]
                        else f"Not resolved (State: {rec['state']})"
                    )
                    output.append(f"  {number}: {status}")

    return "\n".join(output)
