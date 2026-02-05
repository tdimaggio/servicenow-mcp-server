# ServiceNow MCP Server

Connect Claude Desktop to your ServiceNow instance for comprehensive debugging and monitoring through natural conversation.

## Overview

This Model Context Protocol (MCP) server enables Claude Desktop to directly query your ServiceNow instance, providing:

- 🤖 **AI Agent Monitoring** - Track AI Agent executions (multi-step agentic AI)
- 📊 **Now Assist Metrics** - Monitor Now Assist usage (summarization, resolution notes, skills)
- 📝 **Now Assist Metadata** - View GenAI prompts, responses, and user feedback
- 📈 **AI ROI Analysis** - Measure AI impact: Do incidents/changes resolve faster with AI?
- 🔄 **Workflow Debugging** - Monitor workflow executions, history, and detailed logs
- 🔍 **Application Logs** - Query syslog entries with flexible filtering
- 🔌 **REST API Configs** - View outbound REST integration configurations
- 🎫 **Incident Lookup** - Query incident details by number or sys_id for AI activity context

### What is MCP?

The Model Context Protocol (MCP) allows AI assistants like Claude to securely connect to external data sources. This server implements MCP to give Claude read-only access to your ServiceNow debugging tables.

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **macOS** with Homebrew installed ([Install Homebrew](https://brew.sh/))
- ✅ **ServiceNow instance** with REST API access
- ✅ **ServiceNow admin access** to create service accounts and set permissions
- ✅ **Claude Pro or Claude Team subscription** - MCP servers require a paid plan
- ✅ **Claude Desktop (macOS)** installed ([Download here](https://claude.ai/download))
- ✅ **Python 3.8+** (we'll install this if needed)

**Important:** MCP (Model Context Protocol) support is currently only available in Claude Desktop for macOS with a paid subscription (Pro or Team). Free Claude accounts and the web version (claude.ai) do not support MCP servers.

**Time required:** 30-45 minutes

---

## Quick Start

**Important:** Complete the ServiceNow configuration section first to create your service account before proceeding with these steps.

### Part 1: ServiceNow Setup (Do This First!)

Before setting up the MCP server, you need to create a service account in ServiceNow. Jump to the [ServiceNow Configuration](#servicenow-configuration) section below and complete:

1. Creating the Service Account
2. Creating the Role  
3. Granting Table Permissions

Once you have your `mcp.syslog` user credentials, come back here to continue.

---

### Part 2: Local MCP Server Setup

#### Step 1: Install Python

Open Terminal and verify Python is installed:

```bash
python3 --version
```

If Python is not installed, install it via Homebrew:

```bash
brew install python
```

#### Step 2: Clone or Download This Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/servicenow-mcp.git
cd servicenow-mcp
```

Or if you downloaded a ZIP, extract it and navigate to the folder:

```bash
cd ~/servicenow-mcp
```

#### Step 3: Set Up Python Virtual Environment

Create and activate a virtual environment to isolate dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

#### Step 4: Install Dependencies

Install the required Python packages:

```bash
pip install mcp requests python-dotenv
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

#### Step 5: Configure ServiceNow Credentials

**Prerequisites:** You must have completed the ServiceNow configuration section and created the `mcp.syslog` service account.

Create a `.env` file in the project root:

```bash
touch .env
```

Edit the file and add your ServiceNow instance details:

```ini
SERVICENOW_INSTANCE=https://your-instance.service-now.com
SERVICENOW_USERNAME=mcp.syslog
SERVICENOW_PASSWORD=your-secure-password-from-servicenow
```

**Important:** 
- Replace `your-instance` with your actual ServiceNow instance name
- Use the password you set when creating the `mcp.syslog` user in ServiceNow
- Never commit this file to version control (it's already in `.gitignore`)

#### Step 6: Test the Connection

Verify your credentials work before proceeding:

```bash
python test_connection.py
```

Expected output:
```
Testing connection to https://your-instance.service-now.com...
Status code: 200
✓ Connection successful!
✓ Found 2 syslog entries
Sample log: [ConversationProcessor] Found 0 unprocessed conversations...
```

If you see errors, verify:
- Your credentials in `.env` are correct
- The `mcp.syslog` user exists and is active in ServiceNow
- The `claude_mcp` role is assigned to the user
- You ran the table permission script (see ServiceNow Configuration section)

#### Step 7: Configure Claude Desktop

Create or edit Claude Desktop's configuration file:

```bash
mkdir -p ~/.claude
nano ~/.claude/config.json
```

Add the following configuration (replace `YOUR_USERNAME` with your actual Mac username):

```json
{
  "mcpServers": {
    "servicenow-debug": {
      "command": "/Users/YOUR_USERNAME/servicenow-mcp/venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/servicenow-mcp/server.py"]
    }
  }
}
```

**Tips:**
- To find your username, run `whoami` in Terminal
- Use absolute paths (starting with `/Users/`)
- Make sure the paths point to your actual installation directory

Save and exit (Ctrl+X, then Y, then Enter if using nano).

#### Step 8: Restart Claude Desktop

1. **Quit Claude Desktop completely** (Cmd+Q or Claude > Quit Claude)
2. **Reopen Claude Desktop**
3. **Verify the connection:**
   - Open Settings > Developer
   - Look for "servicenow-debug" with status "Connected" or "Running"
   - The hammer icon (🔨) should appear in the message input area

#### Step 9: Test in Claude Desktop

Start a new conversation in Claude Desktop and try these queries:

```
Show me recent Now Assist activity

What AI Agents have executed recently?

Show me workflow logs with errors from the last 24 hours

Are there any workflows currently executing?

Show me recent errors from syslog
```

---

## ServiceNow Configuration

### Creating the Service Account

For security, create a dedicated service account for the MCP server:

1. Navigate to **User Administration > Users**
2. Click **New**
3. Fill in:
   - **User ID**: `mcp.syslog`
   - **First name**: `MCP`
   - **Last name**: `Service Account`
   - **Email**: (your admin email)
   - **Password**: (generate a strong password)
   - **Active**: ✓ Checked
   - **Web service access only**: ✓ Checked (recommended)
4. Click **Submit**

### Assigning Roles

The mcp.syslog user needs two roles:

#### 1. Claude MCP Role (for debugging tables)

Create a custom role with read-only access to debugging tables:

1. Navigate to **User Administration > Roles**
2. Click **New**
3. Fill in:
   - **Name**: `claude_mcp`
   - **Description**: `Read-only access to debug tables for Claude MCP server`
4. Click **Submit**
5. Go back to the `mcp.syslog` user
6. In the **Roles** related list, click **Edit**
7. Add the `claude_mcp` role
8. Click **Save**

#### 2. ITIL Role (for incident access)

Add the ITIL role for incident table access:

**Option A: Use the Script (Recommended)**
1. Navigate to **System Definition > Scripts - Background**
2. Copy the script from `add_itil_role_to_mcp_user.js`
3. Paste and run the script
4. Verify output shows "✓ Added itil role to mcp.syslog user"

**Option B: Manual Assignment**
1. Go to the `mcp.syslog` user record
2. In the **Roles** related list, click **Edit**
3. Add the `itil` role
4. Click **Save**

### Granting Table Permissions

The service account needs read access to specific tables. Run the permission script in ServiceNow:

1. Navigate to **System Definition > Scripts - Background**
2. Copy the script from **Appendix A** below
3. Paste it into the "Run script" field
4. Click **Run script**
5. Verify the output shows "✓ Successfully configured: 8 tables"

This script creates Access Control Lists (ACLs) that grant read-only access to:
- `syslog` - Application logs
- `sn_aia_execution_plan` - AI execution plans
- `sys_generative_ai_metric` - GenAI metrics
- `sys_gen_ai_log_metadata` - GenAI metadata
- `sys_rest_message` - REST API configurations
- `wf_context` - Workflow contexts
- `wf_executing` - Currently executing workflows
- `wf_history` - Workflow execution history
- `wf_log` - Workflow detailed logs

### Verify Permissions

Test the service account access:

1. Impersonate the `mcp.syslog` user (Admin menu > Impersonate User)
2. Navigate to **System Logs > System Log > All**
3. Verify you can see log entries
4. Try accessing `sn_aia_execution_plan.list` in the navigator
5. Exit impersonation

If you cannot see records, review the ACL configuration.

---

## Available Tools

Once configured, Claude Desktop can use these tools organized by category:

### AI & GenAI Tools

#### 1. ai_agent_executions
Track AI Agent execution plans (multi-step agentic AI).

**Use this for:** AI Agents that autonomously perform multi-step actions  
**Not for:** Now Assist skills like summarization or resolution notes

**Parameters:**
- `status` - Filter by status
- `limit` - Max results (default 20)
- `minutes_ago` - Time window (default 60)

**Example:** "Show me AI Agent executions from today"

#### 2. now_assist_metrics
Monitor Now Assist usage metrics and activity.

**Use this for:** Now Assist skills (summarization, resolution notes, text generation)  
**Not for:** AI Agents

**Parameters:**
- `limit` - Max results (default 20)
- `minutes_ago` - Time window (default 60)

**Example:** "Show me Now Assist activity from the last hour"

#### 3. now_assist_metadata
View Now Assist metadata with prompts, responses, and user feedback.

**Parameters:**
- `limit` - Max results (default 20)
- `minutes_ago` - Time window (default 60)

**Example:** "Show me Now Assist feedback and prompts"

#### 4. ai_roi_analysis
Analyze AI ROI by comparing resolution times for AI-assisted vs non-AI records.

**Use this for:** Measuring business value - Do incidents/changes resolve faster with AI?

**Metrics by table:**
- `incident` - Mean Time to Resolution (MTTR)
- `change_request` - Mean Time to Implementation
- `problem` - Mean Time to Root Cause
- `sn_customerservice_case` - Mean Time to Closure

**Parameters:**
- `table_name` - Table to analyze: incident, change_request, problem, sn_customerservice_case (default: incident)
- `breakdown_by` - Break down results by: priority, category, group, or none (default: priority)

**Example:** "Analyze AI ROI for incidents"  
**Example:** "Show me AI impact on change request implementation times"  
**Example:** "Do incidents with AI resolve faster than without?"

### Workflow Tools

#### 5. workflow_context
Monitor workflow contexts to see workflow executions.

**Parameters:**
- `limit` - Max results (default 20)
- `minutes_ago` - Time window (default 60)

**Example:** "Show me recent workflow executions"

#### 6. workflow_executing
View currently executing workflows in real-time.

**Parameters:**
- `workflow_name` - Filter by workflow name (partial match)
- `limit` - Max results (default 20)

**Example:** "Are there any workflows currently running?"

#### 7. workflow_history
Query workflow execution history to see completed and failed workflows.

**Parameters:**
- `workflow_name` - Filter by workflow name (partial match)
- `limit` - Max results (default 20)
- `minutes_ago` - Time window (default 1440 = 24 hours)

**Example:** "Show me workflow executions from the last 24 hours"

#### 8. workflow_logs
Query detailed workflow logs including errors and debugging information.

**Parameters:**
- `workflow_name` - Filter by workflow name (partial match)
- `level` - Filter by log level (error, warn, info, debug)
- `limit` - Max results (default 20)
- `minutes_ago` - Time window (default 1440 = 24 hours)

**Example:** "Show me workflow error logs from today"

### System Tools

#### 9. syslog
Query application logs with flexible filtering.

**Parameters:**
- `message_contains` - Filter by message content
- `source` - Filter by log source
- `level` - Filter by level (0=Error, 1=Warning, 2=Info, 3=Debug)
- `limit` - Max results (default 20)
- `minutes_ago` - Time window (default 60)

**Example:** "Show me errors from syslog in the last 30 minutes"

#### 10. rest_messages
View REST message configurations for outbound integrations.

**Parameters:**
- `limit` - Max results (default 20)
- `minutes_ago` - Time window (default 60)

**Example:** "Show me REST API configurations"

#### 11. incidents
Look up incident records by number or sys_id for context when investigating AI activity.

**Use this for:** Getting full incident details when debugging AI operations on tickets

**Parameters:**
- `number` - Incident number (e.g., INC0009005) - supports partial match
- `sys_id` - Incident sys_id for exact lookup
- `limit` - Max results (default 10)
- `minutes_ago` - Time window (default 1440 = 24 hours)

**Example:** "Look up incident INC0009005"  
**Example:** "Show me recent incidents from today"

---

## Project Structure

```
servicenow-mcp/
├── README.md                           # This file
├── server.py                           # Main MCP server entry point
├── test_connection.py                  # Connection test script
├── test_all_tools.py                   # Tool verification script
├── add_table_permissions.js            # ServiceNow ACL permission script
├── add_itil_role_to_mcp_user.js        # Script to add itil role for incident access
├── requirements.txt                    # Python dependencies
├── .env                                # Credentials (not in git)
├── .gitignore                          # Git ignore rules
├── venv/                               # Python virtual environment (not in git)
├── tools/                              # Modular tool implementations
│   ├── __init__.py                     # Tools package initialization
│   ├── ai/                             # AI & GenAI tools
│   │   ├── __init__.py
│   │   ├── ai_agent_executions.py      # AI Agent execution tracking
│   │   ├── now_assist_metrics.py       # Now Assist usage metrics
│   │   ├── now_assist_metadata.py      # Now Assist prompts & feedback
│   │   └── roi_analysis.py             # AI ROI impact analysis
│   ├── workflows/                      # Workflow debugging tools
│   │   ├── __init__.py
│   │   ├── context.py                  # Workflow contexts
│   │   ├── executing.py                # Currently executing workflows
│   │   ├── history.py                  # Workflow execution history
│   │   └── logs.py                     # Detailed workflow logs
│   └── system/                         # System debugging tools
│       ├── __init__.py
│       ├── syslog.py                   # Application logs
│       ├── rest_messages.py            # REST API configurations
│       └── incidents.py                # Incident lookup tool
├── artifacts/                          # Backup files
│   └── server_with_scheduled_jobs_backup.py
└── table_permissions_needed.md         # Permission documentation
```

---

## Troubleshooting

### Server not showing in Claude Desktop

**Symptoms:** The MCP server doesn't appear in Claude Desktop settings.

**Solutions:**
1. Verify paths in `~/.claude/config.json` are absolute and correct
2. Replace `YOUR_USERNAME` with your actual Mac username (`whoami`)
3. Ensure the virtual environment path is correct
4. Check Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log`

### Connection Timeout Errors

**Symptoms:** Queries timeout or return no results.

**Solutions:**
1. Large tables can cause timeouts - use smaller time windows (`minutes_ago=30`)
2. Reduce `limit` parameter (default is 20, try 10)
3. Add more specific filters (message_contains, source, etc.)
4. Check ServiceNow instance performance

### Authentication Errors

**Symptoms:** "401 Unauthorized" or "403 Forbidden" errors.

**Solutions:**
1. Verify `.env` file has correct credentials (no extra spaces)
2. Check the `SERVICENOW_INSTANCE` URL format (include `https://`)
3. Ensure the `mcp.syslog` user is active in ServiceNow
4. Verify the `claude_mcp` role is assigned to the user
5. Run the permission script again (Appendix A)

### Permission Denied (403) Errors

**Symptoms:** Some tools work, others return 403 Forbidden.

**Solutions:**
1. Re-run the permission script in Appendix A
2. Verify ACLs exist: Navigate to **System Security > Access Control (ACL)**
3. Search for the table name (e.g., `sn_aia_execution_plan`)
4. Check that `claude_mcp` role is in "Requires role" related list
5. Some tables (like `sys_generative_ai_log`) require MAINT access and cannot be accessed by service accounts

### No Data Returned

**Symptoms:** Tools work but show "No records found".

**Solutions:**
1. This is normal if your instance hasn't generated that type of data recently
2. Try expanding the time window: `minutes_ago=1440` (24 hours)
3. For `query_scheduled_jobs`, remove all filters to see all jobs
4. Check the actual table in ServiceNow to confirm data exists

### Python Import Errors

**Symptoms:** `ModuleNotFoundError: No module named 'mcp'`

**Solutions:**
1. Activate the virtual environment: `source venv/bin/activate`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Verify you're using the venv Python: `which python` should show `./venv/bin/python`

---

## Security Best Practices

### Credentials
- ✅ Never commit `.env` files to version control
- ✅ Use a dedicated service account, not your personal account
- ✅ Enable "Web service access only" on the service account
- ✅ Use a strong, unique password for the service account
- ✅ Rotate passwords regularly

### Permissions
- ✅ Grant only READ access to tables
- ✅ Use custom roles, not standard admin roles
- ✅ Regularly audit the `mcp.syslog` user's access
- ✅ Disable the account when not in use (optional)

### Network
- ✅ Ensure ServiceNow instance uses HTTPS
- ✅ Consider IP whitelist restrictions on the service account
- ✅ Use ServiceNow's session timeout settings

---

## Development

### Running Tests

Test all tools to verify they work:

```bash
python test_all_tools.py
```

Expected output:
```
================================================================================
ServiceNow MCP Server Tool Test
================================================================================
Instance: https://your-instance.service-now.com
Username: mcp.syslog
================================================================================

Testing: query_syslog (syslog)
  ✓ SUCCESS - 2 records found
  ...

Summary
================================================================================
Total tools tested: 9
✓ Successful: 9
✗ Failed: 0
```

### Adding New Tools

To add a new tool to query additional ServiceNow tables:

1. **Add the table permission** in ServiceNow (use script from Appendix A as template)
2. **Add the tool function** to `server.py`:

```python
@mcp.tool()
def query_new_table(
    limit: int = 20,
    minutes_ago: int = 60,
) -> str:
    """
    Query description here.
    
    Args:
        limit: Maximum number of results (default 20)
        minutes_ago: Look back this many minutes (default 60)
    """
    query_parts = []
    query_parts.append(f"sys_created_onRELATIVEGT@minute@ago@{minutes_ago}")
    query = "^".join(query_parts)

    url = f"{INSTANCE}/api/now/table/your_table_name"
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
        return "No records found matching your criteria."

    output = []
    for entry in results:
        output.append(
            f"[{entry.get('sys_created_on')}]\n"
            f"  Field: {entry.get('field_name', 'N/A')}"
        )
    return "\n---\n".join(output)
```

3. **Test the new tool** with `test_all_tools.py`
4. **Update this README** with the new tool documentation

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-tool`)
3. Commit your changes (`git commit -am 'Add new debugging tool'`)
4. Push to the branch (`git push origin feature/new-tool`)
5. Create a Pull Request

---

## FAQ

### Q: Can I use this with multiple ServiceNow instances?

**A:** Yes! Create separate directories for each instance with different `.env` files, then add multiple entries to `~/.claude/config.json`:

```json
{
  "mcpServers": {
    "servicenow-prod": {
      "command": "/Users/YOUR_USERNAME/servicenow-mcp-prod/venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/servicenow-mcp-prod/server.py"]
    },
    "servicenow-dev": {
      "command": "/Users/YOUR_USERNAME/servicenow-mcp-dev/venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/servicenow-mcp-dev/server.py"]
    }
  }
}
```

### Q: Does this work on Windows or Linux?

**A:** No, not currently. MCP (Model Context Protocol) support is only available in Claude Desktop for macOS. Windows and Linux versions of Claude Desktop do not yet support MCP servers. Check [Anthropic's documentation](https://www.anthropic.com/claude/mcp) for updates on platform availability.

### Q: Can the MCP server modify data in ServiceNow?

**A:** No. The server only has READ access to tables. It cannot create, update, or delete records. All ACLs grant read-only permissions.

### Q: How much does this cost?

**A:** The server itself is free and open source. You need:
- ServiceNow instance (you already have)
- Claude Pro subscription ($20/month) or Claude Team subscription (pricing varies)

### Q: Do I need Claude Pro or can I use the free version?

**A:** You must have a paid Claude subscription (Pro or Team). MCP server support is not available on free Claude accounts. You need:
1. A paid Claude subscription (Pro $20/month or Team)
2. Claude Desktop for macOS installed
3. Both requirements are mandatory - free accounts and web access do not support MCP servers

### Q: Will this slow down my ServiceNow instance?

**A:** No. The queries are read-only and limited (default 20 records). The `minutes_ago` parameter prevents querying huge datasets. It's comparable to a user running reports.

### Q: Can I schedule automated queries?

**A:** MCP servers are interactive only - they respond to Claude Desktop conversations. For automated monitoring, use ServiceNow's built-in alerting or scheduled reports instead.

---

## Credits

Originally created by [Your Name/Team] based on ServiceNow's REST API and Anthropic's Model Context Protocol.

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - Lightweight MCP server framework
- [Requests](https://requests.readthedocs.io/) - HTTP library
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable management

---

## License

MIT License - See LICENSE file for details

---

## Support

- 🐛 **Bug Reports:** [Open an issue](https://github.com/YOUR_USERNAME/servicenow-mcp/issues)
- 💡 **Feature Requests:** [Open an issue](https://github.com/YOUR_USERNAME/servicenow-mcp/issues)
- 📖 **Documentation:** This README and inline code comments
- 💬 **Questions:** [Open a discussion](https://github.com/YOUR_USERNAME/servicenow-mcp/discussions)

---

## Appendix A: Table Permission Script

Run this script in ServiceNow (**System Definition > Scripts - Background**) to grant the `claude_mcp` role access to all required tables:

```javascript
// ServiceNow Background Script to Add Table Permissions to claude_mcp Role
// Run this in: System Definition > Scripts - Background

// Tables to grant read access
var tables = [
    'syslog',
    'sn_aia_execution_plan',
    'sys_generative_ai_metric',
    'sys_gen_ai_log_metadata',
    'sys_rest_message',
    'wf_context',
    'wf_executing',
    'wf_history',
    'wf_log'
];

// Get the claude_mcp role sys_id
var roleGR = new GlideRecord('sys_user_role');
roleGR.addQuery('name', 'claude_mcp');
roleGR.query();

if (!roleGR.next()) {
    gs.error('claude_mcp role not found. Please create it first.');
} else {
    var roleSysId = roleGR.getUniqueValue();
    gs.info('Found claude_mcp role: ' + roleSysId);
    
    var successCount = 0;
    var errorCount = 0;
    
    // Create ACL for each table
    tables.forEach(function(tableName) {
        try {
            // Check if ACL already exists
            var aclGR = new GlideRecord('sys_security_acl');
            aclGR.addQuery('name', tableName);
            aclGR.addQuery('operation', 'read');
            aclGR.query();
            
            var aclSysId;
            if (!aclGR.next()) {
                // Create new ACL
                aclGR.initialize();
                aclGR.name = tableName;
                aclGR.type = 'record';
                aclGR.operation = 'read';
                aclGR.active = true;
                aclGR.description = 'Allow claude_mcp role to read ' + tableName;
                aclSysId = aclGR.insert();
                gs.info('✓ Created ACL for ' + tableName);
            } else {
                aclSysId = aclGR.getUniqueValue();
                gs.info('○ ACL already exists for ' + tableName);
            }
            
            // Add claude_mcp role to ACL
            var aclRoleGR = new GlideRecord('sys_security_acl_role');
            aclRoleGR.addQuery('sys_security_acl', aclSysId);
            aclRoleGR.addQuery('sys_user_role', roleSysId);
            aclRoleGR.query();
            
            if (!aclRoleGR.next()) {
                aclRoleGR.initialize();
                aclRoleGR.sys_security_acl = aclSysId;
                aclRoleGR.sys_user_role = roleSysId;
                aclRoleGR.insert();
                gs.info('  ✓ Added claude_mcp role to ' + tableName + ' ACL');
                successCount++;
            } else {
                gs.info('  ○ claude_mcp role already assigned to ' + tableName + ' ACL');
                successCount++;
            }
        } catch (e) {
            gs.error('  ✗ Error processing ' + tableName + ': ' + e.message);
            errorCount++;
        }
    });
    
    gs.info('');
    gs.info('=== Permission Setup Complete ===');
    gs.info('✓ Successfully configured: ' + successCount + ' tables');
    if (errorCount > 0) {
        gs.info('✗ Errors encountered: ' + errorCount + ' tables');
    }
    gs.info('');
    gs.info('Next steps:');
    gs.info('1. Verify by impersonating mcp.syslog user');
    gs.info('2. Test access to each table');
    gs.info('3. Restart Claude Desktop to use updated MCP server');
}
```

Expected output:
```
*** Script: Found claude_mcp role: ddccc44e3bb6361066a20c9693e45a37
*** Script: ✓ Created ACL for syslog
*** Script:   ✓ Added claude_mcp role to syslog ACL
*** Script: ○ ACL already exists for sn_aia_execution_plan
*** Script:   ✓ Added claude_mcp role to sn_aia_execution_plan ACL
...
*** Script: === Permission Setup Complete ===
*** Script: ✓ Successfully configured: 9 tables
```

---

## Appendix B: requirements.txt

Save this as `requirements.txt` in the project root:

```
mcp>=0.9.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

## Changelog

### Version 2.1.1 (2026-02-04)
- **Fixed incident tool sys_id field**
  - Added sys_id to query results (was showing as "N/A")
  - Incident lookups now return complete information
- **Added itil role script**
  - Created `add_itil_role_to_mcp_user.js` for granting incident access
  - Cleaner approach than modifying ACL scripts
- **Updated documentation**
  - README now reflects 10 tools total
  - Added itil role requirement to setup instructions

### Version 2.1.0 (2026-02-04)
- **Enhanced tool output for better debugging**
  - `now_assist_metrics` now shows: name, type, source, activity, error messages
  - `now_assist_metadata` now shows: source, model, target info, feedback, errors
  - No more useless "N/A" and empty values
- **Added incident lookup tool** 
  - New `incidents` tool in tools/system/
  - Look up by incident number (INC0009005) or sys_id
  - Shows comprehensive incident details (description, state, priority, work notes)
  - Essential for investigating AI activity on specific tickets
- **Tool count: Now 10 working tools**

### Version 2.0.0 (2026-02-02)
- **Major refactoring to modular structure**
  - Organized tools into category-based folders (ai/, workflows/, system/)
  - Improved code maintainability and scalability
  - Each tool now in its own dedicated file
- **Renamed tools for better Claude Desktop tool selection**
  - `query_ai_execution_plans` → `ai_agent_executions` (clearer AI Agent focus)
  - `query_gen_ai_metrics` → `now_assist_metrics` (clearer Now Assist focus)
  - `query_gen_ai_metadata` → `now_assist_metadata`
  - `query_workflow_context` → `workflow_context`
  - Workflow tools simplified naming (removed "query_" prefix)
- **Improved tool descriptions and documentation**
  - Added clear "Use this for" / "Not for" guidance in AI tools
  - Helps Claude Desktop distinguish between AI Agents vs Now Assist
  - Enhanced inline documentation for each tool
- **Removed non-working tools**
  - Removed `scheduled_jobs` (requires admin access, out of scope)
  - Focus on working tools only (9 total)
- **Updated README with categorized tool listing**
  - Tools organized by AI & GenAI, Workflows, System categories
  - Clearer usage examples and parameter documentation

### Version 1.1.0 (2026-02-02)
- Added 3 workflow debugging tools (wf_executing, wf_history, wf_log)
- Enhanced workflow troubleshooting capabilities
- 9 total working tools
- Updated documentation and permission scripts

### Version 1.0.0 (2026-02-02)
- Initial release
- 6 working tools for ServiceNow debugging
- Comprehensive documentation
- Verified table permissions
- Security best practices implemented

---

**Made with ❤️ for ServiceNow admins and developers**
