
from __future__ import unicode_literals
import frappe
from frappe import _
from retail.retail.doctype.referral_code.referral_code import (
    create_referral_code,
)
from retail.retail.api.posapp import get_customer_names
from frappe.utils import cint, now_datetime
import re
from frappe.contacts.doctype.contact.contact import (
    get_contacts_linked_from,
    get_contacts_linking_to,
    get_contact_display_list
)
from frappe.contacts.doctype.address.address import get_preferred_address
from retail.retail.api.contact import get_party_contact_info
from retail.retail.api.address import get_party_address_info
def after_insert(doc, method):
    create_customer_referral_code(doc)
    create_gift_coupon(doc)


def validate(doc, method):
    validate_referral_code(doc)


def create_customer_referral_code(doc):
    if doc.posa_referral_company:
        company = frappe.get_cached_doc("Company", doc.posa_referral_company)
        if not company.posa_auto_referral:
            return
        create_referral_code(
            doc.posa_referral_company,
            doc.name,
            company.posa_customer_offer,
            company.posa_primary_offer,
            company.posa_referral_campaign,
        )


def create_gift_coupon(doc):
    if doc.posa_referral_code:
        coupon = frappe.new_doc("POS Coupon")
        coupon.customer = doc.name
        coupon.referral_code = doc.posa_referral_code
        coupon.create_coupon_from_referral()


def validate_referral_code(doc):
    referral_code = doc.posa_referral_code
    exist = None
    if referral_code:
        exist = frappe.db.exists("Referral Code", referral_code)
        if not exist:
            exist = frappe.db.exists("Referral Code", {"referral_code": referral_code})
        if not exist:
            frappe.throw(_("This Referral Code {0} not exists").format(referral_code))



@frappe.whitelist(allow_guest=True)
def get_customers_financial_data(pos_profile):
    """
    Return all customers as a list of objects containing customer info, contacts, addresses, debt and total purchases.
    """

    customers = get_customer_names(pos_profile)
    result = []

    for customer in customers:

        debt = frappe.db.get_value(
            "Sales Invoice",
            filters={"customer": customer.name, "docstatus": 1},
            fieldname="sum(outstanding_amount)"
        ) or 0

        total_purchases = frappe.db.get_value(
            "Sales Invoice",
            filters={"customer": customer.name, "docstatus": 1},
            fieldname="sum(total)"
        ) or 0

        customer_doc = frappe.get_doc("Customer", customer.name)
        contact_details = get_party_contact_info("Customer", customer.name)
        address_details = get_party_address_info(
            "Customer",
            customer.name,
            preferred_key="is_shipping_address"
        )

        # دمج كل بيانات العميل في object واحد
        customer_object = customer_doc.as_dict()
        customer_object["contacts"] = contact_details or []
        customer_object["addresses"] = address_details or []
        customer_object["debt"] = debt
        customer_object["total_purchases"] = total_purchases

        result.append(customer_object)

    return result


@frappe.whitelist(allow_guest=True)
def get_customer_profile(customer_name):
    """جلب جميع بيانات العميل الكاملة"""

    # 1. بيانات العميل الأساسية
    customer = frappe.get_doc("Customer", customer_name)

    contact_details = get_party_contact_info('Customer', customer.name)
    address_details = get_party_address_info('Customer', customer.name, preferred_key='is_shipping_address')

    # 2. المشتريات
    purchases = get_customer_purchases(customer_name)

    # 3. المعاملات المحاسبية
    transactions = get_customer_transactions(customer_name)

    # 4. المستندات
    documents = get_customer_documents(customer_name)
    customer_data = {
        "customer_data": customer.as_dict(),
        "contact_details": contact_details,
        "address_details": address_details,
        "debt": get_customer_debt(customer_name),
        "totalPurchases": get_customer_total_purchases(customer_name),
        "discount": get_customer_discount(customer_name),
        "purchases": purchases,
        "transactions": transactions,
        "documents": documents
    }
    return customer_data



def get_customer_debt(customer_name):
    """حساب الديون المتبقية"""
    debt = frappe.db.get_value(
        "Sales Invoice",
        filters={"customer": customer_name, "docstatus": 1},
        fieldname="sum(outstanding_amount)"
    ) or 0
    return float(debt)


