# Copyright (c) 2026, Ahmed Abu-khatwa and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from retail.retail.api.shifts import get_shift_pos_transactions
from retail.retail.api.posapp import get_draft_invoices, get_sales_invoice_child_table
from retail.retail.api.payment_utils import get_shift_invoice_payments, get_shift_unallocated_payments, get_shift_pos_invoices, get_shift_payments_entries, submit_printed_invoices
from frappe.utils import format_time, datetime, get_datetime

class POSClosingShift(Document):
    def validate(self):
        user = frappe.get_all(
            "POS Closing Shift",
            filters={
                "user": self.user,
                "docstatus": 1,
                "pos_opening_shift": self.pos_opening_shift,
                "name": ["!=", self.name],
            },
        )

        if user:
            frappe.throw(
                _(
                    "POS Closing Shift {} against {} between selected period".format(
                        frappe.bold("already exists"), frappe.bold(self.user)
                    )
                ),
                title=_("Invalid Period"),
            )

        if (
            frappe.db.get_value("POS Opening Shift", self.pos_opening_shift, "status")
            != "Open"
        ):
            frappe.throw(
                _("Selected POS Opening Shift should be open."),
                title=_("Invalid Opening Entry"),
            )
        if (
            frappe.db.get_value("POS Opening Shift", self.pos_opening_shift, "status")
            == "Open"
        ):
            allow_close_with_draft_invoice = 0
            if frappe.db.has_column("POS Profile", "custom_allow_close_shift_with_draft_invoice"):
                allow_close_with_draft_invoice = frappe.get_value(
                    "POS Profile",
                    self.pos_profile,
                    "custom_allow_close_shift_with_draft_invoice",
                )

            if not allow_close_with_draft_invoice:
                if get_draft_invoices(self.pos_opening_shift):
                    frappe.throw(
                    _("You should Close your Draft invoice."),
                    title=_("Invoice Draft"),
                )
        self.update_payment_reconciliation()

    def update_payment_reconciliation(self):
        # update the difference values in Payment Reconciliation child table
        # get default precision for site
        precision = (
            frappe.get_cached_value("System Settings", None, "currency_precision") or 3
        )
        for d in self.payment_reconciliation:
            d.difference = +flt(d.closing_amount, precision) - flt(
                d.expected_amount, precision
            )

    def on_submit(self):
        opening_entry = frappe.get_doc("POS Opening Shift", self.pos_opening_shift)
        opening_entry.pos_closing_shift = self.name
        opening_entry.set_status()
        self.delete_draft_invoices()
        opening_entry.save()

    def delete_draft_invoices(self):
        if frappe.get_value("POS Profile", self.pos_profile, "posa_allow_delete"):
            data = frappe.db.sql(
                """
                select
                    name
                from
                    `tabSales Invoice`
                where
                    docstatus = 0 and posa_is_printed = 0 and posa_pos_opening_shift = %s
                """,
                (self.pos_opening_shift),
                as_dict=1,
            )

            for invoice in data:
                frappe.delete_doc("Sales Invoice", invoice.name, force=1)

    @frappe.whitelist()
    def get_payment_reconciliation_details(self):
        currency = frappe.get_cached_value("Company", self.company, "default_currency")
        print("\n\npayment_reconciliation is",self.payment_reconciliation)
        return frappe.render_template(
            "retail/retail/doctype/pos_closing_shift/closing_shift_details.html",
            {"data": self, "currency": currency},
        )


@frappe.whitelist()
def get_cashiers(doctype, txt, searchfield, start, page_len, filters):
    cashiers_list = frappe.get_all("POS Profile User", filters=filters, fields=["user"])
    return [c["user"] for c in cashiers_list]


@frappe.whitelist()
def get_pos_invoices(pos_opening_shift):
    return get_shift_pos_invoices(pos_opening_shift)

