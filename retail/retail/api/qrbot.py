
# POST API endpoint
# URL: /api/method/retail.retail.api.qrbot.receive_barcode
# EX : http://192.168.8.5:8000/api/method/retail.retail.api.qrbot.receive_barcode
# HTTP Body: content={code}
# retail/retail/api/qrbot.py

import frappe
import json
from frappe import _

# في retail/api/qrbot.py

@frappe.whitelist(allow_guest=True)
def get_latest_barcode():
    """
    احصل على آخر باركود اتقبل
    """
    try:
        # احصل من Redis cache (أسرع)
        barcode = frappe.cache().get_value("qrbot:latest_barcode")

        return {
            "status": "success",
            "barcode": barcode,
            "timestamp": frappe.utils.now()
        }
    except:
        return {
            "status": "error",
            "barcode": None
        }

@frappe.whitelist(allow_guest=True)
def receive_barcode():
    """استقبل من الآيفون"""
    try:
        barcode = None
        if frappe.local.form_dict:
            barcode = frappe.form_dict.get("content")
        else:
            try:
                data = json.loads(frappe.local.request.get_data())
                barcode = data.get("barcode") or data.get("content")
            except:
                pass

        if not barcode:
            return {"status": "error", "message": "لا توجد باركود"}

        # ✅ احفظ في cache
        frappe.cache().set_value("qrbot:latest_barcode", barcode, expires_in_sec=3600)

        # ✅ بعت real-time (إذا Socket.IO اشتغلت)
        try:
            frappe.publish_realtime(
                event="qrbot:barcode_received",
                message={"barcode": barcode, "timestamp": frappe.utils.now()},
                user=None
            )
        except:
            pass  # لا تقلق إذا Socket.IO ما اشتغلت

        frappe.logger().info(f"✅ باركود: {barcode}")

        return {
            "status": "success",
            "message": "تم استقبال الباركود",
            "barcode": barcode
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "receive_barcode")
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def process_barcode(barcode):
    """
    معالجة الباركود وتخزينه في Doctype
    الاستخدام: /api/method/retail.retail.api.qrbot.process_barcode?barcode=123456789
    """
    try:
        if not barcode:
            return {
                "status": "error",
                "message": "الباركود مفقود"
            }

        # تحقق من وجود منتج بهذا الباركود
        item = frappe.db.get_value(
            "Item",
            filters={"barcode": barcode},
            fieldname=["name", "item_name", "item_code"]
        )

        if not item:
            return {
                "status": "error",
                "message": f"لم يتم العثور على منتج بهذا الباركود: {barcode}",
                "barcode": barcode
            }

        # إنشاء Scanned Barcode document
        doc = frappe.get_doc({
            "doctype": "Scanned Barcode",
            "barcode_value": barcode,
            "item_code": item[0],
            "item_name": item[1],
            "scan_time": frappe.utils.now()
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        frappe.logger().info(f"✅ تم معالجة الباركود: {barcode} - {item[1]}")

        return {
            "status": "success",
            "message": f"تم تسجيل المنتج: {item[1]}",
            "barcode": barcode,
            "item_code": item[0],
            "item_name": item[1]
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "process_barcode")
        return {
            "status": "error",
            "message": f"خطأ في معالجة الباركود: {str(e)}"
        }


@frappe.whitelist(allow_guest=True)
def get_scanned_barcodes(limit=50):
    """
    الحصول على قائمة الباركودات المسحوبة
    الاستخدام: /api/method/retail.retail.api.qrbot.get_scanned_barcodes?limit=50
    """
    try:
        barcodes = frappe.get_list(
            "Scanned Barcode",
            fields=["name", "barcode_value", "item_code", "item_name", "scan_time"],
            order_by="scan_time desc",
            limit_page_length=limit
        )

        return {
            "status": "success",
            "count": len(barcodes),
            "barcodes": barcodes
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_scanned_barcodes")
        return {
            "status": "error",
            "message": str(e)
        }