def get_customer_total_purchases(customer_name):
    """حساب إجمالي المشتريات"""
    total = frappe.db.get_value(
        "Sales Invoice",
        filters={"customer": customer_name, "docstatus": 1},
        fieldname="sum(total)"
    ) or 0
    return float(total)


def get_customer_discount(customer_name):
    """ Get customer discount percentage from Pricing Rule Depending on Customer or Customer Group """
    customer = frappe.get_doc("Customer", customer_name)

    # 1️⃣ First check for Pricing Rule on Customer
    discount = frappe.db.get_value(
        "Pricing Rule",
        {
            "selling": 1,
            "disable": 0,
            "customer": customer.name
        },
        "discount_percentage"
    )

    if discount:
        return discount

    # 2️⃣ If no specific rule for Customer, check for Customer Group
    discount = frappe.db.get_value(
        "Pricing Rule",
        {
            "selling": 1,
            "disable": 0,
            "customer_group": customer.customer_group
        },
        "discount_percentage"
    )

    # 3️⃣ If no rule found, return 0
    return discount or 0

def get_customer_purchases(customer_name):
    """جلب فواتير المبيعات للعميل"""
    invoices = frappe.get_list(
        "Sales Invoice",
        filters={"customer": customer_name, "docstatus": 1},
        fields=["name", "posting_date", "total", "paid_amount", "outstanding_amount"]
    )

    purchases = []
    for idx, invoice in enumerate(invoices, start=1001):
        outstanding = invoice.outstanding_amount or 0
        paid = invoice.paid_amount or 0

        # حدد الحالة
        if outstanding == 0:
            status = "paid"
        elif paid > 0:
            status = "partial"
        else:
            status = "pending"

        purchases.append({
            "id": idx,
            "invoice_name":str(invoice.name),
            "date": str(invoice.posting_date),
            "amount": float(invoice.total),
            "paid": float(paid),
            "remaining": float(outstanding),
            "status": status
        })

    return purchases


def get_customer_transactions(customer_name):
    """جلب المعاملات المحاسبية للعميل"""
    # جلب من Accounts Receivable
    gl_entries = frappe.get_list(
        "GL Entry",
        filters={
            "party": customer_name,
            "party_type": "Customer"
        },
        fields=["posting_date", "remarks", "debit", "credit", "voucher_no", "voucher_type"],
        order_by="posting_date asc"
    )

    transactions = []
    balance = 0

    for entry in gl_entries:
        debit = entry.debit or 0
        credit = entry.credit or 0
        balance = balance + debit - credit

        transactions.append({
            "date": str(entry.posting_date),
            "description": entry.remarks or "عملية",
            "debit": float(debit),
            "credit": float(credit),
            "balance": float(balance)
        })

    return transactions


def get_customer_documents(customer_name):
    """جلب المستندات المرفوعة للعميل"""
    # جلب من File Attachments
    files = frappe.get_list(
        "File",
        filters={"attached_to_doctype": "Customer", "attached_to_name": customer_name},
        fields=["name", "file_name", "file_type", "creation"]
    )

    documents = []
    for idx, file in enumerate(files, start=1):
        documents.append({
            "id": idx,
            "name": file.file_name.split('/')[-1],  # اسم الملف فقط
            "type": file.file_type or "unknown",
            "uploadedAt": str(file.creation)
        })

    return documents


@frappe.whitelist(allow_guest=True)
def check_customer_exists(phone):
    """
    Check if a customer with this phone number exists
    Returns: { exists: True/False }
    """
    try:
        # Validate phone format
        if not is_valid_egyptian_phone(phone):
            frappe.throw(_("رقم الموبايل غير صحيح"))

        # Check if user exists with this phone
        user = frappe.db.exists("User", {"mobile_no": phone})

        # Check for blocked users
        if user:
            user_doc = frappe.get_doc("User", user)
            if not user_doc.enabled or user_doc.get("custom_is_blocked"):
                frappe.throw(_("تم حظر هذا الحساب. تواصل مع الدعم"))

        return {
            "exists": bool(user),
            "phone": phone
        }

    except Exception as e:
        frappe.log_error(f"Error checking customer: {str(e)}")
        frappe.throw(_("حدث خطأ. حاول مرة أخرى"))


