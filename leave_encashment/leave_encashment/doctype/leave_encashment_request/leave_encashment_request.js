// Copyright (c) 2026, Salumol Baiju and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Encashment Request", {
	refresh(frm) {
          // leave type filter
        frm.trigger("filter_leave_type");

	},

// Fetch salary details for calculation 
employee:function(frm){
    if (frm.doc.employee) {
        // leave type filter
        frm.trigger("filter_leave_type");
        frm.trigger("get_employee_salary_details");

    }
},

filter_leave_type: function(frm) {
    frm.set_query("leave_type", function() {
        return {
            query: "leave_encashment.leave_encashment.doctype.leave_encashment_request.leave_encashment_request.get_encashable_leave_types",
            filters: {

                "is_encashable": 1,
                "employee": frm.doc.employee,
                "leave_balance":[">", 0]

            }
        };
    });
},

get_employee_salary_details: function(frm) {
    frappe.call({
            method: "leave_encashment.leave_encashment.doctype.leave_encashment_request.leave_encashment_request.get_employee_salary_details",
            args: {
                employee: frm.doc.employee
            },
            callback: function(r) {
                frm.set_value("leave_salary_per_day", r.message);
            }
        });
},  

leave_type: function(frm) {
    
    if (frm.doc.leave_type) {
      
    //  Fetch employee leave balance based on selected Leave Type 
    frappe.call({
        method: "leave_encashment.leave_encashment.doctype.leave_encashment_request.leave_encashment_request.get_employee_leave_balance",
        args: {
            employee: frm.doc.employee,
            leave_type: frm.doc.leave_type
        },
        callback: function(r) {
            if (r.message) {
                frm.set_value("available_leave_balance", r.message);
            }
        }
    });
    }
}
});
