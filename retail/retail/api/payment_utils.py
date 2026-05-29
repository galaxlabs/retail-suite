import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_shift_payments_entries(pos_opening_shift):
    return frappe.get_all(
        "Payment Entry",
        filters={
            "docstatus": 1,
            "reference_no": pos_opening_shift,
            "payment_type": "Receive",
        },
        fields=[
            "name",
            "mode_of_payment",
            "paid_amount",
            "reference_no",
            "posting_date",
            "party",
            "owner"
        ],
    )

def submit_printed_invoices(pos_opening_shift):
    # Intentionally disabled for POS flow:
    # auto-submitting invoices during read/summary causes stock validation errors
    # and blocks non-technical cashier workflows.
    return

@frappe.whitelist()
def get_shift_pos_invoices(pos_opening_shift):
    data = frappe.db.sql(
        """
	select
		name
	from
		`tabSales Invoice`
	where
		docstatus < 2 and posa_pos_opening_shift = %s
	""",
        (pos_opening_shift),
        as_dict=1,
    )

    data = [frappe.get_doc("Sales Invoice", d.name).as_dict() for d in data]

    return data



# @frappe.whitelist()
# def get_shift_invoice_payments(invoice_name):
#     """
#     جلب كل Payment Entries المرتبطة بفاتورة معينة،
#     مع حساب المبلغ المخصص لهذه الفاتورة تحديداً.
#     """
#     references = frappe.get_all(
#         "Payment Entry Reference",
#         filters={
#             "reference_doctype": "Sales Invoice",
#             "reference_name":    invoice_name,
#             "docstatus":         1,
#         },
#         fields=["parent", "allocated_amount", "outstanding_amount"]
#     )

#     if not references:
#         return []

#     result = []
#     for ref in references:
#         try:
#             pe = frappe.get_doc("Payment Entry", ref.parent)

#             # تجاهل الدفعات الملغاة
#             if pe.docstatus != 1:
#                 continue

#             # كل الفواتير المرتبطة بهذه الدفعة
#             all_linked = [
#                 {
#                     "invoice_name":     r.reference_name,
#                     "allocated_amount": flt(r.allocated_amount),
#                 }
#                 for r in pe.references
#                 if r.reference_doctype == "Sales Invoice"
#             ]

#             # FIX: aLLOCATED FOR CURRENT INVOICE
#             # total_allocated = sum(flt(r.allocated_amount) for r in pe.references)
#             allocated_to_invoice = sum(
#                 flt(r.allocated_amount)
#                 for r in pe.references
#                 if r.reference_doctype == "Sales Invoice" and r.reference_name == invoice_name
#             )
#             unallocated_amount = flt(pe.paid_amount) - allocated_to_invoice

#             result.append({
#                 "payment_entry":             pe.name,
#                 "posting_date":              str(pe.posting_date),
#                 "mode_of_payment":           pe.mode_of_payment,
#                 "payment_type":              pe.payment_type,
#                 "party":                     pe.party,
#                 "party_name":                pe.party_name,
#                 "paid_amount":               flt(pe.paid_amount),
#                 "allocated_to_this_invoice": flt(ref.allocated_amount),
#                 "unallocated_amount":        unallocated_amount,   # ← جديد
#                 "is_fully_allocated":        unallocated_amount <= 0,  # ← جديد
#                 "all_linked_invoices":       all_linked,
#                 "total_invoices_count":      len(all_linked),
#             })

#         except frappe.DoesNotExistError:
#             # الدفعة محذوفة أو غير موجودة
#             continue

#     return result

@frappe.whitelist()
def get_shift_invoice_payments(invoice_name):
    references = frappe.get_all(
        "Payment Entry Reference",
        filters={
            "reference_doctype": "Sales Invoice",
            "reference_name": invoice_name,
            "docstatus": 1,
        },
        fields=[
            "parent", "allocated_amount", "total_amount",
        ],
    )

    if not references:
        return []

    result = []
    for ref in references:
        try:
            pe = frappe.get_doc("Payment Entry", ref.parent)

            # تجاهل الدفعات الملغاة
            if pe.docstatus != 1:
                continue

            # كل الفواتير المرتبطة بهذه الدفعة
            all_linked = [
                {
                    "invoice_name":     r.reference_name,
                    "allocated_amount": flt(r.allocated_amount),
                    "outstanding_amount": flt(r.outstanding_amount),
                    "total_amount": flt(r.total_amount)
                }
                for r in pe.references
            ]

            allocated_to_invoice = sum(
                flt(r.allocated_amount)
                for r in pe.references
                if r.reference_doctype == "Sales Invoice" and r.reference_name == invoice_name
            )

            result.append({
                "payment_entry": ref.parent,
                "posting_date":              str(pe.posting_date),
                "mode_of_payment":           pe.mode_of_payment,
                "allocated_to_this_invoice": allocated_to_invoice,
                "unallocated_amount":        flt(pe.unallocated_amount),
                "party":                     pe.party,
                "party_name":                pe.party_name,
                "paid_amount":               flt(pe.paid_amount),
                 "is_fully_allocated":       flt(pe.unallocated_amount) <= 0,
                "all_linked_invoices":       all_linked,
                "total_invoices_count":      len(all_linked),
            })

        except frappe.DoesNotExistError:
            # الدفعة محذوفة أو غير موجودة
            continue

    return result