@frappe.whitelist(allow_guest=True)
def register_customer(phone, full_name, password):
    """
    Register a new customer
    Creates both User and Customer records
    """
    try:
        phone = str(phone)
        full_name = str(full_name)
        password = str(password)

        # Validate inputs
        print('*****************************************************************')
        print(f"Registering customer with phone: {phone}, full_name: {full_name}")
        if not is_valid_egyptian_phone(phone):
            frappe.throw(_("رقم الموبايل غير صحيح"))
        print('Phone number validated')
        if len(password) < 6:
            frappe.throw(_("كلمة المرور يجب أن تكون 6 أحرف على الأقل"))
        print('Password validated')
        if not full_name or len(full_name.strip()) < 2:
            frappe.throw(_("من فضلك أدخل اسمك الكامل"))
        print('Full name validated')
        # Check if user already exists
        if frappe.db.exists("User", {"mobile_no": phone}):
            frappe.throw(_("هذا الرقم مسجل بالفعل"))
        print('No existing user with this phone')
        # Check rate limiting (prevent spam registrations)
        check_registration_rate_limit(phone)
        print('Passed rate limit check')
        # Create User
        user = frappe.get_doc({
            "doctype": "User",
            "email": f"{phone}@customer.local",  # Dummy email
            "first_name": full_name,
            "mobile_no": phone,
            "username": phone,
            "enabled": 1,
            "send_welcome_email": 0,
            "user_type": "Website User"
        })

        user.insert(ignore_permissions=True)
        print('User created with name:', user.name)
        # Set password
        # user.new_password = password
        user.new_password = password # --- IGNORE ---
        user.save(ignore_permissions=True)

        # Assign Customer and Accounts Manager role
        user.add_roles("Customer")
        user.add_roles("Accounts Manager")

        print('Customer role assigned')
        print('User registration successful, now creating Customer record')
        # Create Customer
        customer_name = f"{full_name} ({phone})"
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Individual",
            "account_manager":user.name,
            # "mobile_no": phone,
            "customer_group": "Individual",

        })

        customer.insert(ignore_permissions=True)

        # Link User to Customer
        # customer.db_set("custom_user", user.name)
        print('Customer created with name:', customer.name)
        # from erpnext.selling.doctype.customer.customer import make_contact
        # contact_params = {
        #     "doctype": "Customer",
        #     "name": customer_name,
        #     "customer_name": customer_name,
        #     "customer_type": "Individual",
        #     "email_id": str("contact@example.com"),
        #     "mobile_no": str(phone),
        # }
        # print('Creating contact with params:', contact_params)
        # contact = make_contact(frappe._dict(contact_params), is_primary_contact=1)

        # contact.insert(ignore_permissions=True)
        contact_doc = frappe.get_doc({
            "doctype": "Contact",
            "first_name": full_name,
            "mobile_no": phone,
            "email_id": f"{phone}@customer.local",
            "is_primary_contact": 1,
            "is_billing_contact": 1,
            "links": [{"link_doctype": "Customer", "link_name": customer.name}],
        })

        contact_doc.flags.ignore_permissions = True
        contact_doc.insert(ignore_permissions=True)

        frappe.db.commit()

        # Log registration
        log_customer_activity(phone, "registered")

        return {
            "success": True,
            "message": _("تم إنشاء الحساب بنجاح"),
            "user": user.name,
            "customer": customer.name
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Registration error: {str(e)}")
        error_msg = str(e)
        frappe.throw(error_msg)
        if "already exists" in error_msg.lower():
            error_msg = _("هذا الرقم مسجل بالفعل")
        elif "too many" in error_msg.lower():
            error_msg = _("تم تجاوز عدد المحاولات. حاول بعد قليل")

        return {
            "success": False,
            "error": error_msg
        }





@frappe.whitelist(allow_guest=True)
def update_customer_profile(full_name=None, email=None):
    """
    Update customer profile information
    """
    user = frappe.session.user

    if user == "Guest":
        frappe.throw(_("يجب تسجيل الدخول أولاً"))

    user_doc = frappe.get_doc("User", user)

    if full_name:
        user_doc.first_name = full_name

        # Update customer name too
        customer = frappe.db.get_value("Customer", {"custom_user": user}, "name")
        if customer:
            frappe.db.set_value("Customer", customer, "customer_name", full_name)

    if email and email != user_doc.email:
        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            frappe.throw(_("البريد الإلكتروني غير صحيح"))

        user_doc.email = email

    user_doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "message": _("تم تحديث البيانات بنجاح")
    }


