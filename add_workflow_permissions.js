// ServiceNow Background Script to Add Workflow Table Permissions
// Run this in: System Definition > Scripts - Background
//
// This script grants read access to workflow debugging tables for the claude_mcp role

gs.info('=== Adding Workflow Table Permissions to claude_mcp Role ===');

// Workflow tables to grant read access
var tables = [
    'wf_executing',
    'wf_history',
    'wf_log'
];

// Get the claude_mcp role sys_id
var roleGR = new GlideRecord('sys_user_role');
roleGR.addQuery('name', 'claude_mcp');
roleGR.query();

if (!roleGR.next()) {
    gs.error('✗ claude_mcp role not found. Please create it first.');
} else {
    var roleSysId = roleGR.getUniqueValue();
    gs.info('Found claude_mcp role: ' + roleSysId);

    var successCount = 0;
    var errorCount = 0;

    // Create ACL for each table
    tables.forEach(function(tableName) {
        try {
            gs.info('');
            gs.info('Processing table: ' + tableName);

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
                aclGR.admin_overrides = false;  // Important: Allow role-based access
                aclGR.description = 'Allow claude_mcp role to read ' + tableName + ' for workflow debugging';
                aclSysId = aclGR.insert();
                gs.info('  ✓ Created ACL for ' + tableName);
            } else {
                aclSysId = aclGR.getUniqueValue();
                gs.info('  ○ ACL already exists for ' + tableName);

                // Check if admin_overrides is set (potential issue)
                if (aclGR.getValue('admin_overrides') == 'true') {
                    gs.warn('  ⚠ WARNING: admin_overrides is set to true on this ACL');
                    gs.warn('  ⚠ This may prevent non-admin users from accessing records');
                    gs.warn('  ⚠ Consider setting admin_overrides=false if access issues occur');
                }
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
    gs.info('Tables configured:');
    gs.info('  - wf_executing: Currently executing workflows');
    gs.info('  - wf_history: Workflow execution history');
    gs.info('  - wf_log: Detailed workflow logs');
    gs.info('');
    gs.info('Next steps:');
    gs.info('1. Test access by impersonating mcp.syslog user');
    gs.info('2. Navigate to wf_executing.list, wf_history.list, wf_log.list');
    gs.info('3. Run test_workflow_access.py to verify');
    gs.info('4. Restart Claude Desktop to use the new tools');
}
