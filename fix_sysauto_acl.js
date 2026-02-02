// ServiceNow Background Script to Fix sysauto ACL
// Run this in: System Definition > Scripts - Background
//
// PROBLEM: The sysauto table ACL has admin_overrides=true, which means
// even though claude_mcp role is in the required roles list, only users
// with the admin role can actually see records.
//
// SOLUTION: Set admin_overrides=false so that any user with one of the
// required roles (including claude_mcp) can read sysauto records.

gs.info('=== Fixing sysauto ACL for claude_mcp access ===');

// Find the sysauto read ACL
var aclGR = new GlideRecord('sys_security_acl');
aclGR.addQuery('name', 'sysauto');
aclGR.addQuery('operation', 'read');
aclGR.query();

if (aclGR.next()) {
    gs.info('Found sysauto read ACL: ' + aclGR.getUniqueValue());
    gs.info('Current settings:');
    gs.info('  - Name: ' + aclGR.getValue('name'));
    gs.info('  - Operation: ' + aclGR.operation.getDisplayValue());
    gs.info('  - Admin Overrides: ' + aclGR.getValue('admin_overrides'));
    gs.info('  - Active: ' + aclGR.getValue('active'));
    gs.info('  - Description: ' + aclGR.getValue('description'));

    // Check current roles
    var currentRoles = [];
    var roleGR = new GlideRecord('sys_security_acl_role');
    roleGR.addQuery('sys_security_acl', aclGR.getUniqueValue());
    roleGR.query();
    while (roleGR.next()) {
        currentRoles.push(roleGR.sys_user_role.getDisplayValue());
    }
    gs.info('  - Required Roles: ' + currentRoles.join(', '));

    // Fix the issue
    if (aclGR.getValue('admin_overrides') == 'true') {
        gs.info('');
        gs.info('✓ Disabling admin_overrides to allow role-based access...');
        aclGR.setValue('admin_overrides', false);
        aclGR.setValue('description', 'Allow users with required roles to read Scheduled Jobs (claude_mcp, admin, import_admin, import_scheduler)');
        aclGR.update();

        gs.info('');
        gs.info('=== FIX APPLIED SUCCESSFULLY ===');
        gs.info('The sysauto table can now be accessed by users with:');
        gs.info('  - claude_mcp role');
        gs.info('  - admin role');
        gs.info('  - import_admin role');
        gs.info('  - import_scheduler role');
        gs.info('');
        gs.info('Next steps:');
        gs.info('1. Test access as mcp.syslog user');
        gs.info('2. Run: python test_all_tools.py');
        gs.info('3. Verify scheduled jobs are returned');
    } else {
        gs.info('');
        gs.info('⚠ admin_overrides is already set to false');
        gs.info('The ACL should be working correctly with role-based access');
        gs.info('');
        gs.info('If access is still not working, check:');
        gs.info('1. Ensure mcp.syslog user has claude_mcp role');
        gs.info('2. Check for query business rules that might filter records');
        gs.info('3. Verify no domain separation is applied to sysauto');
    }
} else {
    gs.error('✗ sysauto read ACL not found');
    gs.error('');
    gs.error('The ACL may have been deleted or renamed.');
    gs.error('You may need to recreate it manually or use the add_table_permissions.js script');
}
