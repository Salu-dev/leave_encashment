frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Monthly Leave Encashment Amount"] = {
	method: "leave_encashment.leave_encashment.dashboard_chart_source.monthly_leave_encashment_amount.monthly_leave_encashment_amount.get_data",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company"
		}
	]
};