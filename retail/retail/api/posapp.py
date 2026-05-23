import frappe
from frappe import _
import socket
import json
from weasyprint import HTML, CSS
from frappe.utils import nowdate, flt, cstr, nowdate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.stock.get_item_details import get_item_details
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups
from frappe.utils.background_jobs import enqueue
from erpnext.accounts.party import get_party_bank_account
from erpnext.stock.doctype.batch.batch import (
    get_batch_no,
    get_batch_qty,
)
from erpnext.accounts.doctype.payment_request.payment_request import (
    get_dummy_message,
    get_existing_payment_request_amount,
)

from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
    get_loyalty_program_details_with_points,
)
from retail.retail.doctype.pos_coupon.pos_coupon import check_coupon_code
from retail.retail.doctype.delivery_charges.delivery_charges import (
    get_applicable_delivery_charges as _get_applicable_delivery_charges,
)

from frappe.utils.caching import redis_cache
from retail.retail.api.pricing_rule import apply_pricing_rules_for_pos


def pos_cache(fn, pos_profile: dict):

    if not pos_profile.get("posa_use_server_cache"):
        return fn

    ttl = pos_profile.get("posa_server_cache_duration")
    ttl = int(ttl) * 30 if ttl else 1800
    return redis_cache(ttl=ttl)(fn)

@frappe.whitelist()
def get_opening_dialog_data():
    data = {}
    data["companies"] = frappe.get_list(
        "Company",
        fields=["name"],
        limit_page_length=0,
        order_by="name",
        ignore_permissions=True,
    )
    data["pos_profiles_data"] = frappe.get_list(
        "POS Profile",
        filters={"disabled": 0},
        fields=["name", "company", "currency"],
        limit_page_length=0,
        order_by="name",
        ignore_permissions=True,
    )

    pos_profiles_list = []
    for i in data["pos_profiles_data"]:
        pos_profiles_list.append(i.name)

    payment_method_table = (
        "POS Payment Method" if get_version() == 13 else "Sales Invoice Payment"
    )
    data["payments_method"] = frappe.get_list(
        payment_method_table,
        filters={"parent": ["in", pos_profiles_list]},
        fields=["*"],
        limit_page_length=0,
        order_by="parent",
        ignore_permissions=True,
    )
    # set currency from pos profile
    for mode in data["payments_method"]:
        mode["currency"] = frappe.get_cached_value(
            "POS Profile", mode["parent"], "currency"
        )

    return data

@frappe.whitelist()
def create_opening_voucher(pos_profile, company, balance_details):
    balance_details = json.loads(balance_details)

    new_pos_opening = frappe.get_doc(
        {
            "doctype": "POS Opening Shift",
            "period_start_date": frappe.utils.get_datetime(),
            "posting_date": frappe.utils.getdate(),
            "user": frappe.session.user,
            "pos_profile": pos_profile,
            "company": company,
            "docstatus": 1,
        }
    )
    new_pos_opening.set("balance_details", balance_details)
    new_pos_opening.insert(ignore_permissions=True)

    data = {}
    data["pos_opening_shift"] = new_pos_opening.as_dict()
    update_opening_shift_data(data, new_pos_opening.pos_profile)
    return data

@frappe.whitelist()
def check_opening_shift(user):
    open_vouchers = frappe.db.get_all(
        "POS Opening Shift",
        filters={
            "user": user,
            "docstatus": 1,
            "status": "Open",
        },
        fields=["name", "pos_profile"],
        order_by="period_start_date desc",
    )
    if not open_vouchers:
        return None
        #  frappe.throw("You cannot perform this action — No active POS Shift found.")
    data = ""
    if len(open_vouchers) > 0:
        data = {}
        data["pos_opening_shift"] = frappe.get_doc(
            "POS Opening Shift", open_vouchers[0]["name"]
        )
        update_opening_shift_data(data, open_vouchers[0]["pos_profile"])


    return data

def update_opening_shift_data(data, pos_profile):
    data["pos_profile"] = frappe.get_doc("POS Profile", pos_profile)
    data["company"] = frappe.get_doc("Company", data["pos_profile"].company)
    allow_negative_stock = frappe.get_value(
        "Stock Settings", None, "allow_negative_stock"
    )
    data["stock_settings"] = {}
    data["stock_settings"].update({"allow_negative_stock": allow_negative_stock})

@frappe.whitelist()
def get_items(
    pos_profile, price_list=None, item_group="", search_value="", customer=None, warehouse=None
):
    _pos_profile = frappe.parse_json(pos_profile)

    return pos_cache(_get_items, _pos_profile)(
        pos_profile, price_list, item_group, search_value, customer, warehouse
    )

def _get_items(pos_profile, price_list, item_group, search_value, customer=None, warehouse=None):
    pos_profile = frappe.parse_json(pos_profile)
    today = nowdate()
    data = dict()
    posa_display_items_in_stock = pos_profile.get("posa_display_items_in_stock")
    search_serial_no = pos_profile.get("posa_search_serial_no")
    search_batch_no = pos_profile.get("posa_search_batch_no")
    posa_show_template_items = pos_profile.get("posa_show_template_items")
    warehouse = warehouse or pos_profile.get("warehouse")
    print("Warhouse",warehouse)
    print("posa_display_items_in_stock", posa_display_items_in_stock)
    use_limit_search = pos_profile.get("pose_use_limit_search")
    allow_zero_rated_items = pos_profile.get("posa_allow_zero_rated_items")
    search_limit = 0
    if not price_list:
        price_list = pos_profile.get("selling_price_list")

    limit = ""

    condition = ""
    condition += get_item_group_condition(pos_profile.get("name"))

    if use_limit_search:
        search_limit = pos_profile.get("posa_search_limit") or 500
        if search_value:
            data = search_serial_or_batch_or_barcode_number(
                search_value, search_serial_no
            )

        item_code = data.get("item_code") if data.get("item_code") else search_value
        serial_no = data.get("serial_no") if data.get("serial_no") else ""
        batch_no = data.get("batch_no") if data.get("batch_no") else ""
        barcode = data.get("barcode") if data.get("barcode") else ""

        condition += get_seearch_items_conditions(
            item_code, serial_no, batch_no, barcode
        )
        if item_group:
            condition += " AND item_group like '%{item_group}%'".format(
                item_group=item_group
            )
        limit = " LIMIT {search_limit}".format(search_limit=search_limit)

    if not posa_show_template_items:
        condition += " AND has_variants = 0"

    result = []

    items_data = frappe.db.sql(
        """
        SELECT
            name AS item_code,
            item_name,
            description,
            stock_uom,
            image,
            is_stock_item,
            has_variants,
            variant_of,
            item_group,
            idx as idx,
            has_batch_no,
            has_serial_no,
            max_discount,
            brand,
            disabled
        FROM
            `tabItem`
        WHERE
            disabled = 0
                AND is_sales_item = 1
                AND is_fixed_asset = 0
                {condition}
        ORDER BY
            item_name asc
        {limit}
            """.format(
            condition=condition, limit=limit
        ),
        as_dict=1,
    )

    if items_data:
        print("FIRST 5 ITEMS:")
        for x in items_data[:5]:
            print({
                "item_code": x.item_code,
                "stock_uom": x.stock_uom,
                "disabled": x.disabled,
                "item_group": x.item_group
            })

        items = [d.item_code for d in items_data]
        base_filters = {
                "price_list": price_list,
                "item_code": ["in", items],
                "currency": pos_profile.get("currency"),
                "selling": 1,
                "valid_from": ["<=", today],
                "customer": ["in", ["", None, customer]],
            }
        print("BASE FILTERS:", base_filters)
        item_prices_data = frappe.get_all(
            "Item Price",
            fields=["item_code", "price_list_rate", "currency", "uom"],
            # filters=base_filters,
            order_by="valid_from ASC, valid_upto DESC",
        )

        item_prices = {}

        print("FIRST 5 ITEM PRICES:")
        for x in item_prices_data[:5]:
            print({
                "item_code": x.item_code,
                "stock_uom": x.stock_uom,
                "disabled": x.disabled,
                "item_group": x.item_group
            })
        for d in item_prices_data:
            item_prices.setdefault(d.item_code, {})
            item_prices[d.item_code][d.get("uom") or "None"] = d


        customer_group = frappe.db.get_value("Customer", customer, "customer_group")
        print(f"Customer: {customer} gr: {customer_group}")

        pos_items = []
        item_price_map = {}
        for item in items_data:
            item_code = item.item_code
            item_price = {}
            for k, v in list(item_prices.items())[:5]:
                print(k, v)
            if item_prices.get(item_code):
                item_price = (
                    item_prices.get(item_code).get(item.stock_uom)
                    or item_prices.get(item_code).get("None")
                    or {}
                )
                pos_items.append({
                    "doctype": "Sales Invoice Item",
                    "name": item.item_code,          # أي name وهمي
                    "item_code": item.item_code,
                    "item_group": item.item_group,
                    "brand": item.brand,
                    "qty": 1,
                    "uom": item.stock_uom,
                    "conversion_factor": 1,
                    "price_list_rate": item_price.get("price_list_rate", 0),
                    "parenttype": "Sales Invoice",
                    "parent": "POS-TEST",
                })
            item_price_map[item_code] = item_price
        pricing_rule_details = apply_pricing_rules_for_pos(
            items=pos_items,
            customer=customer,
            customer_group=customer_group,
            company=pos_profile.get("company"),
            price_list=price_list,
            currency=pos_profile.get("currency"),
            transaction_date=today
        )
        pricing_rule_map = {}
        for rule in pricing_rule_details:
            if rule.get("item_code"):
                pricing_rule_map[rule["item_code"]] = rule

        print("pricing_rule_map", pricing_rule_map)
        for item in items_data:
            item_code = item.item_code
            item_price = item_price_map.get(item_code, {})
            rule = pricing_rule_map.get(item_code, {})

            discount_percentage = rule.get("discount_percentage", 0)
            discount_amount     = rule.get("discount_amount", 0)
            original_rate       = item_price.get("price_list_rate") or 0
            final_rate = original_rate

            if discount_percentage:
                final_rate = flt(
                    original_rate * (1 - flt(discount_percentage) / 100), 2
                )

            elif discount_amount:
                final_rate = flt(original_rate - discount_amount, 2)

            if not allow_zero_rated_items and flt(final_rate) <= 0:
                continue

            item.update({
                "original_rate": original_rate,
                "rate": final_rate,
                "discount_percentage": discount_percentage,
                "discount_amount": discount_amount,
                "pricing_rules": rule.get("pricing_rules")
            })

            item_barcode = frappe.get_all(
                "Item Barcode",
                filters={"parent": item_code},
                fields=["barcode", "posa_uom"],
            )
            batch_no_data = []
            if search_batch_no:
                batch_list = get_batch_qty(warehouse=warehouse, item_code=item_code)
                if batch_list:
                    for batch in batch_list:
                        if batch.qty > 0 and batch.batch_no:
                            batch_doc = frappe.get_cached_doc(
                                "Batch", batch.batch_no
                            )
                            if (
                                str(batch_doc.expiry_date) > str(today)
                                or batch_doc.expiry_date in ["", None]
                            ) and batch_doc.disabled == 0:
                                batch_no_data.append(
                                    {
                                        "batch_no": batch.batch_no,
                                        "batch_qty": batch.qty,
                                        "expiry_date": batch_doc.expiry_date,
                                        "batch_price": batch_doc.posa_batch_price,
                                        "manufacturing_date": batch_doc.manufacturing_date,
                                    }
                                )
            serial_no_data = []
            if search_serial_no:
                serial_no_data = frappe.get_all(
                    "Serial No",
                    filters={
                        "item_code": item_code,
                        "status": "Active",
                        "warehouse": warehouse,
                    },
                    fields=["name as serial_no"],
                )

            item_stock_qty = 0
            if warehouse:
                item_stock_qty = get_stock_availability(item_code, warehouse) or 0
            print("item_stock_qty", item_stock_qty)
            # print(f"Item: {item_code}, Qty: {item_stock_qty}, Warehouse: {pos_profile.get('warehouse')}")
            if use_limit_search:
                limit = " LIMIT {search_limit}".format(search_limit=search_limit)
            attributes = ""
            if posa_show_template_items and item.has_variants:
                attributes = get_item_attributes(item.item_code)

            item_attributes = ""
            if posa_show_template_items and item.variant_of:
                item_attributes = frappe.get_all(
                    "Item Variant Attribute",
                    fields=["attribute", "attribute_value"],
                    filters={"parent": item.item_code, "parentfield": "attributes"},
                )

            if posa_display_items_in_stock and (
                not item_stock_qty or item_stock_qty < 0
            ):
                continue
            else:
                row = {}
                row.update(item)
                row.update(
                    {
                        "rate": final_rate,
                        "original_rate": original_rate,
                        "discount_percentage": discount_percentage,
                        "discount_amount": discount_amount,
                        "pricing_rules": rule.get("pricing_rules"),
                        "currency": item_price.get("currency") or pos_profile.get("currency"),
                        "item_barcode": item_barcode or [],
                        "actual_qty": item_stock_qty or 0,
                        "serial_no_data": serial_no_data or [],
                        "batch_no_data": batch_no_data or [],
                        "attributes": attributes or "",
                        "item_attributes": item_attributes or "",
                        "warehouse":pos_profile.get('warehouse'),
                        "use_limit_search": use_limit_search
                    }
                )
                result.append(row)
    print("FINAL RESULT LENGTH:", len(result))
    print("items_data:", len(items_data))
    print("item_prices_data:", len(item_prices_data))

    return result