@frappe.whitelist()
def get_shift_unallocated_payments(shift_id):
    """
    تجمع مصدرين:
    1. دفعات مرتبطة بفواتير الشيفت لكن فيها unallocated_amount > 0
    2. دفعات مرتبطة بالشيفت عبر reference_no لكن بدون أي فاتورة
    """
    found_pe = {}  # name → dict، لتجنب التكرار

    # ── المصدر 1: عبر reference_no ────────────────────────
    # (يشمل الدفعات المرتبطة بالشيفت مباشرة بغض النظر عن الفواتير)
    all_pe = frappe.get_all(
        "Payment Entry",
        filters={
            "docstatus":    1,
            "payment_type": "Receive",
            "reference_no": shift_id,
        },
        fields=["name", "mode_of_payment", "paid_amount",
                "unallocated_amount", "party", "party_name", "posting_date"]
    )
    for pe in all_pe:
        if flt(pe.get("unallocated_amount", 0)) > 0.01:
            found_pe[pe["name"]] = {
                "payment_entry":      pe["name"],
                "mode_of_payment":    pe["mode_of_payment"],
                "paid_amount":        flt(pe["paid_amount"]),
                "total_allocated":    flt(pe["paid_amount"]) - flt(pe["unallocated_amount"]),
                "unallocated_amount": flt(pe["unallocated_amount"]),
                "party":              pe["party"],
                "party_name":         pe["party_name"],
                "posting_date":       str(pe["posting_date"]),
                "linked_invoices":    [],   # سنعبئها لاحقاً
                "source":             "reference_no",
            }

    # ── المصدر 2: عبر فواتير الشيفت ───────────────────────
    # (يشمل الدفعات المجزأة — جزء مخصص وجزء غير مخصص)
    invoice_names = frappe.get_all(
        "Sales Invoice",
        filters={"posa_pos_opening_shift": shift_id, "docstatus": 1},
        pluck="name"
    )
    if invoice_names:
        pe_refs = frappe.get_all(
            "Payment Entry Reference",
            filters={
                "reference_doctype": "Sales Invoice",
                "reference_name":    ["in", invoice_names],
            },
            pluck="parent"
        )
        for pe_name in set(pe_refs):
            # لو موجود من المصدر الأول تجاهل — بس حدّث linked_invoices
            pe_doc = frappe.get_doc("Payment Entry", pe_name)
            total_allocated = sum(
                flt(r.allocated_amount)
                for r in pe_doc.references
                if r.reference_doctype == "Sales Invoice"
            )
            unallocated = flt(pe_doc.paid_amount) - total_allocated
            linked = [
                r.reference_name for r in pe_doc.references
                if r.reference_doctype == "Sales Invoice"
            ]

            if pe_name in found_pe:
                # حدّث linked_invoices فقط (البيانات موجودة من المصدر 1)
                found_pe[pe_name]["linked_invoices"] = linked
            elif unallocated > 0.01:
                found_pe[pe_name] = {
                    "payment_entry":      pe_doc.name,
                    "mode_of_payment":    pe_doc.mode_of_payment,
                    "paid_amount":        flt(pe_doc.paid_amount),
                    "total_allocated":    total_allocated,
                    "unallocated_amount": unallocated,
                    "party":              pe_doc.party,
                    "party_name":         pe_doc.party_name,
                    "posting_date":       str(pe_doc.posting_date),
                    "linked_invoices":    linked,
                    "source":             "invoice_ref",
                }

    return list(found_pe.values())




import frappe
from frappe.utils import flt

@frappe.whitelist()
def test_payment_entry_allocation(shift_id):
    """
    يلف على كل فواتير الشيفت ويحسب total_allocated و total_allocated_again لكل Payment Entry
    """
    results = []

    # جلب كل فواتير الشيفت
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={"posa_pos_opening_shift": shift_id, "docstatus": 1},
        pluck="name"
    )

    for invoice_name in invoices:
        # جلب كل الـ Payment Entry References المرتبطة بالفاتورة
        references = frappe.get_all(
            "Payment Entry Reference",
            filters={
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice_name,
                "docstatus": 1
            },
            pluck="parent"
        )

        for pe_name in set(references):
            pe = frappe.get_doc("Payment Entry", pe_name)

            total_allocated = sum(flt(r.allocated_amount) for r in pe.references)

            total_allocated_again = sum(
                flt(r.allocated_amount)
                for r in pe.references
                if r.reference_doctype == "Sales Invoice" and r.reference_name == invoice_name
            )

            results.append({
                "invoice_name": invoice_name,
                "payment_entry": pe.name,
                "paid_amount": flt(pe.paid_amount),
                "total_allocated": total_allocated,
                "total_allocated_again": total_allocated_again,
                "matches": abs(total_allocated_again - total_allocated) < 0.01,
                "unallocated_amount": flt(pe.paid_amount) - total_allocated
            })

    return results
