import frappe
from frappe.utils.password import update_password

DEMO_SITES = [
    {
        "company": "BISMALA",
        "warehouse": "Stores - B",
        "customer_name": "Retail Demo Customer - BISMALA",
        "user_email": "retail.bismala.cashier@example.com",
        "user_first_name": "BISMALA Cashier",
        "profile_name": "Retail Demo POS - BISMALA",
        "password": "Retail@123",
    },
    {
        "company": "FRESHCUT",
        "warehouse": "Stores - FC",
        "customer_name": "Retail Demo Customer - FRESHCUT",
        "user_email": "retail.freshcut.cashier@example.com",
        "user_first_name": "FRESHCUT Cashier",
        "profile_name": "Retail Demo POS - FRESHCUT",
        "password": "Retail@123",
    },
]

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
                "company": company.company_name,
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

    profile.company = company.company_name
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


def run():
    for spec in DEMO_SITES:
        if not frappe.db.exists("Company", spec["company"]):
            continue

        company = frappe.get_doc("Company", spec["company"])
        user = _ensure_user(spec)
        customer = _ensure_customer(spec, company)
        _ensure_pos_profile(spec, user, customer, company)

    frappe.db.commit()


def execute():
    return run()
