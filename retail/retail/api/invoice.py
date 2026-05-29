import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, add_days, getdate, add_days, nowdate
from retail.retail.doctype.pos_coupon.pos_coupon import update_coupon_code_count
from retail.retail.api.posapp import get_company_domain
from retail.retail.doctype.delivery_charges.delivery_charges import (
    get_applicable_delivery_charges,
)
from erpnext.controllers.sales_and_purchase_return import make_return_doc


def create_sales_order(doc):
    if (
        doc.posa_pos_opening_shift
        and doc.pos_profile
        and doc.is_pos
        and doc.posa_delivery_date
        and not doc.update_stock
        and frappe.get_value("POS Profile", doc.pos_profile, "posa_allow_sales_order")
    ):
        sales_order_doc = make_sales_order(doc.name)
        if sales_order_doc:
            sales_order_doc.posa_notes = doc.posa_notes
            sales_order_doc.flags.ignore_permissions = True
            sales_order_doc.flags.ignore_account_permission = True
            sales_order_doc.save()
            sales_order_doc.submit()
            url = frappe.utils.get_url_to_form(
                sales_order_doc.doctype, sales_order_doc.name
            )
            msgprint = "Sales Order Created at <a href='{0}'>{1}</a>".format(
                url, sales_order_doc.name
            )
            frappe.msgprint(
                _(msgprint), title="Sales Order Created", indicator="green", alert=True
            )
            i = 0
            for item in sales_order_doc.items:
                doc.items[i].sales_order = sales_order_doc.name
                doc.items[i].so_detail = item.name
                i += 1

def make_sales_order(source_name, target_doc=None, ignore_permissions=True):
    def set_missing_values(source, target):
        target.ignore_pricing_rule = 1
        target.flags.ignore_permissions = ignore_permissions
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    def update_item(obj, target, source_parent):
        target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)
        target.delivery_date = (
            obj.posa_delivery_date or source_parent.posa_delivery_date
        )

    doclist = get_mapped_doc(
        "Sales Invoice",
        source_name,
        {
            "Sales Invoice": {
                "doctype": "Sales Order",
            },
            "Sales Invoice Item": {
                "doctype": "Sales Order Item",
                "field_map": {
                    "cost_center": "cost_center",
                    "Warehouse": "warehouse",
                    "delivery_date": "posa_delivery_date",
                    "posa_notes": "posa_notes",
                },
                "postprocess": update_item,
            },
            "Sales Taxes and Charges": {
                "doctype": "Sales Taxes and Charges",
                "add_if_empty": True,
            },
            "Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
            "Payment Schedule": {"doctype": "Payment Schedule", "add_if_empty": True},
        },
        target_doc,
        set_missing_values,
        ignore_permissions=ignore_permissions,
    )

    return doclist

def update_coupon(doc, transaction_type):
    for coupon in doc.posa_coupons:
        if not coupon.applied:
            continue
        update_coupon_code_count(coupon.coupon, transaction_type)

def add_loyalty_point(invoice_doc):
    for offer in invoice_doc.posa_offers:
        if offer.offer == "Loyalty Point":
            original_offer = frappe.get_doc("POS Offer", offer.offer_name)
            if original_offer.loyalty_points > 0:
                loyalty_program = frappe.get_value(
                    "Customer", invoice_doc.customer, "loyalty_program"
                )
                if not loyalty_program:
                    loyalty_program = original_offer.loyalty_program
                doc = frappe.get_doc(
                    {
                        "doctype": "Loyalty Point Entry",
                        "loyalty_program": loyalty_program,
                        "loyalty_program_tier": original_offer.name,
                        "customer": invoice_doc.customer,
                        "invoice_type": "Sales Invoice",
                        "invoice": invoice_doc.name,
                        "loyalty_points": original_offer.loyalty_points,
                        "expiry_date": add_days(invoice_doc.posting_date, 10000),
                        "posting_date": invoice_doc.posting_date,
                        "company": invoice_doc.company,
                    }
                )
                doc.insert(ignore_permissions=True)