# ========== HELPER FUNCTIONS ==========

def is_valid_egyptian_phone(phone):
    """
    Validate Egyptian phone number format
    Format: 01XXXXXXXXX (11 digits starting with 01)
    """
    pattern = r'^01[0-2,5]{1}[0-9]{8}$'
    return bool(re.match(pattern, str(phone)))


def check_registration_rate_limit(phone):
    """
    Check if registration attempts are within acceptable limits
    Prevents spam and abuse
    """
    cache_key = f"reg_attempt:{phone}"

    # Get attempt count from cache
    attempts = frappe.cache().get(cache_key) or 0

    if isinstance(attempts, bytes):
        attempts = int(attempts.decode())

    print(attempts)

    if attempts >= 7:  # Max 7 registration attempts per hour
        frappe.throw(_("تم تجاوز عدد المحاولات. حاول بعد ساعة"))

    # Increment counter with 1 hour expiry
    frappe.cache().setex(cache_key, 3600, attempts + 1)


def log_customer_activity(phone, activity_type, details=None):
    """
    Log customer activities for audit trail
    """
    try:
        frappe.get_doc({
            "doctype": "Custom Customer Activity Log",
            "phone": phone,
            "activity_type": activity_type,
            "details": details or "",
            "ip_address": frappe.local.request_ip,
            "timestamp": now_datetime()
        }).insert(ignore_permissions=True)
    except:
        pass  # Don't fail if logging fails


@frappe.whitelist(allow_guest=True)
def check_order_spam(customer):
    """
    Check if customer is spamming orders
    Returns: { is_spam: True/False, message: "" }
    """
    # Check orders in last hour
    one_hour_ago = frappe.utils.add_to_date(now_datetime(), hours=-1)

    recent_orders = frappe.db.count("Sales Order", {
        "customer": customer,
        "creation": (">", one_hour_ago)
    })

    if recent_orders >= 5:  # Max 5 orders per hour
        return {
            "is_spam": True,
            "message": _("تم تجاوز الحد الأقصى للطلبات في الساعة")
        }

    # Check failed payments
    failed_payments = frappe.db.count("Payment Entry", {
        "party": customer,
        "docstatus": 2,  # Cancelled
        "creation": (">", one_hour_ago)
    })

    if failed_payments >= 3:
        return {
            "is_spam": True,
            "message": _("تم تجاوز الحد الأقصى لمحاولات الدفع الفاشلة")
        }

    return {
        "is_spam": False,
        "message": ""
    }


@frappe.whitelist(allow_guest=True)
def block_customer(customer, reason=None):
    """
    Block a customer (Admin only)
    """
    if not frappe.has_permission("Customer", "write"):
        frappe.throw(_("غير مصرح"))

    # Get customer's user
    user = frappe.db.get_value("Customer", customer, "custom_user")

    if user:
        user_doc = frappe.get_doc("User", user)
        user_doc.enabled = 0
        user_doc.custom_is_blocked = 1
        user_doc.custom_block_reason = reason
        user_doc.save(ignore_permissions=True)

        log_customer_activity(user_doc.mobile_no, "blocked", reason)

        frappe.db.commit()

        return {
            "success": True,
            "message": _("تم حظر العميل")
        }

    frappe.throw(_("العميل غير موجود"))


@frappe.whitelist(allow_guest=True)
def unblock_customer(customer):
    """
    Unblock a customer (Admin only)
    """
    if not frappe.has_permission("Customer", "write"):
        frappe.throw(_("غير مصرح"))

    user = frappe.db.get_value("Customer", customer, "custom_user")

    if user:
        user_doc = frappe.get_doc("User", user)
        user_doc.enabled = 1
        user_doc.custom_is_blocked = 0
        user_doc.custom_block_reason = ""
        user_doc.save(ignore_permissions=True)

        log_customer_activity(user_doc.mobile_no, "unblocked")

        frappe.db.commit()

        return {
            "success": True,
            "message": _("تم إلغاء حظر العميل")
        }

    frappe.throw(_("العميل غير موجود"))

