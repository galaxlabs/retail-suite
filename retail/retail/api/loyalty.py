"""
Loyalty Points API
retail/retail/api/loyalty.py
"""

import frappe
from frappe import _
from frappe.utils import today, getdate, now_datetime


# def get_customer_from_session():
#     """Get customer linked to current logged-in user"""
#     user = frappe.session.user
#     if user == "Guest":
#         frappe.throw(_("Please login to access loyalty points"))

#     customer = frappe.db.get_value("Customer", {"customer_primary_contact": user}, "name")
#     if not customer:
#         # fallback: try portal user link
#         customer = frappe.db.get_value(
#             "Portal User", {"user": user, "parenttype": "Customer"}, "parent"
#         )
#     if not customer:
#         frappe.throw(_("No customer account linked to this user"))
#     return customer

def get_customer_from_session():
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
    return customer_id


def get_active_loyalty_program():
    """Get the first active loyalty program"""
    program = frappe.db.get_value(
        "Loyalty Program",
        {"is_active": 1},
        ["name", "points_amount_ratio", "amount_per_point",
         "welcome_points", "referral_points"],
        as_dict=True,
    )
    if not program:
        frappe.throw(_("No active loyalty program found"))
    return program


def calculate_customer_total_points(customer):
    """Calculate net points balance for a customer"""
    earned = frappe.db.sql("""
        SELECT COALESCE(SUM(points), 0)
        FROM `tabLoyalty Point Entry`
        WHERE customer = %s AND entry_type IN ('Earned', 'Adjustment')
    """, customer)[0][0] or 0

    redeemed = frappe.db.sql("""
        SELECT COALESCE(SUM(points), 0)
        FROM `tabLoyalty Point Entry`
        WHERE customer = %s AND entry_type = 'Redeemed'
    """, customer)[0][0] or 0

    return int(earned - redeemed)


def get_current_tier(total_points, tiers):
    """Return current tier and next tier based on total points"""
    current_tier = tiers[0]  # default = first tier (lowest)
    next_tier = None

    for i, tier in enumerate(tiers):
        if total_points >= tier["min_points"]:
            current_tier = tier
            if i + 1 < len(tiers):
                next_tier = tiers[i + 1]

    return current_tier, next_tier


# ──────────────────────────────────────────────
# Public API Methods
# ──────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def get_loyalty_summary():
    """
    Returns loyalty summary for current customer:
    total_points, points_value, current_tier, next_tier,
    tier_progress, points_to_next_tier
    """
    customer = get_customer_from_session()
    print("=====================Customer===========================")
    print("Customer", customer)
    program = get_active_loyalty_program()

    # Tiers sorted ascending by min_points
    tiers = frappe.db.get_all(
        "Loyalty Tier",
        filters={"parent": program.name, "parenttype": "Loyalty Program"},
        fields=["tier_name", "icon", "min_points", "multiplier"],
        order_by="min_points asc",
    )

    total_points = calculate_customer_total_points(customer)
    current_tier, next_tier = get_current_tier(total_points, tiers)

    points_to_next = 0
    tier_progress = 100
    if next_tier:
        points_to_next = next_tier["min_points"] - total_points
        tier_range = next_tier["min_points"] - current_tier["min_points"]
        earned_in_tier = total_points - current_tier["min_points"]
        tier_progress = min(int((earned_in_tier / tier_range) * 100), 99) if tier_range else 99

    summary = {
        "customer": customer,
        "total_points": total_points,
        "points_value": round(total_points * program.amount_per_point, 2),
        "current_tier": {
            "name": current_tier["tier_name"],
            "icon": current_tier["icon"],
            "multiplier": current_tier["multiplier"],
        },
        "next_tier": next_tier["tier_name"] if next_tier else None,
        "points_to_next_tier": points_to_next,
        "tier_progress": tier_progress,
        "tiers": [
            {
                "name": t["tier_name"],
                "icon": t["icon"],
                "min_points": t["min_points"],
                "multiplier": t["multiplier"],
            }
            for t in tiers
        ],
    }
    print("summary",summary)
    return summary


