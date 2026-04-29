import frappe
from frappe import _

@frappe.whitelist()
def send_notification(doc, method):
    old_doc = doc.get_doc_before_save()
    
    if not old_doc:
        return
    
    # Send notification when status changes to Pending Approval
    if old_doc.status != "Pending Approval" and doc.status == "Pending Approval":
        send_approval_notification(doc, "Pending Approval")
    
    # Send notification when status changes to Approved
    if old_doc.status != "Approved" and doc.status == "Approved":
        send_status_change_notification(doc, "Approved")
        send_approval_notification(doc, "Approved")
    
    # Send notification when status changes to Rejected
    if old_doc.status != "Rejected" and doc.status == "Rejected":
        send_status_change_notification(doc, "Rejected")
    
    # Send notification when status changes to Paid
    if old_doc.status != "Paid" and doc.status == "Paid":
        send_status_change_notification(doc, "Paid")


def get_hr_managers():
    """Get all active users with HR Manager role in the same company"""
    return get_active_users_with_role("HR Manager")

def get_account_users():
    """Get all active users with Account User role in the same company"""
    return get_active_users_with_role("Accounts User")

def get_active_users_with_role(role):
    """Get user details for users with a specific role and matching company"""
    role_based_users = frappe.get_all("Has Role", filters={"role": role, "parenttype": "User", "parent": ["!=", "Administrator"]}, fields=["parent"])
    matching_users = []
    for user in role_based_users:
        # Check if user is enabled
        if not frappe.get_value("User", user.parent, "enabled"):
            continue
        matching_users.append(user.parent)
    
    return matching_users


def get_submitted_user(doc):
    """Get the user who create the document"""
    employee_mail_id = frappe.db.get_value("Employee", {"name": doc.employee}, "user_id")
    return employee_mail_id


def send_status_change_notification(doc, status):
    """Send notification to submitted user when status changes"""
    recipient = get_submitted_user(doc)
    
    if not recipient:
        return
    
    if status == "Approved":
        subject = _("Your Leave Encashment Request has been Approved - {0}").format(doc.name)
        message = "Your Leave Encashment Request has been <strong>Approved</strong>."
        message += "The amount will be processed in your next payroll cycle."
        
    elif status == "Rejected":
        subject = _("Your Leave Encashment Request has been Rejected - {0}").format(doc.name)
        message = "Your Leave Encashment Request has been <strong>Rejected</strong>.<\n>"
        message += "Please contact your HR Manager for more details."
        
    elif status == "Paid":
        subject = _("Your Leave Encashment Request has been Paid - {0}").format(doc.name)
        message = "Your Leave Encashment Request has been <strong>Paid</strong>."
        message += "<p>The amount has been included in your salary payment.</p>"
        message += "<p><a href='{4}'>View Request</a></p>"
    else:
        return

           
    args = {
        "message": message,
        "employee_name": doc.employee,
        "leave_type": doc.leave_type,
        "encashed_leaves": doc.requested_leaves,
        "total_encashment_amount": doc.total_encashment_amount,
        "request_url": frappe.utils.get_url_to_form("Leave Encashment Request", doc.name)
    }
    if not recipient:
        return
    
    frappe.sendmail(
        template="leave_encashment_approval_request",
        recipients=[recipient],
        subject=subject,
        args=args,
        header=[subject, "green"],
        now=True
    )

def send_approval_notification(doc, status):
    
    if status == "Pending Approval":
        recipients = get_hr_managers()
        subject = _("Action Required: Leave Encashment Request Pending for Approval - {0}").format(doc.name)
        message = "A new Leave Encashment Request requires your approval."
    elif status == "Approved":
        recipients = get_account_users()
        subject = _("Leave Encashment Request Approved - {0}").format(doc.name)
        message = "A Leave Encashment Request has been approved and requires payroll processing."
       
    else:
        return

    if not recipients:
        return

    args = {

            "message": message,
            "employee_name": doc.employee,
            "leave_type": doc.leave_type,
            "encashed_leaves": doc.requested_leaves,
            "total_encashment_amount": doc.total_encashment_amount,
            "request_url": frappe.utils.get_url_to_form("Leave Encashment Request", doc.name)
        }
    
    frappe.sendmail(
        template="leave_encashment_approval_request",
        recipients=recipients,
        subject=subject,
        args=args,
        header=[subject, "blue"],
        now=True
    )

@frappe.whitelist()
def pending_approval_reminder():
    try:
        pending_approvals = frappe.get_all("Leave Encashment Request", filters={
            "status": "Pending Approval",
            "posting_date": ["<", frappe.utils.add_days(frappe.utils.nowdate(), -3)]
        }, fields=["name", "employee", "employee_name", "leave_type", "requested_leaves", "total_encashment_amount", "posting_date"])
        
        if not pending_approvals:
            return
        
        # Add URL to each approval
        for approval in pending_approvals:
            approval.url = frappe.utils.get_url_to_form("Leave Encashment Request", approval.name)
        
        # get hr managers
        hr_managers = get_active_users_with_role("HR Manager")
        if not hr_managers:
            return

        subject = "Pending Approval Reminder - Leave Encashment Request"
        message = "The following Leave Encashment Requests are pending approval:"
        args = {
            "message": message,
            "pending_approvals": pending_approvals,
        }

        frappe.sendmail(
            template="leave_encashment_approval_reminder",
            recipients=hr_managers,
            subject=subject,
            args=args,
            now=True
        )

    except Exception as e:
        frappe.log_error(e, "Pending Approval Reminder Error")
        return