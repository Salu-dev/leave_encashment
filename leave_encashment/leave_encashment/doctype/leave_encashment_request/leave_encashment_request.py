# Copyright (c) 2026, Salumol Baiju and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt
from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on
from hrms.hr.utils import validate_active_employee
from hrms.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
	get_assigned_salary_structure,
)


class LeaveEncashmentRequest(Document):
	def validate(self):
		validate_active_employee(self.employee)
		self.get_employee_salary_details()
		self.get_employee_leave_details()
		self.validate_duplicate_request()
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

	def on_update(self):
		old_doc = self.get_doc_before_save()
		if old_doc and (old_doc.status != "Approved" and self.status == "Approved"):
			# Automatically create an Additional Salary record and update leave allocation
			self.update_leave_allocation()
			self.create_additional_salary()

	@frappe.whitelist()
	def calculate_encashment_amount(self):
		if self.requested_leaves == 0 or not self.leave_salary_per_day:
			frappe.throw("Requested leaves and leave salary per day are required to calculate encashment amount")
		if self.requested_leaves and self.leave_salary_per_day:
			self.total_encashment_amount = flt(self.requested_leaves) * flt(self.leave_salary_per_day)

	def validate_duplicate_request(self):
		# Check if there's already an draft or pending approval encashment request for the same employee and leave type
		existing_request = frappe.db.exists(
			"Leave Encashment Request",
			{
				"employee": self.employee,
				"leave_type": self.leave_type,
				"leave_allocation": self.leave_allocation,
				"status": ["in", ["Draft", "Pending Approval"]],
				"name": ["!=", self.name]  
			}
		)	
		if existing_request:
			frappe.throw(f"A draft or pending approval encashment request already exists for this employee and leave type {existing_request	}")

	def validate_requested_leaves(self):
		# Validate that requested leaves do not exceed encashable leaves
		if self.requested_leaves:
			requested = flt(self.requested_leaves)
			available = flt(self.available_encashable_leaves)
			if requested > available:
				frappe.throw("Requested leaves cannot be more than available encashable leaves")

	def update_leave_allocation(self):
		# Update leave allocation to reduce encashed leaves
		frappe.db.set_value(
			"Leave Allocation",
			self.leave_allocation,
			"total_leaves_encashed",
			frappe.db.get_value("Leave Allocation", self.leave_allocation, "total_leaves_encashed")
			+ self.requested_leaves,
		)
	def create_additional_salary(self):
		# Create Additional Salary record
		additional_salary = frappe.new_doc("Additional Salary")
		additional_salary.company =self.company
		additional_salary.employee = self.employee
		additional_salary.currency = self.currency
		earning_component = frappe.get_value("Leave Type", self.leave_type, "earning_component")
		if not earning_component:
			frappe.throw(_("Please set Earning Component for Leave type: {0}.").format(self.leave_type))
		additional_salary.salary_component = earning_component
		additional_salary.payroll_date = self.posting_date
		additional_salary.amount = self.total_encashment_amount
		additional_salary.overwrite_salary_structure_amount = 0
		additional_salary.ref_doctype = self.doctype
		additional_salary.ref_docname = self.name
		additional_salary.overwrite_salary_structure_amount = 0
		additional_salary.ref_doctype = self.doctype
		additional_salary.ref_docname = self.name
		additional_salary.submit()
		self.db_set("additional_salary_reference", additional_salary.name)
		self.db_set("additional_salary_reference", additional_salary.name)
			
	# Fetch employee leave balance based on selected Leave Type 
	@frappe.whitelist()
	def get_employee_leave_details(self):

		if self.status in ["Draft", "Pending Approval"]:
			leave_allocation = self.get_leave_allocation()
			if leave_allocation:
				self.get_leave_balance()
				self.get_available_encashable_leave_balance()
			return {
				"available_leave_balance": self.available_leave_balance,
				# "available_encashable_leave_balance": self.available_encashable_leave_balance
			}

	def get_leave_allocation(self):
		
		leave_allocation = frappe.db.get_value("Leave Allocation", 
		{"employee": self.employee, "leave_type": self.leave_type, 
		"from_date": ["<=", self.posting_date], "to_date": [">=", self.posting_date]}, "name")
		
		if not leave_allocation:
			frappe.throw("No leave allocation found for the selected leave type and date")

		self.leave_allocation = leave_allocation
		return leave_allocation

	def get_leave_balance(self):

		leave_balance = get_leave_balance_on(self.employee, self.leave_type, self.posting_date)
		self.available_leave_balance = leave_balance
		# Get valid encashable days based on leave type configuration
		max_encashable_days = frappe.db.get_value("Leave Type", self.leave_type, "max_encashable_leaves") or 0
		self.actual_encashable_days = max_encashable_days

	
	def get_available_encashable_leave_balance(self):
		# Get available encashable leave balance
		encashed_leaves = frappe.db.get_value("Leave Allocation", {"name": self.leave_allocation}, "total_leaves_encashed") or 0
		available_encashable_leaves = float(self.actual_encashable_days) - float(encashed_leaves)
		if self.available_leave_balance < available_encashable_leaves:
			available_encashable_leaves = self.available_leave_balance
		self.available_encashable_leaves = available_encashable_leaves
		

	# Fetch salary details for calculation 
	@frappe.whitelist()
	def get_employee_salary_details(self):
		if not self.employee or not self.posting_date:
			frappe.throw("Employee and Posting Date are required")
		if (self.employee and self.posting_date):
			assigned_salary_structure = get_assigned_salary_structure(self.employee, self.posting_date)
			leave_encashment_amount_per_day = frappe.db.get_value("Salary Structure Assignment", 
			{"salary_structure": assigned_salary_structure, "docstatus": 1, "from_date": ["<=", self.posting_date]}, 
			["leave_encashment_amount_per_day","currency"])
			self.leave_salary_per_day = leave_encashment_amount_per_day[0]
			self.currency = leave_encashment_amount_per_day[1]
			if not leave_encashment_amount_per_day or leave_encashment_amount_per_day[0] <= 0:
				leave_encashment_amount_per_day = frappe.db.get_value("Salary Structure", 
				{"name": assigned_salary_structure}, ["leave_encashment_amount_per_day","currency"])
				if not leave_encashment_amount_per_day or leave_encashment_amount_per_day[0] <= 0:
					frappe.throw("Leave Encashment Amount Per Day not found in Salary Structure please set Salary structure and Salary Structure Assignment")
				else:
					self.leave_salary_per_day = leave_encashment_amount_per_day[0]
					self.currency = leave_encashment_amount_per_day[1]
					