@frappe.whitelist()
def get_all_pos_invoices(**kwargs):

    docstatus = int(kwargs.get("docstatus", 1))
    filters = {"is_pos": 1, "docstatus": docstatus}
    if kwargs.get("pos_opening_shift"):
        filters["posa_pos_opening_shift"] = kwargs["pos_opening_shift"]

    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=["name", "owner","customer", "grand_total", "posting_date", "posting_time", "status", "posa_pos_opening_shift"],
        order_by="posting_date desc"
    )

    for inv in invoices:
        items = frappe.get_all(
            "Sales Invoice Item",
            filters={"parent": inv["name"]},
            fields=["*"]
        )
        inv["items_count"] = len(items)
        inv["items"] = items
        inv["total_qty"] = sum(i["qty"] for i in items)

    total = sum(i.get("grand_total", 0) for i in invoices)
    count = len(invoices)
    return {
        "count": count,
        "total": total,
        "invoices": invoices
    }

# in pos_closing_shift.py
@frappe.whitelist()
def get_payments_entries(pos_opening_shift):
    return get_shift_payments_entries(pos_opening_shift)

@frappe.whitelist()
def make_closing_shift_from_opening(opening_shift):
    opening_shift = json.loads(opening_shift)

    submit_printed_invoices(opening_shift.get("name"))

    closing_shift = frappe.new_doc("POS Closing Shift")
    closing_shift.pos_opening_shift = opening_shift.get("name")
    closing_shift.period_start_date = opening_shift.get("period_start_date")
    closing_shift.period_end_date = frappe.utils.get_datetime()
    closing_shift.pos_profile = opening_shift.get("pos_profile")
    closing_shift.user = opening_shift.get("user")
    closing_shift.company = opening_shift.get("company")
    closing_shift.grand_total = 0
    closing_shift.net_total = 0
    closing_shift.total_quantity = 0

    invoices = get_pos_invoices(opening_shift.get("name"))

    pos_invoices = []
    taxes = []
    payments = {}
    pos_payments_table = []
    # ── 1. ابدأ بـ balance_details (opening amounts) ──
    for detail in opening_shift.get("balance_details", []):
        mop = detail.get("mode_of_payment")
        payments[mop] = frappe._dict({
            "mode_of_payment": mop,
            "opening_amount": flt(detail.get("amount") or 0),
            "expected_amount": 0,
            "closing_amount": 0,
        })

    # ── 2. loop الفواتير ──
    for inv in invoices:
        pos_invoices.append(frappe._dict({
            "sales_invoice": inv.name,
            "posting_date": inv.posting_date,
            "grand_total": inv.grand_total,
            "customer": inv.customer,
        }))
        closing_shift.grand_total += flt(inv.grand_total)
        closing_shift.net_total += flt(inv.net_total)
        closing_shift.total_quantity += flt(inv.total_qty)

        for t in inv.taxes:
            existing_tax = next((tx for tx in taxes if tx.account_head == t.account_head and tx.rate == t.rate), None)
            if existing_tax:
                existing_tax.amount += flt(t.tax_amount)
            else:
                taxes.append(frappe._dict({
                    "account_head": t.account_head,
                    "rate": t.rate,
                    "amount": t.tax_amount,
                }))

        # ✅ الفواتير اللي عندها payments مباشرة
        if inv.payments:
            for p in inv.payments:
                mop = p.mode_of_payment
                if mop not in payments:
                    payments[mop] = frappe._dict({
                        "mode_of_payment": mop,
                        "opening_amount": 0,
                        "expected_amount": 0,
                        "closing_amount": 0,
                    })
                payments[mop].expected_amount += flt(p.amount)

        payment_entries = get_shift_invoice_payments(inv["name"])
        for pe in payment_entries:
            mop = pe["mode_of_payment"]
            if mop not in payments:
                payments[mop] = {
                    "mode_of_payment": mop,
                    "opening_amount": 0,
                    "expected_amount": 0,
                    "closing_amount": 0,
                }
            payments[mop]["expected_amount"] += pe["allocated_to_this_invoice"]


    pos_payments = get_payments_entries(opening_shift.get("name"))

    for py in pos_payments:
        pos_payments_table.append(
            frappe._dict(
                {
                    "payment_entry": py.name,
                    "mode_of_payment": py.mode_of_payment,
                    "paid_amount": py.paid_amount,
                    "posting_date": py.posting_date,
                    "customer": py.party,
                }
            )
        )

    # ── 4. Unallocated payments — مقسمة على mode مش مجموع واحد ──
    unallocated = get_shift_unallocated_payments(opening_shift.get("name"))
    for pe in unallocated:
        mop = pe.get("mode_of_payment")
        if mop not in payments:
            payments[mop] = frappe._dict({
                "mode_of_payment": mop,
                "opening_amount": 0,
                "expected_amount": 0,
                "closing_amount": 0,
            })
        payments[mop]["expected_amount"] += flt(pe.get("unallocated_amount", 0))

    # ── 5. حط الـ closing_amount من closing_details ──
    closing_details = opening_shift.get("closing_details") or []
    if isinstance(closing_details, dict):
        closing_details = [closing_details]

    for mop, pay in payments.items():
        closing_detail = next(
            (d for d in closing_details if d.get("modeOfPayment") == mop), None
        )
        pay.closing_amount = flt(closing_detail.get("closingBalance")) if closing_detail else 0
        diff = pay.expected_amount + pay.opening_amount - pay.closing_amount
        print(f"{mop}: opening={pay.opening_amount}, expected={pay.expected_amount}, closing={pay.closing_amount}, diff={diff}")

    payments_list = list(payments.values())

    closing_shift.set("pos_transactions", pos_invoices)
    closing_shift.set("payment_reconciliation", payments_list)
    closing_shift.set("taxes", taxes)
    closing_shift.set("pos_payments", pos_payments_table)

    if opening_shift.get("user") == frappe.session.user:
        closing_shift.save(ignore_permissions=True)
    else:
        closing_shift.save()

    frappe.db.set_value("POS Opening Shift", opening_shift.get("name"), "status", "Closed")
    frappe.db.set_value("POS Opening Shift", opening_shift.get("name"), "pos_closing_shift", closing_shift.name)
    frappe.db.commit()

    return closing_shift