@frappe.whitelist(allow_guest=True)
def get_points_history(limit=20, offset=0):
    """Returns paginated points transaction history for current customer"""
    customer = get_customer_from_session()
    print("=====================Customer===========================")
    print("Customer", customer)
    entries = frappe.db.get_all(
        "Loyalty Point Entry",
        filters={"customer": customer},
        fields=[
            "name", "entry_type", "points", "balance",
            "description", "reference_name", "creation", "reward_title"
        ],
        order_by="creation desc",
        limit=int(limit),
        start=int(offset),
    )

    history = []
    for e in entries:
        history.append({
            "id": e["name"],
            "type": "earned" if e["entry_type"] in ("Earned", "Adjustment") else "redeemed",
            "entry_type": e["entry_type"],
            "description": e["description"] or e["reward_title"] or e["entry_type"],
            "points": e["points"],
            "balance": e["balance"],
            "date": str(e["creation"]),
            "orderId": e["reference_name"],
        })

    total = frappe.db.count("Loyalty Point Entry", {"customer": customer})

    return {"history": history, "total": total}


@frappe.whitelist(allow_guest=True)
def get_available_rewards():
    """Returns active rewards from the loyalty program"""
    program = get_active_loyalty_program()

    rewards = frappe.db.get_all(
        "Loyalty Reward",
        filters={"parent": program.name, "parenttype": "Loyalty Program", "is_active": 1},
        fields=["name", "reward_title", "description", "icon", "points_required",
                "reward_type", "reward_value"],
        order_by="points_required asc",
    )

    return [
        {
            "id": r["name"],
            "title": r["reward_title"],
            "description": r["description"],
            "icon": r["icon"] or "🎁",
            "points": r["points_required"],
            "reward_type": r["reward_type"],
            "reward_value": r["reward_value"],
        }
        for r in rewards
    ]


@frappe.whitelist(allow_guest=True)
def redeem_reward(reward_id):
    """
    Redeem a reward by deducting points and creating a Loyalty Point Entry
    Returns coupon/discount info
    """
    customer = get_customer_from_session()
    print("=====================Customer===========================")
    print("Customer", customer)
    program = get_active_loyalty_program()

    # Validate reward exists
    reward = frappe.db.get_value(
        "Loyalty Reward",
        {"name": reward_id, "parent": program.name, "is_active": 1},
        ["reward_title", "points_required", "reward_type", "reward_value"],
        as_dict=True,
    )
    if not reward:
        frappe.throw(_("Reward not found or no longer available"))

    # Check balance
    total_points = calculate_customer_total_points(customer)
    if total_points < reward.points_required:
        frappe.throw(
            _("Insufficient points. You have {0} points but need {1}").format(
                total_points, reward.points_required
            )
        )

    new_balance = total_points - reward.points_required

    # Create redemption entry
    entry = frappe.get_doc({
        "doctype": "Loyalty Point Entry",
        "customer": customer,
        "loyalty_program": program.name,
        "entry_type": "Redeemed",
        "points": reward.points_required,
        "balance": new_balance,
        "description": _("Redeemed: {0}").format(reward.reward_title),
        "reward_title": reward.reward_title,
    })
    entry.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "reward_title": reward.reward_title,
        "points_deducted": reward.points_required,
        "new_balance": new_balance,
        "new_points_value": round(new_balance * program.amount_per_point, 2),
        "entry_id": entry.name,
    }


@frappe.whitelist(allow_guest=True)
def get_referral_code():
    """Get or create referral code for current customer"""
    customer = get_customer_from_session()
    print("=====================Customer===========================")
    print("Customer", customer)
    # Check if referral code exists in Referral Code doctype
    ref_code = frappe.db.get_value("Referral Code", {"customer": customer}, "referral_code")

    if not ref_code:
        # Generate a new referral code
        import random, string
        ref_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    return {"referral_code": ref_code, "customer": customer}