@frappe.whitelist()	
# set payroll reference for leave encashment request
def get_encashable_leave_types(doctype, txt, searchfield, start, page_len, filters):
	employee=filters.get("employee")
	if not employee:
		return []
	return  frappe.db.sql(""" SELECT DISTINCT lt.name 
		FROM `tabLeave Type` lt
		JOIN `tabLeave Allocation` la ON lt.name = la.leave_type
		WHERE lt.allow_encashment = 1
		AND la.employee = %(employee)s
		AND la.total_leaves_allocated > 0
		""", {"employee": employee})
	
# set payroll reference for leave encashment request
@frappe.whitelist()
def set_payroll_reference(doc, method):
	try:
		if doc.docstatus == 1:
			for row in doc.earnings:
				if row.salary_component == "Leave Encashment":
					leave_encashment = frappe.db.get_value("Leave Encashment Request",
					{"additional_salary_reference": row.additional_salary}, "name")
					if leave_encashment:
						frappe.db.set_value("Leave Encashment Request", leave_encashment, "payroll_entry_reference", doc.payroll_entry)
						frappe.db.set_value("Leave Encashment Request", leave_encashment, "workflow_state", "Paid")
						break
	except Exception as e:
		frappe.log_error(f"Error in set_payroll_reference: {str(e)}")
		raise e
		
        
@frappe.whitelist()
def generate_preview(doctype, docname):
    html = frappe.get_print(doctype, docname, 'Leave Encashment Request Print Format', doc=None)
    return html
def set_payroll_reference(doc, method):
	try:
		if doc.docstatus == 1:
			for row in doc.earnings:
				if row.salary_component == "Leave Encashment":
					leave_encashment = frappe.db.get_value("Leave Encashment Request",
					{"additional_salary_reference": row.additional_salary}, "name")
					if leave_encashment:
						frappe.db.set_value("Leave Encashment Request", leave_encashment, "payroll_entry_reference", doc.payroll_entry)
						frappe.db.set_value("Leave Encashment Request", leave_encashment, "workflow_state", "Paid")
						frappe.db.set_value("Leave Encashment Request", leave_encashment, "status", "Paid")
						break
	except Exception as e:
		frappe.log_error(f"Error in set_payroll_reference: {str(e)}")
		raise e
		
        
@frappe.whitelist()
def generate_preview(doctype, docname):
    html = frappe.get_print(doctype, docname, 'Leave Encashment Request Print Format', doc=None)
    return html
