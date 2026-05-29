import frappe
from frappe.utils import today, date_diff
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
# ApI GET One Or List Of Department
@frappe.whitelist(allow_guest =True)
def get_departments(company=None):
    filters = {"company":company} if company else {}
    departments = frappe.get_all("Department", filters=filters, fields=["name", "department_name", "company"])
     # Exclude "All Departments"
    if departments:
        frappe.response["status"] = "success"
        frappe.response["http_status_code"] = 200
        frappe.response["message"] = "Departments fetched successfully"
        data = [dept for dept in departments if dept["department_name"] != "All Departments"]
        frappe.response["data"] = data

    else:
        frappe.response["status"] = "error"
        frappe.response["http_status_code"] = 404
        frappe.response["message"] = "No departments found"
        frappe.response["data"] = []


# API create department
#  Also increase No. Departments in company
@frappe.whitelist(allow_guest=True)
def create_department():
    data = frappe.request.get_json()
    department_name = data.get("department_name")
    if not department_name:
        frappe.response["status"] = "error"
        frappe.response["http_status_code"] = 400
        frappe.response["message"] = "Department name is required"
        frappe.response["exc_type"] = "ValidationError"
        return
     # Check for duplicate department name
    department_exists = frappe.db.exists("Department", {"department_name": department_name})
    if department_exists:
     # Check for duplicate department name
        frappe.response["status"] = "error"
        frappe.response["http_status_code"] = 409
        frappe.response["message"] = f"Department '{department_name}' already exists. Please use a different name."
        frappe.response["exc_type"] = "duplicate"
        return
    company = data.get("company")
     # Check if company exists
    if not company:
        frappe.response["status"] = "error"
        frappe.response["http_status_code"] = 404
        frappe.response["message"] = "Company is Fucken required"
        frappe.response["exc_type"] = "ValidationError"
        return

    if company:
        company_exists = frappe.db.exists("Company", {"name": company})
        if not company_exists:
            frappe.response["status"] = "error"
            frappe.response["http_status_code"] = 404
            frappe.response["message"] = f"Company '{company}' does not exist."
            frappe.response["exc_type"] = "ValidationError"
            return
     # Create Department
    try:
        doc = frappe.get_doc({
            "doctype": "Department",
            "department_name": department_name,
            "company": company
        })
        doc.insert(ignore_permissions=True)
        try:
            if company:
                company_doc = frappe.get_doc("Company", company)
                if hasattr(company_doc, "custom_number_of_departments"):
                    company_doc.custom_number_of_departments = (company_doc.custom_number_of_departments or 0) + 1
                    company_doc.save(ignore_permissions=True)
        except Exception as count_error:
            frappe.log_error(
                f"Failed to  count for Department {company}: {str(count_error)}",
                "Department Count Update Error"
            )
            return {
                "success":False,
                "message": f"Department Count Update Error"
            }
        frappe.db.commit()
        return {
            "message": f"Department '{department_name}' created successfully.", "success": True
        }
    except frappe.DuplicateEntryError as e:
        frappe.log_error(frappe.get_traceback(), "Create Department Duplicate Error")
        frappe.response["http_status_code"] = 409
        return {
            "error": f"Department '{department_name}' already exists. Please use a different name.",
            "success": False,
            "error_type": "duplicate"
        }
    except Exception as inner_error:
        # Rollback transaction on any error
        frappe.db.rollback()
        raise inner_error

