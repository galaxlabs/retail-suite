import frappe
from frappe import _
from frappe.utils import now, nowdate
import qrcode
from io import BytesIO
import base64
from frappe.model.naming import NamingSeries, get_default_naming_series
from frappe.client import get_value
from frappe.utils.file_manager import save_file

@frappe.whitelist(allow_guest=True)
def generate_barcode_value(barcode_type):
    import random

    t = barcode_type.upper().replace("-", "").replace(" ", "")

    def gen_ean(length):
        base = [random.randint(0, 9) for _ in range(length - 1)]
        total = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(base))
        check = (10 - (total % 10)) % 10
        return ''.join(map(str, base)) + str(check)

    def gen_upc():
        base = [random.randint(0, 9) for _ in range(11)]
        total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(base))
        check = (10 - (total % 10)) % 10
        return ''.join(map(str, base)) + str(check)

    def gen_isbn13():
        prefix = [9, 7, 8]
        middle = [random.randint(0, 9) for _ in range(9)]
        base = prefix + middle
        total = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(base))
        check = (10 - (total % 10)) % 10
        return ''.join(map(str, base)) + str(check)

    def gen_isbn10():
        digits = [random.randint(0, 9) for _ in range(9)]
        total = sum((i + 1) * d for i, d in enumerate(digits))
        check = total % 11
        return ''.join(map(str, digits)) + ('X' if check == 10 else str(check))

    def gen_issn():
        digits = [random.randint(0, 9) for _ in range(7)]
        total = sum((8 - i) * d for i, d in enumerate(digits))
        check = (11 - (total % 11)) % 11
        return ''.join(map(str, digits)) + ('X' if check == 10 else str(check))

    def gen_pzn():
        digits = [random.randint(0, 9) for _ in range(7)]
        total = sum((i + 2) * d for i, d in enumerate(digits))
        check = total % 11
        if check == 10:
            return gen_pzn()
        return ''.join(map(str, digits)) + str(check)

    def gen_code():
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choices(chars, k=10))
    # def gen_qr():
    #     import uuid
    #     return str(uuid.uuid4())
    def gen_qr():
        import random, string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    generators = {
        'EAN':    lambda: gen_ean(13),
        'EAN13':  lambda: gen_ean(13),
        'EAN12':  lambda: gen_ean(12),
        'EAN8':   lambda: gen_ean(8),
        'JAN':    lambda: gen_ean(13),
        'UPCA':   gen_upc,
        'UPC':    gen_upc,
        'GS1':    lambda: gen_ean(13),
        'GTIN':   lambda: gen_ean(14),
        'ISBN':   gen_isbn13,
        'ISBN10': gen_isbn10,
        'ISBN13': gen_isbn13,
        'ISSN':   gen_issn,
        'PZN':    gen_pzn,
        'CODE39': gen_code,
        'CODE128':gen_code,
        'QR':      gen_qr,
    }

    gen = generators.get(t)
    if not gen:
        frappe.throw(f"Barcode type '{barcode_type}' is not supported")

    value = gen()
    return {'status': 'success', 'value': value}


@frappe.whitelist(allow_guest=True)
def get_barcode_types():
    try:
        meta = frappe.get_meta('Item Barcode')
        barcode_type_field = next(
            (f for f in meta.fields if f.fieldname == 'barcode_type'),
            None
        )
        if not barcode_type_field or not barcode_type_field.options:
            return {'status': 'success', 'data': []}

        types = [t.strip() for t in barcode_type_field.options.split('\n') if t.strip()]
        return {'status': 'success', 'data': types}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'get_barcode_types Error')
        return {'status': 'error', 'message': str(e), 'data': []}


@frappe.whitelist(allow_guest=True)
def get_default_item_series():
    series = get_default_naming_series("Item")
    return series