def auto_set_delivery_charges(doc):
    if not doc.pos_profile:
        return
    if not frappe.get_cached_value(
        "POS Profile", doc.pos_profile, "posa_auto_set_delivery_charges"
    ):
        return

    delivery_charges = get_applicable_delivery_charges(
        doc.company,
        doc.pos_profile,
        doc.customer,
        doc.shipping_address_name,
        doc.posa_delivery_charges,
        restrict=True,
    )

    if doc.posa_delivery_charges:
        if doc.posa_delivery_charges_rate:
            return
        else:
            if len(delivery_charges) > 0:
                doc.posa_delivery_charges_rate = delivery_charges[0].rate
    else:
        if len(delivery_charges) > 0:
            doc.posa_delivery_charges = delivery_charges[0].name
            doc.posa_delivery_charges_rate = delivery_charges[0].rate
        else:
            doc.posa_delivery_charges = None
            doc.posa_delivery_charges_rate = None

def calc_delivery_charges(doc):
    if not doc.pos_profile:
        return

    old_doc = None
    calculate_taxes_and_totals = False
    if not doc.is_new():
        old_doc = doc.get_doc_before_save()
        if not doc.posa_delivery_charges and not old_doc.posa_delivery_charges:
            return
    else:
        if not doc.posa_delivery_charges:
            return
    if not doc.posa_delivery_charges:
        doc.posa_delivery_charges_rate = 0

    charges_doc = None
    if doc.posa_delivery_charges:
        charges_doc = frappe.get_cached_doc(
            "Delivery Charges", doc.posa_delivery_charges
        )
        doc.posa_delivery_charges_rate = charges_doc.default_rate
        charges_profile = next(
            (i for i in charges_doc.profiles if i.pos_profile == doc.pos_profile), None
        )
        if charges_profile:
            doc.posa_delivery_charges_rate = charges_profile.rate

    if old_doc and old_doc.posa_delivery_charges:
        old_charges = next(
            (
                i
                for i in doc.taxes
                if i.charge_type == "Actual"
                and i.description == old_doc.posa_delivery_charges
            ),
            None,
        )
        if old_charges:
            doc.taxes.remove(old_charges)
            calculate_taxes_and_totals = True

    if doc.posa_delivery_charges:
        doc.append(
            "taxes",
            {
                "charge_type": "Actual",
                "description": doc.posa_delivery_charges,
                "tax_amount": doc.posa_delivery_charges_rate,
                "cost_center": charges_doc.cost_center,
                "account_head": charges_doc.shipping_account,
            },
        )
        calculate_taxes_and_totals = True

    if calculate_taxes_and_totals:
        doc.calculate_taxes_and_totals()

