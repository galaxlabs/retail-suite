import frappe


@frappe.whitelist(allow_guest=True)
def get_all_bills_invoices(**kwargs):
    filters ={}
    if kwargs.get("status"):
        filters["status"] = kwargs["status"]
    print("\n\n\filters",filters)
    invoices = frappe.get_all(
        "Purchase Invoice",
        filters=filters,
        fields=["*"],
        order_by="posting_date desc"
    )

    for inv in invoices:
        items = frappe.get_all(
            "Purchase Invoice Item",
            filters={"parent": inv["name"]},
            fields=["*"]
        )
        inv["items_count"] = len(items)
        inv["items"] = items
        inv["total_qty"] = sum(i["qty"] for i in items)

    total = sum(i.get("grand_total", 0) for i in invoices)
    due = sum(i.get("outstanding_amount", 0) for i in invoices)
    pending_inv_count = sum(1 for i in invoices if i.status == "Draft")
    count = len(invoices)
    return {
        "count": count,
        "due": due,
        "total": total,
        "invoices": invoices,
        "count_pending_inv":pending_inv_count
    }
