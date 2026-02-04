// ServiceNow Background Script to Add Incident Read Access to claude_mcp Role
// Run this in: System Definition > Scripts - Background

// Get the claude_mcp role sys_id
var roleGR = new GlideRecord('sys_user_role');
roleGR.addQuery('name', 'claude_mcp');
roleGR.query();

if (!roleGR.next()) {
    gs.error('claude_mcp role not found. Please create it first.');
} else {
    var roleSysId = roleGR.getUniqueValue();
    gs.info('Found claude_mcp role: ' + roleSysId);

    var tableName = 'incident';

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
            aclGR.description = 'Allow claude_mcp role to read incident records for AI debugging';
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
        } else {
            gs.info('  ○ claude_mcp role already assigned to ' + tableName + ' ACL');
        }

        gs.info('');
        gs.info('=== Permission Setup Complete ===');
        gs.info('✓ Successfully configured read access to incident table');
        gs.info('');
        gs.info('Next steps:');
        gs.info('1. Verify by impersonating mcp.syslog user');
        gs.info('2. Navigate to incident.list and confirm you can see records');
        gs.info('3. Restart Claude Desktop to use the updated MCP server');

    } catch (e) {
        gs.error('✗ Error processing ' + tableName + ': ' + e.message);
    }
}