@frappe.whitelist(allow_guest=True)
def create_sales_return(invoice_name: str, items: list, pos_profile_name: str):
    """
    إنشاء فاتورة مرتجع من فاتورة بيع معينة لعدة منتجات وكميات.

    Args:
        invoice_name (str): اسم فاتورة البيع الأصلية.
        items (list): قائمة من العناصر بالشكل:
            [
                {"item_code": "Choco Glazed", "qty": 2},
                {"item_code": "Donut Caramel", "qty": 1}
            ]
    """

    validate_items_before_return(invoice_name, items)

    original_invoice = frappe.get_doc("Sales Invoice", invoice_name)

    # 🔹 التحقق من أن الفاتورة Submitted
    if original_invoice.docstatus != 1:
        frappe.throw(_("Invoice {0} must be submitted before creating a return.").format(invoice_name))

    # 🔹 إنشاء فاتورة المرتجع
    return_doc = make_return_doc("Sales Invoice", invoice_name)
    return_doc.items = []

    total_refund = 0

    for item_data in items:
        item_code = item_data.get("item_code")
        qty = item_data.get("qty")

        if not item_code or not qty:
            frappe.throw(_("Each item must include 'item_code' and 'qty'."))

        # 🔹 ابحث عن المنتج في الفاتورة الأصلية
        original_item = next((i for i in original_invoice.items if i.item_code == item_code), None)
        if not original_item:
            frappe.throw(_("Item {0} not found in invoice {1}.").format(item_code, invoice_name))

        # 🔹 تحقق من الكمية
        if qty <= 0:
            frappe.throw(_("Return quantity for {0} must be greater than 0.").format(item_code))

        if qty > original_item.qty:
            frappe.throw(_("Return quantity for {0} cannot exceed sold quantity ({1}).")
                         .format(item_code, original_item.qty))

        # 🔹 أضف الصنف للفاتورة المرتجع
        amount = -qty * original_item.rate
        total_refund += abs(amount)

        return_doc.append("items", {
            "item_code": item_code,
            "qty": -qty,
            "rate": original_item.rate,
            "amount": amount
        })

    # 🔹 إعادة الحساب
    return_doc.calculate_taxes_and_totals()

    # 🔹 إعداد الدفعة المستردة
    refund_amount = abs(return_doc.grand_total)
    return_doc.payments = []

    if original_invoice.payments:
        return_doc.append("payments", {
            "mode_of_payment": original_invoice.payments[0].mode_of_payment,
            "amount": -refund_amount  # سالب = استرداد للعميل
        })

    return_doc.paid_amount = 0
    return_doc.outstanding_amount = 0
    return_doc.posa_pos_opening_shift = pos_profile_name
    # 🔹 حفظ وتأكيد
    return_doc.insert()
    return_doc.submit()
    frappe.db.commit()

    frappe.msgprint(_(
        f"✅ Return Invoice {return_doc.name} created successfully.\n"
        f"Refund Amount: {refund_amount}"
    ))

    return {
        "return_invoice": return_doc.name,
        "refund_amount": refund_amount,
        "items": items
    }


frappe.whitelist()
def validate_items_before_return(invoice_name, items: list):
    """
    Validate items before creating a return invoice.
    - Ensure invoice exists.
    - Ensure item exists in the original invoice.
    - Ensure quantity is valid (not zero, not exceeding sold quantity).
    """
    if not frappe.db.exists("Sales Invoice", invoice_name):
        frappe.throw(_("Sales Invoice {0} not found").format(invoice_name))

    original_invoice = frappe.get_doc("Sales Invoice", invoice_name)
    original_items = {i.item_code: i.qty for i in original_invoice.items}


    if not isinstance(items, list) or not items:
        frappe.throw(_("Please provide at least one item to return."))

    for item_data in items:
        item_code = item_data.get("item_code")
        item_qty = item_data.get("qty")

        if not item_code:
            frappe.throw(_("Missing item_code in return items."))

        if item_code not in original_items:
            frappe.throw(_(f"Item {item_code} does not exist in Invoice {invoice_name}"))

        original_qty = original_items[item_code]

        # الكمية لازم تكون موجبة فقط، إحنا هنحولها لسالبة بعدين
        if item_qty <= 0:
            frappe.throw(_(f"Return quantity for item {item_code} must be greater than 0."))

        if item_qty > original_qty:
            frappe.throw(_(f"You cannot return more than sold quantity ({original_qty}) for item {item_code}"))

    return True

