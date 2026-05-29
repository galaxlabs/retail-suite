import frappe
import math

from frappe.utils import today, formatdate, flt, datetime
import calendar
from retail.retail.api.payment_utils import get_shift_payments_entries, get_shift_unallocated_payments, get_shift_invoice_payments, get_shift_pos_invoices

@frappe.whitelist(allow_guest=True)
def process_auto_attendance_api(shift_name):
    doc = frappe.get_doc('Shift Type', shift_name)
    doc.process_auto_attendance()


@frappe.whitelist(allow_guest=True)
def get_shift_statistics():
    today = datetime.date.today()

    # بداية الأسبوع (السبت كأول يوم في الأسبوع)
    week_details = get_week_range_in_month(today)
    number_of_week = week_details["week_number"]
    start_of_week = week_details["start_date"]
    end_of_week = week_details["end_date"]
    # بداية الشهر
    start_of_month = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_of_month = today.replace(day=last_day)
    def get_sum(doctype, filters, fieldname):
        conditions = []
        values = []
        for key, val in filters.items():
            if isinstance(val, list):
                # لو الفلتر في شكل ["between", [start, end]]
                if val[0].lower() == "between":
                    conditions.append(f"{key} BETWEEN %s AND %s")
                    values.extend(val[1])
                else:
                    conditions.append(f"{key} {val[0]} %s")
                    values.append(val[1])
            else:
                conditions.append(f"{key}=%s")
                values.append(val)

        where = " AND ".join(conditions)
        sql = f"SELECT SUM({fieldname}) FROM `tab{doctype}` WHERE {where}"
        result = frappe.db.sql(sql, values)
        return result[0][0] or 0

    stats = {
        "today_shifts": frappe.db.count("POS Opening Shift", {"posting_date": today}),
        "today_sales": get_sum("Sales Invoice", {"posting_date": today, "docstatus": 1, "is_pos":1}, "grand_total"),

        # 📅 الأسبوع الحالي (من السبت للجمعة)
        "week_shifts": frappe.db.count(
            "POS Opening Shift",
           {"posting_date": ["between", [start_of_week, end_of_week]]}
        ),
        "week_sales": get_sum(
            "Sales Invoice",
            {"posting_date": ["between", [start_of_week, end_of_week]], "docstatus": 1, "is_pos": 1},
            "grand_total"
        ),

        # 📆 الشهر الحالي
        "month_shifts": frappe.db.count(
            "POS Opening Shift",
            {"posting_date": [">=", start_of_month]}
        ),
        "month_sales": get_sum(
            "Sales Invoice",
            {"posting_date": ["between", [start_of_month, end_of_month]], "docstatus": 1, "is_pos": 1},
            "grand_total"
        ),
    }

    # 🧮 متوسط المبيعات
    stats["average_sales"] = round(
        stats["month_sales"] / stats["month_shifts"] if stats["month_shifts"] else 0, 2
    )

    return stats



def get_week_range_in_month(date=None):
    if date is None:
        date = datetime.date.today()

    # رقم الأسبوع داخل الشهر
    week_number = math.ceil(date.day / 7)

    # اليوم الأول في الشهر
    first_day_of_month = date.replace(day=1)

    # بداية الأسبوع
    start_day = (week_number - 1) * 7 + 1
    start_date = date.replace(day=start_day)

    # نهاية الأسبوع (أقصى حاجة يوم 28 أو نهاية الشهر)
    end_day = min(start_day + 6, (first_day_of_month.replace(month=date.month % 12 + 1, day=1) - datetime.timedelta(days=1)).day)
    end_date = date.replace(day=end_day)

    return {
        "week_number": week_number,
        "start_date": start_date,
        "end_date": end_date
    }