def get_item_notes(item_code):
    notes = set()  # Use a set to avoid duplicate notes
    for child_table_name in ["Notes", "All Notes"]:
        child_notes = frappe.get_all(
            child_table_name,
            filters={"parent": item_code},
            fields=["note"],
            as_list=True,
        )
        notes.update(note[0].strip() for note in child_notes)

    # Limit the number of notes to 2
    return list(notes)

def get_product_bundle(item_code):
    product_bundles = frappe.get_all(
        "Product Bundle",
        filters={"new_item_code": item_code},
        fields=["name"],
        distinct=True,
        as_list=True,
    )
    if product_bundles:
        # Return the first product bundle found
        return frappe.get_doc("Product Bundle", product_bundles[0][0])
    return None

@frappe.whitelist()
def get_single_item(item_code):
    """
    Retrieve a single item from the Item doctype.
    :param item_code: The item code to retrieve.
    :return: Dictionary containing item details.
    """
    # Fetch item details
    item = frappe.get_doc("Item", item_code)

    # Prepare item data dictionary
    item_data = {
        "item_code": item.name,
        "item_name": item.item_name,
        "description": item.description,
        "stock_uom": item.stock_uom,
        "image": item.image,
        "is_stock_item": item.is_stock_item,
        "has_variants": item.has_variants,
        "variant_of": item.variant_of,
        "item_group": item.item_group,
        "has_batch_no": item.has_batch_no,
        "has_serial_no": item.has_serial_no,
        "max_discount": item.max_discount,
        "brand": item.brand,
        "notes": get_item_notes(item.name)  # Get notes for the item
    }

    # Fetch item prices
    price_list = frappe.db.get_value("Price List", {"selling": 1}, "name")
    today = nowdate()
    item_prices_data = frappe.get_all(
        "Item Price",
        fields=["price_list_rate", "currency", "uom"],
        filters={
            "price_list": price_list,
            "item_code": item_code,
            "currency": frappe.defaults.get_global_default("currency"),
            "selling": 1,
            # "valid_from": ["<=", today],
        },
        or_filters=[
            ["valid_upto", ">=", today],
            ["valid_upto", "in", ["", None]],
        ],
        order_by="valid_from ASC, valid_upto DESC",
    )

    # Organize item prices
    item_prices = {}
    for d in item_prices_data:
        item_prices[d.get("uom") or "None"] = d

    # Assign item price to item_data
    item_price = item_prices.get(item_data["stock_uom"]) or item_prices.get("None") or {}
    item_data.update({
        "rate": item_price.get("price_list_rate") or 0,
        "currency": item_price.get("currency") or frappe.defaults.get_global_default("currency"),
    })

    # Fetch item barcode
    item_barcode = frappe.get_all(
        "Item Barcode",
        filters={"parent": item_code},
        fields=["barcode"]
    )
    item_data["item_barcode"] = item_barcode or []

    # Fetch batch and serial data
    item_data["batch_no_data"] = []
    item_data["serial_no_data"] = []

    # Fetch item attributes if it's a variant
    if item.variant_of:
        item_data["item_attributes"] = frappe.get_all(
            "Item Variant Attribute",
            fields=["attribute", "attribute_value"],
            filters={"parent": item_code, "parentfield": "attributes"}
        )

    # Fetch bundle options if it's a bundle
    bundles = get_product_bundle(item_code)
    if bundles:
        item_data["custom_bundle_options"] = bundles

    return item_data

def get_item_group_condition(pos_profile):
    cond = " and 1=1"
    item_groups = get_item_groups(pos_profile)
    if item_groups:
        cond = " and item_group in (%s)" % (", ".join(["%s"] * len(item_groups)))

    return cond % tuple(item_groups)

def get_root_of(doctype):
    """Get root element of a DocType with a tree structure"""
    result = frappe.db.sql(
        """select t1.name from `tab{0}` t1 where
		(select count(*) from `tab{1}` t2 where
			t2.lft < t1.lft and t2.rgt > t1.rgt) = 0
		and t1.rgt > t1.lft""".format(
            doctype, doctype
        )
    )
    return result[0][0] if result else None

@frappe.whitelist()
def get_items_groups():
    print("get_items_groups called....................................")
    return frappe.db.sql(
        """
        select name
        from `tabItem Group`
        where is_group = 0
        order by name
        LIMIT 0, 200 """,
        as_dict=1,
    )

def get_customer_groups(pos_profile):
    customer_groups = []
    if pos_profile.get("customer_groups"):
        # Get items based on the item groups defined in the POS profile
        for data in pos_profile.get("customer_groups"):
            customer_groups.extend(
                [
                    "%s" % frappe.db.escape(d.get("name"))
                    for d in get_child_nodes(
                        "Customer Group", data.get("customer_group")
                    )
                ]
            )

    return list(set(customer_groups))

def get_supplier_groups(pos_profile):
    supplier_groups = []
    if pos_profile.get("supplier_groups"):
        # Get items based on the item groups defined in the POS profile
        for data in pos_profile.get("supplier_groups"):
            supplier_groups.extend(
                [
                    "%s" % frappe.db.escape(d.get("name"))
                    for d in get_child_nodes(
                        "Supplier Group", data.get("supplier_group")
                    )
                ]
            )

    return list(set(supplier_groups))

def get_child_nodes(group_type, root):
    lft, rgt = frappe.db.get_value(group_type, root, ["lft", "rgt"])
    return frappe.db.sql(
        """ Select name, lft, rgt from `tab{tab}` where
			lft >= {lft} and rgt <= {rgt} order by lft""".format(
            tab=group_type, lft=lft, rgt=rgt
        ),
        as_dict=1,
    )

def get_customer_group_condition(pos_profile):
    cond = "disabled = 0"
    customer_groups = get_customer_groups(pos_profile)
    if customer_groups:
        cond = " customer_group in (%s)" % (", ".join(["%s"] * len(customer_groups)))

    return cond % tuple(customer_groups)

def get_supplier_group_condition(pos_profile):
    cond = "disabled = 0"
    supplier_groups = get_supplier_groups(pos_profile)
    if supplier_groups:
        cond = " supplier_group in (%s)" % (", ".join(["%s"] * len(supplier_groups)))

    return cond % tuple(supplier_groups)

@frappe.whitelist()
def get_supplier_names(pos_profile):
    _pos_profile = frappe.parse_json(pos_profile)

    return pos_cache(_get_supplier_names, _pos_profile)(pos_profile)

def _get_supplier_names(pos_profile):
    pos_profile = frappe.parse_json(pos_profile)
    condition = ""
    condition += get_supplier_group_condition(pos_profile)
    suppliers = frappe.db.sql(
        """
        SELECT *
        FROM `tabSupplier`
        ORDER by name
        """,
        as_dict=1,
    )
    return suppliers




@frappe.whitelist()
def get_customer_names(pos_profile):
    _pos_profile = json.loads(pos_profile)
    return pos_cache(_get_customer_names, _pos_profile)(pos_profile)

def _get_customer_names(pos_profile):
    pos_profile = json.loads(pos_profile)
    condition = ""
    condition += get_customer_group_condition(pos_profile)
    customers = frappe.db.sql(
        """
        SELECT *
        FROM `tabCustomer`
        ORDER by name
        """,
        as_dict=1,
    )
    return customers



@frappe.whitelist()
def get_sales_person_names():
    sales_persons = frappe.db.sql(
        """
        SELECT name, sales_person_name
        FROM `tabSales Person`
        ORDER by name
        LIMIT 0, 10000
        """,
        as_dict=1,
    )
    return sales_persons

def add_taxes_from_tax_template(item, parent_doc):
    accounts_settings = frappe.get_cached_doc("Accounts Settings")
    add_taxes_from_item_tax_template = (
        accounts_settings.add_taxes_from_item_tax_template
    )
    if item.get("item_tax_template") and add_taxes_from_item_tax_template:
        item_tax_template = item.get("item_tax_template")
        taxes_template_details = frappe.get_all(
            "Item Tax Template Detail",
            filters={"parent": item_tax_template},
            fields=["tax_type"],
        )

        for tax_detail in taxes_template_details:
            tax_type = tax_detail.get("tax_type")

            found = any(tax.account_head == tax_type for tax in parent_doc.taxes)
            if not found:
                tax_row = parent_doc.append("taxes", {})
                tax_row.update(
                    {
                        "description": str(tax_type).split(" - ")[0],
                        "charge_type": "On Net Total",
                        "account_head": tax_type,
                    }
                )

                if parent_doc.doctype == "Purchase Order":
                    tax_row.update({"category": "Total", "add_deduct_tax": "Add"})
                tax_row.db_insert()

