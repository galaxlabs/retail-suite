# ═══════════════════════════════════════════════════════
#  item_price.py   —  Frappe whitelisted API methods
#  Place in:  your_app/your_app/api/item_price.py
# ═══════════════════════════════════════════════════════

import frappe
from frappe import _


# ──────────────────────────────────────────────────────
#  PRICE LISTS
# ──────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def get_all_price_lists():
    """Return all enabled Price List documents."""
    return frappe.get_all(
        "Price List",
        filters={"enabled": 1},
        fields=["name", "price_list_name", "currency", "buying", "selling"],
        order_by="price_list_name asc"
    )


@frappe.whitelist(allow_guest=True)
def get_pos_price_list():
    """
    Return the default POS price list.
    Checks POS Settings first, then falls back to first active POS Profile.
    """
    # 1️⃣ POS Settings (global)
    if frappe.db.exists("POS Settings", "POS Settings"):
        pos_settings = frappe.get_doc("POS Settings", "POS Settings")
        if pos_settings.get("selling_price_list"):
            pl = frappe.db.get_value(
                "Price List",
                pos_settings.selling_price_list,
                ["name", "price_list_name", "currency"],
                as_dict=True
            )
            if pl:
                pl["is_pos_price_list"] = True
                return pl

    # 2️⃣ Fallback: first enabled POS Profile for current company
    selling_price_list = frappe.db.get_value(
        "POS Profile",
        {"disabled": 0, "company": frappe.defaults.get_user_default("Company")},
        "selling_price_list"
    )
    if selling_price_list:
        pl = frappe.db.get_value(
            "Price List",
            selling_price_list,
            ["name", "price_list_name", "currency"],
            as_dict=True
        )
        if pl:
            pl["is_pos_price_list"] = True
            return pl

    return None


# ──────────────────────────────────────────────────────
#  ITEM PRICES
# ──────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def get_item_prices(price_list=None, item_code=None, currency=None):
    """Return Item Price records with optional filters."""
    filters = {}
    if price_list:
        filters["price_list"] = price_list
    if item_code:
        filters["item_code"] = ["like", f"%{item_code}%"]
    if currency:
        filters["currency"] = currency

    return frappe.get_all(
        "Item Price",
        filters=filters,
        fields=[
            "name",
            "item_code",
            "item_name",
            "price_list",
            "price_list_rate",
            "currency",
            "uom",
            "valid_from",
            "valid_upto",
            "customer",
            "supplier",
            "batch_no",
        ],
        order_by="item_code asc"
    )


@frappe.whitelist(allow_guest=True)
def get_item_price(item_code, price_list):
    """Return a single Item Price for an item in a given price list."""
    filters = {}
    if item_code:
        filters["item_code"] = item_code
    if price_list:
        filters["price_list"] = price_list
    price = frappe.db.get_value(
        "Item Price",
        filters,
        ["name", "item_code", "item_name", "price_list",
         "price_list_rate", "currency", "uom", "valid_from", "valid_upto"],
        as_dict=True,
        order_by="creation desc"
    )
    price_list = []
    if price:
        price_list.append(price)
    return price_list or []

@frappe.whitelist(allow_guest=True)
def create_item_price(
    item_code,
    price_list,
    price_list_rate,
    currency=None,
    uom=None,
    valid_from=None,
    valid_upto=None,
):
    """Create a new Item Price document."""
    if not item_code:
        frappe.throw(_("item_code is required"))
    if not price_list:
        frappe.throw(_("price_list is required"))
    if float(price_list_rate) < 0:
        frappe.throw(_("price_list_rate must be >= 0"))

    item = frappe.get_doc("Item", item_code)

    if not currency:
        currency = (
            frappe.db.get_value("Price List", price_list, "currency")
            or frappe.defaults.get_global_default("currency")
            or "SAR"
        )
    if not uom:
        uom = item.stock_uom

    doc = frappe.get_doc({
        "doctype":         "Item Price",
        "item_code":       item_code,
        "item_name":       item.item_name,
        "price_list":      price_list,
        "price_list_rate": float(price_list_rate),
        "currency":        currency,
        "uom":             uom,
        "valid_from":      valid_from or None,
        "valid_upto":      valid_upto or None,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"name": doc.name, "message": "Item Price created successfully"}


@frappe.whitelist(allow_guest=True)
def update_item_price(
    name,
    price_list_rate=None,
    currency=None,
    uom=None,
    valid_from=None,
    valid_upto=None,
    **kwargs          # absorb extra frontend fields gracefully
):
    """Update an existing Item Price document."""
    if not name:
        frappe.throw(_("name (Item Price ID) is required"))

    doc = frappe.get_doc("Item Price", name)

    if price_list_rate is not None:
        doc.price_list_rate = float(price_list_rate)
    if currency:
        doc.currency = currency
    if uom:
        doc.uom = uom
    if valid_from is not None:
        doc.valid_from = valid_from or None
    if valid_upto is not None:
        doc.valid_upto = valid_upto or None

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"name": doc.name, "message": "Item Price updated successfully"}


@frappe.whitelist(allow_guest=True)
def delete_item_price(name):
    """Delete an Item Price document."""
    if not name:
        frappe.throw(_("name is required"))

    frappe.delete_doc("Item Price", name, ignore_permissions=True)
    frappe.db.commit()

    return {"message": f"Item Price '{name}' deleted successfully"}
