# Copyright (c) 2026, Salumol Baiju and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LeaveEncashmentRequest(Document):
	def validate(self):
		self.validate_date()
		self.validate_leave_type()
		self.validate_requested_leaves()

	def before_save(self):
		old_doc = self.get_doc_before_save()

		# Calculate encashment amount for new records or when relevant fields change
		if (
			self.is_new()
			or old_doc
			and (old_doc.requested_leaves != self.requested_leaves
			or old_doc.leave_salary_per_day != self.leave_salary_per_day)
		):
			self.calculate_encashment_amount()

		# Automatically create an Additional Salary record
		if old_doc and (old_doc.status != "Approved" and self.status == "Approved"):
			self.create_additional_salary()


	def calculate_encashment_amount(self):	
		if self.requested_leaves and self.leave_salary_per_day:
			self.total_encashment_amount = self.requested_leaves * self.leave_salary_per_day

	def validate_date(self):
		if self.posting_date and self.posting_date < frappe.utils.today():
			frappe.throw("Posting Date cannot be in the past")

	def validate_leave_type(self):
		if self.leave_type:
			leave_type = get_leave_type(self.employee)
			if leave_type and self.leave_type not in leave_type:
				frappe.throw("Selected Leave Type does not allow encashment")

			# # Check if employee has already submitted a leave encashment request for the same leave type
			# existing_request = frappe.db.exists("Leave Encashment Request", {
			# 	"employee": self.employee,
			# 	"leave_type": self.leave_type,
			# 	"status": "Approved"
			# })
			# if existing_request:
			# 	frappe.throw("Employee has already submitted a leave encashment request for the same leave type")

	def validate_requested_leaves(self):
		if self.requested_leaves:
			leave_balance = get_employee_leave_balance(self.employee, self.leave_type)
			if leave_balance and self.requested_leaves > leave_balance:
				frappe.throw("Requested leaves cannot be more than available leave balance")

			# check if requested leave is not more than allowed limit
			allowed_limit = frappe.db.get_value("Leave Type", self.leave_type, "max_encashment_limit")
			if allowed_limit and self.requested_leaves > allowed_limit:
				frappe.throw("Requested leaves cannot be more than allowed limit")

			
	def create_additional_salary(self):
		# Create Additional Salary record
		additional_salary = frappe.new_doc("Additional Salary")
		additional_salary.employee = self.employee
		additional_salary.salary_component = "Leave Encashment"
		additional_salary.amount = self.total_encashment_amount
		additional_salary.payroll_date = self.posting_date
		additional_salary.type = "Deduction"
		additional_salary.save()
		additional_salary.submit()
			
# Fetch employee leave balance based on selected Leave Type 
@frappe.whitelist()
def get_employee_leave_balance(employee, leave_type):
    leave_balance = frappe.db.get_value("Leave Allocation", {"employee": employee, "leave_type": leave_type}, "total_leaves_allocated")
    return leave_balance

# Fetch salary details for calculation 
@frappe.whitelist()
def get_employee_salary_details(employee):
    salary_details = frappe.db.get_value("Salary Structure Assignment", {"employee": employee},"leave_encashment_amount_per_day")
    return salary_details


@frappe.whitelist()
def get_leave_type(employee):

	leave_types = frappe.db.sql(""" SELECT DISTINCT lt.name 
	FROM `tabLeave Type` lt
	JOIN `tabLeave Allocation` la ON lt.name = la.leave_type
	WHERE lt.allow_encashment = 1
	AND la.employee = %(employee)s
	AND la.total_leaves_allocated > 0
	""", {"employee": employee})

	return leave_types

@frappe.whitelist()
def get_encashable_leave_types(doctype, txt, searchfield, start, page_len, filters):
	employee=filters.get("employee")
	if not employee:
		return []
	return get_leave_type(employee)
	
	


