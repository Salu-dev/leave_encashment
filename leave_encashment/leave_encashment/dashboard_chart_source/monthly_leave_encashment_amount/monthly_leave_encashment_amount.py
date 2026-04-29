from frappe import _
import frappe

@frappe.whitelist()
def get_data(chart_name=None, chart=None, no_cache=None, filters=None):
    data = frappe.db.sql("""
        SELECT
            DATE_FORMAT(posting_date, '%%b %%Y') AS month,
            SUM(total_encashment_amount) AS amount
        FROM `tabLeave Encashment Request`
        WHERE status="Approved"
        GROUP BY YEAR(posting_date), MONTH(posting_date)
        ORDER BY posting_date
    """, as_dict=True)

    return {
        "labels": [d.month for d in data],
        "datasets": [
            {
                "name": _("Encashment Amount"),
                "values": [d.amount for d in data]
            }
        ]
    }