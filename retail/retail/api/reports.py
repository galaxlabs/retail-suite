import logging
import csv
from io import StringIO
import frappe
from frappe import _
from datetime import datetime, timedelta
from frappe.utils import formatdate,getdate, today, datetime, get_first_day, get_last_day, date_diff, flt, cstr, cint
from erpnext.accounts.report.profit_and_loss_statement.profit_and_loss_statement import execute
from erpnext.accounts.report.cash_flow.cash_flow import execute as cash_flow_execute
from erpnext.accounts.report.balance_sheet.balance_sheet import execute as balance_sheet_execute
from erpnext.accounts.utils import get_fiscal_year
from erpnext.accounts.report.financial_statements import (
	filter_out_zero_value_rows,
	get_fiscal_year_data,
	sort_accounts,
)
from erpnext.accounts.report.consolidated_financial_statement.consolidated_financial_statement import get_columns,get_root_account_name,get_balance_sheet_data, get_companies

def validate_dates(from_date, to_date):
	if not from_date or not to_date:
		frappe.throw(_("From Date and To Date are mandatory"))

	if to_date < from_date:
		frappe.throw(_("To Date cannot be less than From Date"))

@frappe.whitelist(allow_guest=True)
def get_income_statement_report(filters=None):
    """
    Get Income Statement Report with proper data handling

    Args:
        filters (dict): {
            "company": "company_name",
            "filter_based_on": "Fiscal Year" or "Date Range",
            "periodicity": "Monthly" or "Yearly",
            "from_date": "2025-01-01" (optional, for Date Range),
            "to_date": "2025-12-31" (optional, for Date Range)
        }

    Returns:
        dict: Report data with income, expenses, and net profit
    """
    try:
        # Parse filters
        if isinstance(filters, str):
            filters = frappe.parse_json(filters)
        filters = filters or {}

        # Get company
        company = filters.get("company") or frappe.defaults.get_user_default("Company")
        if not company:
            frappe.throw("Company is required")

        # Check permissions
        frappe.has_permission("Company", "read", company)

        # Build filter object
        filter_based_on = filters.get("filter_based_on", "Fiscal Year")
        periodicity = filters.get("periodicity", "Yearly")
        accumulated_values = filters.get("accumulated_values", False)
        print("Filters",filters)
        if filter_based_on == "Date Range":
        # Use dates passed from Vue
            from_date = filters.get("from_date")
            to_date = filters.get("to_date")

            if not from_date or not to_date:
                frappe.throw("From Date and To Date are required for Date Range filter")

            period_start_date = from_date
            period_end_date = to_date
        else:
            # Use fiscal year
            from_fy = filters.get("from_fiscal_year")
            to_fy = filters.get("to_fiscal_year")

            if not from_fy:
                from_fy = frappe.db.get_value(
                    "Fiscal Year",
                    {"disabled": 0},
                    "name",
                    order_by="year_start_date desc"
                )

            if not to_fy:
                to_fy = from_fy

            # Get fiscal year dates
            from_fy_doc = frappe.get_doc("Fiscal Year", from_fy)
            to_fy_doc = frappe.get_doc("Fiscal Year", to_fy)

            period_start_date = from_fy_doc.year_start_date
            period_end_date = to_fy_doc.year_end_date

        # Build report filters for cash_flow_execute
        report_filters = frappe._dict({
            "company": company,
            "filter_based_on": filter_based_on,
            "from_fiscal_year": filters.get("from_fiscal_year", "2025"),
            "to_fiscal_year": filters.get("to_fiscal_year", "2025"),
            "periodicity": periodicity,
            "accumulated_values": accumulated_values,
            "period_start_date": period_start_date,
            "period_end_date": period_end_date
        })

        print("report_filters",report_filters)
        # Execute report
        columns, data, _, chart, report_summary, _ = execute(report_filters)

        # Extract financial summary
        total_income = 0
        total_expenses = 0
        net_profit = 0

        # report_summary contains: [Income, Gross Profit, Expenses, Net Profit, etc]
        try:
            if report_summary and len(report_summary) > 0:
                # Find the correct values from summary
                for summary_row in report_summary:
                    if summary_row.get("label") and "Total Income" in str(summary_row.get("label", "")):
                        total_income = summary_row.get("value", 0)
                    elif summary_row.get("label") and "Total Expense" in str(summary_row.get("label", "")):
                        total_expenses = abs(summary_row.get("value", 0))
                    elif summary_row.get("label") and "Profit" in str(summary_row.get("label", "")):
                        net_profit = summary_row.get("value", 0)
        except Exception:
            # Fallback: calculate from data
            for row in data:
                if isinstance(row, dict):
                    if row.get("account_name") == "Total Income (Credit)":
                        total_income = row.get("total", 0)
                    elif row.get("account_name") == "Total Expense (Debit)":
                        total_expenses = abs(row.get("total", 0))

        if not net_profit:
            net_profit = total_income - total_expenses

        # Calculate additional metrics
        profit_margin = (net_profit / total_income * 100) if total_income != 0 else 0
        expense_ratio = (total_expenses / total_income * 100) if total_income != 0 else 0

        return {
            "status": "success",
            "columns": columns,
            "data": data,
            "chart": chart,
            "summary": {
                "total_income": round(total_income, 2),
                "total_expenses": round(total_expenses, 2),
                "net_profit": round(net_profit, 2),
                "profit_margin": round(profit_margin, 2),
                "expense_ratio": round(expense_ratio, 2),
            },
            "period": {
                "start_date": report_filters.get("period_start_date"),
                "end_date": report_filters.get("period_end_date"),
                "filter_based_on": filter_based_on,
                "periodicity": periodicity,
            },
            "filters": report_filters,
        }

    except frappe.PermissionError as e:
        frappe.log_error(frappe.get_traceback(), "Income Statement Permission Error")
        frappe.throw(f"Permission denied: {str(e)}")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Income Statement Report Error")
        frappe.throw(f"Error generating report: {str(e)}")