@frappe.whitelist(allow_guest=True)
def get_all_barcodes():
    """
    جيب كل المنتجات مع الـ barcodes بتاعتها + preview image
    FIX: استخدام frappe.db.sql مباشرة عشان نضمن إن الـ barcode field بييجي صح
    """
    try:
        # ✅ FIX 1: جيب الـ items مع item_group
        items = frappe.db.get_all(
            'Item',
            fields=['name', 'item_code', 'item_name', 'item_group', 'creation', "disabled", "image"],
            order_by='creation desc'
        )

        products_list = []

        for idx, item in enumerate(items, 1):
            # ✅ FIX 2: استخدام frappe.db.sql مباشرة — frappe.db.get_list
            # بيتجاهل أحياناً الـ barcode field لأنه اسمه نفس الـ doctype
            barcodes_raw = frappe.db.sql("""
                SELECT
                    ib.barcode,
                    ib.barcode_type,
                    ib.uom,
                    ib.name as barcode_name
                FROM `tabItem Barcode` ib
                WHERE ib.parent = %s
                  AND ib.parenttype = 'Item'
                ORDER BY ib.idx ASC
            """, item['name'], as_dict=True)

            barcode_list = []
            for bc in barcodes_raw:
                barcode_value = bc.get('barcode') or ''
                barcode_type  = bc.get('barcode_type') or ''

                # ✅ FIX 3: جيب الـ preview image لو الـ barcode فيه قيمة
                preview = ''
                if barcode_value:
                    preview = generate_barcode_image_base64(barcode_value, barcode_type)

                barcode_list.append({
                    'barcode':      barcode_value,
                    'barcode_type': barcode_type,
                    'uom':          bc.get('uom', ''),
                    'preview':      preview,
                })

            product_data = {
                'id':           idx,
                'sku':          item.get('item_code') or item.get('name', ''),
                'productName':  item.get('item_name') or item.get('name', ''),
                'productImage': item.get('image', ''),
                'productId':    item.get('name', ''),
                'item_group':   item.get('item_group') or '',
                'status':       'inactive' if item.get("disabled") else 'active',
                'creation':     str(item.get('creation', '')),
                'barcodes':     barcode_list,
            }
            products_list.append(product_data)

        return {
            'status': 'success',
            'data':   products_list,
            'total':  len(products_list)
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'get_all_barcodes Error')
        return {'status': 'error', 'message': str(e)}


def generate_barcode_image_base64(barcode_value, barcode_type=''):
    """
    ✅ Helper: يولّد barcode image كـ base64 string
    يرجع '' لو فشل (مش بيكسر الـ response كله)
    """
    try:
        import barcode as python_barcode
        from barcode.writer import ImageWriter

        # Map barcode type names to python-barcode class names
        type_map = {
            'EAN':    'ean13',
            'EAN13':  'ean13',
            'EAN8':   'ean8',
            'UPC-A':  'upca',
            'UPCA':   'upca',
            'CODE39': 'code39',
            'CODE128':'code128',
            'ISBN':   'isbn13',
            'ISBN13': 'isbn13',
            'ISBN10': 'isbn10',
            'ISSN':   'issn',
            'JAN':    'jan',
            'PZN':    'pzn',
        }

        # QR Code — مكتبة مختلفة
        if barcode_type.upper() in ('QR', 'QRCODE', 'QR CODE'):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=6,
                border=2,
            )
            qr.add_data(barcode_value)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()

        # Standard barcodes
        bc_type = type_map.get(barcode_type.upper(), 'code128')
        BarcodeClass = python_barcode.get_barcode_class(bc_type)

        buffer = BytesIO()
        bc = BarcodeClass(str(barcode_value), writer=ImageWriter())
        bc.write(buffer, options={
                'write_text':    True,
                'quiet_zone':    6,       # مسافة جانبية أكبر
                'font_size':     12,      # نص أوضح
                'text_distance': 5,       # ✅ المسافة بين آخر bar والنص (كانت 3 → 5)
                'module_height': 15.0,    # ارتفاع الـ bars
                'module_width':  0.38,    # عرض كل bar
                'background':    'white',
                'foreground':    'black',
        })
        buffer.seek(0)
        return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()

    except Exception as e:
        # ✅ مش بيكسر الـ response — بس يرجع string فاضي
        frappe.log_error(f"Barcode preview failed for '{barcode_value}' ({barcode_type}): {e}")
        return ''

