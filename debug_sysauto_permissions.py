#!/usr/bin/env python3
"""
Debug script to investigate sysauto table permissions
This will help us understand why mcp.syslog can't access sysauto records
"""

import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

INSTANCE = os.getenv("SERVICENOW_INSTANCE")
MCP_USERNAME = os.getenv("SERVICENOW_USERNAME")
MCP_PASSWORD = os.getenv("SERVICENOW_PASSWORD")
ADMIN_USERNAME = os.getenv("SERVICENOW_ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("SERVICENOW_ADMIN_PASSWORD")


def test_table_access(username, password, table_name, user_label):
    """Test access to a table with specific credentials"""
    print(f"\n{'=' * 80}")
    print(f"Testing {table_name} access as: {user_label} ({username})")
    print("=" * 80)

    url = f"{INSTANCE}/api/now/table/{table_name}"
    params = {
        "sysparm_limit": 5,
        "sysparm_display_value": "true",
        "sysparm_fields": "sys_id,name,sys_created_on,active",
    }

    response = requests.get(
        url,
        params=params,
        auth=(username, password),
        headers={"Accept": "application/json"},
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        results = response.json().get("result", [])
        print(f"✓ Records returned: {len(results)}")
        if results:
            print(f"  Sample record: {results[0].get('name', 'N/A')}")
    else:
        print(f"✗ Error: {response.text}")

    return response


def check_acl_configuration(username, password, user_label):
    """Check ACL configuration for sysauto table"""
    print(f"\n{'=' * 80}")
    print(f"Checking ACL Configuration as: {user_label}")
    print("=" * 80)

    # Query ACLs for sysauto
    url = f"{INSTANCE}/api/now/table/sys_security_acl"
    params = {
        "sysparm_query": "name=sysauto^operation=read",
        "sysparm_display_value": "true",
        "sysparm_fields": "sys_id,name,operation,type,active,description,script,condition,admin_overrides",
    }

    response = requests.get(
        url,
        params=params,
        auth=(username, password),
        headers={"Accept": "application/json"},
    )

    if response.status_code == 200:
        acls = response.json().get("result", [])
        print(f"Found {len(acls)} ACL(s) for sysauto read operation")
        for acl in acls:
            print(f"\n  ACL sys_id: {acl.get('sys_id')}")
            print(f"  Name: {acl.get('name')}")
            print(f"  Operation: {acl.get('operation')}")
            print(f"  Type: {acl.get('type')}")
            print(f"  Active: {acl.get('active')}")
            print(f"  Admin Overrides: {acl.get('admin_overrides')}")
            print(f"  Description: {acl.get('description', 'N/A')}")
            print(f"  Has Script: {'Yes' if acl.get('script') else 'No'}")
            print(f"  Has Condition: {'Yes' if acl.get('condition') else 'No'}")

            # Get roles for this ACL
            acl_id = acl.get("sys_id")
            if acl_id:
                check_acl_roles(username, password, acl_id)
    else:
        print(f"✗ Error getting ACLs: {response.text}")


def check_acl_roles(username, password, acl_id):
    """Check which roles are assigned to an ACL"""
    url = f"{INSTANCE}/api/now/table/sys_security_acl_role"
    params = {
        "sysparm_query": f"sys_security_acl={acl_id}",
        "sysparm_display_value": "true",
        "sysparm_fields": "sys_user_role",
    }

    response = requests.get(
        url,
        params=params,
        auth=(username, password),
        headers={"Accept": "application/json"},
    )

    if response.status_code == 200:
        roles = response.json().get("result", [])
        if roles:
            role_names = []
            for r in roles:
                role_val = r.get("sys_user_role")
                if isinstance(role_val, dict):
                    role_names.append(role_val.get("display_value", "Unknown"))
                else:
                    role_names.append(str(role_val))
            print(f"  Required Roles: {', '.join(role_names)}")
        else:
            print(f"  Required Roles: None (public access)")
    else:
        print(f"  Could not retrieve roles")


def check_user_roles(username, password, user_label, target_username):
    """Check what roles a user has"""
    print(f"\n{'=' * 80}")
    print(f"Checking roles for user: {target_username}")
    print("=" * 80)

    # First get the user sys_id
    url = f"{INSTANCE}/api/now/table/sys_user"
    params = {
        "sysparm_query": f"user_name={target_username}",
        "sysparm_display_value": "true",
        "sysparm_fields": "sys_id,user_name,name,active",
    }

    response = requests.get(
        url,
        params=params,
        auth=(username, password),
        headers={"Accept": "application/json"},
    )

    if response.status_code == 200:
        users = response.json().get("result", [])
        if users:
            user = users[0]
            user_id = user.get("sys_id")
            print(f"User: {user.get('name')} ({user.get('user_name')})")
            print(f"Active: {user.get('active')}")

            # Get user's roles
            url = f"{INSTANCE}/api/now/table/sys_user_has_role"
            params = {
                "sysparm_query": f"user={user_id}^state=active",
                "sysparm_display_value": "true",
                "sysparm_fields": "role,inherited",
            }

            response = requests.get(
                url,
                params=params,
                auth=(username, password),
                headers={"Accept": "application/json"},
            )

            if response.status_code == 200:
                user_roles = response.json().get("result", [])
                print(f"\nTotal Roles: {len(user_roles)}")
                for role in user_roles:
                    inherited = role.get("inherited", "false")
                    marker = " (inherited)" if inherited == "true" else ""
                    print(f"  - {role.get('role')}{marker}")
            else:
                print(f"✗ Could not retrieve roles")
    else:
        print(f"✗ Error getting user: {response.text}")


def check_query_business_rules(username, password):
    """Check for query business rules on sysauto table"""
    print(f"\n{'=' * 80}")
    print(f"Checking for Query Business Rules on sysauto")
    print("=" * 80)

    url = f"{INSTANCE}/api/now/table/sys_script"
    params = {
        "sysparm_query": "collection=sysauto^when=before^ORwhen=async",
        "sysparm_display_value": "true",
        "sysparm_fields": "sys_id,name,when,active,description",
    }

    response = requests.get(
        url,
        params=params,
        auth=(username, password),
        headers={"Accept": "application/json"},
    )

    if response.status_code == 200:
        rules = response.json().get("result", [])
        print(f"Found {len(rules)} business rule(s) on sysauto")
        for rule in rules:
            print(f"\n  Rule: {rule.get('name')}")
            print(f"  When: {rule.get('when')}")
            print(f"  Active: {rule.get('active')}")
            print(f"  Description: {rule.get('description', 'N/A')}")
    else:
        print(f"✗ Error checking business rules")


def main():
    print("\n" + "=" * 80)
    print("SYSAUTO PERMISSIONS DIAGNOSTIC TOOL")
    print("=" * 80)

    # Test 1: Access with both users
    test_table_access(ADMIN_USERNAME, ADMIN_PASSWORD, "sysauto", "ADMIN")
    test_table_access(MCP_USERNAME, MCP_PASSWORD, "sysauto", "MCP Service Account")

    # Test 2: Check ACL configuration
    check_acl_configuration(ADMIN_USERNAME, ADMIN_PASSWORD, "ADMIN")

    # Test 3: Check user roles
    check_user_roles(ADMIN_USERNAME, ADMIN_PASSWORD, "ADMIN", MCP_USERNAME)
    check_user_roles(ADMIN_USERNAME, ADMIN_PASSWORD, "ADMIN", ADMIN_USERNAME)

    # Test 4: Check for query business rules
    check_query_business_rules(ADMIN_USERNAME, ADMIN_PASSWORD)

    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Review the ACL configuration above")
    print("2. Check if admin_overrides is set to true")
    print("3. Look for scripts or conditions that may filter records")
    print("4. Check if there are query business rules adding conditions")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
