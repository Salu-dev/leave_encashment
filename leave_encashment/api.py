import frappe 

# api for create leave encashment requests
@frappe.whitelist(allow_guest=True)
def create_leave_encashment_request():
    try:
        data=frappe.form_dict
        employee=data.get("employee")
        if not employee:
            return {"status": "error", "message": "Employee is required"}
        posting_date=data.get("posting_date")
        if not posting_date:
            return {"status": "error", "message": "Posting Date is required"}
        leave_type=data.get("leave_type")
        if not leave_type:
            return {"status": "error", "message": "Leave Type is required"}
        requested_leaves=data.get("requested_leaves")
        if not requested_leaves:
            return {"status": "error", "message": "Requested Leaves is required"}
        leave_encashment_doc=frappe.new_doc("Leave Encashment Request")
        leave_encashment_doc.employee=employee
        leave_encashment_doc.posting_date=posting_date
        leave_encashment_doc.leave_type=leave_type
        leave_encashment_doc.requested_leaves=requested_leaves
        leave_encashment_doc.insert()
        return {"status": "success", "message": "Leave Encashment Request Created Successfully", "doc": leave_encashment_doc.as_dict()}
             
    except Exception as e:
        frappe.log_error(e, "Leave Encashment Request Creation Error")
        return {"status": "error", "message": str(e)}
        
