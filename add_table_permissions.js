// ServiceNow Background Script to Add Table Permissions to claude_mcp Role
// Run this in: System Definition > Scripts - Background

// Tables to grant read access
var tables = [
  "syslog",
  "sn_aia_execution_plan",
  "sys_generative_ai_metric",
  "sys_gen_ai_log_metadata",
  "sys_rest_message",
  "wf_context",
  "wf_executing",
  "wf_history",
  "wf_log",
];

// Get the claude_mcp role sys_id
var roleGR = new GlideRecord("sys_user_role");
roleGR.addQuery("name", "claude_mcp");
roleGR.query();

if (!roleGR.next()) {
  gs.error("claude_mcp role not found");
} else {
  var roleSysId = roleGR.getUniqueValue();
  gs.info("Found claude_mcp role: " + roleSysId);

  var successCount = 0;
  var errorCount = 0;

  // Create ACL for each table
  tables.forEach(function (tableName) {
    try {
      // Check if ACL already exists
      var aclGR = new GlideRecord("sys_security_acl");
      aclGR.addQuery("name", tableName);
      aclGR.addQuery("operation", "read");
      aclGR.query();

      var aclSysId;
      if (!aclGR.next()) {
        // Create new ACL
        aclGR.initialize();
        aclGR.name = tableName;
        aclGR.type = "record";
        aclGR.operation = "read";
        aclGR.active = true;
        aclGR.description = "Allow claude_mcp role to read " + tableName;
        aclSysId = aclGR.insert();
        gs.info("✓ Created ACL for " + tableName + ": " + aclSysId);
      } else {
        aclSysId = aclGR.getUniqueValue();
        gs.info("○ ACL already exists for " + tableName + ": " + aclSysId);
      }

      // Add claude_mcp role to ACL
      var aclRoleGR = new GlideRecord("sys_security_acl_role");
      aclRoleGR.addQuery("sys_security_acl", aclSysId);
      aclRoleGR.addQuery("sys_user_role", roleSysId);
      aclRoleGR.query();

      if (!aclRoleGR.next()) {
        aclRoleGR.initialize();
        aclRoleGR.sys_security_acl = aclSysId;
        aclRoleGR.sys_user_role = roleSysId;
        aclRoleGR.insert();
        gs.info("  ✓ Added claude_mcp role to " + tableName + " ACL");
        successCount++;
      } else {
        gs.info(
          "  ○ claude_mcp role already assigned to " + tableName + " ACL",
        );
        successCount++;
      }
    } catch (e) {
      gs.error("  ✗ Error processing " + tableName + ": " + e.message);
      errorCount++;
    }
  });

  gs.info("");
  gs.info("=== Permission Setup Complete ===");
  gs.info("Successfully configured: " + successCount + " tables");
  if (errorCount > 0) {
    gs.info("Errors encountered: " + errorCount + " tables");
  }
  gs.info("");
  gs.info("Next steps:");
  gs.info("1. Verify by impersonating mcp.syslog user");
  gs.info("2. Test access to each table");
  gs.info("3. Restart Claude Desktop to use updated MCP server");
}