@frappe.whitelist(allow_guest=True)
def get_shifts(name=None,status=None):
    """
    Get POS Opening Shifts with optional status filter.
    If Closed, include linked POS Closing Shift details.
    """

    filters = {}
    if status:
        filters["status"] = status

    if name:
        filters["name"] = name

    # نجيب الـ Opening Shifts
    opening_shifts = frappe.get_all(
        "POS Opening Shift",
        filters=filters,
        fields=["name", "status", "posting_date", "pos_profile", "company", "period_start_date", "period_end_date", "user", "pos_closing_shift"]
    )
    print('print opeing',opening_shifts)
    result = []
    total_qty = 0
    total_sales = 0
    for shift in opening_shifts:
        shift_data = dict(shift)
        opening_cash = frappe.get_all("POS Opening Shift Detail", filters={"parent": shift.name}, fields=["mode_of_payment", "amount"])
        shift_data["opening_cash"] = opening_cash
        total_opening_cash = sum([d.amount for d in opening_cash])
        shift_data["total_opening_cash"] = total_opening_cash
        # لو الشيفت متقفل، نجيب تفاصيل الـ Closing Shift
        if shift.pos_closing_shift:
            closing_shift = frappe.get_doc("POS Closing Shift", shift.pos_closing_shift)

            shift_data["closing_shift"] = {
                "name_closing_shift": closing_shift.name,
                "period_end_date": closing_shift.period_end_date,
                "posting_date":closing_shift.posting_date,
                "grand_total": closing_shift.grand_total,   # اجمالي المبيعات
                "net_total": closing_shift.net_total,       # صافي
                "linked_invoices": [
                    {"invoice": i.sales_invoice, "amount": i.grand_total}
                    for i in closing_shift.get("pos_transactions")
                ],
                "pos_payments": [
                    {"mode_of_payment": m.mode_of_payment, "amount": m.paid_amount}
                    for m in closing_shift.get("pos_payments")
                ],
                "closing_balance":[
                    {"mode_of_payment": c.mode_of_payment, "closing_amount": c.closing_amount}
                    for c in closing_shift.get("payment_reconciliation")
                ]
            }
        else:
            shift_data["closing_shift"] = None
        invoices = get_shift_pos_invoices(shift.name)
        if len(invoices) > 0:
            for d in invoices:
                total_qty += flt(d.total_qty)
                total_sales += flt(d.grand_total)
            shift_data["invoices"] = invoices
            shift_data["total_qty"] = total_qty
            shift_data["total_sales"] = total_sales

        result.append(shift_data)
    print('======================result===============================')
    print("result",result)
    # return result
    if result is not None:

        frappe.response["http_status_code"] = 200

        frappe.response["message"] = {
            "status": "success",
            "http_status_code":200,
            "message": "Shifts fetched successfully",
            "data": result
        }

    else:

        frappe.response["http_status_code"] = 404

        frappe.response["message"] = {
            "status": "error",
            "http_status_code":404,
            "message": "Error fetching shifts",
            "data": []
        }


@frappe.whitelist(allow_guest=True)
def get_shift_pos_transactions(shift_id):
    pos_opening_shift = frappe.get_doc("POS Opening Shift", shift_id).as_dict()
    transactions = []

    # Opening balance entries — always "in"
    for b in pos_opening_shift.balance_details:
        transactions.append({
            "mode_of_payment": b.mode_of_payment,
            "type": "in",
            "amount": abs(flt(b.amount)),
            "description": "Opening Cash",
            "created_at": pos_opening_shift.period_start_date,
            "user_name": frappe.db.get_value("User", pos_opening_shift.user, "full_name") or "System",
        })

    invoices = get_shift_pos_invoices(shift_id)
    for d in invoices:
        is_return = flt(d.grand_total) < 0  # return invoice has negative grand_total

        for p in d.payments:
            payment_amount = flt(p.amount)
            if payment_amount == 0:
                continue

            transactions.append({
                "mode_of_payment": p.mode_of_payment,
                # return invoices flow cash OUT of the drawer
                "type": "out" if is_return else "in",
                "amount": abs(payment_amount),
                "description": (
                    f"مرتجع مبيعات - فاتورة {d.name}"
                    if is_return
                    else f"مبيعات نقدية - فاتورة {d.name}"
                ),
                "created_at": d.posting_date,
                "user_name": frappe.db.get_value("User", d.owner, "full_name") or "النظام",
            })

    # Credit / deferred payment collections — always "in"
    credit_payments = get_shift_payments_entries(shift_id)
    for c in credit_payments:
        transactions.append({
            "mode_of_payment": c.mode_of_payment,
            "type": "in",
            "amount": abs(flt(c.paid_amount)),
            "description": f"تحصيل - دفعة أجل {c.name}",
            "created_at": c.posting_date,
            "user_name": frappe.db.get_value("User", c.owner, "full_name") or "النظام",
            "name": c.name,
            "reference_no": c.reference_no,
            "customer": c.party,
        })

    return transactions

@frappe.whitelist(allow_guest=True)
def calculate_total_cash_collected(transactions):
    total_in = sum(t["amount"] for t in transactions if t["type"] == "in")
    total_out = sum(t["amount"] for t in transactions if t["type"] == "out")
    total_cash_collected = total_in - total_out
    return total_cash_collected