@frappe.whitelist()
def update_invoice(data):
    data = json.loads(data)
    if data.get("name"):
        invoice_doc = frappe.get_doc("Sales Invoice", data.get("name"))
        invoice_doc.update(data)
    else:
        invoice_doc = frappe.get_doc(data)

    count = 0
    invoices = frappe.get_list(
        "Sales Invoice",
        filters={"posting_date": invoice_doc.posting_date,
                 'pos_profile': data.get("pos_profile")},
        fields=["name"],
        limit_start=0,
        limit_page_length=5000,
    )

    if invoices:
        count = len(invoices)

    print("Count:", count)

    invoice_doc.custom_daily_counter = count + 1

    invoice_doc.set_missing_values()
    invoice_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True

    if invoice_doc.is_return and invoice_doc.return_against:
        ref_doc = frappe.get_cached_doc(invoice_doc.doctype, invoice_doc.return_against)
        if not ref_doc.update_stock:
            invoice_doc.update_stock = 0
        if len(invoice_doc.payments) == 0:
            invoice_doc.payments = ref_doc.payments
        invoice_doc.paid_amount = (
            invoice_doc.rounded_total or invoice_doc.grand_total or invoice_doc.total
        )
        for payment in invoice_doc.payments:
            if payment.default:
                payment.amount = invoice_doc.paid_amount
    allow_zero_rated_items = frappe.get_cached_value(
        "POS Profile", invoice_doc.pos_profile, "posa_allow_zero_rated_items"
    )
    for item in invoice_doc.items:
        if not item.rate or item.rate == 0:
            if allow_zero_rated_items:
                item.price_list_rate = 0.00
                item.is_free_item = 1
            else:
                frappe.throw(
                    _("Rate cannot be zero for item {0}").format(item.item_code)
                )
        else:
            item.is_free_item = 0
        add_taxes_from_tax_template(item, invoice_doc)

    if frappe.get_cached_value(
        "POS Profile", invoice_doc.pos_profile, "posa_tax_inclusive"
    ):
        if invoice_doc.get("taxes"):
            for tax in invoice_doc.taxes:
                tax.included_in_print_rate = 1

    invoice_doc.save()

    return invoice_doc

@frappe.whitelist()
def add_items_to_kitchen_screen(items):
    for item in items:
        print(f"\n\n item :{item}")
        kitchen_doc = frappe.new_doc("Kitchen Orders")
        kitchen_doc.item = item.item_code
        kitchen_doc.custom_quantity = item.qty
        kitchen_doc.order_number = item.name
        kitchen_doc.name = item.name
        kitchen_doc.status = "pending"
        # kitchen_doc.item_group = item.item_group
        kitchen_doc.custom_screen_no = item.custom_screen_number
        kitchen_doc.insert()

@frappe.whitelist()
def submit_quick_entry(screens_no):
    try:
        screens_no = json.loads(screens_no)
        print(f"\n\n submit_quick_entry (screens_no)=============> {screens_no}")
        # invoice = json.loads(invoice)
        for item in screens_no:
            kitchen_doc = frappe.new_doc("Kitchen Orders")
            kitchen_doc.item = item['item_code']
            kitchen_doc.custom_quantity = item['qty']
            kitchen_doc.order_number = item['name']
            kitchen_doc.name = item['name']
            kitchen_doc.status = "pending"
            kitchen_doc.custom_screen_no = item['screen_no']
            kitchen_doc.insert()
        return kitchen_doc
    except Exception as e:
        frappe.log_error(f"Error in submit_quick_entry: {e}")
        raise

