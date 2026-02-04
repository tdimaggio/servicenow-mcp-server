// ServiceNow Background Script to Add ITIL Role to mcp.syslog User
// Run this in: System Definition > Scripts - Background
//
// This grants the mcp.syslog user the itil role for incident read access

// Find the mcp.syslog user
var userGR = new GlideRecord('sys_user');
userGR.addQuery('user_name', 'mcp.syslog');
userGR.query();

if (!userGR.next()) {
    gs.error('mcp.syslog user not found!');
} else {
    var userSysId = userGR.getUniqueValue();
    gs.info('Found mcp.syslog user: ' + userSysId);

    // Find the itil role
    var roleGR = new GlideRecord('sys_user_role');
    roleGR.addQuery('name', 'itil');
    roleGR.query();

    if (!roleGR.next()) {
        gs.error('itil role not found!');
    } else {
        var roleSysId = roleGR.getUniqueValue();
        gs.info('Found itil role: ' + roleSysId);

        // Check if user already has the role
        var userRoleGR = new GlideRecord('sys_user_has_role');
        userRoleGR.addQuery('user', userSysId);
        userRoleGR.addQuery('role', roleSysId);
        userRoleGR.query();

        if (userRoleGR.next()) {
            gs.info('○ mcp.syslog already has itil role');
        } else {
            // Add the role
            userRoleGR.initialize();
            userRoleGR.user = userSysId;
            userRoleGR.role = roleSysId;
            userRoleGR.insert();
            gs.info('✓ Added itil role to mcp.syslog user');
        }

        gs.info('');
        gs.info('=== Role Assignment Complete ===');
        gs.info('✓ mcp.syslog now has itil role for incident access');
        gs.info('');
        gs.info('Next steps:');
        gs.info('1. Test by impersonating mcp.syslog user');
        gs.info('2. Navigate to incident.list and confirm you see records');
        gs.info('3. Restart Claude Desktop to test incident lookup');
    }
}