def get_returnable_invoices(customer=None, from_date=None, to_date=None, return_days_limit=None):
    """
    جلب الفواتير القابلة للإرجاع

    Args:
        customer (str): اسم العميل (اختياري)
        from_date (str): تاريخ البداية (اختياري)
        to_date (str): تاريخ النهاية (اختياري)
        return_days_limit (int): عدد الأيام المسموح فيها بالإرجاع (اختياري - مثلاً 7 أيام)

    Returns:
        list: قائمة الفواتير القابلة للإرجاع مع تفاصيلها
    """

    # Build filters
    filters = {
        "docstatus": 1,  # Submitted only
        "is_return": 0   # ليست فاتورة مرتجعة
    }

    if customer:
        filters["customer"] = customer

    if from_date:
        filters["posting_date"] = [">=", from_date]

    if to_date:
        if "posting_date" in filters:
            filters["posting_date"] = ["between", [from_date, to_date]]
        else:
            filters["posting_date"] = ["<=", to_date]

    # Get all submitted non-return invoices
    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=[
            "name",
            "customer",
            "customer_name",
            "posting_date",
            "grand_total",
            "status",
            "is_pos"
        ],
        order_by="posting_date desc"
    )

    returnable_invoices = []

    for invoice in invoices:
        # Check 1: التحقق من الفترة الزمنية
        if return_days_limit:
            invoice_date = getdate(invoice.posting_date)
            max_return_date = add_days(invoice_date, return_days_limit)
            today = getdate(nowdate())

            if today > max_return_date:
                continue  # تجاوزت فترة الإرجاع

        # Check 2: هل فيه كميات متبقية قابلة للإرجاع؟
        returnable_qty = get_returnable_qty(invoice.name)

        if not returnable_qty or returnable_qty["total_returnable"] <= 0:
            continue  # كل الكميات مرتجعة

        # Check 3: هل فيه Return Invoice كاملة؟
        if has_full_return(invoice.name):
            continue  # فيه فاتورة مرتجع كاملة

        # إضافة الفاتورة للقائمة
        invoice_data = {
            "name": invoice.name,
            "customer": invoice.customer,
            "customer_name": invoice.customer_name,
            "posting_date": invoice.posting_date,
            "grand_total": invoice.grand_total,
            "status": invoice.status,
            "is_pos": invoice.is_pos,
            "returnable_items": returnable_qty["items"],
            "total_returnable_qty": returnable_qty["total_returnable"],
            "days_since_invoice": (getdate(nowdate()) - getdate(invoice.posting_date)).days
        }

        returnable_invoices.append(invoice_data)

    return returnable_invoices

def get_returnable_qty(invoice_name):
    """
    حساب الكميات القابلة للإرجاع في الفاتورة

    Args:
        invoice_name (str): اسم الفاتورة

    Returns:
        dict: تفاصيل الكميات القابلة للإرجاع
    """

    # Get original invoice items
    original_items = frappe.get_all(
        "Sales Invoice Item",
        filters={"parent": invoice_name},
        fields=["item_code", "item_name", "qty", "rate", "amount", "name"]
    )

    returnable_items = []
    total_returnable = 0

    for item in original_items:
        # Get returned quantity for this item
        returned_qty = frappe.db.sql("""
            SELECT SUM(ABS(sii.qty)) as returned_qty
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
            WHERE si.docstatus = 1
                AND si.is_return = 1
                AND si.return_against = %s
                AND sii.item_code = %s
        """, (invoice_name, item.item_code), as_dict=True)

        returned_qty = returned_qty[0].returned_qty if returned_qty and returned_qty[0].returned_qty else 0

        # Calculate returnable quantity
        returnable_qty = item.qty - returned_qty

        if returnable_qty > 0:
            returnable_items.append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "original_qty": item.qty,
                "returned_qty": returned_qty,
                "returnable_qty": returnable_qty,
                "rate": item.rate,
                "amount": item.amount
            })
            total_returnable += returnable_qty

    return {
        "items": returnable_items,
        "total_returnable": total_returnable
    }

def has_full_return(invoice_name):
    """
    التحقق من وجود فاتورة مرتجعة كاملة

    Args:
        invoice_name (str): اسم الفاتورة

    Returns:
        bool: True إذا كان فيه فاتورة مرتجعة كاملة
    """

    # Get original total qty
    original_total = frappe.db.sql("""
        SELECT SUM(qty) as total_qty
        FROM `tabSales Invoice Item`
        WHERE parent = %s
    """, invoice_name, as_dict=True)

    original_qty = original_total[0].total_qty if original_total else 0

    # Get returned total qty
    returned_total = frappe.db.sql("""
        SELECT SUM(ABS(sii.qty)) as returned_qty
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1
            AND si.is_return = 1
            AND si.return_against = %s
    """, invoice_name, as_dict=True)

    returned_qty = returned_total[0].returned_qty if returned_total and returned_total[0].returned_qty else 0

    # Check if fully returned
    return returned_qty >= original_qty

