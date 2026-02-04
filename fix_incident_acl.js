// ServiceNow Background Script to Fix Incident ACL for claude_mcp Role
// Run this in: System Definition > Scripts - Background
//
// PROBLEM: The default incident read ACL has admin_overrides=true and a script
// that checks ApproverUtils, which blocks non-admin users even with the role.
//
// SOLUTION: Modify the ACL script to allow claude_mcp role OR existing logic

// Get the claude_mcp role sys_id
var roleGR = new GlideRecord('sys_user_role');
roleGR.addQuery('name', 'claude_mcp');
roleGR.query();

if (!roleGR.next()) {
    gs.error('claude_mcp role not found. Please create it first.');
} else {
    var roleSysId = roleGR.getUniqueValue();
    gs.info('Found claude_mcp role: ' + roleSysId);

    // Find the incident read ACL
    var aclGR = new GlideRecord('sys_security_acl');
    aclGR.addQuery('name', 'incident');
    aclGR.addQuery('operation', 'read');
    aclGR.query();

    if (!aclGR.next()) {
        gs.error('Incident read ACL not found!');
    } else {
        gs.info('Found incident read ACL: ' + aclGR.getUniqueValue());
        gs.info('  Current admin_overrides: ' + aclGR.admin_overrides);
        gs.info('  Current script: ' + aclGR.script);

        // Check if claude_mcp role is already in the ACL script
        var currentScript = aclGR.script + '';
        if (currentScript.indexOf('claude_mcp') > -1) {
            gs.info('✓ claude_mcp already in ACL script - no changes needed');
        } else {
            // Update the script to allow claude_mcp role OR existing logic
            var newScript =
                "// Allow claude_mcp role for MCP server debugging\n" +
                "if (gs.hasRole('claude_mcp')) {\n" +
                "    answer = true;\n" +
                "} else {\n" +
                "    // Original logic\n" +
                "    answer = new ApproverUtils().canApproversRead();\n" +
                "}";

            aclGR.script = newScript;
            aclGR.update();

            gs.info('✓ Updated incident ACL script to allow claude_mcp role');
            gs.info('');
            gs.info('New script:');
            gs.info(newScript);
        }

        gs.info('');
        gs.info('=== Permission Fix Complete ===');
        gs.info('✓ claude_mcp role can now read incident records');
        gs.info('');
        gs.info('Next steps:');
        gs.info('1. Test by impersonating mcp.syslog user');
        gs.info('2. Navigate to incident.list and confirm you see records');
        gs.info('3. Restart Claude Desktop to use the updated access');
    }
}