@frappe.whitelist(allow_guest=True)
def add_points(customer, points, entry_type="Earned", description="", reference_doctype=None, reference_name=None):
    """
    Internal method to add points (called from Sales Invoice hooks etc.)
    Not exposed directly to frontend - called server-side
    """
    if not frappe.has_permission("Loyalty Point Entry", "create"):
        frappe.throw(_("Not permitted"))

    program = get_active_loyalty_program()
    current_balance = calculate_customer_total_points(customer)
    new_balance = current_balance + points if entry_type == "Earned" else current_balance - points

    entry = frappe.get_doc({
        "doctype": "Loyalty Point Entry",
        "customer": customer,
        "loyalty_program": program.name,
        "entry_type": entry_type,
        "points": abs(points),
        "balance": max(new_balance, 0),
        "description": description,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
    })
    entry.insert(ignore_permissions=True)
    frappe.db.commit()
    return entry.name




def on_invoice_submit(doc, method):
    """Auto-earn points when Sales Invoice is submitted"""
    if not doc.customer:
        return
    try:
        program = get_active_loyalty_program()
        # كل 10 جنيه = نقطة
        points = int(doc.grand_total / program.points_amount_ratio)
        if points <= 0:
            return
        add_points(
            customer=doc.customer,
            points=points,
            entry_type="Earned",
            description=f"شراء - فاتورة #{doc.name}",
            reference_doctype="Sales Invoice",
            reference_name=doc.name,
        )
    except Exception as e:
        frappe.log_error(str(e), "Loyalty Points Error")


def on_invoice_cancel(doc, method):
    """Remove points when invoice is cancelled"""
    if not doc.customer:
        return
    try:
        # شيل الـ entry المرتبط بالفاتورة دي
        entry = frappe.db.get_value(
            "Loyalty Point Entry",
            {"reference_name": doc.name, "entry_type": "Earned"},
            "name"
        )
        if entry:
            frappe.delete_doc("Loyalty Point Entry", entry, ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        frappe.log_error(str(e), "Loyalty Points Cancel Error")

# bench execute retail.retail.api.loyalty.migrate_old_invoices

def migrate_old_invoices():
    """Run once to backfill loyalty points for all existing invoices"""

    program = get_active_loyalty_program()

    # جيب كل الفواتير المدفوعة اللي مفيش ليها entry
    invoices = frappe.db.sql("""
        SELECT si.name, si.customer, si.grand_total, si.posting_date
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
          AND si.customer IS NOT NULL
          AND si.grand_total > 0
          AND NOT EXISTS (
              SELECT 1 FROM `tabLoyalty Point Entry` lpe
              WHERE lpe.reference_name = si.name
                AND lpe.entry_type = 'Earned'
          )
        ORDER BY si.posting_date ASC
    """, as_dict=True)

    print(f"Found {len(invoices)} invoices to process...")

    # اتراك كل عميل عشان نحسب الـ balance صح
    customer_balance = {}

    for inv in invoices:
        customer = inv.customer
        points = int(inv.grand_total / program.points_amount_ratio)
        if points <= 0:
            continue

        # جيب الـ balance الحالي للعميل
        if customer not in customer_balance:
            customer_balance[customer] = calculate_customer_total_points(customer)

        customer_balance[customer] += points

        frappe.get_doc({
            "doctype": "Loyalty Point Entry",
            "customer": customer,
            "loyalty_program": program.name,
            "entry_type": "Earned",
            "points": points,
            "balance": customer_balance[customer],
            "description": f"شراء - {inv.name}",
            "reference_doctype": "Sales Invoice",
            "reference_name": inv.name,
        }).insert(ignore_permissions=True)

    frappe.db.commit()
    print(f"Done! Processed {len(invoices)} invoices for {len(customer_balance)} customers.")