import frappe
from frappe import _
from frappe.contacts.doctype.address.address import get_condensed_address


# ─── helpers ──────────────────────────────────────────────────────────────────

def _address_dict(addr_doc) -> dict:
    return {
        "name"               : addr_doc.name,
        "address_title"      : addr_doc.address_title,
        "address_line1"      : addr_doc.address_line1,
        "address_line2"      : addr_doc.address_line2,
        "city"               : addr_doc.city,
        "state"              : addr_doc.state,
        "country"            : addr_doc.country,
        "pincode"            : addr_doc.pincode,
        "is_primary_address" : addr_doc.is_primary_address,
        "is_shipping_address": addr_doc.is_shipping_address,
        "condensed"          : get_condensed_address(addr_doc),
    }


def _get_contacts_with_address(doctype: str, name: str) -> list[dict]:
    """
    بديل عن get_contacts_linking_to —
    كل كونتكت يرجع بـ email_ids + phone_nos + linked_address
    """
    if not frappe.has_permission("Contact", "read"):
        return []

    contact_list = frappe.get_list(
        "Contact",
        filters=[
            ["Dynamic Link", "link_doctype", "=", doctype],
            ["Dynamic Link", "link_name",    "=", name],
            ["Dynamic Link", "parenttype",   "=", "Contact"],
        ],
        fields=["*"],
        order_by="is_primary_contact DESC, `tabContact`.creation ASC",
    )

    for c in contact_list:

        # كل الإيميلات — primary أولاً
        c["email_ids"] = frappe.get_all(
            "Contact Email",
            filters={"parenttype": "Contact", "parent": c.name},
            fields=["email_id", "is_primary"],
            order_by="is_primary DESC",
        )

        # كل الأرقام — primary أولاً
        c["phone_nos"] = frappe.get_all(
            "Contact Phone",
            filters={"parenttype": "Contact", "parent": c.name},
            fields=["phone", "is_primary_phone", "is_primary_mobile_no"],
            order_by="is_primary_phone DESC, is_primary_mobile_no DESC",
        )

        # العنوان المرتبط بالكونتكت (c.address = name of Address doc)
        c["linked_address"] = None
        if c.get("address") and frappe.has_permission("Address", "read"):
            try:
                c["linked_address"] = _address_dict(frappe.get_doc("Address", c["address"]))
            except Exception:
                pass

    return contact_list


