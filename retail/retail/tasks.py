import frappe
from frappe.utils import nowdate, get_datetime, add_to_date

def auto_close_open_shifts():
    """Scheduled task: Auto-close all open POS shifts at midnight and create new ones at 00:05"""
    today = nowdate()
    yesterday = add_to_date(today, days=-1)

    # 1. Close all open shifts from yesterday
    open_shifts = frappe.get_all("POS Opening Shift",
        filters={"status": "Open", "period_start_date": ["<", today]},
        fields=["name", "pos_profile", "company", "user"]
    )
    for shift in open_shifts:
        try:
            closing = frappe.get_doc({
                "doctype": "POS Closing Shift",
                "period_start_date": shift.period_start_date,
                "period_end_date": get_datetime(today + " 00:00:00"),
                "posting_date": today,
                "posting_time": "00:00:00",
                "pos_opening_shift": shift.name,
                "pos_profile": shift.pos_profile,
                "company": shift.company,
                "user": shift.user,
                "docstatus": 1,
            })
            closing.flags.ignore_permissions = True
            closing.insert()

            # Mark opening shift as closed
            frappe.db.set_value("POS Opening Shift", shift.name, "status", "Closed")
            frappe.db.set_value("POS Opening Shift", shift.name, "period_end_date", get_datetime(today + " 00:00:00"))

        except Exception as e:
            print(f"Auto-close shift {shift.name} failed: {e}")

    # 2. Auto-create new opening shifts at 00:05
    if open_shifts:
        pos_profiles = list(set(s.pos_profile for s in open_shifts if s.pos_profile))
        for profile in pos_profiles:
            company = next((s.company for s in open_shifts if s.pos_profile == profile), None)
            user = next((s.user for s in open_shifts if s.pos_profile == profile), "Administrator")
            try:
                existing = frappe.get_all("POS Opening Shift",
                    filters={"status": "Open", "pos_profile": profile, "period_start_date": today},
                    limit=1)
                if existing:
                    continue

                new_shift = frappe.get_doc({
                    "doctype": "POS Opening Shift",
                    "period_start_date": get_datetime(today + " 00:05:00"),
                    "posting_date": today,
                    "user": user,
                    "pos_profile": profile,
                    "company": company,
                    "docstatus": 1,
                })
                new_shift.set("balance_details", [])
                new_shift.flags.ignore_permissions = True
                new_shift.insert()
            except Exception as e:
                print(f"Auto-create shift for {profile} failed: {e}")

    frappe.db.commit()