@frappe.whitelist()
def print_with_ip(receipt_data, order_type, customer_type, order_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    printer_ip = "192.168.1.100"
    printer_address = (printer_ip, 9100)

    css = CSS(string='''@page { size: A3; margin: 1cm }
              body {width: 100%}
              div {width: 100%}
              td {border: 2px solid black; text-align: center; width: 80%; margin: 200px; margin-right: 10%}''')

    receipt = json.loads(receipt_data)
    receipts = ""
    receipts = f"""
                    <h3>order: {order_name}</h3>
                <table>
                    <tr>
                        <th>order type: {order_type}</th>
                        <th>customer: {customer_type}</th>
                    </tr>
                </table>
                """
    for category, items in receipt.items():

        receipts += f"""
            <html>
            <body>
                <div>
                <h2>قسم: {category}</h2>
                <table>
                    <tr><td colspan="2">&nbsp;&nbsp; Name &nbsp;&nbsp;</td><td>&nbsp;&nbsp; qty &nbsp;&nbsp;</td><td colspan="2">&nbsp;&nbsp; Notes &nbsp;&nbsp;</td></tr>"""
        for item in items:

            receipts += f"""
                    <tr><td colspan="2">{item["item_name"]}</td><td>{item["qty"]}</td><td colspan="2">&nbsp;&nbsp; {item["selected_notes"]} &nbsp;&nbsp;</td></tr>
                """
        receipts += f"""
                    </table>
                </div>
            </body>
            </html>
                  """
        html =  HTML(string = receipts)
        # html_pdf = html.write_pdf(f'{category}.pdf', stylesheets=[css])

        try:
            sock.connect(printer_address)
            html_pdf = html.write_pdf(stylesheets=[css])
            sock.sendall(html_pdf)
        finally:
            sock.close()
    return type(html_pdf)
@frappe.whitelist()
def get_all_pos_screens():
    screens = frappe.get_all("POS Screens", fields=["name", "screen_number"])
    return screens


def get_cash_account(invoice_doc, payment_mode=None):
    """
    الأولوية:
    1. لو في payments على الفاتورة → استخدمها
    2. لو في payment_mode ممرر → استخدمه
    3. fallback → default_cash_account للشركة
    """
    # حاول تاخد من payments الفاتورة الأول
    mop = [
        i.mode_of_payment
        for i in invoice_doc.payments
        if "cash" in i.mode_of_payment.lower()
    ]
    if mop:
        return get_bank_cash_account(mop[0], invoice_doc.company)

    # fallback على payment_mode الممرر من الـ payload
    if payment_mode:
        try:
            return get_bank_cash_account(payment_mode, invoice_doc.company)
        except Exception:
            pass

    # آخر fallback → default_cash_account
    return {
        "account": frappe.get_value(
            "Company", invoice_doc.company, "default_cash_account"
        )
    }


def create_payment_entry(invoice_doc, amount, cash_account, mode):
    """Payment Entry مربوط بفاتورة محددة"""

    pe = frappe.get_doc({
        "doctype": "Payment Entry",
        "payment_type": "Receive",
        "party_type": "Customer",
        "party": invoice_doc.customer,
        "paid_to": cash_account["account"],
        "paid_amount": amount,
        "received_amount": amount,
        "mode_of_payment": mode or "Cash",
        "company": invoice_doc.company,
        "references": [
            {
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice_doc.name,
                "allocated_amount": amount
            }
        ]
    })

    pe.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    pe.insert()
    pe.submit()
    return pe


def create_customer_credit(invoice_doc, amount, cash_account, mode):
    """Payment Entry بدون ربط بفاتورة → يُخزّن كـ Customer Credit"""

    pe = frappe.get_doc({
        "doctype": "Payment Entry",
        "payment_type": "Receive",
        "party_type": "Customer",
        "party": invoice_doc.customer,
        "paid_to": cash_account["account"],
        "paid_amount": amount,
        "received_amount": amount,
        "mode_of_payment": mode or "Cash",
        "company": invoice_doc.company,
    })

    pe.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    pe.insert()
    pe.submit()
    return pe


def apply_customer_credit(invoice_doc, data):
    """
    لو العميل عنده رصيد سابق (Customer Credit) وأراد استخدامه،
    يُضاف كـ advance على الفاتورة قبل التسليم.
    """
    is_payment_entry = 0

    if data.get("redeemed_customer_credit"):
        for row in data.get("customer_credit_dict", []):
            if row.get("credit_to_redeem"):
                invoice_doc.append("advances", {
                    "reference_type": "Payment Entry",
                    "reference_name": row["credit_origin"],
                    "allocated_amount": row["credit_to_redeem"],
                })
                invoice_doc.is_pos = 0
                is_payment_entry = 1

    return is_payment_entry


def prepare_invoice(invoice_doc, data):
    if frappe.get_value("POS Profile", invoice_doc.pos_profile, "posa_auto_set_batch"):
        set_batch_nos(invoice_doc, "warehouse", throw=True)

    set_batch_nos_for_bundels(invoice_doc, "warehouse", throw=True)
    # update stock after transactions
    # update_stock_after_tx = frappe.get_value(
    #         "POS Profile", invoice_doc.pos_profile, "custom_update_stock_after_Transactions"
    #     )
    # if update_stock_after_tx:
    invoice_doc.update_stock = 1

    invoice_doc.due_date = data.get("due_date")
    invoice_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    invoice_doc.posa_is_printed = 1
    invoice_doc.save()


def submit_invoice_doc(invoice_doc, data, is_payment_entry, cash_account):
    allow_background = frappe.get_value(
        "POS Profile",
        invoice_doc.pos_profile,
        "posa_allow_submissions_in_background_job",
    )

    if allow_background:

        job = enqueue(
            method=submit_in_background_job,
            queue="short",
            kwargs={
                "invoice": invoice_doc.name,
                "data": data,
                "is_payment_entry": is_payment_entry,
                "cash_account": cash_account,
            },
        )

        return {
            "success": True,
            "status": "queued",
            "message": "Invoice queued for background submission",
            "invoice": invoice_doc.name,
            "job_id": job.id if job else None,
        }

    invoice_doc.submit()

    return {
        "success": True,
        "status": "submitted",
        "message": "Invoice submitted successfully",
        "invoice": invoice_doc.name,
        "docstatus": invoice_doc.docstatus,
    }

@frappe.whitelist()
def save_invoice(invoice, data):
    data = frappe.parse_json(data)
    invoice = frappe.parse_json(invoice)

    if invoice.get("name") and frappe.db.exists("Sales Invoice", invoice.get("name")):
        invoice_doc = frappe.get_doc("Sales Invoice", invoice["name"])

        if invoice.get("customer"):
            invoice_doc.customer = invoice["customer"]

        if invoice.get("items"):
            invoice_doc.items = []
            for item in invoice.get("items"):
                invoice_doc.append("items", item)

        if invoice.get("payments"):
            invoice_doc.payments = []
            for payment in invoice.get("payments"):
                invoice_doc.append("payments", payment)
    else:
        invoice_doc = frappe.get_doc(invoice)

    prepare_invoice(invoice_doc, data)
    return {"name": invoice_doc.name, "status": invoice_doc.docstatus}


@frappe.whitelist()
def submit_invoice(invoice, data):

    data = frappe.parse_json(data)
    invoice = frappe.parse_json(invoice)
    if invoice.get("name") and frappe.db.exists("Sales Invoice", invoice.get("name")):
        invoice_doc = frappe.get_doc("Sales Invoice", invoice["name"])
    else:
        invoice_doc = frappe.get_doc(invoice)

    # =============================
    # 1. POS Profile Fields
    # =============================
    pos = frappe.get_cached_doc("POS Profile", invoice_doc.pos_profile)

    invoice_doc.cost_center      = pos.cost_center
    invoice_doc.taxes_and_charges = pos.taxes_and_charges
    invoice_doc.selling_price_list = pos.selling_price_list
    invoice_doc.write_off_account = pos.write_off_account
    invoice_doc.company          = pos.company
    invoice_doc.tax_category     = pos.tax_category

    for item in invoice_doc.items:
        item.cost_center = pos.cost_center
        item.warehouse   = pos.warehouse
        item.project     = pos.project
        item.expense_account  = pos.expense_account

    paid_amount  = float(invoice.get("summary", {}).get("cash", 0))
    total_amount = float(invoice.get("summary", {}).get("total", 0))

    credit_change = paid_amount - total_amount
    payment_mode  = invoice.get("paymentMethod") or "Cash"

    # =============================
    # 2. POS Profile Settings
    # =============================
    allow_partial     = frappe.get_value("POS Profile", invoice_doc.pos_profile, "posa_allow_partial_payment")
    allow_credit_sale = frappe.get_value("POS Profile", invoice_doc.pos_profile, "posa_allow_credit_sale")
    print("=======================================================")
    print('allow_credit_sale: ', allow_credit_sale)
    print("credit_change",credit_change)
    print("=======================================================")
    # =============================
    # 3. VALIDATION — قبل أي تنفيذ
    # =============================
    if paid_amount > total_amount:
        frappe.throw("المبلغ المدفوع أكبر من إجمالي الفاتورة. يرجى مراجعة المبلغ.")

    # الحالة: العميل دفع أقل (Partial Payment)
    if credit_change < 0 and not allow_partial:
        frappe.throw(
            "لا يمكن تسليم الفاتورة: المبلغ المدفوع أقل من الإجمالي "
            "والـ POS Profile لا يسمح بـ Partial Payment"
        )

    # =============================
    # 4. Cash Account
    # =============================
    cash_account = get_cash_account(invoice_doc, payment_mode)

    # =============================
    # 5. Apply Customer Credit (Advances)
    # =============================
    is_payment_entry = apply_customer_credit(invoice_doc, data)

    # =============================
    # 6. Prepare Invoice (Save قبل Submit)
    # =============================
    prepare_invoice(invoice_doc, data)

    # =============================
    # 7. Submit Invoice
    # =============================

    return submit_invoice_doc(invoice_doc, data, is_payment_entry, cash_account)


'''
    credit_change = paid_amount - total_invoice
    ex. if customer pay more than invoice amount credit_change = 150 - 100 = +50
    ex. Partial Payment credit_change = 60 - 100 = -40
'''
"""
    📋 Data Payload:{
        "redeemed_customer_credit": 0 or 1
        "credit_change": -40,
        "due_date": "2026-03-21",
        "transactionId": "TXN1774096035849104",
        "mode": "sale"
    }

    📋 Invoice -> dict:{
            mode: "sale" or "return",
            transactionType: "sale" or "return",
            cashAmount: 60,
            change: -40, (amount paid - inv amount)
            paymentMethod: Cash, -> str
            originalInvoice: null if sales else orginal returned inv,
            items:[
                {
                    "item_code": "STO-ITEM-2026-00001",
                    "item_name": "Cofee BEans",
                    "rate": 100,
                    "image": "/files/STO-ITEM-2026-000015d3b42.jpg",
                    "barcode": "",
                    "category": "Products",
                    "qty": 1,
                    "addedAt": "2026-03-21T12:26:56.535Z"
                }
            ],
            summary:{
                "itemsCount": 1,
                "subtotal": 100,
                "tax": 0,
                "discount": 0,
                "total": 100,
                "cash": 60,
                "change": -40
            },
            timestamp: "2026-03-21T12:27:15.849Z",
            transactionId:TXN1774096035849104
        }
"""

def set_batch_nos(doc, warehouse_field, throw=False, child_table="items"):
	"""Automatically select `batch_no` for outgoing items in item table"""
	for d in doc.get(child_table):
		qty = d.get("stock_qty") or d.get("transfer_qty") or d.get("qty") or 0
		warehouse = d.get(warehouse_field, None)
		if warehouse and qty > 0 and frappe.db.get_value("Item", d.item_code, "has_batch_no"):
			if not d.batch_no:
				d.batch_no = get_batch_no(d.item_code, warehouse, qty, throw, d.serial_no)
			else:
				batch_qty = get_batch_qty(batch_no=d.batch_no, warehouse=warehouse)
				if flt(batch_qty, d.precision("qty")) < flt(qty, d.precision("qty")):
					frappe.throw(
						_(
							"Row #{0}: The batch {1} has only {2} qty. Please select another batch which has {3} qty available or split the row into multiple rows, to deliver/issue from multiple batches"
						).format(d.idx, d.batch_no, batch_qty, qty)
					)


def set_batch_nos_for_bundels(doc, warehouse_field, throw=False):
    """Automatically select `batch_no` for outgoing items in item table"""
    for d in doc.packed_items:
        qty = d.get("stock_qty") or d.get("transfer_qty") or d.get("qty") or 0
        has_batch_no = frappe.db.get_value("Item", d.item_code, "has_batch_no")
        warehouse = d.get(warehouse_field, None)
        if has_batch_no and warehouse and qty > 0:
            if not d.batch_no:
                d.batch_no = get_batch_no(
                    d.item_code, warehouse, qty, throw, d.serial_no
                )
            else:
                batch_qty = get_batch_qty(batch_no=d.batch_no, warehouse=warehouse)
                if flt(batch_qty, d.precision("qty")) < flt(qty, d.precision("qty")):
                    frappe.throw(
                        _(
                            "Row #{0}: The batch {1} has only {2} qty. Please select another batch which has {3} qty available or split the row into multiple rows, to deliver/issue from multiple batches"
                        ).format(d.idx, d.batch_no, batch_qty, qty)
                    )

def redeeming_customer_credit(
    invoice_doc, data, is_payment_entry, total_cash, cash_account, payments
):
    # redeeming customer credit with journal voucher
    today = nowdate()
    if data.get("redeemed_customer_credit"):
        cost_center = frappe.get_value(
            "POS Profile", invoice_doc.pos_profile, "cost_center"
        )
        if not cost_center:
            cost_center = frappe.get_value(
                "Company", invoice_doc.company, "cost_center"
            )
        if not cost_center:
            frappe.throw(
                _("Cost Center is not set in pos profile {}").format(
                    invoice_doc.pos_profile
                )
            )
        for row in data.get("customer_credit_dict"):
            if row["type"] == "Invoice" and row["credit_to_redeem"]:
                outstanding_invoice = frappe.get_doc(
                    "Sales Invoice", row["credit_origin"]
                )

                jv_doc = frappe.get_doc(
                    {
                        "doctype": "Journal Entry",
                        "voucher_type": "Journal Entry",
                        "posting_date": today,
                        "company": invoice_doc.company,
                    }
                )

                jv_debit_entry = {
                    "account": outstanding_invoice.debit_to,
                    "party_type": "Customer",
                    "party": invoice_doc.customer,
                    "reference_type": "Sales Invoice",
                    "reference_name": outstanding_invoice.name,
                    "debit_in_account_currency": row["credit_to_redeem"],
                    "cost_center": cost_center,
                }

                jv_credit_entry = {
                    "account": invoice_doc.debit_to,
                    "party_type": "Customer",
                    "party": invoice_doc.customer,
                    "reference_type": "Sales Invoice",
                    "reference_name": invoice_doc.name,
                    "credit_in_account_currency": row["credit_to_redeem"],
                    "cost_center": cost_center,
                }

                jv_doc.append("accounts", jv_debit_entry)
                jv_doc.append("accounts", jv_credit_entry)

                jv_doc.flags.ignore_permissions = True
                frappe.flags.ignore_account_permission = True
                jv_doc.set_missing_values()
                jv_doc.save()
                jv_doc.submit()

    if is_payment_entry and total_cash > 0:
        for payment in payments:
            if not payment.amount:
                continue
            payment_entry_doc = frappe.get_doc(
                {
                    "doctype": "Payment Entry",
                    "posting_date": today,
                    "payment_type": "Receive",
                    "party_type": "Customer",
                    "party": invoice_doc.customer,
                    "paid_amount": payment.amount,
                    "received_amount": payment.amount,
                    "paid_from": invoice_doc.debit_to,
                    "paid_to": payment.account,
                    "company": invoice_doc.company,
                    "mode_of_payment": payment.mode_of_payment,
                    "reference_no": invoice_doc.posa_pos_opening_shift,
                    "reference_date": today,
                }
            )

            payment_reference = {
                "allocated_amount": payment.amount,
                "due_date": data.get("due_date"),
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice_doc.name,
            }

            payment_entry_doc.append("references", payment_reference)
            payment_entry_doc.flags.ignore_permissions = True
            frappe.flags.ignore_account_permission = True
            payment_entry_doc.save()
            payment_entry_doc.submit()

def submit_in_background_job(kwargs):
    invoice = kwargs.get("invoice")
    invoice_doc = kwargs.get("invoice_doc")
    data = kwargs.get("data")
    is_payment_entry = kwargs.get("is_payment_entry")
    total_cash = kwargs.get("total_cash")
    cash_account = kwargs.get("cash_account")
    payments = kwargs.get("payments")

    invoice_doc = frappe.get_doc("Sales Invoice", invoice)
    # update_stock_after_tx = frappe.get_value(
    #         "POS Profile", invoice_doc.pos_profile, "custom_update_stock_after_Transactions"
    #     )
    # if update_stock_after_tx:
    invoice_doc.update_stock = 1

    invoice_doc.submit()
    redeeming_customer_credit(
        invoice_doc, data, is_payment_entry, total_cash, cash_account, payments
    )

@frappe.whitelist()
def search_orders(company, currency, order_name=None):
    filters = {
        "billing_status": ["in", ["Not Billed", "Partly Billed"]],
        "docstatus": 1,
        "company": company,
        "currency": currency,
    }
    if order_name:
        filters["name"] = ["like", f"%{order_name}%"]
    orders_list = frappe.get_list(
        "Sales Order",
        filters=filters,
        fields=["name"],
        limit_page_length=0,
        order_by="customer",
    )
    data = []
    for order in orders_list:
        data.append(frappe.get_doc("Sales Order", order["name"]))
    print('/n --------> data',data)
    return data

@frappe.whitelist()
def get_available_credit(customer, company):
    total_credit = []

    outstanding_invoices = frappe.get_all(
        "Sales Invoice",
        {
            "outstanding_amount": ["<", 0],
            "docstatus": 1,
            "is_return": 0,
            "customer": customer,
            "company": company,
        },
        ["name", "outstanding_amount"],
    )

    for row in outstanding_invoices:
        outstanding_amount = -(row.outstanding_amount)
        row = {
            "type": "Invoice",
            "credit_origin": row.name,
            "total_credit": outstanding_amount,
            "credit_to_redeem": 0,
        }

        total_credit.append(row)

    advances = frappe.get_all(
        "Payment Entry",
        {
            "unallocated_amount": [">", 0],
            "party_type": "Customer",
            "party": customer,
            "company": company,
            "docstatus": 1,
        },
        ["name", "unallocated_amount"],
    )

    for row in advances:
        row = {
            "type": "Advance",
            "credit_origin": row.name,
            "total_credit": row.unallocated_amount,
            "credit_to_redeem": 0,
        }

        total_credit.append(row)

    return total_credit

@frappe.whitelist()
def get_draft_invoices(pos_opening_shift):
    invoices_list = frappe.get_list(
        "Sales Invoice",
        filters={
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 0,
            "posa_is_printed": 0,
            "is_pos":1
        },
        fields=["name"],
        limit_page_length=0,
        order_by="modified desc",
    )
    data = []
    for invoice in invoices_list:
        data.append(frappe.get_cached_doc("Sales Invoice", invoice["name"]))
    return data

@frappe.whitelist()
def delete_invoice(invoice):
    if frappe.get_value("Sales Invoice", invoice, "posa_is_printed"):
        frappe.throw(_("This invoice {0} cannot be deleted").format(invoice))
    frappe.delete_doc("Sales Invoice", invoice, force=1)
    return _("Invoice {0} Deleted").format(invoice)

@frappe.whitelist()
def get_items_details(pos_profile, items_data):
    _pos_profile = json.loads(pos_profile)

    return _get_items_details(_pos_profile, items_data)


def _get_items_details(pos_profile, items_data):
    today = nowdate()
    pos_profile = json.loads(pos_profile)
    items_data = json.loads(items_data)
    warehouse = pos_profile.get("warehouse")
    result = []

    if len(items_data) > 0:
        for item in items_data:
            item_code = item.get("item_code")
            item_stock_qty = get_stock_availability(item_code, warehouse)
            has_batch_no, has_serial_no = frappe.get_value(
                "Item", item_code, ["has_batch_no", "has_serial_no"]
            )

            uoms = frappe.get_all(
                "UOM Conversion Detail",
                filters={"parent": item_code},
                fields=["uom", "conversion_factor"],
            )

            serial_no_data = frappe.get_all(
                "Serial No",
                filters={
                    "item_code": item_code,
                    "status": "Active",
                    "warehouse": warehouse,
                },
                fields=["name as serial_no"],
            )

            batch_no_data = []

            batch_list = get_batch_qty(warehouse=warehouse, item_code=item_code)

            if batch_list:
                for batch in batch_list:
                    if batch.qty > 0 and batch.batch_no:
                        batch_doc = frappe.get_cached_doc("Batch", batch.batch_no)
                        if (
                            str(batch_doc.expiry_date) > str(today)
                            or batch_doc.expiry_date in ["", None]
                        ) and batch_doc.disabled == 0:
                            batch_no_data.append(
                                {
                                    "batch_no": batch.batch_no,
                                    "batch_qty": batch.qty,
                                    "expiry_date": batch_doc.expiry_date,
                                    "batch_price": batch_doc.posa_batch_price,
                                    "manufacturing_date": batch_doc.manufacturing_date,
                                }
                            )

            row = {}
            row.update(item)
            row.update(
                {
                    "item_uoms": uoms or [],
                    "serial_no_data": serial_no_data or [],
                    "batch_no_data": batch_no_data or [],
                    "actual_qty": item_stock_qty or 0,
                    "has_batch_no": has_batch_no,
                    "has_serial_no": has_serial_no,
                }
            )

            result.append(row)

    return result


@frappe.whitelist()
def get_item_detail(item, doc=None, warehouse=None, price_list=None):
    item = json.loads(item)
    today = nowdate()
    item_code = item.get("item_code")
    batch_no_data = []
    if warehouse and item.get("has_batch_no"):
        batch_list = get_batch_qty(warehouse=warehouse, item_code=item_code)
        if batch_list:
            for batch in batch_list:
                if batch.qty > 0 and batch.batch_no:
                    batch_doc = frappe.get_cached_doc("Batch", batch.batch_no)
                    if (
                        str(batch_doc.expiry_date) > str(today)
                        or batch_doc.expiry_date in ["", None]
                    ) and batch_doc.disabled == 0:
                        batch_no_data.append(
                            {
                                "batch_no": batch.batch_no,
                                "batch_qty": batch.qty,
                                "expiry_date": batch_doc.expiry_date,
                                "batch_price": batch_doc.posa_batch_price,
                                "manufacturing_date": batch_doc.manufacturing_date,
                            }
                        )

    item["selling_price_list"] = price_list

    max_discount = frappe.get_value("Item", item_code, "max_discount")
    res = get_item_details(
        item,
        doc,
        overwrite_warehouse=False,
    )
    if item.get("is_stock_item") and warehouse:
        res["actual_qty"] = get_stock_availability(item_code, warehouse)
    res["max_discount"] = max_discount
    res["batch_no_data"] = batch_no_data
    return res

def get_stock_availability(item_code, warehouse):
    actual_qty = (
        frappe.db.get_value(
            "Stock Ledger Entry",
            filters={
                "item_code": item_code,
                "warehouse": warehouse,
                "is_cancelled": 0,
            },
            fieldname="qty_after_transaction",
            order_by="posting_date desc, posting_time desc, creation desc",
        )
        or 0.0
    )
    return actual_qty

@frappe.whitelist()
def get_today_invoices():
    current_date = nowdate()
    invoices = frappe.get_list(
        "Sales Invoice",
        filters={"posting_date": current_date},
        fields=["name"]
    )
    invoice_names = [invoice.name for invoice in invoices]
    return invoice_names
@frappe.whitelist()
def create_customer(
    customer_name,
    company,
    pos_profile_doc,
    first_mobile,
    city,
    customer_id=None,
    second_mobile=None,
    email_id=None,
    customer_group=None,
    territory=None,
    customer_type=None,
    gender=None,
    method="create",
    note='',
    # contact fields
    first_name=None,
    last_name=None,
    # address fields
    address_line1=None,
    address_line2=None,
    state=None,
    country="Egypt",
    pincode=None,
):
    from retail.retail.api.contact import create_contact, update_contact
    from retail.retail.api.address import create_address, update_address, get_customer_addresses

    pos_profile = json.loads(pos_profile_doc) if isinstance(pos_profile_doc, str) else pos_profile_doc

    # ── بيانات الكونتكت ──────────────────────────────────────────────
    phone_nos = [
        {"phone": first_mobile, "is_primary_mobile_no": 1, "is_primary_phone": 1},
    ]
    if second_mobile:
        phone_nos.append({"phone": second_mobile, "is_primary_mobile_no": 0, "is_primary_phone": 0})

    email_ids = [{"email_id": email_id, "is_primary": 1}] if email_id else []

    # ── بيانات الأدريس ──────────────────────────────────────────────
    address_payload = {
        "title"              : customer_name,
        "line1"              : address_line1 or city,
        "line2"              : address_line2 or "",
        "city"               : city,
        "state"              : state  or "",
        "country"            : country or "Egypt",
        "pincode"            : pincode or "",
        "is_primary_address" : 1,
        "is_shipping_address": 1,
    }

    # ════════════════════════════════════════════════════════════════
    if method == "create":
        is_exist = frappe.db.exists("Customer", {"customer_name": customer_name})
        if not pos_profile.get("posa_allow_duplicate_customer_names") and is_exist:
            frappe.throw(_("Customer already exists"))

        # 1. Customer
        customer_doc = frappe.get_doc({
            "doctype"             : "Customer",
            "customer_name"       : customer_name,
            "posa_referral_company": company,
            "customer_type"       : customer_type or "Individual",
            "gender"              : gender or "",
            "custom_note"         : note or "",
            "customer_group"      : customer_group or "All Customer Groups",
            "territory"           : territory      or "All Territories",
        })
        customer_doc.insert(ignore_permissions=False)
        frappe.db.commit()

        cust_name = customer_doc.name

        # 2. Address
        saved_address = create_address(
            customer=cust_name,
            **address_payload
        )

        # 3. Contact
        create_contact(
            customer     = cust_name,
            first_name   = first_name or customer_name,
            last_name    = last_name  or "",
            is_primary   = 1,
            email_ids    = email_ids,
            phone_nos    = phone_nos,
            address_name = saved_address["name"] if saved_address else None,
        )

        return customer_doc

    # ════════════════════════════════════════════════════════════════
    elif method == "update":
        customer_doc = frappe.get_doc("Customer", customer_id)
        customer_doc.customer_name = customer_name
        if company:       customer_doc.posa_referral_company = company
        if customer_type: customer_doc.customer_type         = customer_type
        if gender:        customer_doc.gender                = gender
        if note:          customer_doc.custom_note           = note
        if customer_group: customer_doc.customer_group       = customer_group
        if territory:      customer_doc.territory            = territory
        customer_doc.save(ignore_permissions=False)
        frappe.db.commit()

        # ── Contact ──────────────────────────────────────────────
        from frappe.contacts.doctype.contact.contact import get_contacts_linking_to
        contacts = get_contacts_linking_to("Customer", customer_id, fields=["name", "address"])
        primary_contact = next(
            (c for c in contacts if frappe.db.get_value("Contact", c["name"], "is_primary_contact")),
            contacts[0] if contacts else None
        )

        contact_payload = {
            "first_name" : first_name or customer_name,
            "last_name"  : last_name  or "",
            "is_primary" : 1,
            "email_ids"  : email_ids,
            "phone_nos"  : phone_nos,
        }

        # ── Address ──────────────────────────────────────────────
        existing_addresses = get_customer_addresses(customer_id)
        primary_address = next(
            (a for a in existing_addresses if a.get("is_primary_address")),
            existing_addresses[0] if existing_addresses else None
        )

        if primary_address:
            saved_address = update_address(primary_address["name"], **address_payload)
            contact_payload["address_name"] = primary_address["name"]
        else:
            saved_address = create_address(customer=customer_id, **address_payload)
            contact_payload["address_name"] = saved_address["name"] if saved_address else None

        if primary_contact:
            update_contact(primary_contact["name"], **contact_payload)
        else:
            create_contact(customer=customer_id, **contact_payload)

        return customer_doc

@frappe.whitelist()
def get_items_from_barcode(selling_price_list, currency, barcode):
    search_item = frappe.get_all(
        "Item Barcode",
        filters={"barcode": barcode},
        fields=["parent", "barcode", "posa_uom"],
    )
    if len(search_item) == 0:
        return ""
    item_code = search_item[0].parent
    item_list = frappe.get_all(
        "Item",
        filters={"name": item_code},
        fields=[
            "name",
            "item_name",
            "description",
            "stock_uom",
            "image",
            "is_stock_item",
            "has_variants",
            "variant_of",
            "item_group",
            "has_batch_no",
            "has_serial_no",
        ],
    )

    if item_list[0]:
        item = item_list[0]
        filters = {"price_list": selling_price_list, "item_code": item_code}
        prices_with_uom = frappe.db.count(
            "Item Price",
            filters={
                "price_list": selling_price_list,
                "item_code": item_code,
                "uom": item.stock_uom,
            },
        )

        if prices_with_uom > 0:
            filters["uom"] = item.stock_uom
        else:
            filters["uom"] = ["in", ["", None, item.stock_uom]]

        item_prices_data = frappe.get_all(
            "Item Price",
            fields=["item_code", "price_list_rate", "currency",  "uom"],
            filters=filters,
        )

        item_price = 0
        if len(item_prices_data):
            item_price = item_prices_data[0].get("price_list_rate")
            currency = item_prices_data[0].get("currency")

        item.update(
            {
                "rate": item_price,
                "currency": currency,
                "item_code": item_code,
                "barcode": barcode,
                "actual_qty": 0,
                "item_barcode": search_item,
            }
        )
        return item

@frappe.whitelist()
def set_customer_info(customer, fieldname, value=""):
    if fieldname == "loyalty_program":
        frappe.db.set_value("Customer", customer, "loyalty_program", value)

    contact = (
        frappe.get_cached_value("Customer", customer, "customer_primary_contact") or ""
    )

    if contact:
        contact_doc = frappe.get_doc("Contact", contact)
        if fieldname == "email_id":
            contact_doc.set("email_ids", [{"email_id": value, "is_primary": 1}])
            frappe.db.set_value("Customer", customer, "email_id", value)
        elif fieldname == "mobile_no":
            contact_doc.set("phone_nos", [{"phone": value, "is_primary_mobile_no": 1}])
            frappe.db.set_value("Customer", customer, "mobile_no", value)
        contact_doc.save()

    else:
        contact_doc = frappe.new_doc("Contact")
        contact_doc.first_name = customer
        contact_doc.is_primary_contact = 1
        contact_doc.is_billing_contact = 1
        if fieldname == "mobile_no":
            contact_doc.add_phone(value, is_primary_mobile_no=1, is_primary_phone=1)

        if fieldname == "email_id":
            contact_doc.add_email(value, is_primary=1)

        contact_doc.append("links", {"link_doctype": "Customer", "link_name": customer})

        contact_doc.flags.ignore_mandatory = True
        contact_doc.save()
        frappe.set_value(
            "Customer", customer, "customer_primary_contact", contact_doc.name
        )

@frappe.whitelist()
def search_invoices_for_return(invoice_name, company):
    invoices_list = frappe.get_list(
        "Sales Invoice",
        filters={
            "name": ["like", f"%{invoice_name}%"],
            "company": company,
            "docstatus": 1,
            "is_return": 0,
        },
        fields=["name"],
        limit_page_length=0,
        order_by="customer",
    )
    data = []
    is_returned = frappe.get_all(
        "Sales Invoice",
        filters={"return_against": invoice_name, "docstatus": 1},
        fields=["name"],
        order_by="customer",
    )
    if len(is_returned):
        return data
    for invoice in invoices_list:
        data.append(frappe.get_doc("Sales Invoice", invoice["name"]))
    return data

@frappe.whitelist()
def search_invoices_for_current_shift(pos_shift):
    invoices_list = frappe.get_list(
        "Sales Invoice",
        filters={
            "posa_pos_opening_shift": pos_shift,
            "docstatus": 1,
        },
        limit_page_length=0,
        order_by="customer",
    )

    data = []

    if len(invoices_list):
        for invoice in invoices_list:
            invoicee = frappe.get_doc("Sales Invoice", invoice.name)
            data.append(invoicee)
    return data

def get_version():
    branch_name = get_app_branch("erpnext")
    if "12" in branch_name:
        return 12
    elif "13" in branch_name:
        return 13
    else:
        return 13

def get_app_branch(app):
    """Returns branch of an app"""
    import subprocess

    try:
        branch = subprocess.check_output(
            "cd ../apps/{0} && git rev-parse --abbrev-ref HEAD".format(app), shell=True
        )
        branch = branch.decode("utf-8")
        branch = branch.strip()
        return branch
    except Exception:
        return ""

@frappe.whitelist()
def get_offers(profile):
    pos_profile = frappe.get_doc("POS Profile", profile)
    company = pos_profile.company
    warehouse = pos_profile.warehouse
    date = nowdate()

    values = {
        "company": company,
        "pos_profile": profile,
        "warehouse": warehouse,
        "valid_from": date,
        "valid_upto": date,
    }
    data = frappe.db.sql(
        """
        SELECT *
        FROM `tabPOS Offer`
        WHERE
        disable = 0 AND
        company = %(company)s AND
        (pos_profile is NULL OR pos_profile  = '' OR  pos_profile = %(pos_profile)s) AND
        (warehouse is NULL OR warehouse  = '' OR  warehouse = %(warehouse)s) AND
        (valid_from is NULL OR valid_from  = '' OR  valid_from <= %(valid_from)s) AND
        (valid_upto is NULL OR valid_from  = '' OR  valid_upto >= %(valid_upto)s)
    """,
        values=values,
        as_dict=1,
    )
    return data

@frappe.whitelist()
def get_customer_addresses(customer):
    return frappe.db.sql(
        """
        SELECT
            address.name,
            address.address_line1,
            address.address_line2,
            address.address_title,
            address.city,
            address.state,
            address.country,
            address.address_type
        FROM `tabAddress` as address
        INNER JOIN `tabDynamic Link` AS link
				ON address.name = link.parent
        WHERE link.link_doctype = 'Customer'
            AND link.link_name = '{0}'
            AND address.disabled = 0
        ORDER BY address.name
        """.format(
            customer
        ),
        as_dict=1,
    )

@frappe.whitelist()
def make_address(args):
    args = json.loads(args)
    address = frappe.get_doc(
        {
            "doctype": "Address",
            "address_title": args.get("name"),
            "address_line1": args.get("address_line1"),
            "address_line2": args.get("address_line2"),
            "city": args.get("city"),
            "state": args.get("state"),
            "pincode": args.get("pincode"),
            "country": args.get("country"),
            "address_type": "Shipping",
            "links": [
                {"link_doctype": args.get("doctype"), "link_name": args.get("customer")}
            ],
        }
    ).insert()

    return address

def build_item_cache(item_code):
    parent_item_code = item_code

    attributes = [
        a.attribute
        for a in frappe.db.get_all(
            "Item Variant Attribute",
            {"parent": parent_item_code},
            ["attribute"],
            order_by="idx asc",
        )
    ]

    item_variants_data = frappe.db.get_all(
        "Item Variant Attribute",
        {"variant_of": parent_item_code},
        ["parent", "attribute", "attribute_value"],
        order_by="name",
        as_list=1,
    )

    disabled_items = set([i.name for i in frappe.db.get_all("Item", {"disabled": 1})])

    attribute_value_item_map = frappe._dict({})
    item_attribute_value_map = frappe._dict({})

    item_variants_data = [r for r in item_variants_data if r[0] not in disabled_items]
    for row in item_variants_data:
        item_code, attribute, attribute_value = row
        # (attr, value) => [item1, item2]
        attribute_value_item_map.setdefault((attribute, attribute_value), []).append(
            item_code
        )
        # item => {attr1: value1, attr2: value2}
        item_attribute_value_map.setdefault(item_code, {})[attribute] = attribute_value

    optional_attributes = set()
    for item_code, attr_dict in item_attribute_value_map.items():
        for attribute in attributes:
            if attribute not in attr_dict:
                optional_attributes.add(attribute)

    frappe.cache().hset(
        "attribute_value_item_map", parent_item_code, attribute_value_item_map
    )
    frappe.cache().hset(
        "item_attribute_value_map", parent_item_code, item_attribute_value_map
    )
    frappe.cache().hset("item_variants_data", parent_item_code, item_variants_data)
    frappe.cache().hset("optional_attributes", parent_item_code, optional_attributes)

def get_item_optional_attributes(item_code):
    val = frappe.cache().hget("optional_attributes", item_code)

    if not val:
        build_item_cache(item_code)

    return frappe.cache().hget("optional_attributes", item_code)

@frappe.whitelist()
def get_item_attributes(item_code):
    attributes = frappe.db.get_all(
        "Item Variant Attribute",
        fields=["attribute"],
        filters={"parenttype": "Item", "parent": item_code},
        order_by="idx asc",
    )

    optional_attributes = get_item_optional_attributes(item_code)

    for a in attributes:
        values = frappe.db.get_all(
            "Item Attribute Value",
            fields=["attribute_value", "abbr"],
            filters={"parenttype": "Item Attribute", "parent": a.attribute},
            order_by="idx asc",
        )
        a.values = values
        if a.attribute in optional_attributes:
            a.optional = True

    return attributes

@frappe.whitelist()
def create_payment_request(doc):
    doc = json.loads(doc)
    for pay in doc.get("payments"):
        if pay.get("type") == "Phone":
            if pay.get("amount") <= 0:
                frappe.throw(_("Payment amount cannot be less than or equal to 0"))

            if not doc.get("contact_mobile"):
                frappe.throw(_("Please enter the phone number first"))

            pay_req = get_existing_payment_request(doc, pay)
            if not pay_req:
                pay_req = get_new_payment_request(doc, pay)
                pay_req.submit()
            else:
                pay_req.request_phone_payment()

            return pay_req

def get_new_payment_request(doc, mop):
    payment_gateway_account = frappe.db.get_value(
        "Payment Gateway Account",
        {
            "payment_account": mop.get("account"),
        },
        ["name"],
    )

    args = {
        "dt": "Sales Invoice",
        "dn": doc.get("name"),
        "recipient_id": doc.get("contact_mobile"),
        "mode_of_payment": mop.get("mode_of_payment"),
        "payment_gateway_account": payment_gateway_account,
        "payment_request_type": "Inward",
        "party_type": "Customer",
        "party": doc.get("customer"),
        "return_doc": True,
    }
    return make_payment_request(**args)

def get_payment_gateway_account(args):
    return frappe.db.get_value(
        "Payment Gateway Account",
        args,
        ["name", "payment_gateway", "payment_account", "message"],
        as_dict=1,
    )

def get_existing_payment_request(doc, pay):
    payment_gateway_account = frappe.db.get_value(
        "Payment Gateway Account",
        {
            "payment_account": pay.get("account"),
        },
        ["name"],
    )

    args = {
        "doctype": "Payment Request",
        "reference_doctype": "Sales Invoice",
        "reference_name": doc.get("name"),
        "payment_gateway_account": payment_gateway_account,
        "email_to": doc.get("contact_mobile"),
    }
    pr = frappe.db.exists(args)
    if pr:
        return frappe.get_doc("Payment Request", pr)

def make_payment_request(**args):
    """Make payment request"""

    args = frappe._dict(args)

    ref_doc = frappe.get_doc(args.dt, args.dn)
    gateway_account = get_payment_gateway_account(args.get("payment_gateway_account"))
    if not gateway_account:
        frappe.throw(_("Payment Gateway Account not found"))

    grand_total = get_amount(ref_doc, gateway_account.get("payment_account"))
    if args.loyalty_points and args.dt == "Sales Order":
        from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
            validate_loyalty_points,
        )

        loyalty_amount = validate_loyalty_points(ref_doc, int(args.loyalty_points))
        frappe.db.set_value(
            "Sales Order",
            args.dn,
            "loyalty_points",
            int(args.loyalty_points),
            update_modified=False,
        )
        frappe.db.set_value(
            "Sales Order",
            args.dn,
            "loyalty_amount",
            loyalty_amount,
            update_modified=False,
        )
        grand_total = grand_total - loyalty_amount

    bank_account = (
        get_party_bank_account(args.get("party_type"), args.get("party"))
        if args.get("party_type")
        else ""
    )

    existing_payment_request = None
    if args.order_type == "Shopping Cart":
        existing_payment_request = frappe.db.get_value(
            "Payment Request",
            {
                "reference_doctype": args.dt,
                "reference_name": args.dn,
                "docstatus": ("!=", 2),
            },
        )

    if existing_payment_request:
        frappe.db.set_value(
            "Payment Request",
            existing_payment_request,
            "grand_total",
            grand_total,
            update_modified=False,
        )
        pr = frappe.get_doc("Payment Request", existing_payment_request)
    else:
        if args.order_type != "Shopping Cart":
            existing_payment_request_amount = get_existing_payment_request_amount(
                args.dt, args.dn
            )

            if existing_payment_request_amount:
                grand_total -= existing_payment_request_amount

        pr = frappe.new_doc("Payment Request")
        pr.update(
            {
                "payment_gateway_account": gateway_account.get("name"),
                "payment_gateway": gateway_account.get("payment_gateway"),
                "payment_account": gateway_account.get("payment_account"),
                "payment_channel": gateway_account.get("payment_channel"),
                "payment_request_type": args.get("payment_request_type"),
                "currency": ref_doc.currency,
                "grand_total": grand_total,
                "mode_of_payment": args.mode_of_payment,
                "email_to": args.recipient_id or ref_doc.owner,
                "subject": _("Payment Request for {0}").format(args.dn),
                "message": gateway_account.get("message") or get_dummy_message(ref_doc),
                "reference_doctype": args.dt,
                "reference_name": args.dn,
                "party_type": args.get("party_type") or "Customer",
                "party": args.get("party") or ref_doc.get("customer"),
                "bank_account": bank_account,
            }
        )

        if args.order_type == "Shopping Cart" or args.mute_email:
            pr.flags.mute_email = True

        pr.insert(ignore_permissions=True)
        if args.submit_doc:
            pr.submit()

    if args.order_type == "Shopping Cart":
        frappe.db.commit()
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = pr.get_payment_url()

    if args.return_doc:
        return pr

    return pr.as_dict()