@frappe.whitelist()
def submit_closing_shift(closing_shift):
    closing_shift = json.loads(closing_shift)
    closing_shift_doc = frappe.get_doc(closing_shift)
    closing_shift_doc.flags.ignore_permissions = True
    closing_shift_doc.save()
    closing_shift_doc.submit()
    return closing_shift_doc.name


@frappe.whitelist()
def get_shift_summary(pos_opening_shift_name):

    if isinstance(pos_opening_shift_name, str):
            try:
                parsed = json.loads(pos_opening_shift_name)
                if isinstance(parsed, dict) and parsed.get("name"):
                    pos_opening_shift_name = parsed.get("name")
            except Exception:
                pass

    pos_opening_shift = frappe.get_doc("POS Opening Shift", pos_opening_shift_name).as_dict()
    submit_printed_invoices(pos_opening_shift.get("name"))

    invoices = get_pos_invoices(pos_opening_shift.get("name"))
    pos_payments = get_payments_entries(pos_opening_shift.get("name"))

    taxes = []
    payments = []
    pos_transactions = []
    pos_payments_table = []

    # balance_details ممكن تكون None لو الشيفت لسه مفتوح جديد
    for detail in (pos_opening_shift.get("balance_details") or []):
        payments.append(
            frappe._dict({
                "mode_of_payment": detail.get("mode_of_payment"),
                "opening_amount": detail.get("amount") or 0,
                "expected_amount": detail.get("amount") or 0,
                "closing_amount": 0,
            })
        )

    total_sales = 0
    total_qty = 0
    net_total = 0

    for d in invoices:
        total_sales += flt(d.grand_total)
        total_qty += flt(d.total_qty)
        net_total += flt(d.net_total)

        invoice_doc = frappe.get_doc("Sales Invoice", d.name)
        invoice_qty = sum(flt(it.qty) for it in (invoice_doc.items or []))

        is_return = flt(d.grand_total) < 0

        pos_transactions.append(frappe._dict({
            "sales_invoice": d.name,
            "posting_time": format_time(d.posting_time, "hh:mm a"),
            "posting_date": d.posting_date,
            "grand_total": d.grand_total,
            "customer": d.customer,
            "total_qty": invoice_qty,
            "Cashier": d.owner,
            "status": d.status,
            "is_return": is_return
        }))

        # 🔸 الضرائب
        for t in d.taxes:
            existing_tax = [tx for tx in taxes if tx.account_head == t.account_head and tx.rate == t.rate]
            if existing_tax:
                existing_tax[0].amount += flt(t.tax_amount)
            else:
                taxes.append(frappe._dict({
                    "account_head": t.account_head,
                    "rate": t.rate,
                    "amount": t.tax_amount,
                }))

        # 🔸 المدفوعات (Sales Invoice Payments)
        for p in d.payments:
            existing_pay = [pay for pay in payments if pay.mode_of_payment == p.mode_of_payment]

            print('existing_pay: ', existing_pay)
            payment_amount = flt(p.amount)
            if flt(d.grand_total) < 0 and payment_amount > 0:
                payment_amount = -payment_amount

            if existing_pay:
                existing_pay[0].expected_amount += payment_amount
            else:
                payments.append(frappe._dict({
                    "mode_of_payment": p.mode_of_payment,
                    "opening_amount": 0,
                    "expected_amount": payment_amount,
                }))

    # 🔹 مدفوعات Payment Entry
    for py in pos_payments:
        pos_payments_table.append(frappe._dict({
            "payment_entry": py.name,
            "mode_of_payment": py.mode_of_payment,
            "paid_amount": py.paid_amount,
            "posting_date": py.posting_date,
            "customer": py.party,
        }))

        existing_pay = [pay for pay in payments if pay.mode_of_payment == py.mode_of_payment]
        if existing_pay:
            existing_pay[0].expected_amount += flt(py.paid_amount)
        else:
            payments.append(frappe._dict({
                "mode_of_payment": py.mode_of_payment,
                "opening_amount": 0,
                "expected_amount": py.paid_amount,
            }))

    # ✅ النتيجة النهائية
    return {
        "total_sales": total_sales,
        "net_total": net_total,
        "total_quantity": total_qty,
        "transactions": pos_transactions,
        "taxes": taxes,
        "payments": payments,
        "pos_payments": pos_payments_table
    }

