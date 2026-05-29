# retail/retail/api/user_management.py

import frappe
from frappe import _
from functools import wraps

@frappe.whitelist(allow_guest=True)
def get_all_users():
    """Get all system users"""
    try:
        users = frappe.get_all(
            "User",
            filters={"name": ["not in", ["Guest", "Administrator"]]},
            fields=[
                "name", "full_name", "email", "enabled",
                "user_image", "creation", "last_login",
                "user_type"
            ],
            order_by="creation desc"
        )

        for user in users:
            # Get roles for each user
            roles = frappe.get_all(
                "Has Role",
                filters={"parent": user["name"], "parenttype": "User"},
                fields=["role"]
            )
            user["roles"] = [r["role"] for r in roles]
            user["status"] = "Active" if user["enabled"] else "Inactive"

        return {"status": "success", "data": users}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_all_users")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def create_user(data):
    """Create new user with roles"""
    try:
        import json
        if isinstance(data, str):
            data = json.loads(data)

        # Check if user exists
        if frappe.db.exists("User", data.get("email")):
            return {"status": "error", "message": "User with this email already exists"}

        user = frappe.new_doc("User")
        user.email      = data.get("email")
        user.first_name = data.get("first_name")
        user.last_name  = data.get("last_name", "")
        user.full_name  = f"{data.get('first_name')} {data.get('last_name', '')}".strip()
        user.enabled    = 1
        user.user_type  = data.get("user_type", "System User")
        user.send_welcome_email = 0

        # Add roles
        for role in data.get("roles", []):
            user.append("roles", {"role": role})

        user.insert(ignore_permissions=True)

        # Set password if provided
        if data.get("password"):
            from frappe.utils.password import update_password
            update_password(user.name, data.get("password"))

        frappe.db.commit()

        return {
            "status": "success",
            "data": {"name": user.name},
            "message": f"User {user.full_name} created successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_user")
        frappe.db.rollback()
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def update_user(name, data):
    """Update existing user"""
    try:
        import json
        if isinstance(data, str):
            data = json.loads(data)

        user = frappe.get_doc("User", name)
        user.first_name = data.get("first_name", user.first_name)
        user.last_name  = data.get("last_name", user.last_name)
        user.full_name  = f"{data.get('first_name')} {data.get('last_name', '')}".strip()
        user.enabled    = data.get("enabled", user.enabled)

        # Update roles - clear and re-add
        user.roles = []
        for role in data.get("roles", []):
            user.append("roles", {"role": role})

        user.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "data": {"name": user.name},
            "message": "User updated successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_user")
        frappe.db.rollback()
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def delete_user(name):
    """Disable user (soft delete)"""
    try:
        # لا نحذف المستخدم بالكامل - بنعمله disable
        user = frappe.get_doc("User", name)
        user.enabled = 0
        user.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": f"User {name} has been disabled"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "delete_user")
        return {"status": "error", "message": str(e)}

def require_roles(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_roles = frappe.get_roles()

            if not any(role in user_roles for role in roles):
                frappe.throw("Not permitted", frappe.PermissionError)

            return func(*args, **kwargs)
        return wrapper
    return decorator


@frappe.whitelist(allow_guest=True)
@require_roles("System Manager")
def get_available_roles():
    """Get all available roles"""
    try:

        if  "System Manager"  not  in  frappe.  get_roles(  frappe  .  session  .  user):
            frappe.throw(  _  (" "), frappe.PermissionError)
        roles = frappe.get_all(
            "Role",
            filters={
                "name": ["not in", ["Guest", "All", "Administrator"]],
                "disabled": 0
            },
            fields=["name"],
            order_by="name asc"
        )
        return {"status": "success", "data": [r["name"] for r in roles]}

    except Exception as e:
        return {"status": "error", "message": str(e)}



@frappe.whitelist(allow_guest=True)
def get_current_user_info():
    """Get current logged in user full info"""
    try:
        user_name = frappe.session.user
        user = frappe.get_doc("User", user_name)

        roles = frappe.get_all(
            "Has Role",
            filters={"parent": user_name, "parenttype": "User"},
            fields=["role"]
        )

        # Get employee info if exists
        employee = frappe.db.get_value(
            "Employee",
            {"user_id": user_name},
            ["department", "designation", "date_of_joining"],
            as_dict=True
        )

        return {
            "status": "success",
            "data": {
                "name":        user.full_name or user.name,
                "email":       user.email,
                "user_image":  user.user_image or "",
                "enabled":     user.enabled,
                "roles":       [r["role"] for r in roles],
                "department":  employee.department if employee else "N/A",
                "designation": employee.designation if employee else "N/A",
                "join_date":   str(employee.date_of_joining) if employee else "N/A",
                "status":      "Active" if user.enabled else "Inactive"
            }
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_current_user_info")
        return {"status": "error", "message": str(e)}