def get_amount(ref_doc, payment_account=None):
    """get amount based on doctype"""
    grand_total = 0
    for pay in ref_doc.payments:
        if pay.type == "Phone" and pay.account == payment_account:
            grand_total = pay.amount
            break

    if grand_total > 0:
        return grand_total

    else:
        frappe.throw(
            _("Payment Entry is already created or payment account is not matched")
        )

@frappe.whitelist()
def get_pos_coupon(coupon, customer, company):
    res = check_coupon_code(coupon, customer, company)
    return res

@frappe.whitelist()
def get_active_gift_coupons(customer, company):
    coupons = []
    coupons_data = frappe.get_all(
        "POS Coupon",
        filters={
            "company": company,
            "coupon_type": "Gift Card",
            "customer": customer,
            "used": 0,
        },
        fields=["coupon_code"],
    )
    if len(coupons_data):
        coupons = [i.coupon_code for i in coupons_data]
    return coupons

@frappe.whitelist()
def get_customer_info(customer):
    customer = frappe.get_doc("Customer", customer)

    res = {"loyalty_points": None, "conversion_factor": None}

    res["email_id"] = customer.email_id
    res["first_mobile"] = customer.custom_first_mobile
    res["second_mobile"] = customer.custom_second_mobile
    res["custom_city"] = customer.custom_city
    # res["custom_customer_note"] = customer.custom_note
    res["custom_customer_note"] = getattr(customer, "custom_note", None)
    res["image"] = customer.image
    res["loyalty_program"] = customer.loyalty_program
    res["customer_price_list"] = customer.default_price_list
    res["customer_group"] = customer.customer_group
    res["customer_type"] = customer.customer_type
    res["territory"] = customer.territory
    res["birthday"] = customer.posa_birthday
    res["gender"] = customer.gender
    res["tax_id"] = customer.tax_id
    res["posa_discount"] = customer.posa_discount
    res["name"] = customer.name
    res["customer_name"] = customer.customer_name
    res["customer_group_price_list"] = frappe.get_value(
        "Customer Group", customer.customer_group, "default_price_list"
    )

    if customer.loyalty_program:
        lp_details = get_loyalty_program_details_with_points(
            customer.name,
            customer.loyalty_program,
            silent=True,
            include_expired_entry=False,
        )
        res["loyalty_points"] = lp_details.get("loyalty_points")
        res["conversion_factor"] = lp_details.get("conversion_factor")

    return res