@frappe.whitelist(allow_guest=True)
def get_income_statement_by_period(company=None, from_date=None, to_date=None):
    """
    Get Income Statement for a specific date range
    """
    filters = {
        "company": company or frappe.defaults.get_user_default("Company"),
        "filter_based_on": "Date Range",
        "from_date": from_date or get_first_day(today()),
        "to_date": to_date or get_last_day(today()),
        "periodicity": "Monthly"
    }
    return get_income_statement_report(filters)


@frappe.whitelist(allow_guest=True)
def get_income_statement_yearly(company=None):
    """
    Get Income Statement for the current fiscal year
    """
    filters = {
        "company": company or frappe.defaults.get_user_default("Company"),
        "filter_based_on": "Fiscal Year",
        "periodicity": "Yearly"
    }
    return get_income_statement_report(filters)


@frappe.whitelist(allow_guest=True)
def get_income_statement_monthly(company=None):
    """
    Get Income Statement with monthly breakdown
    """
    filters = {
        "company": company or frappe.defaults.get_user_default("Company"),
        "filter_based_on": "Fiscal Year",
        "periodicity": "Monthly"
    }
    return get_income_statement_report(filters)


@frappe.whitelist(allow_guest=True)
def test_income_statement():
    """Test function"""
    return get_income_statement_yearly()