# ─────────────────────────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=False)
def get_party_profile(doctype, name):
    try:
        if not frappe.db.exists(doctype, name):
            frappe.throw(_("{0} {1} not found").format(doctype, name))

        doc        = frappe.get_doc(doctype, name)
        basic_data = doc.as_dict()

        # ✅ الكونتكتات مع إيميلات + أرقام + عنوان مرتبط
        contacts = _get_contacts_with_address(doctype, name)

        # ── العناوين ─────────────────────────────────────────────────────────
        primary_address_data  = {}
        shipping_address_data = {}
        all_addresses         = []

        for row in frappe.get_all(
            "Dynamic Link",
            filters={"link_doctype": doctype, "link_name": name, "parenttype": "Address"},
            fields=["parent"],
            distinct=True,
        ):
            try:
                addr_dict = _address_dict(frappe.get_doc("Address", row["parent"]))
                all_addresses.append(addr_dict)
                if addr_dict["is_primary_address"]:
                    primary_address_data  = addr_dict
                if addr_dict["is_shipping_address"]:
                    shipping_address_data = addr_dict
            except Exception:
                continue

        # list كامل لعناوين الشحن (ممكن أكتر من واحد)
        shipping_addresses = [a for a in all_addresses if a["is_shipping_address"]]
        if not shipping_addresses and primary_address_data:
            shipping_addresses = [primary_address_data]

        # ── مالية + طلبات ─────────────────────────────────────────────────────
        financial_data    = {}
        orders            = []
        customer_invoices = []
        transactions      = []

        if doctype == "Supplier":
            financial_data = get_supplier_financial_summary(name)

        elif doctype == "Customer":
            from erpnext.selling.doctype.customer.customer import get_customer_outstanding

            company = frappe.db.get_single_value("Global Defaults", "default_company")
            financial_data = {
                "due_amount" : get_customer_outstanding(name, company),
                "total_sales": frappe.db.get_value(
                    "Sales Invoice",
                    {"customer": name, "docstatus": 1},
                    "SUM(grand_total) as total",
                ) or 0,
            }

            orders       = get_customer_orders(name).get("orders", [])
            transactions = get_customer_transactions(customer_name=name)

            for inv in frappe.get_all(
                "Sales Invoice",
                filters={"customer": name, "docstatus": 1},
                fields=["name as invoice_name", "posting_date as date",
                        "grand_total as amount", "status"],
                order_by="posting_date desc",
                limit=100,
            ):
                paid = frappe.db.get_value(
                    "Payment Entry Reference",
                    {"reference_name": inv["invoice_name"],
                     "reference_doctype": "Sales Invoice"},
                    "SUM(allocated_amount)",
                ) or 0

                raw = inv.get("status", "")
                mapped = (
                    "paid"      if raw == "Paid"                     else
                    "partial"   if raw in ("Partly Paid", "Overdue") else
                    "cancelled" if raw in ("Cancelled", "Return")    else
                    "pending"
                )

                customer_invoices.append({
                    "invoice_name": inv["invoice_name"],
                    "date"        : str(inv["date"]) if inv["date"] else "",
                    "amount"      : inv["amount"] or 0,
                    "paid"        : paid,
                    "remaining"   : (inv["amount"] or 0) - paid,
                    "status"      : mapped,
                })

        return {
            "status"            : "success",
            "party_type"        : doctype,
            "party_name"        : name,
            "basic_data"        : basic_data,
            "contacts"          : contacts,            # ✅ email_ids + phone_nos + linked_address
            "addresses"         : all_addresses,
            "primary_address"   : primary_address_data,
            "shipping_address"  : shipping_address_data,   # backward compat
            "shipping_addresses": shipping_addresses,      # ✅ list كامل
            "financial_data"    : financial_data,
            "purchases"         : orders,
            "customer_invoices" : customer_invoices,
            "transactions"      : transactions,
        }

    except Exception as e:
        frappe.log_error(title="Error getting party profile", message=frappe.get_traceback())
        frappe.throw(str(e))

@frappe.whitelist(allow_guest=True)
def get_customer_info():
    """
    Get current logged-in customer information
    """
    user = frappe.session.user

    if user == "Guest":
        frappe.throw(_("يجب تسجيل الدخول أولاً"))

    print("user ",user)
    user_doc = frappe.get_doc("User", user)
    # print("user_doc",user_doc.nameuser)

    # Get linked customer
    customer_id =  frappe.db.get_value("Customer", {"account_manager": user_doc.name},"name")
    if not customer_id:
        print("No Customer Linked to This User")
        return {}
    return get_party_profile("Customer", customer_id)

from frappe.utils import now, flt

