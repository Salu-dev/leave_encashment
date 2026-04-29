import frappe

def adjust_user_permissions(doc, method=None):
    roles = [row.role for row in doc.roles]

    if "HR Manager" in roles or "Accounts User" in roles:
        frappe.db.delete(
            "User Permission",
            {
                "user": doc.name,
                "allow": "Employee"
            }
        )