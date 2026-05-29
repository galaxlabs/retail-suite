# retail/retail/api/purchase_receipt.py

import frappe
from frappe import _
from frappe.utils import nowtime, nowdate, today
import json

@frappe.whitelist(allow_guest=True)
def get_purchase_receipts():
    try:
        receipts = frappe.get_all(
            "Purchase Receipt",
            fields=[
                "name",
                "posting_date",
                "supplier",
                "status",
                "grand_total",
                "total_qty",
                "net_total",
                "docstatus",
            ],
            order_by="posting_date desc"
        )

        for receipt in receipts:
            receipt["items"] = frappe.get_all(
                "Purchase Receipt Item",
                filters={"parent": receipt["name"]},
                fields=[
                    "item_code",
                    "item_name",
                    "description",
                    "warehouse",
                    "uom",
                    "qty as qty",
                    "rate as rate",
                    "amount as total"
                ]
            )

        return {"status": "success", "data": receipts}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_purchase_receipts")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_purchase_receipt(name):
    """Get single purchase receipt by name"""
    try:
        receipt = frappe.get_doc("Purchase Receipt", name)

        data = {
            "name": receipt.name,
            "receipt_no": receipt.name,
            "posting_date": str(receipt.posting_date),
            "status": receipt.status.lower() if receipt.status else "Draft",
            "supplier": receipt.supplier,
            "invoice_no": receipt.bill_no or "",
            "payment_terms": receipt.payment_terms_template or "",
            "due_date": str(receipt.payment_schedule[0].due_date) if receipt.payment_schedule else "",
            "shipping_cost": receipt.total_taxes_and_charges or 0,
            "tax_rate": 0,
            "discount_rate": receipt.additional_discount_percentage or 0,
            "subtotal": receipt.net_total,
            "discount_amount": receipt.discount_amount or 0,
            "tax_amount": receipt.total_taxes_and_charges or 0,
            "total_amount": receipt.grand_total,
            "notes": receipt.remarks or "",
            "items": []
        }

        for item in receipt.items:
            data["items"].append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "warehouse": item.warehouse or "",
                "description": item.description or "",
                "qty": item.qty,
                "rate": item.rate,
                "total": item.amount
            })

        return {"status": "success", "data": data}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_purchase_receipt")
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def create_purchase_receipt(data):
    try:
        import json
        if isinstance(data, str):
            data = json.loads(data)

        receipt = frappe.new_doc("Purchase Receipt")
        receipt.supplier      = data.get("supplier")
        receipt.posting_date  = data.get("posting_date")
        receipt.bill_no       = data.get("invoice_no", "")
        receipt.remarks       = data.get("notes", "")
        receipt.additional_discount_percentage = data.get("discount_rate", 0)

        warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse") or "Stores - R"

        for item in data.get("items", []):
            receipt.append("items", {
                "item_code":   item.get("item_code"),
                "item_name":   item.get("item_name"),
                "description": item.get("description", ""),
                "qty":         item.get("qty"),
                "rate":        item.get("rate"),
                "amount":      item.get("total"),
                "uom":         item.get("uom", "Nos"),
                "warehouse":   warehouse
            })

        receipt.insert(ignore_permissions=True)

        # ✅ لو المستخدم اختار إنه مش Draft → نعمل Submit
        if data.get("submit_doc"):
            receipt.submit()

        frappe.db.commit()

        return {
            "status":  "success",
            "data":    {"name": receipt.name, "docstatus": receipt.docstatus},
            "message": "Purchase Receipt created successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_purchase_receipt")
        frappe.db.rollback()
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def submit_purchase_receipt(name):
    """Submit a draft purchase receipt"""
    try:
        receipt = frappe.get_doc("Purchase Receipt", name)
        if receipt.docstatus == 0:  # Draft فقط
            receipt.submit()
            frappe.db.commit()
            return {
                "status":  "success",
                "message": f"{name} submitted successfully",
                "data":    {"docstatus": 1, "status": receipt.status}
            }
        else:
            return {"status": "error", "message": "Document is not in Draft status"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "submit_purchase_receipt")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def cancel_purchase_receipt(name):
    """Cancel a submitted purchase receipt"""
    try:
        receipt = frappe.get_doc("Purchase Receipt", name)
        if receipt.docstatus == 1:  # Submitted فقط
            receipt.cancel()
            frappe.db.commit()
            return {
                "status":  "success",
                "message": f"{name} cancelled successfully"
            }
        else:
            return {"status": "error", "message": "Document is not submitted"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "cancel_purchase_receipt")
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def update_purchase_receipt(name, data):
    """Update existing purchase receipt"""
    try:
        import json
        if isinstance(data, str):
            data = json.loads(data)

        receipt = frappe.get_doc("Purchase Receipt", name)

        if receipt.docstatus != 0:
            frappe.throw(f"Cannot edit receipt '{name}' — it is already submitted or cancelled.")
        print("=============Data===========",data)
        # ── Header fields ─────────────────────────────────────────────────────
        receipt.supplier     = data.get("supplier",      receipt.supplier)
        receipt.posting_date = data.get("posting_date",  receipt.posting_date)
        receipt.remarks      = data.get("remarks")       or data.get("notes")      or receipt.remarks
        receipt.additional_discount_percentage = data.get("additional_discount_percentage") or \
                                                 data.get("discount_rate") or 0
        print("=============Data===========",data)
        # ── Default warehouse fallback ─────────────────────────────────────────
        default_warehouse = (
            frappe.db.get_single_value("Stock Settings", "default_warehouse") or ""
        )

        # ── Clear and re-add items ────────────────────────────────────────────
        receipt.items = []
        print("=============Data===========",data)
        for item in data.get("items", []):
            # ✅ amount — Vue بيبعت "amount" مش "total"
            qty  = float(item.get("qty")  or 0)
            rate = float(item.get("rate") or 0)
            print("=============Rate===========")
            print("Rate",rate)
            amount = item.get("amount") or item.get("total") or (qty * rate)

            receipt.append("items", {
                "item_code":   item.get("item_code"),
                "item_name":   item.get("item_name")   or "",
                "description": item.get("description") or "",
                "qty":         qty,
                "rate":        rate,
                "amount":      amount,
                "uom":         item.get("uom")       or "Nos",
                "warehouse":   item.get("warehouse") or default_warehouse,
            })

        receipt.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status":  "success",
            "data":    {"name": receipt.name},
            "message": f"Purchase Receipt {receipt.name} updated successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_purchase_receipt")
        frappe.db.rollback()
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def delete_purchase_receipt(name):
    """Delete purchase receipt"""
    try:
        frappe.delete_doc("Purchase Receipt", name, ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": f"Purchase Receipt {name} deleted successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "delete_purchase_receipt")
        frappe.db.rollback()
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def get_suppliers():
    """Get all suppliers"""
    try:
        suppliers = frappe.get_all(
            "Supplier",
            fields=["name", "supplier_name", "supplier_type"],
            filters={"disabled": 0},
            order_by="supplier_name asc"
        )
        return {"status": "success", "data": suppliers}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_suppliers")
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def create_purchase_invoice_from_receipt(
    receipt_name,
    posting_date=None,
    posting_time=None,
    set_posting_time=0,
    items=None,
    remarks=None,
):
    """
    Create a Purchase Invoice from a Purchase Receipt.
    Uses pr_detail (not purchase_receipt_item) for correct row-level linking.
    """
    try:
        receipt = frappe.get_doc("Purchase Receipt", receipt_name)

        # ── Validate ──────────────────────────────────────────────────────────
        if receipt.docstatus != 1:
            return {"status": "error", "message": "Receipt must be submitted first"}

        if receipt.status not in ("To Bill", "Partly Billed"):
            return {
                "status":  "error",
                "message": f"Receipt status is '{receipt.status}', cannot create invoice"
            }

        # ── Parse items override ───────────────────────────────────────────────
        if isinstance(items, str):
            items = json.loads(items)

        items_override = {}
        if items:
            for row in items:
                items_override[row["item_code"]] = row

        # ── Build invoice ─────────────────────────────────────────────────────
        invoice = frappe.new_doc("Purchase Invoice")
        invoice.supplier = receipt.supplier
        invoice.company  = receipt.company
        invoice.currency = getattr(receipt, "currency", None) or frappe.defaults.get_user_default("currency")
        invoice.remarks  = remarks or receipt.remarks or ""

        # Buying price list (optional, safe fallback)
        if getattr(receipt, "buying_price_list", None):
            invoice.buying_price_list = receipt.buying_price_list

        # ── Posting date / time ───────────────────────────────────────────────
        if int(set_posting_time) and posting_date:
            invoice.set_posting_time = 1
            invoice.posting_date     = posting_date
            invoice.posting_time     = posting_time or nowtime()
        else:
            invoice.set_posting_time = 0
            invoice.posting_date     = today()
            invoice.posting_time     = nowtime()

        invoice.bill_date = invoice.posting_date

        # ── Items ─────────────────────────────────────────────────────────────
        default_expense_account = frappe.db.get_value(
            "Company",
            receipt.company,
            "default_expense_account"
        )

        for receipt_item in receipt.items:
            override = items_override.get(receipt_item.item_code, {})

            qty  = float(override.get("qty",  receipt_item.qty  or 0))
            rate = float(override.get("rate", receipt_item.rate or 0))

            invoice.append("items", {
                "item_code":        receipt_item.item_code,
                "item_name":        receipt_item.item_name,
                "description":      receipt_item.description or receipt_item.item_name or "",
                "qty":              qty,
                "rate":             rate,
                "amount":           qty * rate,
                "uom":              override.get("uom", receipt_item.uom or "Nos"),
                "stock_uom":        receipt_item.stock_uom,
                "conversion_factor": receipt_item.conversion_factor or 1,
                "warehouse":        override.get("warehouse", receipt_item.warehouse),
                # ✅ الربط الصح بالـ Receipt

                "purchase_receipt": receipt_name,
                "pr_detail":        receipt_item.name,        # row-level link → يحدّث billing_status
                "expense_account":  receipt_item.expense_account or default_expense_account,
                "cost_center":      receipt_item.cost_center,
            })

        # ── Taxes ─────────────────────────────────────────────────────────────
        for tax in receipt.get("taxes", []):
            invoice.append("taxes", {
                "charge_type":  tax.charge_type,
                "account_head": tax.account_head,
                "description":  tax.description,
                "rate":         tax.rate,
                "cost_center":  tax.cost_center,
            })

        # ── Save ──────────────────────────────────────────────────────────────
        invoice.insert(ignore_permissions=True)
        invoice.submit()
        frappe.db.commit()
        return {
            "status":  "success",
            "data":    {
                "name":        invoice.name,
                "docstatus":   invoice.docstatus,
                "grand_total": invoice.grand_total,
            },
            "message": f"Purchase Invoice {invoice.name} created successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_purchase_invoice_from_receipt")
        frappe.db.rollback()
        return {"status": "error", "message": str(e)}