def calculate_total_cash_collected(shift_id):
    from frappe.utils import flt

    transactions = get_shift_pos_transactions(shift_id)

    total = 0.0
    for tx in transactions:
        amount = flt(tx.get("amount", 0))
        if tx.get("type") == "in":
            total += amount
        elif tx.get("type") == "out":
            total -= amount

    return total

def calculate_total_cash_collected(shift_id):
    from frappe.utils import flt

    transactions = get_shift_pos_transactions(shift_id)
    total = sum(
        flt(tx["amount"]) if tx["type"] == "in" else -flt(tx["amount"])
        for tx in transactions
    )

    # أضف الغير مخصصة إن أردت احتسابها
    unallocated = get_shift_unallocated_payments(shift_id)
    total += sum(flt(pe.get("unallocated_amount", 0)) for pe in unallocated)

    return total


def init_payments_from_opening(opening_shift: dict):
    opening = {}
    for detail in opening_shift.get("balance_details", []):
        mop = detail.get("mode_of_payment")
        opening[mop] = {
            "mode_of_payment": mop,
            "opening_amount": flt(detail.get("amount") or 0),
            "expected_amount": 0,
            "closing_amount": 0,
        }
    return opening

def summarize_invoices(invoices):
    summary = {
        "grand_total": 0,
        "net_total": 0,
        "total_quantity": 0
    }
    for inv in invoices:
        summary["grand_total"] += inv["grand_total"]
        summary["net_total"] += inv["net_total"]
        summary["total_quantity"] += inv["total_qty"]
    return summary

def compute_expected_from_invoices(invoices, payments):
    """تحسب expected_amount لكل طريقة دفع من الفواتير"""
    payments_dict = {}

    for inv in invoices:
        # 1️⃣ دفعات POS المباشرة
        if inv["payments"]:
            for p in inv["payments"]:
                mop = p.mode_of_payment
                if mop not in payments:
                    payments[mop] = {
                        "mode_of_payment": mop,
                        "opening_amount": 0,
                        "expected_amount": 0,
                        "closing_amount": 0,
                    }
                payments[mop]["expected_amount"] += p.amount

        # 2️⃣ Payment Entries المرتبطة بالفاتورة (دائمًا)
        payment_entries = get_shift_invoice_payments(inv["name"])
        for pe in payment_entries:
            mop = pe["mode_of_payment"]
            if mop not in payments:
                payments[mop] = {
                    "mode_of_payment": mop,
                    "opening_amount": 0,
                    "expected_amount": 0,
                    "closing_amount": 0,
                }
            payments[mop]["expected_amount"] += pe["allocated_to_this_invoice"]

    # طبع النتيجة للمراجعة
    print("✅ Aggregated Payments:", payments)
    return payments

