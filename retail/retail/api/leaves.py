# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, date_diff, add_days
from datetime import datetime, timedelta


class LeaveRequest(Document):
	"""Leave Request Document"""

	def validate(self):
		"""Validate Leave Request"""
		self.validate_mandatory_fields()
		self.validate_date_range()
		self.calculate_number_of_days()
		self.validate_leave_balance()

	def validate_mandatory_fields(self):
		"""Validate all mandatory fields"""
		mandatory_fields = ['employee', 'leave_type', 'company', 'from_date', 'to_date', 'leave_approver']

		for field in mandatory_fields:
			if not self.get(field):
				frappe.throw(f'{frappe.unscrub(field)} is mandatory')

	def validate_date_range(self):
		"""Validate from_date is before to_date"""
		from_date = getdate(self.from_date)
		to_date = getdate(self.to_date)

		if from_date > to_date:
			frappe.throw('From Date must be before or equal to To Date')

		# Check if dates are in the past
		today = getdate()
		if from_date < today:
			frappe.throw('Cannot apply leave for past dates')

	def calculate_number_of_days(self):
		"""Calculate number of days between from_date and to_date"""
		from_date = getdate(self.from_date)
		to_date = getdate(self.to_date)

		# Calculate days (inclusive of both start and end date)
		days = date_diff(to_date, from_date) + 1
		self.number_of_days = days

	def validate_leave_balance(self):
		"""Validate if employee has sufficient leave balance"""
		employee = frappe.get_doc('Employee', self.employee)
		leave_type = frappe.get_doc('Leave Type', self.leave_type)

		# Get total approved leaves for this leave type
		approved_leaves = frappe.db.sql("""
			SELECT SUM(number_of_days) FROM `tabLeave Request`
			WHERE employee = %s
			AND leave_type = %s
			AND status = 'Approved'
			AND docstatus = 1
			AND from_date >= %s
		""", (self.employee, self.leave_type, frappe.utils.get_first_day(self.from_date)), as_list=True)

		used_days = approved_leaves[0][0] if approved_leaves[0][0] else 0
		available_balance = leave_type.total_leaves_allowed - used_days

		if self.number_of_days > available_balance:
			frappe.throw(f'Insufficient leave balance. Available: {available_balance} days, Requested: {self.number_of_days} days')

	def on_submit(self):
		"""On Submit - Update leave balance"""
		self.update_leave_allocation()

	def on_cancel(self):
		"""On Cancel - Revert leave balance"""
		self.update_leave_allocation(is_cancel=True)

	def update_leave_allocation(self, is_cancel=False):
		"""Update employee leave allocation"""
		if self.status != 'Approved':
			return

		leave_allocation = frappe.db.get_value(
			'Leave Allocation',
			filters={'employee': self.employee, 'leave_type': self.leave_type, 'docstatus': 1},
			fieldname=['name']
		)

		if leave_allocation:
			doc = frappe.get_doc('Leave Allocation', leave_allocation[0])
			if is_cancel:
				doc.number_of_leaves_allocated += self.number_of_days
			else:
				doc.number_of_leaves_allocated -= self.number_of_days
			doc.save()

	def before_submit(self):
		"""Before Submit"""
		if self.status == 'Rejected':
			frappe.throw('Cannot submit a rejected leave request')


@frappe.whitelist(allow_guest=True)
def create_leave_request(employee, employee_name, leave_type, company, from_date, to_date,
						 number_of_days, reason, leave_approver, leave_approver_name, status='Pending'):
	"""Create a new leave request"""
	try:
		leave_request = frappe.new_doc('Leave Application')
		leave_request.employee = employee
		leave_request.employee_name = employee_name
		leave_request.leave_type = leave_type
		leave_request.company = company
		leave_request.from_date = from_date
		leave_request.to_date = to_date
		leave_request.number_of_days = number_of_days
		leave_request.reason = reason
		leave_request.leave_approver = leave_approver
		leave_request.leave_approver_name = leave_approver_name
		leave_request.status = status
		leave_request.insert()
		frappe.db.commit()

		return {
			'status': 'success',
			'message': 'Leave request created successfully',
			'data': leave_request.as_dict()
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'create_leave_request')
		return {
			'status': 'error',
			'message': str(e),
			'data': {}
		}


@frappe.whitelist(allow_guest=True)
def update_leave_request(name, employee, employee_name, leave_type, company, from_date, to_date,
						 number_of_days, reason, leave_approver, leave_approver_name, status):
	"""Update an existing leave request"""
	try:
		leave_request = frappe.get_doc('Leave Application', name)
		leave_request.employee = employee
		leave_request.employee_name = employee_name
		leave_request.leave_type = leave_type
		leave_request.company = company
		leave_request.from_date = from_date
		leave_request.to_date = to_date
		leave_request.number_of_days = number_of_days
		leave_request.reason = reason
		leave_request.leave_approver = leave_approver
		leave_request.leave_approver_name = leave_approver_name
		leave_request.status = status
		leave_request.save()
		frappe.db.commit()

		return {
			'status': 'success',
			'message': 'Leave request updated successfully',
			'data': leave_request.as_dict()
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'update_leave_request')
		return {
			'status': 'error',
			'message': str(e),
			'data': {}
		}


