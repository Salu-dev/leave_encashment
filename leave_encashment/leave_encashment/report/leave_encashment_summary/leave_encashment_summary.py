# Copyright (c) 2026, Salumol Baiju and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns=get_columns()
	data=get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "name",
			"label": "ID",
			"fieldtype": "Link",
			"options": "Leave Encashment Request",
			"width": 140
		},
		{
			"fieldname": "employee",
			"label": "Employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120
		},
		{
			"fieldname": "employee_name",
			"label": "Employee Name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "company",
			"label": "Company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 150
		},
		{
			"fieldname": "department",
			"label": "Department",
			"fieldtype": "Link",
			"options": "Department",
			"width": 150
		},
		{
			"fieldname": "designation",
			"label": "Designation",
			"fieldtype": "Link",
			"options": "Designation",
			"width": 120
		},
		{
			"fieldname": "leave_type",
			"label": "Leave Type",
			"fieldtype": "Link",
			"options": "Leave Type",
			"width": 120
		},
		{
			"fieldname": "posting_date",
			"label": "Posting Date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "available_leave_balance",
			"label": "Available Leave Balance",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "requested_leaves",
			"label": "Requested Leaves",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "available_encashable_leaves",
			"label": "Available Encashable Leaves",
			"fieldtype": "Float",
			"width": 140
		},
		{
			"fieldname": "leave_salary_per_day",
			"label": "Salary Per Day",
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "total_encashment_amount",
			"label": "Total Encashment Amount",
			"fieldtype": "Currency",
			"width": 140
		},
		{
			"fieldname": "status",
			"label": "Status",
			"fieldtype": "Select",
			"width": 100
		},
		{
			"fieldname": "payroll_entry_reference",
			"label": "Payroll Entry",
			"fieldtype": "Link",
			"options": "Payroll Entry",
			"width": 120
		}
	]

def get_data(filters):

	filters = frappe._dict(filters or {})
	encashment_filter=[]
	data=[]
	
	if filters.employee:
		encashment_filter.append(["employee", "=", filters.employee])
	if filters.company:
		encashment_filter.append(["company", "=", filters.company])
	if filters.department:
		encashment_filter.append(["department", "=", filters.department])
	if filters.leave_type:
		encashment_filter.append(["leave_type", "=", filters.leave_type])
	if filters.status:
		encashment_filter.append(["status", "=", filters.status])
	if filters.from_date:
		encashment_filter.append(["posting_date", ">=", filters.from_date])
	if filters.to_date:
		encashment_filter.append(["posting_date", "<=", filters.to_date])

	data = frappe.get_list("Leave Encashment Request", filters=encashment_filter, fields=["*"],
		order_by="employee,posting_date")

	return data