def add_unallocated_to_payments(payments, unallocated):
    for pe in unallocated:
        mop = pe.get("mode_of_payment")
        if mop not in payments:
            payments[mop] = {
                "mode_of_payment": mop,
                "opening_amount": 0,
                "expected_amount": 0,
                "closing_amount": 0,
            }
        payments[mop]["expected_amount"] += flt(pe.get("unallocated_amount", 0))
    return payments


def add_allocated_from_payment_entries(payments, pos_payments):
    for py in pos_payments:
        mop = py.mode_of_payment
        from frappe.utils import flt
        if mop not in payments:
            payments[mop] = {
                "mode_of_payment": mop,
                "opening_amount": 0,
                "expected_amount": 0,
                "closing_amount": 0,
            }

        invoice_refs = frappe.get_all(
            "Payment Entry Reference",
            filters={
                "parent": py.name,
                "reference_doctype": "Sales Invoice"
            },
            fields=["allocated_amount"]
        )

        allocated = sum(flt(r.allocated_amount) for r in invoice_refs)
        payments[mop]["expected_amount"] += allocated

    return payments

def add_payment_mode_to_opening(shift_id, mode_of_payment, opening_amount=0.0):
    opening_shift = frappe.get_doc("POS Opening Shift", shift_id)

    existing = next(
        (b for b in opening_shift.balance_details if b.get("mode_of_payment") == mode_of_payment),
        None
    )

    if not existing:
        opening_shift.append("balance_details", {
            "mode_of_payment": mode_of_payment,
            "amount": opening_amount
        })
        # Tell Frappe to skip the submit validation check
        opening_shift.flags.ignore_validate_update_after_submit = True
        opening_shift.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"✅ Added {mode_of_payment} to balance_details of {shift_id}")
    else:
        print(f"ℹ️ {mode_of_payment} already exists in balance_details")


@frappe.whitelist()
def get_shift_payment_summary(opening_shift_name):
    """يرجع الـ expected amount لكل mode of payment"""
    opening_shift = frappe.get_doc("POS Opening Shift", opening_shift_name)
    invoices = get_pos_invoices(opening_shift_name)

    payments = {}

    # Opening amounts
    for detail in opening_shift.balance_details:
        mop = detail.mode_of_payment
        payments[mop] = {
            "mode_of_payment": mop,
            "opening_amount": flt(detail.amount),
            "expected_amount": flt(detail.amount),  # يبدأ بالـ opening
        }

    # Invoice payments
    for inv in invoices:
        if inv.payments:
            for p in inv.payments:
                mop = p.mode_of_payment
                if mop not in payments:
                    payments[mop] = {
                        "mode_of_payment": mop,
                        "opening_amount": 0,
                        "expected_amount": 0,
                    }
                payments[mop]["expected_amount"] += flt(p.amount)

        # Payment entries
        for pe in get_shift_invoice_payments(inv.name):
            mop = pe["mode_of_payment"]
            if mop not in payments:
                payments[mop] = {
                    "mode_of_payment": mop,
                    "opening_amount": 0,
                    "expected_amount": 0,
                }
            payments[mop]["expected_amount"] += flt(pe["allocated_to_this_invoice"])

    # Unallocated
    for pe in get_shift_unallocated_payments(opening_shift_name):
        mop = pe.get("mode_of_payment")
        if mop not in payments:
            payments[mop] = {
                "mode_of_payment": mop,
                "opening_amount": 0,
                "expected_amount": 0,
            }
        payments[mop]["expected_amount"] += flt(pe.get("unallocated_amount", 0))

    return list(payments.values())
