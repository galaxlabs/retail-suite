

import frappe
from frappe import _
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def get_stock_ledger_data(**trackingData):
    """
    Get stock ledger data with filters
    """
    # item_code=None, warehouse=None, from_date=None, to_date=None, movement_type=None
    data = frappe.parse_json(trackingData)
    item_code =  data['item_code']
    warehouse =  data['warehouse']
    from_date =  data['from_date']
    to_date =  data['to_date']
    movement_type =  data['movement_type']
    filters = {}

    if item_code:
        filters['item_code'] = item_code

    if warehouse:
        filters['warehouse'] = warehouse

    if from_date:
        filters['posting_date'] = ['>=', from_date]

    if to_date:
        filters['posting_date'] = ['<=', to_date]

    # Get Stock Ledger entries
    stock_ledger_data = frappe.get_list(
        'Stock Ledger Entry',
        filters=filters,
        fields=[
            'name',
            'posting_date',
            'item_code',
            'actual_qty as quantity',
            'warehouse',
            'voucher_type',
            'voucher_no'
        ],
        order_by='posting_date desc'
    )

    # Enrich data with item details
    result = []
    for entry in stock_ledger_data:
        item = frappe.get_value('Item', entry['item_code'], ['item_name', 'item_code'])

        # Map voucher types to movement types
        #  Voucher Type ?
        # 1- Purchase Receipt
        # 2- Delivery Note
        # 3- Stock Entry -> transfer
        # 4- Stock Reconciliation -> adjustment

        type_mapping = {
            'Purchase Receipt': 'purchase',
            'Stock Entry': 'transfer',
            'Stock Reconciliation': 'adjustment',
            'Sales Invoice': 'sale',
            'Delivery Note': 'sale'
        }

        movement_type_mapped = type_mapping.get(entry['voucher_type'], 'other')

        # Filter by movement type if specified
        if movement_type and movement_type_mapped != movement_type:
            continue

        result.append({
            'id': entry['name'],
            'date': entry['posting_date'],
            'itemCode': entry['item_code'],
            'itemName': item[1] if item else '',
            'warehouse': entry['warehouse'],
            'type': movement_type_mapped,
            'quantity': entry['quantity'],
            'reference': entry['voucher_no'],
            'notes': f"via {entry['voucher_type']}"
        })

    return result


@frappe.whitelist(allow_guest=True)
def get_items_list():
    """
    Get list of all items for filter dropdown
    """
    items = frappe.get_list(
        'Item',
        filters={'disabled': 0},
        fields=['item_code', 'item_name'],
        limit_page_length=500
    )
    return items


@frappe.whitelist(allow_guest=True)
def get_inventory_summary(item_code=None, from_date=None, to_date=None):
    """
    Get summary of inbound/outbound/net change
    """
    filters = {}

    if item_code:
        filters['item_code'] = item_code

    if from_date:
        filters['posting_date'] = ['>=', from_date]

    if to_date:
        filters['posting_date'] = ['<=', to_date]

    entries = frappe.get_list(
        'Stock Ledger Entry',
        filters=filters,
        fields=['actual_qty']
    )

    total_inbound = sum(e['actual_qty'] for e in entries if e['actual_qty'] > 0)
    total_outbound = sum(abs(e['actual_qty']) for e in entries if e['actual_qty'] < 0)
    net_change = total_inbound - total_outbound

    return {
        'totalInbound': total_inbound,
        'totalOutbound': total_outbound,
        'netChange': net_change,
        'totalTransactions': len(entries)
    }


# ===================================================================
# # Purchase Receipt
# ===================================================================

@frappe.whitelist(allow_guest=True)
def get_purchase_receipt_statuses():
    meta = frappe.get_meta("Purchase Receipt")
    field = meta.get_field("status")

    if not field or not field.options:
        return []

    return field.options.split("\n")


@frappe.whitelist(allow_guest=True)
def get_purchase_receipts():
    receipts = frappe.get_all(
        "Purchase Receipt",
        fields=["name", "supplier", "posting_date", "status", "grand_total"],
        order_by="creation desc",
        limit=10
    )

    for r in receipts:
        doc = frappe.get_doc("Purchase Receipt", r.name)
        r["items"] = doc.items

    return receipts