# ===================================================================
# CashFlow Report
# ===================================================================
@frappe.whitelist(allow_guest=True)
def get_cash_flow_report(filters):
    print("\nFilter",filters)
    """
    Return Cash Flow data formatted for Vue UI
    """
    if isinstance(filters, str):
        filters = frappe.parse_json(filters)
    filters = filters or {}

    # Get company
    company = filters.get("company") or frappe.defaults.get_user_default("Company")
    if not company:
        frappe.throw("Company is required")

    # Check permissions
    frappe.has_permission("Company", "read", company)

    # Build filter object - respect the filters passed from Vue
    filter_based_on = filters.get("filter_based_on", "Fiscal Year")
    periodicity = filters.get("periodicity", "Yearly")
    accumulated_values = filters.get("accumulated_values", False)

    # Handle date range vs fiscal year
    if filter_based_on == "Date Range":
        # Use dates passed from Vue
        from_date = filters.get("from_date")
        to_date = filters.get("to_date")

        if not from_date or not to_date:
            frappe.throw("From Date and To Date are required for Date Range filter")

        period_start_date = from_date
        period_end_date = to_date
    else:
        # Use fiscal year
        from_fy = filters.get("from_fiscal_year")
        to_fy = filters.get("to_fiscal_year")

        if not from_fy:
            from_fy = frappe.db.get_value(
                "Fiscal Year",
                {"disabled": 0},
                "name",
                order_by="year_start_date desc"
            )

        if not to_fy:
            to_fy = from_fy

        # Get fiscal year dates
        from_fy_doc = frappe.get_doc("Fiscal Year", from_fy)
        to_fy_doc = frappe.get_doc("Fiscal Year", to_fy)

        period_start_date = from_fy_doc.year_start_date
        period_end_date = to_fy_doc.year_end_date

    # Build report filters for cash_flow_execute
    report_filters = frappe._dict({
        "company": company,
        "filter_based_on": filter_based_on,
        "from_fiscal_year": filters.get("from_fiscal_year", "2025"),
        "to_fiscal_year": filters.get("to_fiscal_year", "2025"),
        "periodicity": periodicity,
        "accumulated_values": accumulated_values,
        "period_start_date": period_start_date,
        "period_end_date": period_end_date
    })

    frappe.logger().info(f"Cash Flow Report Filters: {report_filters}")

    try:
        # Execute the cash flow report
        columns, data, _, chart, report_summary = cash_flow_execute(report_filters)
    except Exception as e:
        frappe.logger().error(f"Error executing cash flow: {str(e)}")
        frappe.throw(f"Error generating cash flow report: {str(e)}")

    result = {
        "operating": [],
        "investing": [],
        "financing": [],
        "totals": {
            "operating": 0,
            "investing": 0,
            "financing": 0,
        }
    }

    current_section = None
    frappe.logger().info(f"Processing {len(data)} rows from cash flow report")

    for row in data:
        account = row.get("account", "").replace("'", "").strip()
        total = flt(row.get("total", 0))
        indent = row.get("indent", 0)

        # Detect section headers
        if indent == 0:
            if "Operations" in account:
                current_section = "operating"
                frappe.logger().info(f"Detected Operating section: {account}")
                continue

            if "Investing" in account:
                current_section = "investing"
                frappe.logger().info(f"Detected Investing section: {account}")
                continue

            if "Financing" in account:
                current_section = "financing"
                frappe.logger().info(f"Detected Financing section: {account}")
                continue

        # Capture section totals
        if "Net Cash" in account and indent == 0:
            if current_section:
                result["totals"][current_section] = total
                frappe.logger().info(f"Section total {current_section}: {total}")
            continue

        # Add line items (indent == 1)
        if indent == 1 and current_section and account and account != "None":
            result[current_section].append({
                "name": account,
                "description": "",
                "amount": total,
            })
            frappe.logger().info(f"Added {current_section} item: {account} = {total}")

    result["net_cash_change"] = (
        result["totals"]["operating"]
        + result["totals"]["investing"]
        + result["totals"]["financing"]
    )

    # Return the filters that were actually used
    result["report_filters"] = {
        "company": company,
        "filter_based_on": filter_based_on,
        "from_fiscal_year": filters.get("from_fiscal_year"),
        "to_fiscal_year": filters.get("to_fiscal_year"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
        "periodicity": periodicity,
        "accumulated_values": accumulated_values,
        "period_start_date": str(period_start_date),
        "period_end_date": str(period_end_date)
    }

    frappe.logger().info(f"Cash Flow Result: Operating={result['totals']['operating']}, Investing={result['totals']['investing']}, Financing={result['totals']['financing']}")

    return result
# ===================================================================
# beginningcash balance Report
# ===================================================================
@frappe.whitelist(allow_guest=True)
def get_beginning_cash_balance(filters=None):
    """
    جلب رصيد النقدية والبنوك في بداية الفترة
    المصدر: Opening Entry (GL Entry مع voucher_type = 'Opening Entry')
    """
    if isinstance(filters, str):
        filters = frappe.parse_json(filters)
    filters = filters or {}

    company = filters.get("company") or frappe.defaults.get_user_default("Company")
    if not company:
        frappe.throw("Company is required")

    from erpnext.accounts.utils import get_fiscal_year
    from datetime import timedelta

    filter_based_on = filters.get("filter_based_on", "Fiscal Year")

    # جلب تاريخ بداية الفترة
    if filter_based_on == "Date Range":
        period_start_date = frappe.utils.get_datetime(filters.get("from_date")).date()
    else:
        fy_name = filters.get("from_fiscal_year")
        if not fy_name:
            fy_name = frappe.db.get_value(
                "Fiscal Year",
                {"disabled": 0},
                "name",
                order_by="year_start_date desc"
            )
        fy_doc = frappe.get_doc("Fiscal Year", fy_name)
        period_start_date = fy_doc.year_start_date

    period_before_start = period_start_date - timedelta(days=1)

    frappe.logger().info(f"Period: {period_before_start} to {period_start_date}")

    # جلب جميع حسابات النقدية والبنوك (ليست مجموعات)
    cash_bank_accounts = frappe.db.get_list(
        "Account",
        filters={
            "company": company,
            "account_type": ["in", ["Bank", "Cash"]],
            "disabled": 0,
            "is_group": 0
        },
        fields=["name", "account_type", "account_name"]
    )

    if not cash_bank_accounts:
        frappe.msgprint("لا توجد حسابات بنكية أو نقدية في الشركة")
        return {
            "beginning_balance": 0,
            "accounts": [],
            "period_start_date": str(period_start_date),
            "as_on_date": str(period_before_start)
        }

    account_names = [acc["name"] for acc in cash_bank_accounts]

    # 1️⃣ جلب Opening Entries (أول مرة في السنة المالية)
    opening_balance_query = """
    SELECT
        gle.account,
        SUM(gle.debit - gle.credit) as balance
    FROM `tabGL Entry` gle
    WHERE
        gle.company = %s
        AND gle.account IN ({})
        AND gle.voucher_type = 'Opening Entry'
        AND gle.posting_date = %s
    GROUP BY gle.account
    """.format(','.join(['%s']*len(account_names)))

    opening_data = frappe.db.sql(
        opening_balance_query,
        [company] + account_names + [period_start_date],
        as_dict=True
    )

    frappe.logger().info(f"Opening Entry data: {opening_data}")

    # بناء قاموس من Opening Entry
    opening_dict = {row["account"]: row["balance"] for row in opening_data}

    # 2️⃣ إذا ما فيش opening entry، جلب الرصيد من GL Entry قبل الفترة
    if not opening_dict:
        frappe.logger().warning("No Opening Entry found, using GL Entry balance")

        gl_query = """
        SELECT
            account,
            SUM(debit - credit) as balance
        FROM `tabGL Entry`
        WHERE
            company = %s
            AND account IN ({})
            AND posting_date <= %s
            AND voucher_type != 'Period Closing Voucher'
        GROUP BY account
        """.format(','.join(['%s']*len(account_names)))

        gl_data = frappe.db.sql(
            gl_query,
            [company, period_before_start] + account_names,
            as_dict=True
        )

        opening_dict = {row["account"]: row["balance"] for row in gl_data}

    total_beginning_balance = 0
    account_details = []

    # دمج البيانات
    for account in cash_bank_accounts:
        account_name = account["name"]
        balance = opening_dict.get(account_name, 0) or 0

        total_beginning_balance += balance
        account_details.append({
            "account": account_name,
            "account_type": account["account_type"],
            "account_name": account["account_name"],
            "balance": balance
        })

    frappe.logger().info(f"Total Beginning Balance: {total_beginning_balance}, Accounts: {len(account_details)}")

    return {
        "beginning_balance": total_beginning_balance,
        "accounts": account_details,
        "period_start_date": str(period_start_date),
        "as_on_date": str(period_before_start),
        "source": "Opening Entry" if opening_dict else "GL Entry"
    }


@frappe.whitelist(allow_guest=True)
def create_opening_entry(company, opening_date=None):
    """
    إنشاء Opening Entry تلقائيًا
    يجلب الأرصدة من آخر يوم في السنة المالية السابقة
    """
    if isinstance(opening_date, str):
        opening_date = frappe.utils.get_datetime(opening_date).date()

    if not opening_date:
        from erpnext.accounts.utils import get_fiscal_year
        fy_data = get_fiscal_year(frappe.utils.today(), company=company)
        opening_date = fy_data[1]  # year_start_date

    from datetime import timedelta
    before_opening = opening_date - timedelta(days=1)

    frappe.logger().info(f"Creating opening entry for {company} on {opening_date}")

    # جلب الأرصدة قبل تاريخ الفتح
    closing_balances = frappe.db.sql("""
        SELECT
            account,
            SUM(debit - credit) as balance
        FROM `tabGL Entry`
        WHERE
            company = %s
            AND posting_date <= %s
            AND voucher_type != 'Period Closing Voucher'
        GROUP BY account
        HAVING SUM(debit - credit) != 0
    """, [company, before_opening], as_dict=True)

    if not closing_balances:
        frappe.msgprint("لا توجد أرصدة لإنشاء opening entry")
        return None

    # إنشاء Journal Entry
    jv = frappe.new_doc("Journal Entry")
    jv.voucher_type = "Opening Entry"
    jv.posting_date = opening_date
    jv.company = company
    jv.user_remark = "Opening Balance Transfer"

    for row in closing_balances:
        account = row["account"]
        balance = row["balance"]

        if balance > 0:
            jv.append("accounts", {
                "account": account,
                "debit": balance,
                "credit": 0
            })
        elif balance < 0:
            jv.append("accounts", {
                "account": account,
                "debit": 0,
                "credit": abs(balance)
            })

    # موازنة القيد (Equity account)
    equity_account = frappe.db.get_value(
        "Account",
        {"company": company, "account_type": "Equity", "is_group": 0},
        "name"
    )

    if equity_account:
        total_debit = sum([acc.debit for acc in jv.accounts])
        total_credit = sum([acc.credit for acc in jv.accounts])
        difference = total_debit - total_credit

        if difference > 0:
            jv.append("accounts", {
                "account": equity_account,
                "debit": 0,
                "credit": difference
            })
        elif difference < 0:
            jv.append("accounts", {
                "account": equity_account,
                "debit": abs(difference),
                "credit": 0
            })

    jv.save()
    frappe.msgprint(f"تم إنشاء Opening Entry: {jv.name}")
    return jv.name

# =====================================================================
# =====================================================================
# =====================================================================
# =====================================================================
# =====================================================================
# =====================================================================
import frappe
from frappe.utils import flt
import logging
from erpnext.accounts.utils import get_fiscal_year
from erpnext.accounts.report.financial_statements import get_fiscal_year_data
from erpnext.accounts.report.consolidated_financial_statement.consolidated_financial_statement import (
    get_columns,
    get_companies,
    get_balance_sheet_data,
)

@frappe.whitelist(allow_guest=True)
def get_balance_sheet_report(filters=None):
    """
    Return Balance Sheet data formatted for Vue UI with hierarchical account structure
    Supports filters: company, filter_based_on, from_fiscal_year, to_fiscal_year, from_date, to_date, periodicity
    """
    if isinstance(filters, str):
        filters = frappe.parse_json(filters)
    filters = filters or {}

    # Get company
    company = filters.get("company") or frappe.defaults.get_user_default("Company")
    if not company:
        frappe.throw("Company is required")

    # Check permissions
    frappe.has_permission("Company", "read", company)

    # Build filter object
    periodicity = filters.get("periodicity", "Yearly")
    accumulated_values = filters.get("accumulated_values", False)
    show_zero_values = filters.get("show_zero_values", False)
    filter_based_on = filters.get("filter_based_on", "Fiscal Year")

    # Handle date range vs fiscal year
    if filter_based_on == "Date Range":
        from_date = filters.get("from_date")
        to_date = filters.get("to_date")
        if not from_date or not to_date:
            frappe.throw("From Date and To Date are required for Date Range filter")
        period_end_date = to_date
    else:
        to_fy = filters.get("to_fiscal_year")
        if not to_fy:
            to_fy = frappe.db.get_value(
                "Fiscal Year",
                {"disabled": 0},
                "name",
                order_by="year_start_date desc"
            )

        if not to_fy:
            frappe.throw("No active Fiscal Year found")

        to_fy_doc = frappe.get_doc("Fiscal Year", to_fy)
        period_end_date = to_fy_doc.year_end_date

    from_fy = filters.get("from_fiscal_year")
    if not from_fy and filter_based_on != "Date Range":
        from_fy = to_fy

    # Build report filters
    report_filters = frappe._dict({
        "company": company,
        "filter_based_on": filter_based_on,
        "from_fiscal_year": from_fy if filter_based_on != "Date Range" else "",
        "to_fiscal_year": to_fy if filter_based_on != "Date Range" else "",
        "periodicity": periodicity,
        "accumulated_values": accumulated_values,
        "show_zero_values": show_zero_values,
        "from_date": filters.get("from_date", ""),
        "to_date": filters.get("to_date", period_end_date) if filter_based_on == "Date Range" else "",
        "as_on_date": period_end_date,
        "report": "Balance Sheet",
        "presentation_currency": filters.get("presentation_currency", ""),
    })

    frappe.logger().info(f"Balance Sheet Report Filters: {report_filters}")

    try:
        # Get fiscal year data
        fiscal_year = get_fiscal_year_data(
            from_fy if filter_based_on != "Date Range" else None,
            to_fy if filter_based_on != "Date Range" else None
        )

        # Get companies list
        companies_column, companies = get_companies(report_filters)

        # Get columns
        columns = get_columns(companies_column, report_filters)

        # Execute the balance sheet report
        data, message, chart, report_summary = get_balance_sheet_data(
            fiscal_year,
            companies,
            columns,
            report_filters
        )
    except Exception as e:
        frappe.logger().error(f"Error executing balance sheet: {str(e)}")
        frappe.throw(f"Error generating balance sheet report: {str(e)}")

    # Clean up data
    cleaned_data = []
    # print("Data",data)
    for row in data:
        if isinstance(row, dict):
            clean_row = {}
            for key, value in row.items():
                if hasattr(value, 'default_factory'):
                    clean_row[key] = dict(value)
                else:
                    clean_row[key] = value
            cleaned_data.append(clean_row)
        else:
            cleaned_data.append(row)
    # print("cleaned_data",cleaned_data)

    # Organize data by sections - collect ALL accounts (parent + children)
    assets = []
    liabilities = []
    equity = []
    totals = {}

    for row in cleaned_data:
        if not row or not isinstance(row, dict):
            continue
        if not is_valid_account(row):
            continue
        account_name = row.get("account_name", "").replace("'", "").strip()
        account = row.get("account", "").replace("'", "").strip()

        root_type = row.get("root_type")

        if root_type == "Asset":
            assets.append(row)
        elif root_type == "Liability":
            liabilities.append(row)
        elif root_type == "Equity":
            equity.append(row)

        # Skip empty rows
        if not account_name or not account or account == "None":
            continue

    assets_root_account = get_root_account(assets)
    liabilities_root_account = get_root_account(liabilities)
    equity_root_account = get_root_account(equity)

    # Validate balance sheet equation
    total_assets = get_total_level_1(assets, assets_root_account)
    total_liabilities = get_total_level_1(liabilities, liabilities_root_account)
    total_equity = get_total_level_1(equity, equity_root_account)

    assets_row = next((r for r in assets if r["account"] == assets_root_account), None)
    if assets_row:
        assets_row["total"] = total_assets

    lib_row = next((r for r in liabilities if r["account"] == liabilities_root_account), None)
    if lib_row:
        lib_row["total"] = total_liabilities

    equity_row = next((r for r in equity if r["account"] == equity_root_account), None)
    if equity_row:
        equity_row["total"]= total_equity

    total_liabilities_and_equity = total_liabilities + total_equity
    difference = abs(total_assets - total_liabilities_and_equity)
    parsed_result = {
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "totals": {
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity
        },
        "balance_sheet_equation": {
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "total_liabilities_and_equity": total_liabilities_and_equity,
            "difference": round(difference, 2),
            "is_balanced": difference < 1
        },
        "report_filters": {
            "company": company,
            "filter_based_on": filter_based_on,
            "from_fiscal_year": from_fy,
            "to_fiscal_year": to_fy,
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date"),
            "periodicity": periodicity,
            "accumulated_values": accumulated_values,
            "show_zero_values": show_zero_values,
            "as_on_date": str(period_end_date)
        },
        "message": message,
        "status": "success"
    }

    frappe.logger().info(
        f"Balance Sheet Result: "
        f"Assets={total_assets}, "
        f"Liabilities={total_liabilities}, "
        f"Equity={total_equity}, "
        f"Balanced={parsed_result['balance_sheet_equation']['is_balanced']}, "
        f"Asset Accounts={len(assets)}, "
        f"Liability Accounts={len(liabilities)}, "
        f"Equity Accounts={len(equity)}"
    )

    print("\nparsed_result",parsed_result)
    return parsed_result

def get_root_account(rows):
    for r in rows:
        if r.get("parent_account") is None:
            return r.get("account")
    return None

def get_total_level_1(rows, root_account):
    return sum(
        (r.get("pos") or 0)
        for r in rows
        if r.get("has_value")
        and r.get("parent_account") == root_account
    )


def get_total_from_leaves(rows, root_account):
    accounts = {r["account"]: r for r in rows}

    def is_under_root(row):
        parent = row.get("parent_account")
        while parent:
            if parent == root_account:
                return True
            parent = accounts.get(parent, {}).get("parent_account")
        return False

    return sum(
        r.get("pos", 0) or 0
        for r in rows
        if r.get("has_value") and is_under_root(r)
    )

def is_valid_account(row):
    if not row:
        return False

    name = str(row.get("account_name", ""))
    if "Total" in name:
        return False
    if "Profit / Loss" in name:
        return False

    return True


# =====================================================================
# =====================================================================
# =====================================================================
import frappe
from frappe.utils import flt
from erpnext.accounts.utils import get_fiscal_year
from erpnext.accounts.report.financial_statements import get_fiscal_year_data
from erpnext.accounts.report.consolidated_financial_statement.consolidated_financial_statement import (
    get_columns,
    get_companies,
    get_balance_sheet_data,
)

@frappe.whitelist(allow_guest=True)
def get_balance_sheet_report_data(filters=None):
    """
    Return Balance Sheet data formatted for Vue UI
    Supports filters: company, filter_based_on, from_fiscal_year, to_fiscal_year, from_date, to_date, periodicity
    """
    if isinstance(filters, str):
        filters = frappe.parse_json(filters)
    filters = filters or {}

    # Get company
    company = filters.get("company") or frappe.defaults.get_user_default("Company")
    if not company:
        frappe.throw("Company is required")

    # Check permissions
    frappe.has_permission("Company", "read", company)

    # Build filter object
    periodicity = filters.get("periodicity", "Yearly")
    accumulated_values = filters.get("accumulated_values", False)
    show_zero_values = filters.get("show_zero_values", False)
    filter_based_on = filters.get("filter_based_on", "Fiscal Year")

    # Handle date range vs fiscal year
    if filter_based_on == "Date Range":
        from_date = filters.get("from_date")
        to_date = filters.get("to_date")
        if not from_date or not to_date:
            frappe.throw("From Date and To Date are required for Date Range filter")
        period_end_date = to_date
    else:
        to_fy = filters.get("to_fiscal_year")
        if not to_fy:
            to_fy = frappe.db.get_value(
                "Fiscal Year",
                {"disabled": 0},
                "name",
                order_by="year_start_date desc"
            )

        if not to_fy:
            frappe.throw("No active Fiscal Year found")

        to_fy_doc = frappe.get_doc("Fiscal Year", to_fy)
        period_end_date = to_fy_doc.year_end_date

    # Get from_fiscal_year if not provided
    from_fy = filters.get("from_fiscal_year")
    if not from_fy and filter_based_on != "Date Range":
        from_fy = to_fy

    # Build report filters
    report_filters = frappe._dict({
        "company": company,
        "filter_based_on": filter_based_on,
        "from_fiscal_year": from_fy if filter_based_on != "Date Range" else "",
        "to_fiscal_year": to_fy if filter_based_on != "Date Range" else "",
        "periodicity": periodicity,
        "accumulated_values": accumulated_values,
        "show_zero_values": show_zero_values,
        "from_date": filters.get("from_date", ""),
        "to_date": filters.get("to_date", period_end_date) if filter_based_on == "Date Range" else "",
        "as_on_date": period_end_date,
        "report": "Balance Sheet",
        "presentation_currency": filters.get("presentation_currency", ""),
    })

    try:
        # Get fiscal year data
        fiscal_year = get_fiscal_year_data(
            from_fy if filter_based_on != "Date Range" else None,
            to_fy if filter_based_on != "Date Range" else None
        )

        # Get companies list
        companies_column, companies = get_companies(report_filters)

        # Get columns
        columns = get_columns(companies_column, report_filters)

        # Execute the balance sheet report
        data, message, chart, report_summary = get_balance_sheet_data(
            fiscal_year,
            companies,
            columns,
            report_filters
        )

        # Clean up data
        cleaned_data = []
        for row in data:
            if isinstance(row, dict):
                clean_row = {}
                for key, value in row.items():
                    if hasattr(value, 'default_factory'):
                        clean_row[key] = dict(value)
                    else:
                        clean_row[key] = value
                cleaned_data.append(clean_row)
            else:
                cleaned_data.append(row)

        # Organize data by sections
        assets = []
        liabilities = []
        equity = []
        totals = {}

        for row in cleaned_data:
            if not row or not isinstance(row, dict):
                continue

            account_name = row.get("account_name", "").replace("'", "").strip()

            # Skip empty rows
            if not account_name or account_name == "None":
                continue

            # Capture section totals
            if "Total Asset" in account_name:
                totals["total_assets"] = flt(row.get("total", 0))
                continue

            if "Total Liability" in account_name:
                totals["total_liabilities"] = flt(row.get("total", 0))
                continue

            if "Total (Credit)" in account_name and "Provisional" not in account_name:
                totals["total_all"] = flt(row.get("total", 0))
                continue

            # Skip provisional and other summary rows
            if any(skip in account_name for skip in ["Provisional", "Unclosed", "Credit"]) and "Total" not in account_name:
                continue

            # Determine section
            if "Asset" in account_name or "Application of Funds" in account_name:
                if flt(row.get("indent", 0)) == 0:
                    continue  # Skip section header
                assets.append(row)
            elif "Liabilit" in account_name or "Source of Funds" in account_name:
                if flt(row.get("indent", 0)) == 0:
                    continue  # Skip section header
                liabilities.append(row)
            elif "Equit" in account_name:
                if flt(row.get("indent", 0)) == 0:
                    continue  # Skip section header
                equity.append(row)

        # Calculate equity if not present
        if "total_equity" not in totals:
            total_all = totals.get("total_all", 0)
            total_liab = totals.get("total_liabilities", 0)
            totals["total_equity"] = flt(total_all) - flt(total_liab)

        return {
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
            "totals": {
                "total_assets": flt(totals.get("total_assets", 0)),
                "total_liabilities": flt(totals.get("total_liabilities", 0)),
                "total_equity": flt(totals.get("total_equity", 0))
            },
            "filters": report_filters,
            "message": message,
            "status": "success"
        }

    except Exception as e:
        frappe.logger().error(f"Error executing balance sheet: {str(e)}")
        frappe.throw(f"Error generating balance sheet report: {str(e)}")


# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------

@frappe.whitelist(allow_guest=True)
def get_balance_sheet_snapshot(company=None, as_on_date=None):
    """
    Get a quick balance sheet snapshot for a specific company and date
    Returns only the totals
    """
    if not company:
        company = frappe.defaults.get_user_default("Company")

    if not as_on_date:
        as_on_date = today()

    frappe.has_permission("Company", "read", company)

    # Build filters
    filters = frappe._dict({
        "company": company,
        "as_on_date": as_on_date,
        "filter_based_on": "Date Range",
        "from_date": "2000-01-01",
        "to_date": as_on_date
    })

    try:
        result = balance_sheet_execute(filters)
        columns = result[0] if result else []
        data = result[1] if len(result) > 1 else []
    except Exception as e:
        frappe.logger().error(f"Error executing balance sheet snapshot: {str(e)}")
        frappe.throw(f"Error generating balance sheet snapshot: {str(e)}")

    totals = {
        "total_assets": 0,
        "total_liabilities": 0,
        "total_equity": 0
    }

    current_section = None

    for row in data:
        if not row or len(row) == 0:
            continue

        account_name = row.get("account_name", "").replace("'", "").strip()
        balance = flt(row.get("total", 0))
        indent = flt(row.get("indent", 0))

        if indent == 0:
            if "Asset" in account_name or "Application of Funds" in account_name:
                current_section = "assets"
            elif "Liabilit" in account_name or "Source of Funds" in account_name:
                current_section = "liabilities"
            elif "Equit" in account_name:
                current_section = "equity"

        if "Total Asset" in account_name:
            totals["total_assets"] = balance
        elif "Total Liability" in account_name:
            totals["total_liabilities"] = balance
        elif "Equit" in account_name and "Total" in account_name:
            totals["total_equity"] = balance

    return {
        "company": company,
        "as_on_date": str(as_on_date),
        "total_assets": totals["total_assets"],
        "total_liabilities": totals["total_liabilities"],
        "total_equity": totals["total_equity"],
        "total_liabilities_and_equity": totals["total_liabilities"] + totals["total_equity"],
        "is_balanced": abs(totals["total_assets"] - (totals["total_liabilities"] + totals["total_equity"])) < 1
    }


@frappe.whitelist(allow_guest=True)
def get_balance_sheet_snapshot(company=None, as_on_date=None):
    """
    Get a quick balance sheet snapshot for a specific company and date
    Returns only the totals
    """
    if not company:
        company = frappe.defaults.get_user_default("Company")

    if not as_on_date:
        as_on_date = today()

    frappe.has_permission("Company", "read", company)

    # Build filters
    filters = frappe._dict({
        "company": company,
        "as_on_date": as_on_date,
        "filter_based_on": "Date Range",
        "from_date": "2000-01-01",
        "to_date": as_on_date
    })

    try:
        columns, data, _, chart, report_summary = balance_sheet_execute(filters)
    except Exception as e:
        frappe.logger().error(f"Error executing balance sheet snapshot: {str(e)}")
        frappe.throw(f"Error generating balance sheet snapshot: {str(e)}")

    totals = {
        "total_assets": 0,
        "total_liabilities": 0,
        "total_equity": 0
    }

    current_section = None

    for row in data:
        account = row.get("account", "").replace("'", "").strip()
        balance = flt(row.get("balance", 0))
        indent = row.get("indent", 0)

        if indent == 0:
            if "Asset" in account:
                current_section = "assets"
            elif "Liabilit" in account:
                current_section = "liabilities"
            elif "Equit" in account:
                current_section = "equity"

        if "Total" in account and indent == 0:
            if current_section == "assets":
                totals["total_assets"] = balance
            elif current_section == "liabilities":
                totals["total_liabilities"] = balance
            elif current_section == "equity":
                totals["total_equity"] = balance

    return {
        "company": company,
        "as_on_date": str(as_on_date),
        **totals,
        "total_liabilities_and_equity": totals["total_liabilities"] + totals["total_equity"],
        "is_balanced": abs(totals["total_assets"] - (totals["total_liabilities"] + totals["total_equity"])) < 1
    }
# =====================================================================


@frappe.whitelist(allow_guest=True)
def get_accounts_receivable_data():
    """
    Fetch Accounts Receivable data from ERPNext
    Returns comprehensive AR analytics and invoice details
    """
    try:
        # Get all unpaid and partially paid invoices
        invoices = frappe.get_list(
            'Sales Invoice',
            filters={
                'docstatus': 1,  # Submitted documents only
                'status': ['!=', 'Cancelled']
            },
            fields=[
                'name',
                'customer',
                'customer_name',
                'posting_date',
                'due_date',
                'grand_total',
                'outstanding_amount',
                'status'
            ],
            order_by='due_date asc'
        )

        # Process invoices and calculate metrics
        receivables = []
        today = getdate()

        for invoice in invoices:
            if invoice['outstanding_amount'] <= 0:
                status = 'Paid'
            elif getdate(invoice['due_date']) >= today:
                status = 'Due'
            else:
                status = 'Overdue'

            days_overdue = 0
            if status == 'Overdue':
                days_overdue = (today - getdate(invoice['due_date'])).days

            receivables.append({
                'id': invoice['name'],
                'customer': invoice['customer_name'] or invoice['customer'],
                'invoiceNo': invoice['name'],
                'amount': int(invoice['outstanding_amount']),
                'dueDate': str(invoice['due_date']),
                'status': status,
                'daysOverdue': days_overdue,
                'totalAmount': int(invoice['grand_total']),
                'paidAmount': int(invoice['grand_total'] - invoice['outstanding_amount'])
            })

        # Calculate key metrics
        total_receivable = sum(inv['amount'] for inv in receivables)
        paid_invoices = [inv for inv in receivables if inv['status'] == 'Paid']
        collected_month = sum(inv['paidAmount'] for inv in paid_invoices if
                            (today - getdate(inv['dueDate'])).days <= 30)

        overdue_receivables = [inv for inv in receivables if inv['status'] in ['Overdue']]
        overdue_amount = sum(inv['amount'] for inv in overdue_receivables)

        collection_rate = (sum(inv['paidAmount'] for inv in receivables) /
                          sum(inv['totalAmount'] for inv in receivables) * 100) if receivables else 0

        # Aging analysis
        aging_data = calculate_aging(receivables, today)

        # Top customers by outstanding amount
        top_customers = get_top_customers(receivables)

        # Status summary
        status_summary = get_status_summary(receivables)

        return {
            'receivables': receivables,
            'agingData': aging_data,
            'totalReceivable': total_receivable,
            'collectedMonth': collected_month,
            'overdueAmount': overdue_amount,
            'collectionRate': collection_rate,
            'topCustomers': top_customers,
            'statusCounts': status_summary['counts'],
            'statusAmounts': status_summary['amounts'],
            'lastUpdated': str(today)
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _('Accounts Receivable Error'))
        frappe.throw(_('Error fetching Accounts Receivable data: {0}').format(str(e)))


def calculate_aging(receivables, today):
    """Calculate aging report (Current, 31-60, 61-90, 90+)"""
    aging_buckets = {
        'Current (0-30)': {'min': 0, 'max': 30, 'amount': 0, 'color': 'text-green-600', 'bgColor': 'bg-green-500'},
        'Overdue (31-60)': {'min': 31, 'max': 60, 'amount': 0, 'color': 'text-orange-600', 'bgColor': 'bg-orange-500'},
        'Overdue (61-90)': {'min': 61, 'max': 90, 'amount': 0, 'color': 'text-red-600', 'bgColor': 'bg-red-500'},
        'Overdue (90+)': {'min': 91, 'max': float('inf'), 'amount': 0, 'color': 'text-red-700', 'bgColor': 'bg-red-700'}
    }

    for inv in receivables:
        days_diff = (today - getdate(inv['dueDate'])).days
        for bucket_name, bucket in aging_buckets.items():
            if bucket['min'] <= days_diff <= bucket['max']:
                bucket['amount'] += inv['amount']
                break

    total_amount = sum(bucket['amount'] for bucket in aging_buckets.values())

    aging_list = []
    for idx, (period, bucket) in enumerate(aging_buckets.items()):
        percentage = (bucket['amount'] / total_amount * 100) if total_amount > 0 else 0
        aging_list.append({
            'id': idx + 1,
            'period': period,
            'amount': int(bucket['amount']),
            'percentage': round(percentage),
            'color': bucket['color'],
            'bgColor': bucket['bgColor']
        })

    return aging_list


def get_top_customers(receivables):
    """Get top 5 customers by outstanding amount"""
    customer_totals = {}
    for inv in receivables:
        customer = inv['customer']
        customer_totals[customer] = customer_totals.get(customer, 0) + inv['amount']

    sorted_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)

    return [{'name': customer, 'amount': amount} for customer, amount in sorted_customers[:5]]