def get_company_domain(company):
    return frappe.get_cached_value("Company", cstr(company), "domain")

@frappe.whitelist()
def get_applicable_delivery_charges(
    company, pos_profile, customer, shipping_address_name=None
):
    return _get_applicable_delivery_charges(
        company, pos_profile, customer, shipping_address_name
    )

def auto_create_items():
    # create 20000 items
    for i in range(20000):
        item_code = "AUTO-ITEM-{}".format(i)
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": item_code,
                "item_name": item_code,
                "description": item_code,
                "item_group": "Auto Items",
                "is_stock_item": 0,
                "stock_uom": "Nos",
                "is_sales_item": 1,
                "is_purchase_item": 0,
                "is_fixed_asset": 0,
                "is_sub_contracted_item": 0,
                "is_pro_applicable": 0,
                "is_manufactured_item": 0,
                "is_service_item": 0,
                "is_non_stock_item": 0,
                "is_batch_item": 0,
                "is_table_item": 0,
                "is_variant_item": 0,
                "is_stock_item": 1,
                "opening_stock": 1000,
                "valuation_rate": 50 + i,
                "standard_rate": 100 + i,
            }
        )
        print("Creating Item: {}".format(item_code))
        item.insert(ignore_permissions=True)
        frappe.db.commit()

