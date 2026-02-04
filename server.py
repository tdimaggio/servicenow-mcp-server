"""
ServiceNow MCP Server - Modular Version

This MCP server provides debugging and monitoring tools for ServiceNow instances.
Tools are organized by category for better maintainability.
"""

import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("servicenow-debug")

# Import all tools from modular structure
from tools.ai import (
    query_ai_agent_executions,
    query_now_assist_metadata,
    query_now_assist_metrics,
)
from tools.system import (
    query_incidents,
    query_rest_messages,
    query_syslog,
)
from tools.workflows import (
    query_workflow_context,
    query_workflow_executing,
    query_workflow_history,
    query_workflow_log,
)


# Register AI tools
@mcp.tool()
def ai_agent_executions(
    status: str = "",
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """Query AI Agent execution plans (multi-step agentic AI)"""
    return query_ai_agent_executions(status, limit, minutes_ago)


@mcp.tool()
def now_assist_metrics(
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """Query Now Assist usage metrics (summarization, resolution notes, skills)"""
    return query_now_assist_metrics(limit, minutes_ago)


@mcp.tool()
def now_assist_metadata(
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """Query Now Assist metadata with user feedback and prompts"""
    return query_now_assist_metadata(limit, minutes_ago)


# Register workflow tools
@mcp.tool()
def workflow_context(
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """Query workflow contexts to see workflow executions"""
    return query_workflow_context(limit, minutes_ago)


@mcp.tool()
def workflow_executing(
    workflow_name: str = "",
    limit: int = 20,
) -> str:
    """Query currently executing workflows in real-time"""
    return query_workflow_executing(workflow_name, limit)


@mcp.tool()
def workflow_history(
    workflow_name: str = "",
    limit: int = 20,
    minutes_ago: int = 1440,
) -> str:
    """Query workflow execution history (completed and failed)"""
    return query_workflow_history(workflow_name, limit, minutes_ago)


@mcp.tool()
def workflow_logs(
    workflow_name: str = "",
    level: str = "",
    limit: int = 20,
    minutes_ago: int = 1440,
) -> str:
    """Query detailed workflow logs with error filtering"""
    return query_workflow_log(workflow_name, level, limit, minutes_ago)


# Register system tools
@mcp.tool()
def syslog(
    message_contains: str = "",
    source: str = "",
    level: str = "",
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """Query ServiceNow application logs (syslog)"""
    return query_syslog(message_contains, source, level, limit, minutes_ago)


@mcp.tool()
def rest_messages(
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """Query REST message configurations for outbound integrations"""
    return query_rest_messages(limit, minutes_ago)


@mcp.tool()
def incidents(
    number: str = "",
    sys_id: str = "",
    limit: int = 10,
    minutes_ago: int = 1440,
) -> str:
    """Query incident records by number or sys_id for AI activity context"""
    return query_incidents(number, sys_id, limit, minutes_ago)


if __name__ == "__main__":
    mcp.run()