# @frappe.whitelist(allow_guest=True)
# def create_purchase_invoice_from_receipt(receipt_name):
#     """Create Purchase Invoice from Purchase Receipt"""
#     try:
#         receipt = frappe.get_doc("Purchase Receipt", receipt_name)

#         # تأكد إنه Submitted وحالته To Bill
#         if receipt.docstatus != 1:
#             return {"status": "error", "message": "Receipt must be submitted first"}

#         if receipt.status not in ["To Bill", "Partly Billed"]:
#             return {"status": "error", "message": f"Receipt status is '{receipt.status}', cannot create invoice"}

#         # إنشاء الـ Invoice
#         invoice = frappe.new_doc("Purchase Invoice")
#         invoice.supplier      = receipt.supplier
#         invoice.posting_date  = frappe.utils.today()
#         invoice.bill_date     = frappe.utils.today()
#         invoice.remarks       = receipt.remarks or ""

#         # ربط الـ Invoice بالـ Receipt
#         for item in receipt.items:
#             invoice.append("items", {
#                 "item_code":             item.item_code,
#                 "item_name":             item.item_name,
#                 "description":           item.description or "",
#                 "qty":                   item.qty,
#                 "rate":                  item.rate,
#                 "amount":                item.amount,
#                 "uom":                   item.uom or "Nos",
#                 "purchase_receipt":      receipt_name,        # ✅ الربط
#                 "pr_detail":             item.name,           # ✅ الربط بالـ item
#                 "expense_account":       frappe.db.get_value(
#                                             "Company",
#                                             frappe.defaults.get_user_default("Company"),
#                                             "default_expense_account"
#                                         )
#             })

#         invoice.insert(ignore_permissions=True)
#         invoice.submit()
#         frappe.db.commit()

#         return {
#             "status":  "success",
#             "data":    {"name": invoice.name},
#             "message": f"Purchase Invoice {invoice.name} created successfully"
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "create_purchase_invoice_from_receipt")
#         frappe.db.rollback()
#         return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_purchase_invoice_for_receipt(receipt_name):
    """Check if invoice already exists for this receipt"""
    try:
        invoices = frappe.get_all(
            "Purchase Invoice Item",
            filters={"purchase_receipt": receipt_name, "docstatus": 1},
            fields=["parent"],
            distinct=True
        )
        return {
            "status": "success",
            "data": [i.parent for i in invoices]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