def get_all_shift_payment_entries(shift_id):
    invoices = get_shift_pos_invoices(shift_id)
    invoice_names = [inv.name for inv in invoices]

    if not invoice_names:
        return []

    return frappe.db.sql("""
        SELECT
            pe.name as payment_entry,
            pe.paid_amount,
            pe.unallocated_amount,
            SUM(
                CASE
                    WHEN per.reference_name IN %(invoices)s
                    THEN per.allocated_amount
                    ELSE 0
                END
            ) as allocated_amount
        FROM `tabPayment Entry` pe
        LEFT JOIN `tabPayment Entry Reference` per
            ON per.parent = pe.name
        WHERE pe.docstatus = 1
        GROUP BY pe.name
        HAVING allocated_amount > 0 OR pe.unallocated_amount > 0
    """, {"invoices": tuple(invoice_names)}, as_dict=1)


@frappe.whitelist(allow_guest=True)
def get_shift_details(shift_id):

    pos_opening_shift = frappe.get_doc("POS Opening Shift", shift_id).as_dict()

    closing_cash    = 0
    closing_balance = {}

    if pos_opening_shift.status == "Closed":
        closing_name = pos_opening_shift.get("pos_closing_shift")
        if closing_name:
            pos_closing_shift = frappe.get_doc("POS Closing Shift", closing_name).as_dict()
            closing_table     = pos_closing_shift.payment_reconciliation
            closing_cash      = sum([c.closing_amount for c in closing_table])
            closing_balance   = {c.mode_of_payment: c.closing_amount for c in closing_table}

    # 1-sum(opening_balance.values())
    opening_balance = {b.mode_of_payment: b.amount for b in pos_opening_shift.balance_details}

    total_sales          = 0
    payments_map         = {}
    invoice_list         = []
    staff_map            = {}

    pos_transactions     = get_shift_pos_transactions(shift_id)
    total_cash_collected = calculate_total_cash_collected(pos_transactions) if pos_transactions else 0

    invoices = get_shift_pos_invoices(shift_id)

    for d in invoices:
        total_sales += flt(d.grand_total)

        cashier_id   = d.owner
        cashier_name = frappe.db.get_value("User", cashier_id, "full_name") or cashier_id

        # ── 1. دفعات الـ POS المباشرة على الفاتورة ──────────
        pos_payments = [
            {
                "source":          "pos",
                "mode_of_payment": p.mode_of_payment,
                "amount":          flt(p.amount),
            }
            for p in d.payments
        ]

        # ── 2. Payment Entries المرتبطة بالفاتورة ────────────
        payment_entries = get_shift_invoice_payments(d.name)
        pe_payments = [
            {
                "source":                    "payment_entry",
                "payment_entry":             pe["payment_entry"],
                "mode_of_payment":           pe["mode_of_payment"],
                "amount":                    pe["allocated_to_this_invoice"],
                "paid_amount":               pe["paid_amount"],
                "party":                     pe["party"],
                "party_name":                pe["party_name"],
                "posting_date":              pe["posting_date"],
                "all_linked_invoices":       pe["all_linked_invoices"],
                "total_invoices_count":      pe["total_invoices_count"],
            }
            for pe in payment_entries
        ]

        # ── دمج الاتنين ───────────────────────────────────────
        all_payments = pos_payments + pe_payments

        # ── primary payment method ────────────────────────────
        if pos_payments:
            payment_method = pos_payments[0]["mode_of_payment"]
        elif pe_payments:
            payment_method = pe_payments[0]["mode_of_payment"]
        else:
            payment_method = "unknown"

        invoice_list.append({
            "name":             d.name,
            "posting_date":     str(d.posting_date),
            "posting_time":     str(d.posting_time) if d.get("posting_time") else "",
            "customer":         d.customer,
            "customer_name":    frappe.db.get_value("Customer", d.customer, "customer_name")
                                if d.customer else "Walk-in",
            "grand_total":      flt(d.grand_total),
            "total":            flt(d.grand_total),
            "total_qty":        flt(d.total_qty),
            "payment_method":   payment_method,
            # ── الجديد ──────────────────────────────────────
            "pos_payments":     pos_payments,      # دفعات POS مباشرة
            "payment_entries":  pe_payments,        # Payment Entries
            "all_payments":     all_payments,       # الكل مع بعض
            # ── قديم للتوافق ─────────────────────────────────
            "payments":         pos_payments,
            "cashier_name":     cashier_name,
            "owner":            cashier_id,
            "status":           d.status,
        })

        # ── payments aggregation (للـ reconciliation table) ───
        for p in all_payments:
            mop = p["mode_of_payment"]
            if mop not in payments_map:
                payments_map[mop] = {"count": 0, "expected_amount": 0.0}
            payments_map[mop]["count"]           += 1
            payments_map[mop]["expected_amount"] += flt(p["amount"])

        # ── staff ─────────────────────────────────────────────
        if cashier_id not in staff_map:
            staff_map[cashier_id] = {
                "user_id":        cashier_id,
                "name":           cashier_name,
                "initials":       "".join([n[0] for n in cashier_name.split()])[:2].upper(),
                "invoices_count": 0,
                "total_sales":    0.0,
            }
        staff_map[cashier_id]["invoices_count"] += 1
        staff_map[cashier_id]["total_sales"]    += flt(d.grand_total)

    # ── Build payments reconciliation list ────────────────────
    all_modes     = set(payments_map.keys()) | set(opening_balance.keys()) | set(closing_balance.keys())
    payments_list = []
    for mop in all_modes:
        expected = payments_map.get(mop, {}).get("expected_amount", 0)
        opening  = opening_balance.get(mop, 0)
        closing  = closing_balance.get(mop, 0)
        payments_list.append({
            "mode_of_payment": mop,
            "count":           payments_map.get(mop, {}).get("count", 0),
            "expected_amount": expected,
            "opening_amount":  opening,
            "closing_amount":  closing,
            "difference":      closing - (opening + expected),
        })
        print("payments_list",payments_list)
    # ── تتبع الفروقات لكل فاتورة ──────────────────────
    reconciliation_issues = []

    for inv in invoice_list:
        invoice_total   = flt(inv["grand_total"])
        # 2-Payment in Invoice (POS)
        pos_total       = sum(flt(p["amount"]) for p in inv["pos_payments"])
        # 3-Allocated Payments (Payment Entry)
        pe_total        = sum(flt(p["amount"]) for p in inv["payment_entries"])
        total_collected = pos_total + pe_total
        difference      = invoice_total - total_collected

        # هل في فرق؟
        if abs(difference) > 0.01:   # تسامح 0.01 لتجنب مشاكل الكسور
            reconciliation_issues.append({
                "invoice":          inv["name"],
                "customer":         inv["customer_name"],
                "invoice_total":    invoice_total,
                "pos_collected":    pos_total,
                "pe_collected":     pe_total,
                "total_collected":  total_collected,
                "difference":       difference,
                "issue_type":       "overpaid" if difference < 0 else "underpaid",
            })

    # ── الدفعات غير المخصصة ───────────────────────────
    unallocated_payments = get_shift_unallocated_payments(shift_id)
    # 4-unallocated_total
    unallocated_total = sum(flt(p["unallocated_amount"]) for p in unallocated_payments)
    # ✅ DEBUG هنا
    all_payment_entries = get_all_shift_payment_entries(shift_id)

    total_pe_paid = sum(flt(pe["paid_amount"]) for pe in all_payment_entries)
    total_allocated = sum(flt(pe["allocated_amount"]) for pe in all_payment_entries)
    total_unallocated = sum(flt(pe["unallocated_amount"]) for pe in all_payment_entries)

    print(f"""
    PE CHECK:
    Paid: {total_pe_paid}
    Allocated: {total_allocated}
    Unallocated: {total_unallocated}
    Diff: {total_pe_paid - (total_allocated + total_unallocated)}
    """)
    return {
        "id":                   pos_opening_shift.name,
        "name":                 pos_opening_shift.name,
        "status":               pos_opening_shift.status.lower(),
        "opened_at":            str(pos_opening_shift.period_start_date),
        "closed_at":            str(pos_opening_shift.period_end_date)
                                if pos_opening_shift.status == "Closed" else None,
        "period_start_date":    str(pos_opening_shift.period_start_date),
        "period_end_date":      str(pos_opening_shift.period_end_date)
                                if pos_opening_shift.period_end_date else None,
        "opened_by_name":       frappe.db.get_value("User", pos_opening_shift.user, "full_name"),
        "closed_by_name":       frappe.db.get_value("User", pos_opening_shift.closed_by, "full_name")
                                if pos_opening_shift.get("closed_by") else None,
        "opening_cash":         sum(opening_balance.values()),
        "closing_cash":         closing_cash,
        "total_sales":          flt(total_sales),
        "total_cash_collected": total_cash_collected,
        "invoices_count":       len(invoices),
        "invoices":             invoice_list,
        "payments":             payments_list,
        "transactions":         pos_transactions,
        "staff_performance":    list(staff_map.values()),
        "unallocated_total":      unallocated_total,
        "reconciliation_issues":  reconciliation_issues,    # ← جديد
        "unallocated_payments":   unallocated_payments,     # ← جديد
        "has_issues":             len(reconciliation_issues) > 0,  # ← جديد
    }

@frappe.whitelist(allow_guest=True)
def cancel_and_delete_shift_assignment(name):
    doc = frappe.get_doc("Shift Assignment", name)

    if doc.docstatus == 1:
        doc.cancel()

    frappe.delete_doc("Shift Assignment", name)

    return {
        'status': 201,
        "message": "Shift Assignement {0}Deleted Successfully".format(name)
    }

