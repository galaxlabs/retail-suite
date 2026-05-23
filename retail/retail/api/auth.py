# auth.py
import frappe
from frappe.auth import check_password
from frappe.utils import now
import secrets
import string


@frappe.whitelist(allow_guest=True)
def get_logged_user():
    return frappe.session.user

@frappe.whitelist(allow_guest=True)
def authenticate_and_generate_api_key(username, password):
    """
    Authenticate user and generate API key
    متبع نفس pattern لـ frappe.sessions.Session
    """

    # ✅ 1. تحقق من بيانات المستخدم
    user = frappe.get_doc('User', username)

    check_password(username, password)

    # ❌ تأكد إن الحساب مش معطل
    if not user.enabled:
        frappe.throw('User is disabled', frappe.PermissionError)

    # ✅ 2. خلق API key و secret
    api_key = frappe.generate_hash()[:16]
    api_secret = frappe.generate_hash()[:16]

    # احفظ الـ API credentials في الـ User
    user.api_key = api_key
    user.api_secret = api_secret
    user.save(ignore_permissions=True)

    # Token auth is used by the standalone Vercel frontend, so no cookie session row is needed.
    user_doctype = frappe.qb.DocType("User")
    (
        frappe.qb.update(user_doctype)
        .set(user_doctype.last_login, now())
        .set(user_doctype.last_ip, frappe.local.request_ip or "")
        .set(user_doctype.last_active, now())
        .where(user_doctype.name == username)
    ).run()

    frappe.db.commit()

    # ✅ 6. رجع البيانات
    return {
        'success': True,
        'message': 'Authentication successful',
        'data': {
            'user': user.name,
            'full_name': user.full_name,
            'email': user.email,
            'api_key': api_key,
            'api_secret': api_secret,
            'generated_at': now(),
            'user_id': user.name,
            'user_type': user.user_type,
            'role': [role.role for role in user.roles]
        }
    }

# def generate_api_credentials(user):
#     """
#     Generate API key and secret for user

#     Args:
#         user (str): Username

#     Returns:
#         tuple: (api_key, api_secret)
#     """

#     # Generate random API key (32 characters)
#     api_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

#     # Generate random API secret (64 characters)
#     api_secret = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(64))

    # return api_key, api_secret
def generate_api_credentials():
    """
    Generate API key and secret for user

    Args:
        user (str): Username

    Returns:
        tuple: (api_key, api_secret)
    """

    # Generate random API key (32 characters)

    # if not user_doc.api_key:
    api_key = frappe.generate_hash(length=15)
    # if not user_doc.api_secret:
    api_secret = frappe.generate_hash(length=15)
    # user_doc.save(ignore_permissions=True)

    return api_key, api_secret

@frappe.whitelist()
def regenerate_api_key(user=None):
    """
    Regenerate API credentials for current user or specified user

    Args:
        user (str, optional): Username (only for administrators)

    Returns:
        dict: New API credentials
    """

    # If no user specified, use current user
    if not user:
        user = frappe.session.user

    # Check permissions - only allow regeneration for self or if user is Administrator
    if user != frappe.session.user and not frappe.has_permission("User", "write"):
        frappe.throw("Not permitted to regenerate API key for other users")

    try:
        # Get user document
        user_doc = frappe.get_doc("User", user)

        # Generate new credentials
        api_key, api_secret = generate_api_credentials(user)

        # Update user document
        user_doc.api_key = api_key
        user_doc.api_secret = api_secret
        user_doc.save(ignore_permissions=True)

        return {
            "success": True,
            "message": "API credentials regenerated successfully",
            "data": {
                "api_key": api_key,
                "api_secret": api_secret,
                "generated_at": now()
            }
        }

    except Exception as e:
        frappe.logger().error(f"API regeneration error: {str(e)}")
        return {
            "success": False,
            "message": "Failed to regenerate API credentials",
            "error": str(e)
        }

@frappe.whitelist()
def get_user_api_credentials():
    """
    Get current user's API credentials

    Returns:
        dict: User's API credentials
    """

    try:
        user_doc = frappe.get_doc("User", frappe.session.user)

        return {
            "success": True,
            "data": {
                "user": user_doc.name,
                "api_key": user_doc.api_key,
                "has_api_secret": bool(user_doc.api_secret),
                "api_secret": user_doc.api_secret if frappe.has_permission("User", "write") else "***hidden***"
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Failed to retrieve API credentials",
            "error": str(e)
        }

# Usage example for API authentication
@frappe.whitelist(allow_guest=True)
def api_login_example():
    """
    Example of how to use the generated API credentials for authentication

    To use the API credentials, send requests with headers:
    - Authorization: token {api_key}:{api_secret}

    Or as query parameters:
    - ?cmd=your_method&api_key={api_key}&api_secret={api_secret}
    """

    return {
        "message": "This endpoint demonstrates API authentication usage",
        "examples": {
            "header_auth": "Authorization: token your_api_key:your_api_secret",
            "query_auth": "?cmd=your_method&api_key=your_api_key&api_secret=your_api_secret"
        }
    }


