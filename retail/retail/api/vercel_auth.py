import frappe
from frappe.auth import check_password
from frappe.utils import now


@frappe.whitelist(allow_guest=True)
def token_login(username=None, password=None):
    if not username or not password:
        frappe.throw("Username and password are required", frappe.AuthenticationError)

    user = frappe.get_doc("User", username)
    check_password(username, password)

    if not user.enabled:
        frappe.throw("User is disabled", frappe.PermissionError)

    api_key = frappe.generate_hash(length=16)
    api_secret = frappe.generate_hash(length=16)

    user.api_key = api_key
    user.api_secret = api_secret
    user.last_login = now()
    user.last_ip = frappe.local.request_ip or ""
    user.last_active = now()
    user.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "message": "Authentication successful",
        "data": {
            "user": user.name,
            "user_id": user.name,
            "full_name": user.full_name,
            "email": user.email,
            "user_type": user.user_type,
            "api_key": api_key,
            "api_secret": api_secret,
            "role": [role.role for role in user.roles],
            "generated_at": now(),
        },
    }
