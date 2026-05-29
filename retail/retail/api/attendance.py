import frappe
from frappe import _
from frappe.utils import get_datetime
from hrms.hr.doctype.attendance.attendance import mark_attendance, mark_bulk_attendance
from hrms.hr.doctype.employee_checkin.employee_checkin import mark_attendance_and_link_log, skip_attendance_in_checkins
import json

@frappe.whitelist(allow_guest =True)
def get_checkins(company=None):
    filters = {"company":company} if company else {}
    checkins = frappe.get_all("Employee Checkin", filters=filters, fields=["*"])

    if len(checkins) > 0:
        frappe.response["status"] = "success"
        frappe.response["http_status_code"] = 200
        frappe.response["message"] = "Employees Checkin fetched successfully"
        data = [ch for ch in checkins ]
        frappe.response["data"] = data
    elif len(checkins) == 0:
        frappe.response["status"] = "success"
        frappe.response["http_status_code"] = 200
        frappe.response["message"] = "No Employee Checkin found"
    else:
        frappe.response["status"] = "error"
        frappe.response["http_status_code"] = 404
        frappe.response["message"] = "Error Fetch Employee Checkin"
        frappe.response["data"] = []
    print("frappe.response:", frappe.response, type(frappe.response))



@frappe.whitelist(allow_guest=True)
def get_checkins_for_attendance(employee, attendance_date):
	"""
	الحصول على سجلات الدخول والخروج (Employee Checkin) للموظف في تاريخ معين
	"""

	try:
		checkins = frappe.get_list(
			"Employee Checkin",
			filters={
				"employee": employee,
				"creation": ["like", f"{attendance_date}%"]
			},
			fields=["name", "employee", "log_type", "time", "skip_auto_attendance", "attendance"],
			order_by="time asc"
		)

		return {
			"success": True,
			"count": len(checkins),
			"data": checkins
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		frappe.throw(str(e))

@frappe.whitelist(allow_guest=True)
def get_monthly_attendance_summary(employee, month, year):
	"""
	الحصول على ملخص الحضور الشهري
	"""

	try:
		from datetime import datetime

		from_date = f"{year}-{str(month).zfill(2)}-01"

		if month == 12:
			to_date = f"{year + 1}-01-01"
		else:
			to_date = f"{year}-{str(month + 1).zfill(2)}-01"

		to_date = (datetime.strptime(to_date, "%Y-%m-%d") - frappe.utils.timedelta(days=1)).strftime("%Y-%m-%d")

		records = frappe.get_list(
			"Attendance",
			filters={
				"employee": employee,
				"attendance_date": ["between", [from_date, to_date]],
				"docstatus": 1
			},
			fields=["status", "working_hours"]
		)

		summary = {
			"employee": employee,
			"month": month,
			"year": year,
			"total_days": len(records),
			"present": sum(1 for r in records if r.status == "Present"),
			"absent": sum(1 for r in records if r.status == "Absent"),
			"half_day": sum(1 for r in records if r.status == "Half Day"),
			"total_working_hours": sum(r.working_hours or 0 for r in records)
		}

		return {
			"success": True,
			"data": summary
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		frappe.throw(str(e))


@frappe.whitelist(allow_guest=True)
def create_attendance(
employee,
attendance_date,
status,
shift=None,
leave_type=None,
late_entry=False,
early_exit=False
):
    try:

        if not frappe.db.exists("Employee", employee):
            frappe.throw(_("الموظف {0} غير موجود").format(employee))

        name = mark_attendance(
            employee=employee,
            attendance_date=attendance_date,
            status=status,
            shift=shift,
            leave_type=leave_type,
            late_entry=late_entry,
            early_exit=early_exit
        )

        if not name:
            return {
                "status": "failed",
                "message": _("Failed to mark attendance for employee {0} on {1}").format(employee, attendance_date)
            }

        return {
            "status": "success",
            "message": _("Attendance marked successfully for employee {0} on {1}").format(employee, attendance_date),
            "attendance_id": name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist(allow_guest=True)
def bulk_mark_attendance(data):
    """
    وظيفة لتسجيل الحضور لعدة أيام للموظف الواحد

    Parameters:
    - data: JSON object يحتوي على:
      {
        "employee": "EMP001",
        "status": "Present",
        "unmarked_days": ["2024-01-15", "2024-01-16", "2024-01-17"],
        "shift": "Morning" (اختياري)
      }
    """

    try:
        # تحويل البيانات إذا كانت string
        if isinstance(data, str):
            data = json.loads(data)

        data = frappe._dict(data)

        # التحقق من البيانات الأساسية
        if not data.employee:
            frappe.throw(_("يجب تحديد الموظف"))

        if not data.status:
            frappe.throw(_("يجب تحديد الحالة"))

        if not data.unmarked_days or len(data.unmarked_days) == 0:
            frappe.throw(_("يجب تحديد تاريخ واحد على الأقل"))

        # التحقق من وجود الموظف
        if not frappe.db.exists("Employee", data.employee):
            frappe.throw(_("الموظف {0} غير موجود").format(data.employee))

        # استدعاء الدالة الأصلية
        result = mark_bulk_attendance(data)

        frappe.msgprint(
            _("تم تسجيل الحضور لـ {0} أيام بنجاح").format(len(data.unmarked_days)),
            alert=True
        )

        return result

    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        frappe.throw(str(e))


@frappe.whitelist(allow_guest=True)
def get_employee_attendance_history(employee=None, from_date=None, to_date=None, limit=30):
    """
    الحصول على سجل الحضور للموظف

    Parameters:
    - employee: رقم الموظف
    - from_date: من تاريخ (اختياري)
    - to_date: إلى تاريخ (اختياري)
    - limit: عدد السجلات المطلوبة
    """

    try:
        filters = {}
        if employee:
            filters = {"employee": employee}

        if from_date and to_date:
            filters["attendance_date"] = ["between", [from_date, to_date]]

        attendance_records = frappe.get_list(
            "Attendance",
            filters=filters,
            fields=["*"],
            order_by="attendance_date desc",
            limit_page_length=limit
        )

        return {
            "success": True,
            "count": len(attendance_records),
            "data": attendance_records
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        frappe.throw(str(e))


@frappe.whitelist(allow_guest=True)
def get_monthly_attendance_summary(employee, month, year):
    """
    الحصول على ملخص الحضور الشهري

    Parameters:
    - employee: رقم الموظف
    - month: الشهر (1-12)
    - year: السنة

    Returns: إحصائيات (حاضر، غائب، نصف يوم، إجازة)
    """

    try:
        from datetime import datetime

        # تحديد فترة الشهر
        from_date = f"{year}-{str(month).zfill(2)}-01"

        if month == 12:
            to_date = f"{year + 1}-01-01"
        else:
            to_date = f"{year}-{str(month + 1).zfill(2)}-01"

        to_date = (datetime.strptime(to_date, "%Y-%m-%d") - frappe.utils.timedelta(days=1)).strftime("%Y-%m-%d")

        # الحصول على سجلات الحضور
        records = frappe.get_list(
            "Attendance",
            filters={
                "employee": employee,
                "attendance_date": ["between", [from_date, to_date]],
                "docstatus": 1  # Submitted only
            },
            fields=["status"]
        )

        # حساب الإحصائيات
        summary = {
            "employee": employee,
            "month": month,
            "year": year,
            "total_days": len(records),
            "present": sum(1 for r in records if r.status == "Present"),
            "absent": sum(1 for r in records if r.status == "Absent"),
            "half_day": sum(1 for r in records if r.status == "Half Day"),
            "work_from_home": sum(1 for r in records if r.status == "Work From Home"),
            "on_leave": sum(1 for r in records if r.status == "On Leave")
        }

        return {
            "success": True,
            "data": summary
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        frappe.throw(str(e))


@frappe.whitelist(allow_guest=True)
def check_attendance_exists(employee, attendance_date):
    """
    التحقق من وجود سجل حضور للموظف في تاريخ معين
    """

    try:
        exists = frappe.db.exists("Attendance", {
            "employee": employee,
            "attendance_date": attendance_date
        })

        return {
            "success": True,
            "exists": bool(exists),
            "attendance_id": exists if exists else None
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        frappe.throw(str(e))


@frappe.whitelist(allow_guest=True)
def cancel_and_delete_attendance(name):
    doc = frappe.get_doc("Attendance", name)

    if doc.docstatus == 1:
        doc.cancel()

    frappe.delete_doc("Attendance", name)


@frappe.whitelist(allow_guest=True)
def bulk_cancel_and_delete_attendance(attendance_ids):
    """
    Cancel and delete one or multiple Attendance records.
    attendance_ids can be:
    - list
    - JSON string
    """

    if isinstance(attendance_ids, str):
        attendance_ids = frappe.parse_json(attendance_ids)

    if not attendance_ids:
        frappe.throw("No attendance records provided")

    deleted = []
    failed = []

    for name in attendance_ids:
        try:
            doc = frappe.get_doc("Attendance", name)

            # لو Submitted → Cancel
            if doc.docstatus == 1:
                doc.cancel()

            # Delete
            frappe.delete_doc(
                "Attendance",
                name,
                force=True,       # مهم
                ignore_permissions=True
            )

            deleted.append(name)

        except Exception as e:
            failed.append({
                "name": name,
                "error": str(e)
            })
            frappe.log_error(
                frappe.get_traceback(),
                f"Failed to delete Attendance {name}"
            )

    return {
        "status": "success" if not failed else "partial",
        "deleted": deleted,
        "failed": failed,
        "message": f"Deleted {len(deleted)} attendance record(s). Failed: {len(failed)}"
    }

@frappe.whitelist(allow_guest=True)
def edit_attendance(attendance_data):
    try:
        # If attendance_data comes as JSON string
        if isinstance(attendance_data, str):
            attendance_data = frappe.parse_json(attendance_data)

        # Example: fetch existing Attendance
        attendance = frappe.get_doc("Attendance", attendance_data.get("name"))

        # Update fields dynamically
        for key, value in attendance_data.items():
            if key != "name":
                attendance.set(key, value)

        attendance.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Attendance record updated successfully",
            "data": attendance.as_dict()
        }

    except Exception as e:
        frappe.log_error(
            title="Edit Attendance Error",
            message=frappe.get_traceback()
        )

        return {
            "status": "error",
            "message": str(e) or "Unknown error occurred"
        }
