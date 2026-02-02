"""
System debugging tools for ServiceNow
"""

from .rest_messages import query_rest_messages
from .syslog import query_syslog

__all__ = [
    "query_syslog",
    "query_rest_messages",
]