@frappe.whitelist(allow_guest=True)
def create_order(customer, items_json, total, delivery_date, shipping_address, notes=None):
    """
    Create a Sales Order from external source (e.g., customer app).

    Args:
        customer (str): Customer ID or name
        items_json (str): JSON string of item list
        total (float): Total order value
        shipping_address (str): Optional shipping address
        notes (str): Optional notes

    Returns:
        dict: Response with status and message
    """
    try:
        # Validate input parameters
        if not customer:
            return {
                "status": "error",
                "message": _("Customer is required")
            }

        if not items_json:
            return {
                "status": "error",
                "message": _("Items are required")
            }

        # Parse items JSON
        try:
            items = frappe.loa(items_json)
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": _("Invalid JSON format for items: {0}").format(str(e))
            }

        if not items or len(items) == 0:
            return {
                "status": "error",
                "message": _("No items provided")
            }

        # Validate customer exists
        if not frappe.db.exists("Customer", customer):
            return {
                "status": "error",
                "message": _("Customer '{0}' does not exist").format(customer)
            }

        # Create new Sales Order
        so = frappe.new_doc("Sales Order")
        so.customer = customer
        so.transaction_date = now()
        so.delivery_date = delivery_date  # Customer can but date you want to delivery date

        # Set workflow state if it exists
        #قيد الانتظار
        try:
            so.workflow_state = "In Review"
        except:
            pass  # Workflow might not be configured

        # Add items to sales order
        for item_data in items:
            item_code = item_data.get("item_code")
            qty = flt(item_data.get("qty", 1))
            rate = flt(item_data.get("rate", 0))

            # Validate item exists
            if not frappe.db.exists("Item", item_code):
                frappe.log_error(
                    title="Invalid Item Code",
                    message=f"Item {item_code} does not exist"
                )
                continue

            # Get default warehouse for item
            warehouse = item_data.get("warehouse")

            so.append("items", {
                "item_code": item_code,
                "qty": qty,
                "rate": rate,
                "warehouse": warehouse,
                "delivery_date":delivery_date
            })

        # Check if any items were added
        if not so.items:
            return {
                "status": "error",
                "message": _("No valid items found")
            }

        # Set optional fields
        if shipping_address:
            # Validate shipping address exists
            if frappe.db.exists("Address", shipping_address):
                so.shipping_address_name = shipping_address
            # if Customer do not have Address record in back end or want to ship to anther one
            # he should fill and create anther shipping address to link  with field shipping_address_name in SO
            so.shipping_address_name = shipping_address
        if notes:
            so.posa_notes = notes

        # Set total if provided (for validation)
        if total:
            so.total = flt(total)

        # Save the Sales Order
        so.insert(ignore_permissions=True)

        # Submit if auto-submit is required
        # so.submit()  # Uncomment if you want to auto-submit

        frappe.db.commit()

        return {
            "status": "success",
            "message": _("Order created successfully"),
            "order_id": so.name,
            "order_total": so.grand_total
        }

    except frappe.ValidationError as e:
        frappe.db.rollback()
        frappe.log_error(
            title="Order Creation Validation Error",
            message=frappe.get_traceback()
        )
        return {
            "status": "error",
            "message": _("Validation Error: {0}").format(str(e))
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(
            title="Create Order Failed",
            message=frappe.get_traceback()
        )
        return {
            "status": "error",
            "message": _("Failed to create order: {0}").format(str(e))
        }

@frappe.whitelist(allow_guest=True)
def get_customer_orders(customer):
    """
    Get all orders for a specific customer with order items
    Args:
        customer (str): Customer ID or name
    Returns:
        dict: Response with orders list including items
    """
    try:
        if not customer:
            return {
                "status": "error",
                "message": _("Customer is required")
            }

        # Get orders with basic info
        orders = frappe.get_all(
            "Sales Order",
            filters={"customer": customer},
            fields=[
                "name",
                "transaction_date",
                "grand_total",
                "status",
                "workflow_state",
                "customer_name",
                "shipping_address_name",
                "shipping_address",
                "delivery_date",
                "total_qty",
                "net_total",
                "total_taxes_and_charges"
            ],
            order_by="creation desc"
        )

        # Get items for each order
        for order in orders:
            # Get order items
            order_items = frappe.get_all(
                "Sales Order Item",
                filters={"parent": order.name},
                fields=[
                    "item_code",
                    "item_name",
                    "qty",
                    "rate",
                    "amount",
                    "description",
                    "uom",
                    "stock_qty"
                ],
                order_by="idx asc"
            )

            # Add items to order
            order["items"] = order_items
            order["phone"] = frappe.db.get_value(
                "Customer",
                {"Customer_name":customer},
                [ "mobile_no"]
            )

            # Get shipping address details if available
            if order.get("shipping_address_name"):
                try:
                    address = frappe.get_doc("Address", order.shipping_address_name)
                    order["shipping_address"] = {
                        "address_line1": address.address_line1,
                        "address_line2": address.address_line2,
                        "city": address.city,
                        "state": address.state,
                        "country": address.country,
                        "pincode": address.pincode
                    }
                except:
                    order["shipping_address"] = None

        return {
            "status": "success",
            "orders": orders,
            "total_orders": len(orders)
        }

    except Exception as e:
        frappe.log_error(
            title="Get Customer Orders Failed",
            message=frappe.get_traceback()
        )
        return {
            "status": "error",
            "message": str(e)
        }