@frappe.whitelist()
def search_serial_or_batch_or_barcode_number(search_value, search_serial_no):
    # search barcode no
    barcode_data = frappe.db.get_value(
        "Item Barcode",
        {"barcode": search_value},
        ["barcode", "parent as item_code"],
        as_dict=True,
    )
    if barcode_data:
        return barcode_data
    # search serial no
    if search_serial_no:
        serial_no_data = frappe.db.get_value(
            "Serial No", search_value, ["name as serial_no", "item_code"], as_dict=True
        )
        if serial_no_data:
            return serial_no_data
    # search batch no
    batch_no_data = frappe.db.get_value(
        "Batch", search_value, ["name as batch_no", "item as item_code"], as_dict=True
    )
    if batch_no_data:
        return batch_no_data
    return {}

def get_seearch_items_conditions(item_code, serial_no, batch_no, barcode):
    if serial_no or batch_no or barcode:
        return " and name = {0}".format(frappe.db.escape(item_code))
    return """ and (name like {item_code} or item_name like {item_code})""".format(
        item_code=frappe.db.escape("%" + item_code + "%")
    )

@frappe.whitelist()
def get_item_groups_2(pos_profile):
    pos_item_groups = frappe.get_all("POS Item Group", filters={"parent": pos_profile}, fields=["item_group"])
    response = []
    for pos_group in pos_item_groups:
        item_group = frappe.get_all("Item Group", filters={"name": pos_group["item_group"]}, fields=['name','image', 'is_group', 'parent_item_group', 'custom_printer_ip'])
        response.append(item_group)
    print('\n\n\nget_item_groups_2 ===>',response)
    return response

@frappe.whitelist()
def get_sales_invoice_child_table(sales_invoice, sales_invoice_item):
    parent_doc = frappe.get_doc("Sales Invoice", sales_invoice)
    child_doc = frappe.get_doc(
        "Sales Invoice Item", {"parent": parent_doc.name, "name": sales_invoice_item}
    )
    return child_doc


# ─────────────────────────────────────────────────────────────
#  CREATE ORDER
# ─────────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def create_order(customer, items_json, total,
                 shipping_address=None, delivery_date=None,
                 delivery_slot=None, notes=None):
    print("===================================================================")
    print("Customer",customer)
    print("items_json",items_json)
    try:
        # ── Basic validation ──────────────────────────────────
        if not customer:
            return {"status": "error", "message": _("Customer is required")}

        if not items_json:
            return {"status": "error", "message": _("Items are required")}

        if not shipping_address:
            return {
                "status": "error",
                "message": _("Shipping address is required to place an order")
            }

        if not frappe.db.exists("Address", shipping_address):
            return {
                "status": "error",
                "message": _("Shipping address '{0}' does not exist").format(shipping_address)
            }

        if not frappe.db.exists("Customer", customer):
            return {
                "status": "error",
                "message": _("Customer '{0}' does not exist").format(customer)
            }

        # ── Parse items ───────────────────────────────────────
        try:
            items = frappe.parse_json(items_json)
            from frappe.utils import today

        except Exception as e:
            return {"status": "error",
                    "message": _("Invalid items JSON: {0}").format(str(e))}

        if not items:
            return {"status": "error", "message": _("No items provided")}

        # ── Delivery date defaults to tomorrow ────────────────
        from frappe.utils import add_days, getdate
        requested_delivery = getdate(delivery_date) if delivery_date else add_days(today(), 1)

        # ── Build Sales Order ─────────────────────────────────
        so = frappe.new_doc("Sales Order")
        so.customer              = customer
        so.transaction_date      = today()
        so.delivery_date         = requested_delivery
        so.shipping_address_name = shipping_address
        so.custom_delivery_slot  = delivery_slot or ""

        if notes:
            so.posa_notes = notes

        # ── Add items ─────────────────────────────────────────
        for item_data in items:
            item_code = item_data.get("item_code")
            qty       = flt(item_data.get("qty", 1))
            rate      = flt(item_data.get("rate", 0))

            if not frappe.db.exists("Item", item_code):
                frappe.log_error(
                    title="Invalid Item Code",
                    message=f"Item {item_code} does not exist – skipped"
                )
                continue

            settings = frappe.get_single("Online Store Settings")
            warehouse = settings.online_warehouse

            if not warehouse:
                frappe.throw("لم يتم تحديد مخزن الأونلاين")

            so.append("items", {
                "item_code":     item_code,
                "qty":           qty,
                "rate":          rate,
                "warehouse":     warehouse,
                "delivery_date": requested_delivery,

            })

        if not so.items:
            return {"status": "error", "message": _("No valid items found")}

        # ── Insert بدون workflow عشان نتجنب الـ validation error ──
        so.flags.ignore_links       = True
        so.flags.ignore_permissions = True
        so.insert(ignore_permissions=True)

        # ── بعد الـ insert، نحط الـ workflow_state مباشرة في الـ DB ──
        # بنتجنب بكده أي workflow engine validation
        frappe.db.set_value(
            "Sales Order",
            so.name,
            "workflow_state",
            "In Review",
            update_modified=False
        )

        frappe.db.commit()

        return {
            "status":      "success",
            "message":     _("Order created successfully"),
            "order_id":    so.name,
            "order_total": so.grand_total
        }

    except frappe.ValidationError as e:
        frappe.db.rollback()
        frappe.log_error(title="Order Creation Validation Error",
                         message=frappe.get_traceback())
        return {"status": "error",
                "message": _("Validation Error: {0}").format(str(e))}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Create Order Failed",
                         message=frappe.get_traceback())
        return {"status": "error",
                "message": _("Failed to create order: {0}").format(str(e))}


