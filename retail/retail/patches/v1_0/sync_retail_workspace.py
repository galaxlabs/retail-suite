import json
from pathlib import Path

import frappe

WORKSPACE_FILE = Path(__file__).resolve().parents[2] / "workspace" / "retail" / "retail.json"


def _load_workspace_payload():
    payload = json.loads(WORKSPACE_FILE.read_text())
    payload["doctype"] = "Workspace"
    return payload


def run():
    if not WORKSPACE_FILE.exists():
        return

    payload = _load_workspace_payload()
    name = payload["name"]

    if frappe.db.exists("Workspace", name):
        doc = frappe.get_doc("Workspace", name)
        for field in [
            "charts",
            "content",
            "custom_blocks",
            "docstatus",
            "for_user",
            "hide_custom",
            "icon",
            "idx",
            "indicator_color",
            "is_hidden",
            "label",
            "module",
            "number_cards",
            "parent_page",
            "public",
            "quick_lists",
            "restrict_to_domain",
            "sequence_id",
            "title",
        ]:
            if field in payload:
                setattr(doc, field, payload[field])

        doc.set("charts", payload.get("charts", []))
        doc.set("custom_blocks", payload.get("custom_blocks", []))
        doc.set("links", payload.get("links", []))
        doc.set("number_cards", payload.get("number_cards", []))
        doc.set("quick_lists", payload.get("quick_lists", []))
        doc.set("roles", payload.get("roles", []))
        doc.set("shortcuts", payload.get("shortcuts", []))
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc(payload)
        doc.insert(ignore_permissions=True)

    for field, value in {
        "public": 1,
        "module": "Retail",
        "icon": "shopping-cart",
        "indicator_color": "green",
        "label": "Retail",
        "title": "Retail",
        "for_user": "",
    }.items():
        frappe.db.set_value("Workspace", name, field, value)

    frappe.db.commit()


def execute():
    return run()