@frappe.whitelist(allow_guest=True)
def get_leave_requests(employee=None, status=None, leave_type=None, company=None, from_date=None, to_date=None, leave_approver=None):
	"""Get all leave requests with optional filters"""
	try:
		filters = {}

		if employee:
			filters['employee'] = employee
		if status:
			filters['status'] = status
		if leave_type:
			filters['leave_type'] = leave_type
		if company:
			filters['company'] = company
		if leave_approver:
			filters['leave_approver'] = leave_approver

		leave_requests = frappe.get_list(
			'Leave Application',
			filters=filters,
			fields=['*'],
			order_by='creation desc'
		)

		# Filter by date range if provided
		if from_date:
			from_date = getdate(from_date)
			leave_requests = [lr for lr in leave_requests if getdate(lr.from_date) >= from_date]

		if to_date:
			to_date = getdate(to_date)
			leave_requests = [lr for lr in leave_requests if getdate(lr.to_date) <= to_date]

		return {
			'status': 'success',
			'message': 'Leave requests fetched successfully',
			'data': leave_requests
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'get_leave_requests')
		return {
			'status': 'error',
			'message': str(e),
			'data': []
		}


@frappe.whitelist(allow_guest=True)
def delete_leave_request(name):
	"""Delete a leave request"""
	try:
		frappe.delete_doc('Leave Application', name)
		frappe.db.commit()

		return {
			'status': 'success',
			'message': 'Leave request deleted successfully'
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'delete_leave_request')
		return {
			'status': 'error',
			'message': str(e)
		}


@frappe.whitelist(allow_guest=True)
def approve_leave_request(name):
	"""Approve a leave request"""
	try:
		leave_request = frappe.get_doc('Leave Application', name)
		leave_request.status = 'Approved'
		leave_request.save()
		frappe.db.commit()

		return {
			'status': 'success',
			'message': 'Leave request approved successfully'
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'approve_leave_request')
		return {
			'status': 'error',
			'message': str(e)
		}


@frappe.whitelist(allow_guest=True)
def reject_leave_request(name):
	"""Reject a leave request"""
	try:
		leave_request = frappe.get_doc('Leave Application', name)
		leave_request.status = 'Rejected'
		leave_request.save()
		frappe.db.commit()

		return {
			'status': 'success',
			'message': 'Leave request rejected successfully'
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'reject_leave_request')
		return {
			'status': 'error',
			'message': str(e)
		}


@frappe.whitelist(allow_guest=True)
def cancel_leave_request(name):
	"""Cancel a leave request"""
	try:
		leave_request = frappe.get_doc('Leave Application', name)
		leave_request.status = 'Cancelled'
		leave_request.save()
		frappe.db.commit()

		return {
			'status': 'success',
			'message': 'Leave request cancelled successfully'
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'cancel_leave_request')
		return {
			'status': 'error',
			'message': str(e)
		}


@frappe.whitelist(allow_guest=True)
def get_leave_balance(employee):
	"""Get leave balance for an employee"""
	try:
		leave_allocations = frappe.get_list(
			'Leave Allocation',
			filters={'employee': employee, 'docstatus': 1},
			fields=['leave_type', 'number_of_leaves_allocated']
		)

		balance = {}

		for allocation in leave_allocations:
			leave_type = allocation.leave_type
			allocated = allocation.number_of_leaves_allocated

			# Get used leaves
			used_leaves = frappe.db.sql("""
				SELECT SUM(number_of_days) FROM `tabLeave Request`
				WHERE employee = %s
				AND leave_type = %s
				AND status = 'Approved'
				AND docstatus = 1
			""", (employee, leave_type), as_list=True)

			used = used_leaves[0][0] if used_leaves[0][0] else 0
			remaining = allocated - used

			balance[leave_type] = {
				'allocated': allocated,
				'used': used,
				'remaining': remaining
			}

		return {
			'status': 'success',
			'message': 'Leave balance fetched successfully',
			'data': balance
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'get_leave_balance')
		return {
			'status': 'error',
			'message': str(e),
			'data': {}
		}


@frappe.whitelist(allow_guest=True)
def get_leave_statistics(employee=None, company=None, start_date=None, end_date=None):
	"""Get leave statistics"""
	try:
		filters = {}

		if employee:
			filters['employee'] = employee
		if company:
			filters['company'] = company

		leave_requests = frappe.get_list(
			'Leave Application',
			filters=filters,
			fields=['employee', 'leave_type', 'status', 'number_of_days', 'from_date']
		)

		statistics = {
			'total_leaves': 0,
			'approved_leaves': 0,
			'pending_leaves': 0,
			'rejected_leaves': 0,
			'cancelled_leaves': 0,
			'by_type': {}
		}

		for leave in leave_requests:
			# Filter by date range if provided
			if start_date and getdate(leave.from_date) < getdate(start_date):
				continue
			if end_date and getdate(leave.from_date) > getdate(end_date):
				continue

			statistics['total_leaves'] += leave.number_of_days

			if leave.status == 'Approved':
				statistics['approved_leaves'] += leave.number_of_days
			elif leave.status == 'Pending':
				statistics['pending_leaves'] += leave.number_of_days
			elif leave.status == 'Rejected':
				statistics['rejected_leaves'] += leave.number_of_days
			elif leave.status == 'Cancelled':
				statistics['cancelled_leaves'] += leave.number_of_days

			# By leave type
			if leave.leave_type not in statistics['by_type']:
				statistics['by_type'][leave.leave_type] = {
					'total': 0,
					'approved': 0,
					'pending': 0
				}

			statistics['by_type'][leave.leave_type]['total'] += leave.number_of_days
			if leave.status == 'Approved':
				statistics['by_type'][leave.leave_type]['approved'] += leave.number_of_days
			elif leave.status == 'Pending':
				statistics['by_type'][leave.leave_type]['pending'] += leave.number_of_days

		return {
			'status': 'success',
			'message': 'Leave statistics fetched successfully',
			'data': statistics
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'get_leave_statistics')
		return {
			'status': 'error',
			'message': str(e),
			'data': {}
		}