def get_top_suppliers(payables):
    """Get top 5 customers by outstanding amount"""
    supplier_totals = {}
    for inv in payables:
        supplier = inv['supplier']
        supplier_totals[supplier] = supplier_totals.get(supplier, 0) + inv['amount']

    sorted_suppliers = sorted(supplier_totals.items(), key=lambda x: x[1], reverse=True)

    return [{'name': supplier, 'amount': amount} for supplier, amount in sorted_suppliers[:5]]

def get_status_summary(invoices):
    """Get count and amount by status"""
    statuses = [inv.get("status") for inv in invoices]
    counts = {status.lower(): 0 for status in statuses}
    amounts = {status.lower(): 0 for status in statuses}

    for inv in invoices:
        status_key = inv['status'].lower()
        counts[status_key] += 1
        amounts[status_key] += inv['amount']

    return {'counts': counts, 'amounts': amounts}

def normalize_status_summary(summary):
    fixed = {
        "paid": 0,
        "overdue": 0,
        "due": 0,
        "draft": 0
    }

    for k, v in summary.get("amounts", {}).items():
        key = k.lower()
        if key in fixed:
            fixed[key] = v

    return fixed

@frappe.whitelist(allow_guest=True)
def export_ar_report():
    """
    Export Accounts Receivable report to CSV
    """
    try:
        data = get_accounts_receivable_data()

        # Create CSV content using StringIO
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['Customer', 'Invoice #', 'Amount', 'Due Date', 'Status', 'Days Overdue'])

        # Write data rows
        for inv in data.get('receivables', []):
            writer.writerow([
                inv.get('customer', ''),
                inv.get('invoiceNo', ''),
                inv.get('amount', 0),
                inv.get('dueDate', ''),
                inv.get('status', ''),
                inv.get('daysOverdue', 0)
            ])

        csv_content = output.getvalue()

        # Generate filename with current date
        filename = 'accounts_receivable_{}.csv'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))

        # Return as downloadable file
        frappe.response['type'] = 'download'
        frappe.response['filename'] = filename
        frappe.response['filecontent'] = csv_content.encode('utf-8')

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _('Export AR Report Error'))
        frappe.throw(_('Error exporting report: {0}').format(str(e)))