# ─────────────────────────────────────────────────────────────
#  UPDATE SHIPPING ADDRESS
#  • Only allowed while workflow_state == "In Review"
# ─────────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def update_order_address(order_name, shipping_address):
    """
    Update the shipping address on a Sales Order.
    Only permitted when the order is still in "In Review" state.

    Args:
        order_name       (str): Sales Order name
        shipping_address (str): New Address docname

    Returns:
        dict: { status, message }
    """
    try:
        if not order_name or not shipping_address:
            return {"status": "error",
                    "message": _("order_name and shipping_address are required")}

        # ── Fetch order ───────────────────────────────────────
        so = frappe.get_doc("Sales Order", order_name)

        # ── Check editable state ──────────────────────────────
        editable_states = ["In Review", "Draft"]
        current_state   = so.workflow_state or so.docstatus

        if current_state not in editable_states:
            state_label = _get_state_label(current_state)
            return {
                "status":  "error",
                "message": _(
                    "Cannot update address. Order is already '{0}'. "
                    "Only orders 'In Review' can be edited."
                ).format(state_label)
            }

        # ── Validate new address ──────────────────────────────
        if not frappe.db.exists("Address", shipping_address):
            return {"status": "error",
                    "message": _("Address '{0}' does not exist").format(shipping_address)}

        # ── Apply update ──────────────────────────────────────
        addr_doc = frappe.get_doc("Address", shipping_address)

        so.shipping_address_name    = shipping_address
        # so.custom_shipping_address_display = _build_address_display(addr_doc)
        so.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status":           "success",
            "message":          _("Shipping address updated successfully"),
            "new_address_name": addr_doc.address_title,
            "new_address":      {
                "address_line1": addr_doc.address_line1,
                "address_line2": addr_doc.address_line2,
                "city":          addr_doc.city,
                "state":         addr_doc.state,
                "country":       addr_doc.country,
            }
        }

    except frappe.DoesNotExistError:
        return {"status": "error",
                "message": _("Order '{0}' not found").format(order_name)}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Update Order Address Failed",
                         message=frappe.get_traceback())
        return {"status": "error",
                "message": _("Failed to update address: {0}").format(str(e))}


# ─────────────────────────────────────────────────────────────
#  CANCEL ORDER
#  • Only allowed while workflow_state == "In Review"
#  • After "Confirmed" → customer must contact support
# ─────────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def cancel_order(order_name, reason=None):
    """
    Cancel a Sales Order placed by the customer.
    Only permitted when the order is still in "In Review" state.

    Args:
        order_name (str): Sales Order name
        reason     (str): Optional cancellation reason

    Returns:
        dict: { status, message }
    """
    try:
        if not order_name:
            return {"status": "error", "message": _("order_name is required")}

        so = frappe.get_doc("Sales Order", order_name)

        # ── Only "In Review" orders can be self-cancelled ─────
        cancellable_states = ["In Review", "Draft"]
        current_state      = so.workflow_state or ""

        if current_state not in cancellable_states:
            state_label = _get_state_label(current_state)
            return {
                "status":  "error",
                "message": _(
                    "Cannot cancel. Order is already '{0}'. "
                    "Please contact support to cancel confirmed orders."
                ).format(state_label)
            }

        # ── Apply cancellation ────────────────────────────────
        try:
            so.workflow_state = "Cancelled"
        except Exception:
            pass

        if reason:
            existing_notes = so.posa_notes or ""
            so.posa_notes = f"{existing_notes}\n[إلغاء] {reason}".strip()

        so.save(ignore_permissions=True)
        frappe.db.commit()

        # Optional: log activity
        frappe.log_error(
            title="Order Cancelled by Customer",
            message=f"Order {order_name} cancelled. Reason: {reason or 'Not provided'}"
        )

        return {
            "status":  "success",
            "message": _("Order '{0}' has been cancelled successfully").format(order_name)
        }

    except frappe.DoesNotExistError:
        return {"status": "error",
                "message": _("Order '{0}' not found").format(order_name)}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Cancel Order Failed",
                         message=frappe.get_traceback())
        return {"status": "error",
                "message": _("Failed to cancel order: {0}").format(str(e))}


# ─────────────────────────────────────────────────────────────
#  GET CUSTOMER ORDERS  (with full address details)
# ─────────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_customer_orders(customer):
    """
    Fetch all orders for a customer, including items and shipping address details.

    Args:
        customer (str): Customer name

    Returns:
        dict: { status, orders, total_orders }
    """
    try:
        if not customer:
            return {"status": "error", "message": _("Customer is required")}

        orders = frappe.get_all(
            "Sales Order",
            filters={"customer": customer},
            fields=[
                "name",
                "transaction_date",
                "delivery_date",
                "grand_total",
                "net_total",
                "total_taxes_and_charges",
                "status",
                "workflow_state",
                "customer_name",
                "shipping_address_name",
                # "custom_shipping_address_display",
                # "custom_delivery_slot",
                "posa_notes",
                "total_qty",
            ],
            order_by="creation desc"
        )

        for order in orders:
            # ── Items ─────────────────────────────────────────
            order["items"] = frappe.get_all(
                "Sales Order Item",
                filters={"parent": order.name},
                fields=[
                    "item_code", "item_name", "qty",
                    "rate", "amount", "uom",
                    "description", "image"
                ],
                order_by="idx asc"
            )

            # ── Resolve shipping address ──────────────────────
            addr_name = order.get("shipping_address_name")
            if addr_name and frappe.db.exists("Address", addr_name):
                try:
                    addr = frappe.get_doc("Address", addr_name)
                    order["shipping_address"] = {
                        "address_title": addr.address_title,
                        "address_line1": addr.address_line1,
                        "address_line2": addr.address_line2,
                        "city":          addr.city,
                        "state":         addr.state,
                        "country":       addr.country,
                        "pincode":       addr.pincode,
                    }
                except Exception:
                    order["shipping_address"] = None
            else:
                order["shipping_address"] = None

            # ── Editable flag (convenience for frontend) ──────
            state = order.get("workflow_state") or order.get("status") or ""
            order["can_edit"]   = state in ("In Review", "Draft")
            order["can_cancel"] = state in ("In Review", "Draft")

        return {
            "status":       "success",
            "orders":       orders,
            "total_orders": len(orders)
        }

    except Exception as e:
        frappe.log_error(title="Get Customer Orders Failed",
                         message=frappe.get_traceback())
        return {"status": "error", "message": str(e)}


# ─────────────────────────────────────────────────────────────
#  GET CUSTOMER ADDRESSES
# ─────────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def get_customer_addresses(customer):
    """
    Return all addresses linked to a customer.

    Args:
        customer (str): Customer name

    Returns:
        dict: { status, addresses }
    """
    try:
        if not customer:
            return {"status": "error", "message": _("Customer is required")}

        # Get address names linked to customer via Dynamic Link
        linked = frappe.get_all(
            "Dynamic Link",
            filters={"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
            fields=["parent"]
        )

        address_names = [r.parent for r in linked]

        if not address_names:
            return {"status": "success", "addresses": []}

        addresses = []
        for addr_name in address_names:
            try:
                addr = frappe.get_doc("Address", addr_name)
                addresses.append({
                    "name":          addr.name,
                    "address_title": addr.address_title,
                    "address_line1": addr.address_line1,
                    "address_line2": addr.address_line2 or "",
                    "city":          addr.city,
                    "state":         addr.state or "",
                    "country":       addr.country,
                    "pincode":       addr.pincode or "",
                })
            except Exception:
                continue

        return {"status": "success", "addresses": addresses}

    except Exception as e:
        frappe.log_error(title="Get Customer Addresses Failed",
                         message=frappe.get_traceback())
        return {"status": "error", "message": str(e)}


# ─────────────────────────────────────────────────────────────
#  PRIVATE HELPERS
# ─────────────────────────────────────────────────────────────
def _build_address_display(addr_doc):
    """Build a single-line address string from an Address doc."""
    parts = [
        addr_doc.address_line1,
        addr_doc.address_line2,
        addr_doc.city,
        addr_doc.state,
        addr_doc.country,
    ]
    return "، ".join(p for p in parts if p)


def _get_state_label(state):
    labels = {
        "In Review":  "قيد المراجعة",
        "Confirmed":  "مؤكد",
        "Preparing":  "قيد التحضير",
        "Shipped":    "في الطريق",
        "Delivered":  "تم التوصيل",
        "Cancelled":  "ملغي",
    }
    return labels.get(state, state)


# ───────────────────────────────────
# ───────────────────────────────────

@frappe.whitelist(allow_guest=False)
def get_order_details(order_id: str) -> dict:
    """
    Returns full order details for the track order page.
    Only the customer who owns the order can fetch it.
    """
    print("====================================================================")
    print("====================================================================",order_id)
    # ── 1. Identify the logged-in customer ───────────────────────────────────
    customer = _get_customer_or_throw()

    # ── 2. Fetch the Sales Order ─────────────────────────────────────────────
    if not frappe.db.exists("Sales Order", {"name": order_id, "customer": customer}):
        frappe.throw(_("الطلب غير موجود أو لا تملك صلاحية الوصول إليه"), frappe.PermissionError)

    order = frappe.get_doc("Sales Order", order_id)

    # ── 3. Shipping address details ──────────────────────────────────────────
    shipping_address = None
    address_name = order.get("custom_shipping_address") or order.get("shipping_address_name")

    if address_name and frappe.db.exists("Address", address_name):
        addr = frappe.get_doc("Address", address_name)
        shipping_address = {
            "address_line1": addr.address_line1,
            "address_line2": addr.address_line2,
            "city":          addr.city,
            "state":         addr.state,
            "country":       addr.country,
            "pincode":       addr.pincode,
        }

    # ── 4. Build items list ──────────────────────────────────────────────────
    items = []
    for item in order.items:
        image = frappe.db.get_value("Item", item.item_code, "image")
        items.append({
            "item_code":  item.item_code,
            "item_name":  item.item_name,
            "qty":        item.qty,
            "uom":        item.uom,
            "rate":       item.rate,
            "amount":     item.amount,
            "image":      image or "",
        })

    # ── 5. Driver info (custom fields — adjust field names if different) ──────
    driver_name  = order.get("custom_driver_name")  or ""
    driver_phone = order.get("custom_driver_phone") or ""

    # ── 6. Return payload ────────────────────────────────────────────────────
    return {
        "name":                          order.name,
        "transaction_date":              str(order.transaction_date),
        "delivery_date":                 str(order.delivery_date) if order.delivery_date else None,
        "status":                        order.status,
        "workflow_state":                order.get("workflow_state") or "",

        # Totals
        "net_total":                     order.net_total,
        "total_taxes_and_charges":       order.total_taxes_and_charges,
        "grand_total":                   order.grand_total,

        # Address
        "custom_shipping_address_name":  order.get("custom_shipping_address_name") or address_name or "",
        "shipping_address":              shipping_address,

        # Driver
        "custom_driver_name":            driver_name,
        "custom_driver_phone":           driver_phone,

        # Items
        "items": items,
    }


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_customer_or_throw() -> str:
    """
    Returns the Customer linked to the current portal user.
    Throws 403 if the user is a guest or has no linked customer.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("يجب تسجيل الدخول أولاً"), frappe.AuthenticationError)

    customer = frappe.db.get_value("Customer", {"account_manager": frappe.session.user}, "name")

    # Fallback: check Contact → Customer link
    if not customer:
        contact = frappe.db.get_value("Contact", {"email_id": frappe.session.user}, "name")
        if contact:
            link = frappe.db.get_value(
                "Dynamic Link",
                {"parent": contact, "link_doctype": "Customer"},
                "link_name"
            )
            customer = link or None

    if not customer:
        frappe.throw(_("لم يتم ربط حسابك بعميل"), frappe.PermissionError)

    return customer
