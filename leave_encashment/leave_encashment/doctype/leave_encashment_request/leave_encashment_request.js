// Copyright (c) 2026, Salumol Baiju and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Encashment Request", {
	refresh(frm) {
		// leave type filter
		frm.trigger("filter_leave_type");
		// preview button to show print format
		frm.trigger("preview_print_format");
	},

	preview_print_format: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Preview"), function() {
				frappe.call({
					method: "leave_encashment.leave_encashment.doctype.leave_encashment_request.leave_encashment_request.generate_preview",
					args: {
						doctype: frm.doctype,
						docname: frm.docname,
					},
					freeze: true,
					callback: (r) => {
						const newWindow = window.open('', '_blank');
						newWindow.document.write(r.message);
						newWindow.document.close();
					},
					error: (r) => {
						frappe.msgprint(r);
					},
				});
			});
		}
	},


	// Fetch salary details for calculation
	employee: function(frm) {
		if (frm.doc.employee) {
			// leave type filter
			frm.trigger("filter_leave_type");
			frm.trigger("get_employee_salary_details");
			frm.trigger("get_employee_leave_details");
			frm.trigger("calculate_encashment_amount");
		}
	},

	filter_leave_type: function(frm) {
		frm.set_query("leave_type", function() {
			return {
				query: "leave_encashment.leave_encashment.doctype.leave_encashment_request.leave_encashment_request.get_encashable_leave_types",
				filters: {
					"is_encashable": 1,
					"employee": frm.doc.employee,
				}
			};
		});
	},

	get_employee_salary_details: function(frm) {
		if (frm.doc.employee && frm.doc.posting_date) {
			frappe.call({
				method: "get_employee_salary_details",
				doc: frm.doc,
				callback: function(r) {
					frm.refresh();
				}
			});
		}
	},

	posting_date: function(frm) {
		frm.trigger("get_employee_salary_details");
		frm.trigger("get_employee_leave_details");
	},

	leave_type: function(frm) {
		frm.trigger("get_employee_leave_details");
	},

	requested_leaves: function(frm) {
		if (frm.doc.requested_leaves > frm.doc.available_encashable_leaves) {
			frappe.throw({
				title: "Invalid Request",
				message: __("Requested Leaves cannot exceed Available Encashable Leaves."),
			});
			frm.set_value("requested_leaves", 0);
		}
		frm.trigger("calculate_encashment_amount");
	},

	get_employee_leave_details: function(frm) {
		if (frm.doc.employee && frm.doc.leave_type && frm.doc.posting_date) {
			frappe.call({
				method: "get_employee_leave_details",
				doc: frm.doc,
				callback: function(r) {
					if (r.message) {
						frm.refresh_fields();
					}
				}
			});
		}
	},

	calculate_encashment_amount: function(frm) {
		if (frm.doc.requested_leaves && frm.doc.leave_salary_per_day) {
			frappe.call({
				method: "calculate_encashment_amount",
				doc: frm.doc,
				callback: function(r) {
					if (r.message) {
						frm.refresh_field("total_encashment_amount");
					}
				}
			});
		}
	},
});