# API Delete Department
@frappe.whitelist(allow_guest=True)
def delete_department(department_name):
    """Update Company counts when  Department is deleted
         Delelte All Employee For this Department
    """
    department_exists = frappe.db.exists("Department", {"department_name": department_name})
    if not department_exists:
        return {
            "status": "error",
            "message": f"Department '{department_name}' does not exist."
        }

     # Get Department Document
    department = frappe.get_doc("Department",{"department_name":department_name})
    company = department.company

    employees = frappe.get_all("Employee", filters={"department": department.name}, pluck="name")
    for emp in employees:
        frappe.delete_doc("Employee", emp, force=1)


    if company:
        company_doc = frappe.get_doc("Company", company)
        if hasattr(company_doc, "custom_number_of_departments"):
            dept_count = frappe.db.count("Department", {"company": company})
            frappe.db.set_value("Company", company, "custom_number_of_departments", dept_count)

        if hasattr(company_doc, "custom_number_of_employees"):
            emp_count = frappe.db.count("Employee", {"company": company})
            frappe.db.set_value("Company", company, "custom_number_of_employees", emp_count)

    frappe.delete_doc("Department", department.name, force=1)
    frappe.db.commit()
    return {
        "status": "success",
        "message": f"Department {department_name} deleted successfully"}

# API Remove Department Linked from Company
@frappe.whitelist(allow_guest=True)
def remove_department_from_company(department):
    department_name = department
    if not department_name:
        frappe.throw("Department name is required")
    department_doc = frappe.get_doc("Department", department_name)
    company_name = department_doc.company

    company_doc = frappe.get_doc("Company", company_name)
    original_len = len(company_doc.custom_department_list)

    company_doc.custom_department_list = [
        dep for dep in company_doc.custom_department_list
        if dep.department != department_name
    ]

    if len(company_doc.custom_department_list) < original_len:
        company_doc.save()
        frappe.db.commit()
        return{
            "status":1,
            "message": f'{department_name} removed from company {company_name}'
            }
    else:
        return{
            "status":0,
            "message": f'{department_name} not found in company {company_name}'
        }