# ===========================================================
#  Accounts Payable
# ===========================================================

@frappe.whitelist(allow_guest=True)
def get_accounts_payable_data(filters=None):
    """
    Fetch Accounts Payable data from ERPNext
    Returns comprehensive PR analytics and invoice details
    """
    try:
        # Parse filters
        if isinstance(filters, str):
            filters = frappe.parse_json(filters)
        filters = filters or {}

        # Build filters
        invoice_filters = {}
        # Optional filters
        if filters.get("supplier"):
            invoice_filters["supplier"] = filters.get("supplier")

        if filters.get("from_date") and filters.get("to_date"):
            invoice_filters["posting_date"] = [
                "between",
                [filters.get("from_date"), filters.get("to_date")]
            ]
        if filters.get("status"):
            invoice_filters["status"] = filters.get("status")

        if filters.get("invoice_no"):
            invoice_filters["name"] = filters.get("invoice_no")

        # Get all unpaid and partially paid invoices
        invoices = frappe.get_list(
            'Purchase Invoice',
            filters=invoice_filters,
            fields=[
                'name',
                'supplier',
                'supplier_name',
                'posting_date',
                'due_date',
                'grand_total',
                'outstanding_amount',
                'status'
            ],
            order_by='due_date asc'
        )

        # Process invoices and calculate metrics
        payables = []
        today = getdate()

        for invoice in invoices:
            days_overdue = 0
            if invoice.get("status") == 'Overdue' and invoice.get("due_date"):
                days_overdue = (
                    today - getdate(invoice['due_date'])
                ).days

            payables.append({
                'id': invoice['name'],
                'supplier': invoice['supplier_name'] or invoice['supplier'],
                'invoiceNo': invoice['name'],
                'amount': int(invoice['outstanding_amount']),
                'dueDate': str(invoice['due_date']),
                'status': invoice.get("status"),
                'daysOverdue': days_overdue,
                'totalAmount': int(invoice['grand_total']),
                'paidAmount': int(invoice['grand_total'] - invoice['outstanding_amount'])
            })

        # Calculate key metrics
        total_payable = sum(inv['amount'] for inv in payables)
        paid_invoices = [inv for inv in payables if inv['status'] == 'Paid']
        collected_month = sum(inv['paidAmount'] for inv in paid_invoices if
                            (today - getdate(inv['dueDate'])).days <= 30)

        overdue_payable = [inv for inv in payables if inv['status'] in ['Overdue']]
        overdue_amount = sum(inv['amount'] for inv in overdue_payable)

        collection_rate = (sum(inv['paidAmount'] for inv in payables) /
                          sum(inv['totalAmount'] for inv in payables) * 100) if payables else 0

        # Aging analysis
        aging_data = calculate_aging(payables, today)

        # Top customers by outstanding amount
        top_suppliers = get_top_suppliers(payables)

        # Status summary
        status_summary = get_status_summary(payables)

        return {
            'payables': payables,
            'agingData': aging_data,
            'totalPayable': total_payable,
            'collectedMonth': collected_month,
            'overdueAmount': overdue_amount,
            'collectionRate': collection_rate,
            'topSuppliers': top_suppliers,
            'statusCounts': normalize_status_summary(status_summary),
            'statusAmounts': normalize_status_summary(status_summary),
            'lastUpdated': str(today)
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _('Accounts Receivable Error'))
        frappe.throw(_('Error fetching Accounts Receivable data: {0}').format(str(e)))


# ============================================
# EXPORT ACCOUNTS PAYABLE REPORT
# ============================================

@frappe.whitelist(allow_guest=True)
def export_ap_report():
    """
    Export Accounts Payable report to CSV
    """
    try:
        # Get AP data
        data = get_accounts_payable_data()

        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Supplier',
            'Bill #',
            'Amount',
            'Due Date',
            'Status',
            'Days Overdue'
        ])

        # Write data rows
        for bill in data.get('payables', []):
            writer.writerow([
                bill.get('supplier', ''),
                bill.get('invoiceNo', ''),
                f"${bill.get('amount', 0):,.2f}",
                bill.get('dueDate', ''),
                bill.get('status', ''),
                bill.get('daysOverdue', 0)
            ])

        csv_content = output.getvalue()

        # Generate filename
        filename = f'accounts_payable_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        # Set response type for file download
        frappe.response['type'] = 'download'
        frappe.response['filename'] = filename
        frappe.response['filecontent'] = csv_content

        return {
            'success': True,
            'message': 'Report exported successfully',
            'filename': filename
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _('Export AP Report Error'))
        frappe.throw(_('Error exporting report: {0}').format(str(e)))