@frappe.whitelist(allow_guest=True)
def get_returnable_invoices_api(customer=None, from_date=None, to_date=None, return_days_limit=None):
    """
    API للحصول على الفواتير القابلة للإرجاع
    يمكن استدعاؤها من Frontend
    """
    if return_days_limit:
        return_days_limit = int(return_days_limit)

    return get_returnable_invoices(
        customer=customer,
        from_date=from_date,
        to_date=to_date,
        return_days_limit=return_days_limit
    )

@frappe.whitelist(allow_guest=True)
def get_invoice_return_details(invoice_name):
    """
    الحصول على تفاصيل الإرجاع لفاتورة معينة
    """
    if not frappe.has_permission("Sales Invoice", "read"):
        frappe.throw(_("No permission to read Sales Invoice"))

    returnable_qty = get_returnable_qty(invoice_name)
    has_full = has_full_return(invoice_name)

    invoice = frappe.get_doc("Sales Invoice", invoice_name)

    return {
        "invoice_name": invoice_name,
        "customer": invoice.customer,
        "posting_date": invoice.posting_date,
        "grand_total": invoice.grand_total,
        "returnable_items": returnable_qty["items"],
        "total_returnable_qty": returnable_qty["total_returnable"],
        "has_full_return": has_full,
        "can_return": returnable_qty["total_returnable"] > 0 and not has_full
    }

def examples():
    """
    أمثلة على استخدام الـ Functions
    """

    # مثال 1: جلب كل الفواتير القابلة للإرجاع
    all_returnable = get_returnable_invoices()
    print(f"Found {len(all_returnable)} returnable invoices")

    # مثال 2: جلب فواتير عميل معين
    customer_returnable = get_returnable_invoices(customer="John Doe")

    # مثال 3: جلب فواتير خلال فترة معينة
    date_range_returnable = get_returnable_invoices(
        from_date="2025-01-01",
        to_date="2025-10-12"
    )

    # مثال 4: جلب فواتير يمكن إرجاعها خلال 7 أيام فقط
    recent_returnable = get_returnable_invoices(return_days_limit=7)

    # مثال 5: تفاصيل فاتورة معينة
    details = get_invoice_return_details("ACC-SINV-2025-00259")
    print(f"Can return: {details['can_return']}")
    print(f"Returnable items: {len(details['returnable_items'])}")

    # مثال 6: طباعة تفاصيل الفواتير
    for invoice in all_returnable:
        print(f"\nInvoice: {invoice['name']}")
        print(f"Customer: {invoice['customer_name']}")
        print(f"Date: {invoice['posting_date']}")
        print(f"Days old: {invoice['days_since_invoice']}")
        print(f"Returnable items: {invoice['total_returnable_qty']}")

        for item in invoice['returnable_items']:
            print(f"  - {item['item_name']}: {item['returnable_qty']} units")

def get_overpaid_invoices(shift_name):
    # نجيب الفواتير المدفوعة في الشيفت
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "docstatus": 1,
            "status": "Paid",
            "posa_pos_opening_shift": shift_name,
            "paid_amount": [">", "grand_total"]
        },
        fields=["name", "grand_total", "paid_amount"]
    )

    result = [
         {"name": inv["name"],"grand_total": inv["grand_total"], "paid_amount": inv["paid_amount"],"overpaid": inv["paid_amount"] - inv["grand_total"]}
        for inv in invoices
        if inv["paid_amount"] > inv["grand_total"]
    ]

    return result


def get_payment(invoice_name):
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    for payment in doc.payments:
        print(payment.mode_of_payment, payment.amount)


def fix_overpaid_invoice(invoice_name):
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    correct_amount = doc.grand_total

    # تعديل مباشر على child table
    for payment in doc.payments:
        frappe.db.set_value(
            "Sales Invoice Payment",  # child doctype
            payment.name,             # row name
            "amount",
            correct_amount
        )

    # تعديل paid_amount على الفاتورة
    frappe.db.set_value("Sales Invoice", invoice_name, "paid_amount", correct_amount)
    frappe.db.commit()

    print(f"✓ Fixed {invoice_name}: {doc.paid_amount} → {correct_amount}")
