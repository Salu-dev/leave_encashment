import frappe
from frappe.permissions import add_permission, update_permission_property


def after_install():
    setup_leave_encashment_permissions()


def setup_leave_encashment_permissions():
    """Create or update Role Permissions for Leave Encashment Request."""
    doctype = "Leave Encashment Request"

    role_permissions = {
        "System Manager": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "print": 1,
            "email": 1,
            "export": 1,
            "report": 1,
            "share": 1,
            "import": 1,
        },
        "HR Manager": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "print": 1,
            "email": 1,
            "export": 1,
            "report": 1,
            "share": 1,
            "import": 0,
        },
        "Accounts User": {
            "read": 1,
            "write": 1,
            "create": 0,
            "delete": 0,
            "print": 1,
            "email": 1,
            "export": 1,
            "report": 1,
            "share": 0,
            "import": 0,
        },
        "Employee": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "print": 1,
            "email": 0,
            "export": 0,
            "report": 0,
            "share": 0,
            "if_owner": 1,
            "import": 0,
        },
        
    }

    for role, permissions in role_permissions.items():
        # Create permission row if it does not exist
        add_permission(doctype, role, permlevel=0)

        # Update all permission properties
        for perm_type, value in permissions.items():
            update_permission_property(
                doctype=doctype,
                role=role,
                permlevel=0,
                ptype=perm_type,
                value=value,
            )

    frappe.clear_cache(doctype=doctype)
    frappe.db.commit()
