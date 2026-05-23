import frappe
from frappe.utils import now_datetime, today
from frappe.utils.password import update_password

DEMO_USER = {
    "company": "Gromax",
    "warehouse": "Stores - G",
    "customer_name": "Retail Demo Customer - GROMAX",
    "user_email": "retail.gromax.cashier@example.com",
    "user_first_name": "GROMAX Cashier",
    "profile_name": "Retail Demo POS - GROMAX",
    "password": "Retail@123",
    "opening_amount": 1000,
}

DEMO_ROLES = ["Accounts Manager", "Accounts User", "Sales Manager"]


def _ensure_user(spec):
    if frappe.db.exists("User", spec["user_email"]):
        user = frappe.get_doc("User", spec["user_email"])
    else:
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": spec["user_email"],
                "first_name": spec["user_first_name"],
                "enabled": 1,
                "user_type": "System User",
                "send_welcome_email": 0,
            }
        )
        user.insert(ignore_permissions=True)

    existing_roles = {row.role for row in user.roles}
    for role in DEMO_ROLES:
        if frappe.db.exists("Role", role) and role not in existing_roles:
            user.append("roles", {"role": role})

    user.enabled = 1
    user.user_type = "System User"
    user.save(ignore_permissions=True)
    update_password(user.name, spec["password"], logout_all_sessions=False)
    return user


def _ensure_customer(spec, company):
    customer_name = frappe.db.get_value("Customer", {"customer_name": spec["customer_name"]}, "name")
    if customer_name:
        customer = frappe.get_doc("Customer", customer_name)
    else:
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": spec["customer_name"],
                "customer_type": "Individual",
                "customer_group": "Individual",
                "territory": "All Territories",
                "default_currency": company.default_currency,
                "default_price_list": "Standard Selling",
            }
        )
        customer.insert(ignore_permissions=True)

    customer.customer_type = "Individual"
    customer.customer_group = "Individual"
    customer.territory = "All Territories"
    customer.default_currency = company.default_currency
    customer.default_price_list = "Standard Selling"
    customer.save(ignore_permissions=True)
    return customer


def _ensure_pos_profile(spec, user, customer, company):
    existing_name = frappe.db.exists("POS Profile", spec["profile_name"])
    if existing_name:
        profile = frappe.get_doc("POS Profile", existing_name)
    else:
        profile = frappe.get_doc(
            {
                "doctype": "POS Profile",
                "name": spec["profile_name"],
                "company": company.name,
                "warehouse": spec["warehouse"],
                "customer": customer.name,
                "customer_group": "Individual",
                "territory": "All Territories",
                "selling_price_list": "Standard Selling",
                "currency": company.default_currency,
                "income_account": company.default_income_account,
                "expense_account": company.default_expense_account,
                "cost_center": company.cost_center,
                "write_off_account": company.write_off_account,
                "write_off_cost_center": company.cost_center,
                "ignore_pricing_rule": 1,
                "allow_rate_change": 1,
                "allow_discount_change": 1,
                "auto_add_item_to_cart": 1,
                "validate_stock_on_save": 1,
                "hide_unavailable_items": 0,
                "hide_images": 0,
                "print_receipt_on_order_complete": 1,
            }
        )

    profile.company = company.name
    profile.warehouse = spec["warehouse"]
    profile.customer = customer.name
    profile.customer_group = "Individual"
    profile.territory = "All Territories"
    profile.selling_price_list = "Standard Selling"
    profile.currency = company.default_currency
    profile.income_account = company.default_income_account
    profile.expense_account = company.default_expense_account
    profile.cost_center = company.cost_center
    profile.write_off_account = company.write_off_account
    profile.write_off_cost_center = company.cost_center
    profile.print_receipt_on_order_complete = 1
    profile.ignore_pricing_rule = 1
    profile.allow_rate_change = 1
    profile.allow_discount_change = 1
    profile.auto_add_item_to_cart = 1
    profile.validate_stock_on_save = 1
    profile.hide_unavailable_items = 0
    profile.hide_images = 0

    if not any(row.mode_of_payment == "Cash" for row in profile.payments):
        profile.append("payments", {"mode_of_payment": "Cash", "default": 1, "allow_in_returns": 1})
    else:
        for row in profile.payments:
            if row.mode_of_payment == "Cash":
                row.default = 1
                row.allow_in_returns = 1

    if not any(row.user == user.name for row in profile.applicable_for_users):
        profile.append("applicable_for_users", {"user": user.name, "default": 1})
    else:
        for row in profile.applicable_for_users:
            if row.user == user.name:
                row.default = 1

    if existing_name:
        profile.save(ignore_permissions=True)
    else:
        profile.insert(ignore_permissions=True)
    return profile


def _ensure_opening_shift(spec, user, profile, company):
    existing = frappe.get_all(
        "POS Opening Shift",
        filters={
            "company": company.name,
            "pos_profile": profile.name,
            "user": user.name,
            "docstatus": 1,
        },
        fields=["name", "status", "pos_closing_shift"],
        limit=1,
    )
    if existing:
        opening = frappe.get_doc("POS Opening Shift", existing[0].name)
        if opening.status == "Open" and not opening.pos_closing_shift:
            _ensure_closing_shift(opening, spec, profile, company, user)
        return opening

    opening = frappe.get_doc(
        {
            "doctype": "POS Opening Shift",
            "period_start_date": now_datetime(),
            "posting_date": today(),
            "company": company.name,
            "pos_profile": profile.name,
            "user": user.name,
            "balance_details": [
                {
                    "mode_of_payment": "Cash",
                    "amount": spec["opening_amount"],
                }
            ],
        }
    )
    opening.insert(ignore_permissions=True)
    opening.submit()
    _ensure_closing_shift(opening, spec, profile, company, user)
    return opening


def _ensure_closing_shift(opening, spec, profile, company, user):
    if opening.pos_closing_shift:
        return frappe.get_doc("POS Closing Shift", opening.pos_closing_shift)

    opening_amount = opening.balance_details[0].amount if opening.balance_details else spec["opening_amount"]
    closing = frappe.get_doc(
        {
            "doctype": "POS Closing Shift",
            "period_end_date": now_datetime(),
            "posting_date": today(),
            "pos_opening_shift": opening.name,
            "company": company.name,
            "pos_profile": profile.name,
            "user": user.name,
            "grand_total": 0,
            "net_total": 0,
            "total_quantity": 0,
            "payment_reconciliation": [
                {
                    "mode_of_payment": "Cash",
                    "opening_amount": opening_amount,
                    "expected_amount": opening_amount,
                    "closing_amount": opening_amount,
                }
            ],
        }
    )
    closing.insert(ignore_permissions=True)
    closing.submit()
    return closing


def run():
    if not frappe.db.exists("Company", DEMO_USER["company"]):
        return

    company = frappe.get_doc("Company", DEMO_USER["company"])
    user = _ensure_user(DEMO_USER)
    customer = _ensure_customer(DEMO_USER, company)
    profile = _ensure_pos_profile(DEMO_USER, user, customer, company)
    _ensure_opening_shift(DEMO_USER, user, profile, company)
    frappe.db.commit()


def execute():
    return run()