@frappe.whitelist(allow_guest=True)
def get_item_barcodes(item_code):
    """
    جلب جميع الـ Barcodes للمنتج

    Args:
        item_code: كود المنتج

    Returns:
        list: قائمة الـ Barcodes
    """
    try:
        item_doc = frappe.get_doc('Item', item_code)

        # جلب الـ Child Table
        barcodes_list = []
        if item_doc.barcodes:
            for barcode in item_doc.barcodes:
                barcodes_list.append({
                    'idx': barcode.idx,  # رقم الصف
                    'barcode': barcode.barcode,
                    'barcode_type': barcode.barcode_type,
                    'item_code': item_code,
                    'item_name': item_doc.item_name,
                    'parent': item_code,
                    'parenttype': 'Item',
                    'parentfield': 'barcodes',
                })

        return {
            'status': 'success',
            'data': barcodes_list
        }

    except frappe.DoesNotExistError:
        return {
            'status': 'error',
            'message': _('Item not found')
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Item Barcodes Error')
        return {
            'status': 'error',
            'message': str(e)
        }

@frappe.whitelist(allow_guest=True)
def update_item_barcode(item_code, old_barcode, barcode_data):
    """
    Update a single barcode in an Item document.
    Looks up the row by the OLD barcode value (not row index).
    Returns an error if the new barcode already exists on another item.
    """
    try:
        if isinstance(barcode_data, str):
            barcode_data = frappe.parse_json(barcode_data)

        new_barcode_value = barcode_data.get('barcode', old_barcode)

        # ── Uniqueness check ──────────────────────────────────────
        # If the barcode value is actually changing, make sure it
        # doesn't already exist on ANY other item.
        if new_barcode_value != old_barcode:
            duplicate = frappe.db.exists(
                'Item Barcode',
                {
                    'barcode': new_barcode_value,
                    'parent': ['!=', item_code]
                }
            )
            if duplicate:
                return {
                    'status': 'error',
                    'message': _(
                        'Barcode {0} already exists on another item. '
                        'Barcode must be unique.'
                    ).format(new_barcode_value)
                }

        # ── Fetch & locate row ────────────────────────────────────
        item_doc = frappe.get_doc('Item', item_code)

        barcode_row = next(
            (row for row in item_doc.barcodes if row.barcode == old_barcode),
            None
        )

        if not barcode_row:
            return {
                'status': 'error',
                'message': _('Barcode {0} not found on item {1}').format(
                    old_barcode, item_code
                )
            }

        # ── Apply updates ─────────────────────────────────────────
        if 'barcode' in barcode_data:
            barcode_row.barcode = barcode_data['barcode']
        if 'barcode_type' in barcode_data:
            barcode_row.barcode_type = barcode_data['barcode_type']
        if 'uom' in barcode_data:
            barcode_row.uom = barcode_data['uom']

        item_doc.save()
        frappe.db.commit()

        return {
            'status': 'success',
            'message': _('Barcode updated successfully'),
            'data': {
                'barcode':      barcode_row.barcode,
                'barcode_type': barcode_row.barcode_type,
                'uom':          barcode_row.uom,
            }
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Update Item Barcode Error')
        return {
            'status': 'error',
            'message': str(e)
        }


@frappe.whitelist(allow_guest=True)
def add_item_barcode(barcode_data):
    """
    إضافة barcode جديد للمنتج

    Args:
        item_code: كود المنتج
        barcode_data: بيانات الـ Barcode الجديد

    Returns:
        dict: النتيجة
    """
    try:
        item_doc = frappe.get_doc('Item',barcode_data.get('item_code'))

        # إضافة صف جديد في الـ Child Table
        new_barcode = {
            'barcode': barcode_data.get('value'),
            'barcode_type': barcode_data.get('type', 'CODE128'),
            'posa_uom': barcode_data.get('posa_uom'),
            'uom': barcode_data.get('posa_uom'),
        }

        item_doc.append('barcodes', new_barcode)
        item_doc.save()

        # جلب الـ row الجديد
        new_row = item_doc.barcodes[-1]
        if new_row:
            # image = generate_barcode_img(new_row.barcode, new_row.barcode_type)
            preview = generate_barcode_image_base64(barcode_value, barcode_type)
            if preview:
                    return {
                        'status': 'success',
                        'message': _('Barcode added successfully'),
                        'data': {
                            'idx': new_row.idx,
                            'barcode': new_row.barcode,
                            'barcode_type': new_row.barcode_type,
                            'posa_uom': new_row.posa_uom,
                            'uom': new_row.uom,
                            'image': preview
                        }
                    }
            else:
                return {
                        'status': 'error',
                        'message': _('Barcode failed generated'),
                        'data': {}
                    }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Add Item Barcode Error')
        return {
            'status': 'error',
            'message': str(e)
        }


@frappe.whitelist(allow_guest=True)
def delete_item_barcode(item_code, barcode):
    """
    حذف barcode من المنتج

    Args:
        item_code: كود المنتج
        barcode: قيمة الـ barcode المراد حذفه

    Returns:
        dict: النتيجة
    """
    try:
        item_doc = frappe.get_doc('Item', item_code)

        # البحث عن الصفوف التي تحتوي على نفس قيمة barcode
        rows_to_remove = [
            idx for idx, row in enumerate(item_doc.barcodes)
            if row.barcode == barcode
        ]

        if not rows_to_remove:
            return {
                'status': 'error',
                'message': _('Barcode not found')
            }

        # حذف من الخلف للأمام لتجنب مشاكل الـ indexing
        for idx in reversed(rows_to_remove):
            del item_doc.barcodes[idx]

        item_doc.save()

        return {
            'status': 'success',
            'message': _('Barcode deleted successfully')
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Delete Item Barcode Error')
        return {
            'status': 'error',
            'message': str(e)
        }

@frappe.whitelist(allow_guest=True)
def bulk_update_item_barcodes(item_code, barcodes_data):
    """
    تحديث عدة barcodes في نفس الوقت

    Args:
        item_code: كود المنتج
        barcodes_data: قائمة البيانات الجديدة

    Returns:
        dict: النتيجة
    """
    try:
        item_doc = frappe.get_doc('Item', item_code)

        results = {
            'success': [],
            'failed': []
        }

        for barcode_update in barcodes_data:
            try:
                row_index = barcode_update.get('idx')
                barcode_row = None

                for row in item_doc.barcodes:
                    if row.idx == row_index:
                        barcode_row = row
                        break

                if not barcode_row:
                    results['failed'].append({
                        'idx': row_index,
                        'error': 'Row not found'
                    })
                    continue

                # تحديث الحقول
                for key, value in barcode_update.items():
                    if key != 'idx' and hasattr(barcode_row, key):
                        setattr(barcode_row, key, value)

                results['success'].append({
                    'idx': barcode_row.idx,
                    'barcode': barcode_row.barcode,
                    'barcode_type': barcode_row.barcode_type
                })

            except Exception as e:
                results['failed'].append({
                    'idx': barcode_update.get('idx'),
                    'error': str(e)
                })

        # حفظ المنتج مرة واحدة
        item_doc.save()

        return {
            'status': 'success',
            'successful_updates': len(results['success']),
            'failed_updates': len(results['failed']),
            'data': results
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Bulk Update Item Barcodes Error')
        return {
            'status': 'error',
            'message': str(e)
        }

def generate_barcode_svg(barcode_value, barcode_type):
    """
    توليد SVG للـ barcode
    """
    try:
        if barcode_type == 'QR':
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(barcode_value)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
        else:
            # يمكن تحسين هذا لأنواع أخرى
            img = qrcode.QRCode()
            img.add_data(barcode_value)
            img.make()
            img = img.make_image()

        # تحويل للـ base64 SVG (مبسط)
        svg = f'<svg width="100" height="100"><text x="10" y="50">{barcode_value}</text></svg>'
        return svg

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'generate_barcode_svg Error')
        return '<svg></svg>'



@frappe.whitelist(allow_guest=True)
def generate_barcode_img(barcode_value, barcode_type):
    try:
        if not barcode_value:
            return {
                'status': 'error',
                'message': 'Barcode value is empty',
                'data': ''
            }

        barcode_type_clean = (barcode_type or '').upper().strip()

        # ✅ QR
        if barcode_type_clean in ('QR', 'QRCODE'):
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(barcode_value)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format="PNG")

            base64_img = base64.b64encode(buffer.getvalue()).decode()

            return {
                'status': 'success',
                'data': f'data:image/png;base64,{base64_img}'
            }

        # ✅ Barcode
        preview = generate_barcode_image_base64(barcode_value, barcode_type_clean)

        return {
            'status': 'success',
            'data': preview
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'generate_barcode_img Error')
        return {
            'status': 'error',
            'message': str(e),
            'data': ''
        }

@frappe.whitelist(allow_guest=True)
def get_unit_of_measures():
    return frappe.get_list("UOM","name")

@frappe.whitelist(allow_guest=True)
def get_item_category():
    return frappe.get_list("Item Group","name")



def clear_posa_cache():
    """مسح جميع cache keys المتعلقة بـ POS Items"""
    try:
        # الطريقة الصحيحة للوصول لـ Redis client
        redis_client = frappe.cache()

        # البحث عن جميع keys المتعلقة بـ get_items
        keys = redis_client.keys("*__get_items*") or []

        if keys:
            # حذف جميع الـ keys
            redis_client.delete(*keys)
            frappe.logger().info(f"Cleared {len(keys)} cache keys")

        # أيضاً مسح Item cache
        frappe.cache().delete_value("Item")

    except Exception as e:
        frappe.logger().warning(f"Cache clearing error: {e}")


@frappe.whitelist(allow_guest=True)
def delete_item(item_code):
    """
    حذف Item وتنظيف الـ cache
    """
    try:
        # التحقق من وجود الـ Item
        if not frappe.db.exists("Item", item_code):
            return {"status": "error", "message": f"Item {item_code} does not exist"}

        # حذف الـ Item بشكل صحيح عبر الـ ORM
        item_doc = frappe.get_doc("Item", item_code)
        item_doc.delete(ignore_permissions=True)

        # أو استخدم:
        # frappe.delete_doc("Item", item_code, ignore_permissions=True)

        frappe.db.commit()

        # مسح الـ cache بعد الحذف مباشرة
        clear_posa_cache()

        return {
            "status": "success",
            "message": f"Item {item_code} deleted successfully"
        }

    except frappe.DoesNotExistError:
        return {"status": "error", "message": f"Item {item_code} not found"}
    except Exception as e:
        frappe.logger().error(f"Error deleting item: {e}")
        return {"status": "error", "message": str(e)}

def handle_item_image(image_data, item_code):
    """
    معالجة رفع الصورة وإنشاء File document
    Returns: مسار الملف أو None
    """
    try:
        # إذا كانت الصورة بالفعل مسار (مثل /files/...)
        if isinstance(image_data, str) and image_data.startswith('/files/'):
            return image_data

        # إذا كانت base64
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            # فك تشفير base64
            header, encoded = image_data.split(',', 1)
            image_bytes = base64.b64decode(encoded)

            # استخراج نوع الملف من header
            file_type = header.split(';')[0].replace('data:image/', '')
            if file_type == 'jpeg':
                file_type = 'jpg'

            file_name = f"{item_code}.{file_type}"

            # استخدام save_file من frappe لحفظ الملف بشكل صحيح
            file_doc = save_file(
                fname=file_name,
                content=image_bytes,
                dt="Item",
                dn=item_code,
                is_private=0
            )

            print(f"\n\nFile saved: {file_doc.file_url}")
            return file_doc.file_url

        return None

    except Exception as e:
        frappe.logger().error(f"Error handling image: {e}")
        print(f"\n\nError in image upload: {e}")
        return None


def clear_posa_cache():
    """
    مسح cache POS
    """
    try:
        frappe.cache().delete_key("posa_items")
        frappe.cache().delete_key("posa_categories")
    except:
        pass


@frappe.whitelist(allow_guest=True)
def update_item(item_code, item_data):
    """
    تحديث Item وتنظيف الـ cache
    """
    try:
        # FIX 1: Parse JSON if it's a string
        if isinstance(item_data, str):
            item_data = frappe.parse_json(item_data)

        # FIX 2: Get the Item document
        item_doc = frappe.get_doc("Item", item_code)

        print("==================== Update Item =====================")

        # FIX 3: Handle image separately if provided
        image_url = None
        if "image" in item_data and item_data["image"]:
            image_url = handle_item_image(item_data["image"], item_code)
            if image_url:
                item_data["image"] = image_url

        # FIX 4: Update fields - only update if they exist and are not empty
        for key, value in item_data.items():
            # Skip if value is None or empty string (unless it's intentional)
            if value is None or value == "":
                continue

            # Check if attribute exists in the doctype
            if hasattr(item_doc, key) or key in item_doc.fields_dict:
                setattr(item_doc, key, value)
            else:
                frappe.logger().warning(f"Field {key} does not exist in Item doctype")

        # FIX 5: Save the document
        item_doc.save(ignore_permissions=True)
        frappe.db.commit()

        # FIX 6: Clear cache after successful save
        clear_posa_cache()

        # FIX 7: Return the complete document data
        return {
            "status": "success",
            "message": f"Item {item_code} updated successfully",
            "data": item_doc.as_dict()
        }

    except frappe.DoesNotExistError:
        frappe.logger().error(f"Item {item_code} not found")
        return {
            "status": "error",
            "message": f"Item {item_code} not found"
        }

    except frappe.ValidationError as e:
        frappe.logger().error(f"Validation error updating item: {e}")
        return {
            "status": "error",
            "message": f"Validation error: {str(e)}"
        }

    except Exception as e:
        frappe.logger().error(f"Error updating item: {e}")
        frappe.db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }


from frappe.model.document import Document
from datetime import datetime


def before_insert(doc,method):
    """يعمل قبل الحفظ الأول فقط"""
    if doc.naming_series:
            generate_item_code(doc)

def before_save(doc,method):
    """يعمل قبل الحفظ الأول فقط"""
    if doc.naming_series:
        generate_item_code(doc)

from frappe.model.naming import make_autoname
def generate_item_code():
    year = nowdate().split('-')[0]

    # دور على آخر رقم موجود فعلاً في الـ Items
    last_item = frappe.db.sql("""
        SELECT name FROM `tabItem`
        WHERE name REGEXP %s
        ORDER BY CAST(SUBSTRING_INDEX(name, '-', -1) AS UNSIGNED) DESC
        LIMIT 1
    """, (f'^STO-ITEM-{year}-[0-9]+$',), as_dict=True)

    if last_item:
        try:
            last_num = int(last_item[0]['name'].split('-')[-1])
            next_num = last_num + 1
        except (ValueError, IndexError):
            next_num = 1
    else:
        next_num = 1

    return f'STO-ITEM-{year}-{str(next_num).zfill(5)}'

@frappe.whitelist(allow_guest=True)
def add_item(item_data):
    try:
        if isinstance(item_data, str):
            item_data = frappe.parse_json(item_data)

        required_fields = ["item_name", "item_group"]
        for field in required_fields:
            if field not in item_data:
                return {"status": "error", "message": f"Required field missing: {field}"}

        # retry لو في race condition
        max_retries = 5
        item_code = None

        for attempt in range(max_retries):
            item_code = generate_item_code()

            # لو مش موجود استخدمه
            if not frappe.db.exists("Item", item_code):
                break

            # لو موجود جرب التالي
            if attempt == max_retries - 1:
                return {"status": "error", "message": "Could not generate unique item code"}

        # معالجة الصورة
        image_path = None
        if item_data.get("image"):
            image_path = handle_item_image(item_data.get("image"), item_code)
            item_data["image"] = image_path if image_path else item_data.pop("image", None)

        # شيل naming_series عشان Frappe متولدش كود تاني
        item_data.pop("naming_series", None)

        item_doc = frappe.get_doc({
            "doctype": "Item",
            **item_data,
            "item_code": item_code,
            "has_serial_no": 0,
        })

        item_doc.name = item_code
        item_doc.flags.name_set = True

        item_doc.insert(ignore_permissions=True)
        # frappe.db.commit()
        frappe.db.rollback()

        clear_posa_cache()
        return {
            "status": "success",
            "message": f"Item {item_doc.item_code} added successfully",
            "item_code": item_doc.item_code,
            "item": item_doc.as_dict(),
            "image": image_path
        }

    except frappe.DuplicateEntryError:
        return {"status": "error", "message": "Item already exists"}
    except frappe.ValidationError as e:
        return {"status": "error", "message": f"Validation error: {str(e)}"}
    except Exception as e:
        frappe.logger().error(f"Error adding item: {e}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_inventory_balance():
    """
    Returns a flat list of items × warehouses with actual_qty,
    rate, item_group, and image — ready for the Inventory Balance page.
    """
    try:
        # ── 1. Stock Ledger balance per item × warehouse ──────────
        bin_rows = frappe.db.sql(
            """
            SELECT
                b.item_code,
                b.warehouse,
                b.actual_qty
            FROM `tabBin` b
            WHERE b.actual_qty != 0
            ORDER BY b.item_code, b.warehouse
            """,
            as_dict=True,
        )

        if not bin_rows:
            return {"status": "success", "data": [], "message": "No stock data found"}

        # ── 2. Pull item master data in one query ─────────────────
        item_codes = list({row["item_code"] for row in bin_rows})

        item_rows = frappe.db.sql(
            """
            SELECT
                i.item_code,
                i.item_name,
                i.item_group,
                i.description,
                i.image,
                ip.price_list_rate AS rate
            FROM `tabItem` i
            LEFT JOIN `tabItem Price` ip
                ON  ip.item_code   = i.item_code
                AND ip.selling      = 1
                AND ip.price_list   = 'Standard Selling'
            WHERE i.item_code IN %(item_codes)s
              AND i.disabled = 0
            """,
            {"item_codes": item_codes},
            as_dict=True,
        )

        # index by item_code for fast lookup
        item_map = {row["item_code"]: row for row in item_rows}

        # ── 3. Merge bin + item data ──────────────────────────────
        result = []
        for bin_row in bin_rows:
            item = item_map.get(bin_row["item_code"])
            if not item:
                continue  # skip disabled / deleted items

            result.append(
                {
                    "item_code":   item["item_code"],
                    "item_name":   item["item_name"]   or item["item_code"],
                    "item_group":  item["item_group"]  or "",
                    "description": item["description"] or "",
                    "image":       item["image"]        or "",
                    "rate":        float(item["rate"] or 0),
                    "warehouse":   bin_row["warehouse"],
                    "actual_qty":  float(bin_row["actual_qty"]),
                }
            )

        return {
            "status":  "success",
            "data":    result,
            "message": f"{len(result)} records fetched successfully",
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_inventory_balance Error")
        return {"status": "error", "data": [], "message": str(e)}