# /* ===============================
# API Create Employee
# =============================== */
@frappe.whitelist(allow_guest=True)
def create_employee(**data):
    try:
        # Validate department exists

        if department_name := data.get("department"):
            dep_name = None

            if frappe.db.exists("Department", department_name):
                dep_name = department_name

            elif frappe.db.exists("Department", {"department_name": department_name}):
                dep_name = frappe.get_value("Department", {"department_name": department_name},"name")

            if not dep_name:
                return {
                    "status": "error",
                    "message": f"Department '{department_name}' does not exist. Please create it first."
                }
            dep_doc = frappe.get_doc("Department", dep_name)
            data["department"] = dep_doc.name

        # Validate company exists
        if company_name := data.get("company"):
            if not frappe.db.exists("Company", company_name):
                return {
                    "status": "error",
                    "message": f"Company '{company_name}' does not exist."
                }
            company_doc = frappe.get_doc("Company", company_name)
            data["company"] = company_doc.name

        if data.get("date_of_birth"):
            age = int(date_diff(today(), data["date_of_birth"])/365)
            if age < 12:

                return {
                    "status": "error",
                    "message": "Date of birth indicates an age less than 12 years, which is not valid."
                }
            if age > 80:
                return {
                    "status": "error",
                    "message": "Date of birth indicates an age greater than 80 years, which is not valid."
                }
        # Set CTC from salary
        data["ctc"] = data.get("salary", 0)

        employee = None
        if data.get("name") and frappe.db.exists("Employee", data["name"]):
            employee = frappe.get_doc("Employee", data["name"])
            employee.update(data)
            employee.save(ignore_permissions=True)
        else:
            # Create and insert employee document
            employee = frappe.get_doc({
                "doctype": "Employee",
                **data
            }).insert(ignore_permissions=True)
        # Update company employee count
        if company_name:
            try:
                if hasattr(employee, "custom_days_employed") and employee.date_of_joining:
                    employee.custom_days_employed = date_diff(today(), employee.date_of_joining)

                if hasattr(company_doc, "custom_number_of_employees"):
                    company_doc.custom_number_of_employees = (company_doc.custom_number_of_employees or 0) + 1
                    company_doc.save(ignore_permissions=True)
            except frappe.DoesNotExistError:
                frappe.log_error(f"Company {company_name} not found", "Create Employee Error")

        # Update department employee count
        if department_name:
            try:
                if hasattr(dep_doc, "custom_number_of_employees"):
                    dep_doc.custom_number_of_employees = (dep_doc.custom_number_of_employees or 0) + 1
                    dep_doc.save(ignore_permissions=True)
            except frappe.DoesNotExistError:
                frappe.log_error(f"Department {department_name} not found", "Create Employee Error")

        frappe.db.commit()
        return {
            "status": "success",
            "employee": employee.name
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Create Employee Error")
        return {"status": "error", "message": str(e)}

# API GET Employee
@frappe.whitelist(allow_guest =True)
def get_employees(company=None, department=None):
    filters = {}
    if company: filters["company"] = company
    if department: filters["department"] = department

    employees = frappe.get_all("Employee",
        filters=filters,
        fields=["*"]
    )
    if employees:
        frappe.response["status"] = "success"
        frappe.response["http_status_code"] = 200
        frappe.response["message"] = "Employees fetched successfully"
        frappe.response["data"] = [{**emp, "salary": emp.pop("ctc", None)} for emp in employees]
    else:
        frappe.response["status"] = "error"
        frappe.response["http_status_code"] = 404
        frappe.response["message"] = "No employees found"
        frappe.response["data"] = []


@frappe.whitelist(allow_guest=True)
def search_employees(query=''):
	"""
	البحث عن الموظفين حسب:
	- الاسم الكامل (employee_name)
	- رقم الموظف (name)
	- الاسم الأول (first_name)
	- الاسم الأوسط (middle_name)
	- رقم الهاتف (phone_number)

	Parameters:
	- query: نص البحث
	"""

	try:
		if not query or len(query.strip()) < 2:
			return []

		query = query.lower().strip()

		# البحث في قاعدة البيانات
		employees = frappe.get_list(
			"Employee",
			filters={
				"status": "Active"
			},
			fields=[
				"name",
				"employee_name",
				"first_name",
				"middle_name",
				"phone_number",
				"department",
				"company",
				"designation"
			],
			limit_page_length=500
		)

		# تصفية النتائج حسب الاستعلام
		results = []
		for emp in employees:
			emp_name = emp.get("employee_name", "").lower() if emp.get("employee_name") else ""
			emp_id = emp.get("name", "").lower() if emp.get("name") else ""
			phone = emp.get("phone_number", "").lower() if emp.get("phone_number") else ""
			first_name = emp.get("first_name", "").lower() if emp.get("first_name") else ""
			middle_name = emp.get("middle_name", "").lower() if emp.get("middle_name") else ""

			# البحث
			if (
				query in emp_name or
				query in emp_id or
				query in phone or
				query in first_name or
				query in middle_name
			):
				results.append({
					"name": emp.get("name"),
					"employee_name": emp.get("employee_name"),
					"first_name": emp.get("first_name"),
					"middle_name": emp.get("middle_name"),
					"phone_number": emp.get("phone_number"),
					"department": emp.get("department"),
					"company": emp.get("company"),
					"designation": emp.get("designation")
				})

		# إرجاع أول 10 نتائج
		return results[:10]

	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		frappe.throw(str(e))

@frappe.whitelist(allow_guest=True)
def get_one_employee_details():
    employee_name = frappe.request.args.get('employee_name')

    if not employee_name:
        return {
            "status": "error",
            "http_status_code": 400,
            "message": "Employee name is required",
            "data": {}
        }

    if not frappe.db.exists("Employee", employee_name):
        return {
            "status": "error",
            "http_status_code": 404,
            "message": f"Employee '{employee_name}' does not exist",
            "data": {}
        }

    try:
        employee = frappe.get_doc("Employee", employee_name)
        emp_data = employee.as_dict()
        emp_data["salary"] = emp_data.pop("ctc", None)

        return {
            "status": "success",
            "http_status_code": 200,
            "message": "Employee fetched successfully",
            "data": emp_data
        }
    except Exception as e:
        return {
            "status": "error",
            "http_status_code": 404,
            "message": f"Employee '{employee_name}' not found",
            "data": {}
        }
# في ملف: retail/retail/api/staff.py



# 1. جلب سجل الرواتب (آخر 12 شهر)
@frappe.whitelist(allow_guest=True)
def get_salary_history():
    employee_name = frappe.request.args.get('employee_name')

    if not employee_name:
        return {
            "status": "error",
            "message": "Employee name is required",
            "data": []
        }

    try:
        # جلب شهادات الراتب من Frappe
        salary_slips = frappe.db.get_list(
            'Salary Slip',
            filters={
                'employee': employee_name,
                'docstatus': 1  # معتمد فقط
            },
            fields=[
                'name',
                'posting_date',
                'gross_pay',
                'total_deduction',
                'net_pay'
            ],
            order_by='posting_date desc',
            limit=12
        )

        salary_history = []
        for slip in salary_slips:
            posting_date = slip['posting_date']
            month_name = get_arabic_month(posting_date.month)
            year = posting_date.year

            # جلب تفاصيل الراتب
            slip_doc = frappe.get_doc('Salary Slip', slip['name'])

            # حساب المكافأة من earnings
            bonus = 0
            for earning in slip_doc.earnings:
                if 'bonus' in earning.salary_component.lower():
                    bonus += earning.amount

            salary_history.append({
                'month': f"{month_name} {year}",
                'salary': slip['gross_pay'] - bonus,
                'bonus': bonus,
                'deductions': slip['total_deduction'],
                'net': slip['net_pay']
            })

        return {
            "status": "success",
            "message": "Salary history fetched successfully",
            "data": salary_history
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": []
        }


# 2. جلب إحصائيات الحضور
@frappe.whitelist(allow_guest=True)
def get_attendance_stats(employee_name, month=None, from_date=None, to_date=None):
    # employee_name = frappe.request.args.get('employee_name')
    # month = frappe.request.args.get('month')  # اختياري: شهر معين (YYYY-MM)
    # from_date = frappe.request.args.get('from_date')  # اختياري: تاريخ البداية
    # to_date = frappe.request.args.get('to_date')  # اختياري: تاريخ النهاية

    if not employee_name:
        return {
            "status": "error",
            "message": "Employee name is required",
            "data": {}
        }

    try:
        # تحديد نطاق التواريخ بناءً على المدخلات
        if from_date and to_date:
            # الحالة الثانية: تاريخين محددين
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        elif month:
            # الحالة الأولى: شهر معين (من أول الشهر إلى آخره)
            from_date = datetime.strptime(month, '%Y-%m').replace(day=1)
            to_date = (from_date + relativedelta(months=1)).replace(day=1) - timedelta(days=1)
        else:
            # الحالة الافتراضية: الشهر الحالي
            today = datetime.now()
            from_date = today.replace(day=1)
            to_date = (today + relativedelta(months=1)).replace(day=1) - timedelta(days=1)

        # جلب سجلات الحضور
        attendance_records = frappe.db.get_list(
            'Attendance',
            filters={
                'employee': employee_name,
                'attendance_date': ['>=', from_date.date()],
                'attendance_date': ['<=', to_date.date()],
                'docstatus': 1
            },
            fields=['status', 'attendance_date'],
            order_by='attendance_date asc'
        )

        # حساب الإحصائيات
        present = sum(1 for r in attendance_records if r['status'] == 'Present')
        absent = sum(1 for r in attendance_records if r['status'] == 'Absent')
        leave = sum(1 for r in attendance_records if r['status'] == 'On Leave')
        total_days = present + absent + leave
        percentage = (present / total_days * 100) if total_days > 0 else 0

        return {
            "status": "success",
            "message": "Attendance stats fetched successfully",
            "data": {
                "present": present,
                "absent": absent,
                "on_leave": leave,
                "total_days": total_days,
                "percentage": round(percentage, 2),
                "from_date": from_date.strftime('%Y-%m-%d'),
                "to_date": to_date.strftime('%Y-%m-%d'),
                "attendance_records": attendance_records
            }
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": f"Invalid date format. Use YYYY-MM for month or YYYY-MM-DD for dates: {str(e)}",
            "data": {}
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": {}
        }


# 3. جلب تقييم الأداء
@frappe.whitelist(allow_guest=True)
def get_performance():
    employee_name = frappe.request.args.get('employee_name')

    if not employee_name:
        return {
            "status": "error",
            "message": "Employee name is required",
            "data": {}
        }

    try:
        # جلب تقييم الأداء من Frappe
        appraisal = frappe.db.get_list(
            'Appraisal',
            filters={
                'employee': employee_name,
                'docstatus': 1
            },
            fields=['name', 'rating', 'comments'],
            order_by='creation desc',
            limit=1
        )

        if appraisal:
            appraisal_doc = frappe.get_doc('Appraisal', appraisal[0]['name'])

            # جلب مبيعات الموظف (إذا كان في المبيعات)
            sales = get_employee_sales(employee_name)

            return {
                "status": "success",
                "message": "Performance fetched successfully",
                "data": {
                    "rating": appraisal_doc.rating or 0,
                    "sales": sales,
                    "notes": appraisal_doc.comments or ""
                }
            }
        else:
            return {
                "status": "success",
                "message": "No appraisal found",
                "data": {
                    "rating": 0,
                    "sales": 0,
                    "notes": ""
                }
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": {}
        }


# دالة مساعدة: جلب مبيعات الموظف
def get_employee_sales(employee_name, months=1):
    try:
        from_date = datetime.now() - relativedelta(months=months)

        invoices = frappe.db.get_list(
            'Sales Invoice',
            filters={
                'sales_person': employee_name,
                'posting_date': ['>=', from_date],
                'docstatus': 1
            },
            fields=['grand_total']
        )

        total_sales = sum(inv['grand_total'] for inv in invoices)
        return total_sales

    except:
        return 0


# دالة مساعدة: تحويل رقم الشهر إلى اسم عربي
def get_arabic_month(month_num):
    months = {
        1: "يناير",
        2: "فبراير",
        3: "مارس",
        4: "أبريل",
        5: "مايو",
        6: "يونيو",
        7: "يوليو",
        8: "أغسطس",
        9: "سبتمبر",
        10: "أكتوبر",
        11: "نوفمبر",
        12: "ديسمبر"
    }
    return months.get(month_num, "")
# API Delete Employee
@frappe.whitelist(allow_guest=True)
def delete_employee(employee_name):
    """
    Delete an employee and update employee counts in Company and Department doctypes.
    """
    employee_exists = frappe.db.exists("Employee", employee_name)
    if not employee_exists:
        return {
            "status": "error",
            "message": f"Employee '{employee_name}' does not exist."
        }

     # Get Employee Document
    employee = frappe.get_doc("Employee", employee_name)
    company_name = employee.company
    department_name = employee.department
    try:
        # frappe.delete_doc("Employee", employee_name, force=1)
        employee.delete()
            # Update employee count in Doctype Company
        if company_name:
            company_doc = frappe.get_doc("Company", company_name)
            if hasattr(company_doc, "custom_number_of_employees"):
                company_count = frappe.db.count("Employee", {"company": company_name})
                frappe.db.set_value("Company", company_name, "custom_number_of_employees", company_count)

        # Update employee count in Doctype Department
        if department_name:
            dept_doc = frappe.get_doc("Department", department_name)
            if hasattr(dept_doc, "custom_number_of_employees"):
                dept_count = frappe.db.count("Employee", {"department": department_name})
                frappe.db.set_value("Department", department_name, "custom_number_of_employees", dept_count)

        frappe.db.commit()

        return {
            "status": "success",
            "message": f"Employee {employee_name} deleted successfully.",
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Delete Employee Error")
        return {
            "status": "error",
            "message": f"Error deleting employee '{employee_name}': {str(e)}"
        }




# /* ===============================
# API Designations
# =============================== */
@frappe.whitelist(allow_guest =True)
def get_designations():
    designations = frappe.get_all("Designation",["name","designation_name"])
    if designations:
        frappe.response["status"] = "success"
        frappe.response["http_status_code"] = 200
        frappe.response["message"] = "Designations fetched successfully"
        frappe.response["data"] = designations
    else:
        frappe.response["status"] = "error"
        frappe.response["http_status_code"] = 404
        frappe.response["message"] = "No designations found"
        frappe.response["data"] = []


# API Create Designation
@frappe.whitelist(allow_guest=True)
def create_designation(designation_name):
    try:
        if not designation_name:
            frappe.throw("Designation Name is required")
            return {
                "error": "Designation Name is required",
                "success": False
            }
        if frappe.db.exists("Designation", {"designation_name": designation_name}):
            frappe.throw(f"Designation '{designation_name}' already exists")
            return {
                "error": f"Designation '{designation_name}' already exists. Please use a different name.",
                "success": False,
                "error_type": "duplicate"
            }
        doc = frappe.get_doc({
            "doctype": "Designation",
            "designation_name": designation_name
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {
            "message": f"Designation '{designation_name}' created successfully.", "success": True
        }
    except frappe.DuplicateEntryError as e:
        frappe.log_error(frappe.get_traceback(), "Create Designation Duplicate Error")
        frappe.response["http_status_code"] = 409
        return {
            "error": f"Designation '{designation_name}' already exists. Please use a different name.",
            "success": False,
            "error_type": "duplicate"
        }
    except Exception as inner_error:
        # Rollback transaction on any error
        frappe.db.rollback()
        raise inner_error

# Api Delete Designation
@frappe.whitelist(allow_guest=True)
def delete_designation(designation_name):
    designation_exists = frappe.db.exists("Designation", {"designation_name": designation_name})
    if not designation_exists:
        return {
            "status": "error",
            "message": f"Designation '{designation_name}' does not exist."
        }
    designation = frappe.get_doc("Designation", {"designation_name": designation_name})
    frappe.delete_doc("Designation", designation.name, force=1)
    frappe.db.commit()
    return {
        "status": "success",
        "message": f"Designation {designation_name} deleted successfully"
    }


@frappe.whitelist(allow_guest =True)
def create_user(**kwargs):
    email = kwargs.get("email")
    first_name = kwargs.get("first_name")
    role = kwargs.get("role")
    if not email or not first_name or not role:
        return {
            "success": False,
            "message": "Missing required fields: email, first_name, or role"
        }

    if frappe.db.exists('User',{"email":email}):
        return {
            "success": False,
            "message": f"User with email {email} already exists."
        }
    else:
        try:
            user = frappe.get_doc({"doctype":"User","email":email,"first_name":first_name,"role_profile_name": role})
            user.insert(ignore_permissions=True)
            frappe.db.commit()
            return {
                "success": True,
                "message": f"User {email} created successfully.",
                "user": user.name
            }
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Create User Failed")
            return {
                "success": False,
                "message": f"Error Create User Failed {str(e)}",
            }


#API create company
@frappe.whitelist(allow_guest=True)
def create_company():
    try:
        data = frappe.request.get_json()

        if not data:
            frappe.throw("No data provided")

        company_name = data.get("company_name", "").strip()
        abbr = data.get("abbr", "").strip().upper()
        default_currency = data.get("default_currency")
        country = data.get("country")

        if not all([company_name, abbr, default_currency, country]):
            frappe.throw("All fields are required")

        # Check duplicates
        if frappe.db.exists("Company", {"company_name": company_name}):
            frappe.throw(f"Company '{company_name}' already exists")

        if frappe.db.exists("Company", {"abbr": abbr}):
            frappe.throw(f"Company with abbreviation '{abbr}' already exists")

        # Create minimal company record
        frappe.db.sql("""
            INSERT INTO `tabCompany`
            (name, company_name, abbr, default_currency, country,
             creation, modified, owner, modified_by, docstatus)
            VALUES
            (%s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, 0)
        """, (company_name, company_name, abbr, default_currency, country,
              frappe.session.user, frappe.session.user))

        frappe.db.commit()

        return {
            "message": f"Company '{company_name}' created successfully",
            "company_name": company_name,
            "success": True
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Simple Company Error")
        frappe.response["http_status_code"] = 500
        return {"error": str(e), "success": False}

#API delete company
@frappe.whitelist(allow_guest=True)
def delete_company(company):
    try:
        frappe.db.delete("Company", {"name": company})
        frappe.db.delete("Department", {"company": company})
        frappe.db.delete("Employee", {"company": company})
        frappe.db.commit()
        return {
            "message": f"Company '{company}' Deleted  successfully.",
            "company_name": company ,
            "success": True
        }
    except Exception as e:
        return {
            "message": f" Failed to Delete Company '{company}'.",
            "company_name": company,
            "success": False
        }


# /* ===============================
# API Roles
# =============================== */
@frappe.whitelist(allow_guest=True)
def create_role(role_name):
    try:
        if not role_name:
            frappe.throw("Role Name is required")
            return {
                "error": "Role Name is required",
                "success": False
            }
        if frappe.db.exists("Role", {"role_name": role_name}):
            frappe.throw(f"Role '{role_name}' already exists")
            return {
                "error": f"Role '{role_name}' already exists. Please use a different name.",
                "success": False,
                "error_type": "duplicate"
            }
        doc = frappe.get_doc({
            "doctype": "Role",
            "role_name": role_name
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {
            "message": f"Role '{role_name}' created successfully.", "success": True
        }
    except frappe.DuplicateEntryError as e:
        frappe.log_error(frappe.get_traceback(), "Create Role Duplicate Error")
        frappe.response["http_status_code"] = 409
        return {
            "error": f"Role '{role_name}' already exists. Please use a different name.",
            "success": False,
            "error_type": "duplicate"
        }
    except Exception as inner_error:
        # Rollback transaction on any error
        frappe.db.rollback()
        raise inner_error

# Api GET Roles
@frappe.whitelist(allow_guest =True)
def get_roles():
    roles = frappe.get_all("Role", fields=["name", "role_name"], filters={ "name" : ["!=", "All"]})
    if roles:
        frappe.response["status"] = "success"
        frappe.response["http_status_code"] = 200
        frappe.response["message"] = "Roles fetched successfully"
        frappe.response["data"] = roles
    else:
        frappe.response["status"] = "error"
        frappe.response["http_status_code"] = 404
        frappe.response["message"] = "No roles found"
        frappe.response["data"] = []


# Api Delete Role
@frappe.whitelist(allow_guest =True)
def delete_role(role_name):
    role_exists = frappe.db.exists("Role", {"role_name": role_name})
    if not role_exists:
        return {
            "status": "error",
            "message": f"Role '{role_name}' does not exist."
        }
    role = frappe.get_doc("Role", {"role_name": role_name})
    frappe.delete_doc("Role", role.name, force=1)
    frappe.db.commit()
    return {
        "status": "success",
        "message": f"Role {role_name} deleted successfully"
    }

#API GET Companies
@frappe.whitelist(allow_guest =True)
def get_companies():
    companies = frappe.get_all("Company", fields=["name", "company_name","custom_number_of_employees","custom_number_of_departments"])
    return companies


def calculate_employment_days(doc, method):
    if doc.date_of_joining:
        doc.custom_days_employed = date_diff(today(), doc.date_of_joining)
        frappe.db.commit()

@frappe.whitelist(allow_guest=True)
def delete_user_permission(email):
    perms = frappe.get_all("User Permission",{"user":email})

    if perms:
        for perm in perms:
            frappe.db.delete("User Permission",{"name":perm.name})
        frappe.db.commit()
        return {"message": f"Deleted {len(perms)} permissions for {email}"}
    else:
        return{
            "message":"No Permissions Found for{0}".format(email)
        }
