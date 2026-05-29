// api.js File //

import { api } from './auth.js'
import { createResource, createDocumentResource, createListResource, call } from 'frappe-ui'

export const getTerritoriesApi = async () => {
    const resource =  createListResource({
          doctype: 'Territory',
          fields: JSON.stringify(['name']),
          auto: true,
          limit_page_length: 100,

      })
      await resource.list.promise
      console.log("API Territories: ", resource.data)
      return resource.data || []
}

export const getCountriesApi = async () => {
  const resource = createListResource({
        doctype: 'Country',
        fields: JSON.stringify(['name']),
        limit_page_length: 300,
      })
      await resource.list.promise
      console.log("API Countries: ", resource.data)
      return resource.data || []
}

export const getCompanies = async () => {
try {
    const response = await call("retail.retail.api.common.load_companies")
    return response
} catch (err) {
    console.error("Error loading companies:", err)
    return []
}
}

export const getFiscalYears = async () => {
try {
    const response = await call("retail.retail.api.common.load_fiscal_years")
    return response
} catch (err) {
    console.error("Error loading fiscal years:", err)
    return []
}
}

// ==================================================
// API Get Notifications Log
// ==================================================
export const getNotifications = async (user) => {
  try {
    const resource = createListResource({
      doctype: 'Notification Log',
      fields: [
        'name', 'subject', 'email_content', 'creation',
        'read', 'type', 'document_type', 'document_name',
        'for_user', 'from_user'
      ],
      filters: { for_user: user },
      orderBy: 'creation desc',
      pageLength: 20,
      debug: 0,
      // make the first request automatically
      auto: true,
    })

    resource.fetch()
    await resource.list.promise
    console.log("API Get Notifications: ", resource.data)
    return resource.data || []
  } catch (err) {
    console.error('Error loading notifications:', err)
    return []
  }
}


export const updateNotificationStatus = async (notificationId, read) => {
  try {
    const response = await api.put(`/api/resource/Notification Log/${notificationId}`, {
      read: read ? 1 : 0
    })
    return response.data
  } catch (err) {
    console.error('Error updating notification:', err)
    throw err
  }
}

export const markNotificationAsRead = async (notificationId) => {
  try {
    const response = await call('frappe.client.set_value', {
      doctype: 'Notification Log',
      name: notificationId,
      fieldname: { read: 1 }
    })
    return response.status === 200
  } catch (err) {
    console.error('Error marking notification as read:', err)
    return false
  }
}

export const markAllNotificationsAsRead = async (notificationIds) => {
  try {
    const promises = notificationIds.map(id =>
      call('frappe.client.set_value', {
        doctype: 'Notification Log',
        name: id,
        fieldname: { read: 1 }
      })
    )
    await Promise.all(promises)
    return true
  } catch (err) {
    console.error('Error marking all notifications as read:', err)
    return false
  }
}

export const deleteNotificationAPI = async (notificationId) => {
  try {
    const response = await api.delete(`/api/resource/Notification Log/${notificationId}`)
    return response.data
  } catch (err) {
    console.error('Error deleting notification:', err)
    throw err
  }
}
//======================================================
// API Get Messages
// =====================================================
export const getMessages = async () => {
  try {
    const resources = createListResource({
        doctype:'Communication',
        fields: [
          'name',
          'subject',
          'content',
          'sender',
          'creation'
        ],
        filters: {
          communication_type: 'Chat'
        },
        order_by: 'creation desc',
        limit_page_length: 10
      })

    resources.fetch()
    await resources.list.promise
    return resources.data || []
  } catch (err) {
    console.error('Error loading messages:', err)
    return []
  }
}

export const getCurrentUserInfoApi = async () => {
  try {
    console.log('🚀 START getCurrentUserInfoApi')

    // 1. Get current user
    const currentUser = createResource({
      url: 'retail.retail.api.auth.get_logged_user'
    })

    console.log('📦 currentUser resource created:', currentUser)

    await currentUser.reload()

    if (currentUser.error) {
      throw new Error(`get_logged_user failed: ${currentUser.error}`)
    }

    console.log('📥 currentUser response raw:', currentUser.data)

    const user = currentUser.data

    console.log('👤 extracted user:', user)

    if (!user || user === 'Guest') {
      console.warn('⚠️ Guest or empty user')
      return null
    }

    // 2. Get User Doc
    const userDoc = createDocumentResource({
      doctype: 'User',
      name: user
    })

    console.log('📦 userDoc resource created:', userDoc)

    await userDoc.reload()

    console.log('📥 userDoc raw doc:', userDoc.doc)

    const userData = userDoc.doc

    // 3. Roles
    console.log('🔐 fetching roles for:', user)

    // const userRoles = await getUserRoles(user)

    // console.log('🎭 roles result:', userRoles)

    const result = {
      user,
      email: userData?.email || '',
      full_name: userData?.full_name || user,
      user_image: userData?.user_image || '',
      // roles: userRoles || []
    }

    console.log('✅ FINAL RESULT:', result)

    return result

  } catch (error) {
    console.error('❌ ERROR in getCurrentUserInfoApi:', error)
    throw error
  }
}

//======================================================
// API Get Users
// =====================================================
export const getUsers = async () => {
    try {

        const result = createListResource({
            doctype: 'User',
            fields:['name'],
            auto: true,
            limit_page_length: 100
        })
        result.fetch()
        await result.list.promise
        console.log("API Get Users",result.data)
        return result.data || []

    } catch (e) {
        console.log('error API Get Users', e)
    }
}

export const getUserRoles = async (user) => {
  const res = await call(
    'frappe.core.doctype.user.user.get_roles',
    { uid: user }
  )

  console.log("🛡️ Roles raw response:", res)

  const roles = res || []

  console.log("🛡️ Roles parsed:", roles)

  return roles
}

// Suppliers Invoice
export const getSuppliersBills = async (filters = {}) => {
    try {
        const response = await call('retail.retail.api.bills.get_all_bills_invoices',
            { params: filters }
        );

        return response; // Assuming the invoices are in response.data.data
    } catch (error) {
        console.error('Error fetching invoices:', error);
        throw error;
    }
}


// ─── Get Price Lists ──────────────────────────────────────────────────────────
export const getPriceLists = async () => {
  try {
    const response = await call(
      'retail.retail.api.common.get_price_lists'
    )
        console.log("retail.retail.api.common.\get_price_lists", response)
    return response || []
  } catch (error) {
    console.error('❌ getPriceLists:', error)
    return []
  }
}


// ─── Get Warehouses ───────────────────────────────────────────────────────────

export const getWarehouses = async () => {
  try {
    const response = await call(
      'retail.retail.api.common.get_warehouses'
    )

    console.log("retail.retail.api.common.get_warehouses", response)
    return response || []
  } catch (error) {
    console.error('❌ getWarehouses:', error)
    return []
  }
}
// POST Create Sample Items

export const createSampleItems = async (sample_products) => {
    try {
        const response = await call('retail.retail.api.setting.create_all_sample_items',
            { sample_products: sample_products }
        )
        console.log("api createSampleItems", response)
        return response
    }
    catch (error) {

    }

}

export const deleteSampleItems = async () => {
    try {
        const response = await call(
            'retail.retail.api.setting.delete_all_sample_items'
        )
        console.log("🗑️ deleteSampleItems:", response)
        return response
    } catch (error) {
        console.error("❌ deleteSampleItems error:", error)
    }
}

// *******************************
//3  Get Customers Financial Data
// *******************************
export const CustomersFinancialData = async (pos_profile) => {
    try {
        const response = await call('retail.retail.api.customer.get_customers_financial_data',
           { pos_profile: JSON.stringify(pos_profile)
        })
        console.log("api CustomersFinancialData", response.data.message)
        return response
    }
    catch (error) {
        console.error(error)
    }

}

// ***********************************
//4 Get One Customer Full Details
// ***********************************
export const fetchCustomerProfileApi = async (customer_name) => {
    try {
        const response = await call('retail.retail.api.customer.get_customer_profile',
           { customer_name: customer_name }
          )
        console.log("api fetchCustomerProfileApi", response.data.message)
        return response
    }
    catch (error) {
        console.error(error)
    }

}

// *******************************
// 1 Get Suppliers Financial Data
// *******************************
export const SuppliersFinancialData = async (pos_profile) => {
    try {
        const response = await call('retail.retail.api.supplier.get_suppliers_financial_data', {
            params: { pos_profile: JSON.stringify(pos_profile) }
        })
        console.log("api SuppliersFinancialData", response.data.message)
        return response
    }
    catch (error) {
        console.error(error)
    }

}

// ***********************************
//  2 Get One Supplier Full Details
// ***********************************
export const SupplierFinancialDetails = async (supplier_name) => {
    try {
        const response = await call('retail.retail.api.supplier.get_supplier_profile', {
            params: { supplier_name: supplier_name }
        })
        console.log("api", response.data.message)
        return response
    }
    catch (error) {
        console.error(error)
    }

}

// =========================================================
//  Api Create Supplier
// =========================================================

export const createSupplierApi = async (supplierData) => {
    try {
        const response = await call('retail.retail.api.supplier.create_supplier', {
            supplier_name: supplierData.supplier_name || null,
            supplier_group: supplierData.supplier_group || null,
            supplier_type: supplierData.supplier_type || null,
            mobile_no: supplierData.mobile_no || null,
            email_id: supplierData.email_id || null,
            address_line1: supplierData.address_line1 || '',
            address_line2: supplierData.address_line2 || '',
            city: supplierData.city || '',
            state: supplierData.state || '',
            country: supplierData.country || '',
            pin_code: supplierData.pin_code || '',
            status: 0,
            custom_note: supplierData.custom_note || null,
        })
        console.log("api createSupplier", response)
        return response || response.data
    }
    catch (error) {
        console.error("❌ createSupplier error:", error)
    }

}

// =========================================================
//  Api Update Supplier
// =========================================================

export const updateSupplierApi = async (supplierName, supplierData) => {
    try {
        console.log("Updating supplier with data:", supplierData, "and name:", supplierName)
        const response = await call('retail.retail.api.supplier.update_supplier', {
            supplier_name: supplierName || null,
            data: JSON.stringify(supplierData)
        })
        console.log("api updateSupplier", response)
        return response || response.data
    }
    catch (error) {
        console.error("❌ updateSupplier error:", error)
    }

}

// =========================================================
//  Api Update Supplier constacts
// =========================================================
export const updateSupplierContactsApi = async (supplier_name, contacts) => {
    try {
      console.log("Updating Contacts :", contacts, "and name:", supplier_name)
        const response = await call('retail.retail.api.supplier.update_supplier_contacts', {
            supplier_name: supplier_name,
            contacts_json: JSON.stringify(contacts)
        })
        console.log("api updateSupplierContactsApi", response)
        return response || response.data
    }
    catch (error) {
        console.error("❌ updateSupplierContactsApi error:", error)
    }

}

// =========================================================
//  Api Delete Supplier
// =========================================================

export const deleteSupplierApi = async (supplier_name) => {
    try {
        const response = await call('retail.retail.api.supplier.delete_supplier', {
            supplier_name: supplier_name
        })
        console.log("api deleteSupplier", response)
        return response || response.data
    }
    catch (error) {
        console.error("❌ deleteSupplier error:", error)
    }

}
// =========================================================
//  Api Get Suppliers Groups
// =========================================================
export const getSupplierGroups = async () => {
    try {
        const response = await call('retail.retail.api.supplier.get_supplier_groups')
        console.log("api getSupplierGroups", response)
        return response || response.data
    }
    catch (error) {
        console.error("❌ getSupplierGroups error:", error)
    }

}

// =========================================================
//  Api Create Payment Entry
// =========================================================

export const createPaymentEntry = async (paymentData) => {
    try {
        const response = await call('retail.retail.api.payment_entry.process_pos_payment', {
            payment_data: JSON.stringify(paymentData)
        })
        console.log("api createPaymentEntry", response)
        return response || response.data
    }
    catch (error) {
        console.error("❌ createPaymentEntry error:", error)
    }

}

// ======================================================================
// Income Statement Report APIs
// File: retail.retail.api.reports.{method}
// ======================================================================
export const getIncomeStatementYearly = async (company = null) => {
  try {
    const response = await call('retail.retail.api.reports.get_income_statement_yearly', {
      params: {
        company: company || 'pos'
      }
    })
    console.log("✅ getIncomeStatementYearly", response)
    return response
  } catch (error) {
    console.error("❌ getIncomeStatementYearly error:", error)
    throw error
  }
}


export const getIncomeStatementMonthly = async (company = null) => {
  try {
    const response = await call('retail.retail.api.reports.get_income_statement_monthly', {
      params: {
        company: company || 'pos'
      }
    })
    console.log("✅ getIncomeStatementMonthly", response)
    return response
  } catch (error) {
    console.error("❌ getIncomeStatementMonthly error:", error)
    throw error
  }
}

export const getIncomeStatementByPeriod = async (params) => {
  try {
    const response = await call('retail.retail.api.reports.get_income_statement_by_period', {
      params: {
        company: params.company || 'pos',
        from_date: params.from_date,
        to_date: params.to_date
      }
    })
    console.log("✅ getIncomeStatementByPeriod", response)
    return response
  } catch (error) {
    console.error("❌ getIncomeStatementByPeriod error:", error)
    throw error
  }
}

/* =========================================
   1. api.js - API Staff - Create Employee
========================================= */

export const createEmployee = async (employeeData) => {
  try {
    const response = await call(
      'retail.retail.api.staff.create_employee',
      employeeData
    )

    // Return the entire message object (which contains status and message)
    return response
  } catch (err) {
    console.error('Error Create Employee:', err)
    // Return error in consistent format
    return {
      status: 'error',
      message: err?.response?.data?.message || err.message || 'Unknown error occurred'
    }
  }
}

/* =========================================
   2. api.js - API Staff - Get Employees
========================================= */
export const getEmployeesApi = async (company, department) => {
  try {
    const response = await call(
      'retail.retail.api.staff.get_employees',
      {
        params: {
          // Add any required parameters here
          company,
          department,
        }
      }
    )

    // Return the entire message object (which contains status and message)
    return response.data
  } catch (err) {
    console.error('Error Get Employees:', err)
    // Return error in consistent format
    return {
      status: 'error',
      message: err?.response?.data?.message || err.message || 'Unknown error occurred'
    }
  }
}

/* =========================================
   3. api.js - API Staff - Delete Employee
========================================= */
export const deleteEmployeeApi = async (employeeName) => {
  try {
    // const response = await call('retail.retail.api.staff.delete_employee', {employee_name:employeeName})
    const response = await api.delete(
    `retail.retail.api.staff.delete_employee?employee_name=${employeeName}`
  );

    // Return the entire message object (which contains status and message)
    return response
  } catch (err) {
    console.error('Error Delete Employee:', err)
    // Return error in consistent format
    return {
      status: 'error',
      message: err?.response?.data?.message || err.message || 'Unknown error occurred'
    }
  }
}
/* =========================================
   4. api.js - API Staff - Get One Employee Details
========================================= */
export const getEmployeeApi = async (employeeName) => {
  try {
    const response = await call(
      `retail.retail.api.staff.get_one_employee_details?employee_name=${encodeURIComponent(employeeName)}`
    )

    // Log the full response to see what we're getting
    console.log('Raw response:', response)
    console.log('Response data:', response.data)

    // Frappe wraps the actual response in response.data.message
    const data = response.data.message

    if (typeof data === 'string') {
      // If it's a string, try to parse it
      const parsed = JSON.parse(data)
      return parsed
    }

    // Otherwise return as is
    return data
  } catch (err) {
    console.error('Error Get One Employee Details:', err)
    console.error('Error response:', err?.response?.data)
    return {
      status: 'error',
      message: err?.response?.data?.message || err.message || 'Unknown error occurred'
    }
  }
}

/* =========================================
   5. api.js - API Staff - Get Salary History
========================================= */
export const getSalaryHistory = async (employeeName) => {
  try {
    const response = await call(
      `retail.retail.api.staff.get_salary_history?employee_name=${encodeURIComponent(employeeName)}`
    )
    return response
  } catch (err) {
    console.error('Error getting salary history:', err)
    return {
      status: 'error',
      message: err?.message || 'Unknown error',
      data: []
    }
  }
}

export const getAttendanceStats = async (employeeName, options = {}) => {

  try {
    let url = `retail.retail.api.staff.get_attendance_stats?employee_name=${encodeURIComponent(employeeName)}`

    // إذا تم تحديد شهر
    if (options.month) {
      url += `&month=${options.month}`
    }

    // إذا تم تحديد تاريخين
    if (options.from_date && options.to_date) {
      url += `&from_date=${options.from_date}&to_date=${options.to_date}`
    }

    const response = await call(url)
    console.log('Attendance Stats Response api js:', response)
    return response
  } catch (err) {
    console.error('Error getting attendance stats:', err)
    return {
      status: 'error',
      message: err?.message || 'Unknown error',
      data: {}
    }
  }
}

export const getPerformance = async (employeeName) => {
  try {
    const response = await call(
      `retail.retail.api.staff.get_performance?employee_name=${encodeURIComponent(employeeName)}`
    )
    return response
  } catch (err) {
    console.error('Error getting performance:', err)
    return {
      status: 'error',
      message: err?.message || 'Unknown error',
      data: {}
    }
  }
}
/* =========================================
   1. api.js - API Staff - Create Department
========================================= */
export const createDepartmentApi = async (departmentData) => {
  try {
    const response = await call(
      'retail.retail.api.staff.create_department',
      departmentData
    )

    // Return the entire message object (which contains status and message)
    return response
  } catch (err) {
    console.error('Error Create Department:', err)
    // Return error in consistent format
    return {
      status: 'error',
      message: err?.response?.data?.message || err.message || 'Unknown error occurred'
    }
  }
}
/* =========================================
// 2. api.js - API Staff - Get Departments
========================================= */
export const getDepartmentsApi = async (company) => {
  try {
    const response = await call(
      'retail.retail.api.staff.get_departments',
      {
        params: { company }
      }
    )

    // Return the entire message object (which contains status and message)
    return response.data
  } catch (err) {
    console.error('Error Get Departments:', err)
    // Return error in consistent format
    return {
      status: 'error',
      message: err?.response?.data?.message || err.message || 'Unknown error occurred'
    }
  }
}
/* =========================================
   3. api.js - API Staff - Delete Department
========================================= */
export const deleteDepartmentApi = async (departmentName) => {
  try {
    const response = await api.delete(
      'retail.retail.api.staff.delete_department',
       { department_name: departmentName }

    )
    return response
  } catch (err) {
    console.error('Error Delete Department:', err)
  }
}

/* =========================================
// 1. api.js - API Staff  - Get Desgnations
========================================= */
export const getDesignationsApi = async () => {
  try {
    const response = await call(
      'retail.retail.api.staff.get_designations'
    )
    return response.data
  } catch (err) {
    console.error('Error Get Designations:', err)
  }
}

/* =========================================
2- api.js - API Staff  - Create Desgnation
========================================= */
export const createDesignationApi = async (designationData) => {
  try {
    const response = await call(
      'retail.retail.api.staff.create_designation',
      designationData
    )
    return response
  } catch (err) {
    console.error('Error Create Designation:', err)
  }
}

/* =========================================
3- api.js - API Staff  - Delete Desgnation
========================================= */
export const deleteDesignationApi = async (designationName) => {

  try {
    const response = await api.delete(
      'retail.retail.api.staff.delete_designation',
       { designation_name: designationName }

    )
    return response
  } catch (err) {
    console.error('Error Delete Designation:', err)
    // Return error in consistent format
    return {
      status: 'error',
      message: err?.response?.data?.message || err.message || 'Unknown error occurred'
    }
  }
}

/* =========================================
4- api.js - API Staff  - Get Roles
========================================= */

export const getRolesApi = async () => {
  try {
        const response = await call(
      'retail.retail.api.staff.get_roles'
    )
        return response
    } catch (err) {
        console.error('Error Get Roles:', err)
    }
}

// ==========================================================
// Delete Role API
// ==========================================================
export const deleteRoleApi = async (roleName) => {
    try {
        const response = await api.delete(
      'retail.retail.api.staff.delete_role',
      { role_name: roleName }
    )

        return response
    } catch (err) {
        console.error('Error Delete Role:', err)
    }
}

// ==========================================================
// Create Role API
// ==========================================================
export const createRoleApi = async (roleData) => {
    try {
        const response = await call('retail.retail.api.staff.create_role', roleData)
        return response
    } catch (err) {
        console.error('Error Create Role:', err)
    }
}
// ===========================================================================
// End Staff APIs attendance, departments, designations, roles
// ===========================================================================
export const createAttendanceRecord = async (attendanceData) => {
  try {
    const response = await call('retail.retail.api.attendance.create_attendance', {...attendanceData })

    return response
  } catch (err) {
    console.error('Error Create Attendance Record:', err)
    // Return error in consistent format
    return {
        status: 'error',
        message: err?.response?.data?.message || err.message || 'Unknown error occurred'
    }
  }
  }
// ===========================================================================
// Edit APIs attendance, departments, designations, roles
// ===========================================================================
export const EditAttendanceRecord = async (attendanceData) => {
    try {
        const response = await call('retail.retail.api.attendance.edit_attendance',
          {attendance_data: attendanceData}
          )

        return response
    } catch (err) {
        console.error('Error Create Attendance Record:', err)
    }
}
// ==========================================================================
// Delete Single Attendance Record
// ==========================================================================
export const deleteAttendanceApi = async (attendanceId) => {
  try {
    console.log('Deleting attendance record:', attendanceId)

    const res = await call(
      'retail.retail.api.attendance.cancel_and_delete_attendance',
       { name: attendanceId }
    )

    console.log('Delete Response:', res)

    return {
      status: res.status === 200 ? 'success' : 'error',
      data: res.data,
      message: 'Attendance record deleted successfully'
    }
  } catch (error) {
    console.error('Error deleting attendance record:', error)
    throw error
  }
}
// ==========================================================================
// Delete Multiple Attendance Records (Cancel + Delete)
// ==========================================================================
export const deleteMultipleAttendanceApi = async (attendanceIds) => {
  try {
    console.log('Deleting multiple attendance records:', attendanceIds)

    const response = await call('retail.retail.api.attendance.bulk_cancel_and_delete_attendance',
    { attendance_ids: attendanceIds }
    )
    return response

  } catch (error) {
    console.error('Error deleting multiple attendance records:', error)
  }
}

// ==========================================================================
// Delete Attendance by Date Range (Admin function)
// ==========================================================================
export const deleteAttendanceByDateRangeApi = async (startDate, endDate) => {
  try {
    console.log(`Deleting attendance records between ${startDate} and ${endDate}`)

    const res = await api.delete('/api/resource/Attendance', {
            filters: [
              ['Attendance', 'attendance_date', '>=', startDate],
              ['and'],
              ['Attendance', 'attendance_date', '<=', endDate]
            ]
      })

    return {
      status: res.status === 200 ? 'success' : 'error',
      data: res.data,
      message: 'Attendance records deleted successfully'
    }
  } catch (error) {
    console.error('Error deleting attendance by date range:', error)
    throw error
  }
}

// ==========================================================================
// Delete Attendance by Employee
// ==========================================================================
export const deleteAttendanceByEmployeeApi = async (employeeId, startDate = null, endDate = null) => {
  try {
    console.log(`Deleting attendance records for employee: ${employeeId}`)

    let filters = [['Attendance', 'employee', '=', employeeId]]

    if (startDate && endDate) {
      filters.push(['and'])
      filters.push(['Attendance', 'attendance_date', '>=', startDate])
      filters.push(['and'])
      filters.push(['Attendance', 'attendance_date', '<=', endDate])
    }

    const res = await api.delete('/api/resource/Attendance', {
      params: {
        filters: JSON.stringify(filters)
      }
    })

    return {
      status: res.status === 200 ? 'success' : 'error',
      data: res.data,
      message: 'Employee attendance records deleted successfully'
    }
  } catch (error) {
    console.error('Error deleting employee attendance:', error)
    throw error
  }
}

// ==========================================================================
// Get Api  employees Attendance APIs
// ==========================================================================

export const getAttendenceApi = async (filters = {}) => {
  try {
    const response = await call(
      'retail.retail.api.attendance.get_employee_attendance_history',
      {
        params: {
          filters: JSON.stringify(filters)
        }
      }
    )

    // Return the entire message object (which contains status and message)

    return response.data
  } catch (err) {
    console.error('Error Get Attendance Records:', err)
    // Return error in consistent format
    return {
      status: 'error',
      message: err?.response?.data?.message || err.message || 'Unknown error occurred'
    }
  }
}

// ==========================================================================
// Get Checkins
// ==========================================================================
export const getEmployeeCheckinsApi = async (employee_name, attendance_date) => {
  try {
    const res = await call('retail.retail.api.attendance.get_checkins_for_attendance', {
      params: {
        employee: employee_name,
        attendance_date: attendance_date
      }
    });
    return res.data;
  } catch (error) {
    console.error('Error fetching checkins:', error);
    throw error;
  }
};

// ==========================================================================
// Create Employee Checkin
// ==========================================================================
export const getCheckinsApi = async (filters) => {
  try {
    const response = await call(
      'retail.retail.api.attendance.get_checkins',
      {
        params: {
          filters: JSON.stringify(filters)
        }
      }
    )
    return response.data;
  } catch (error) {
    console.error('Error fetch checkins:', error);
    throw error;
  }
};


// ==========================================================================
// Create Employee Checkin
// ==========================================================================
export const createCheckinApi = async (data) => {
  try {
    const res = await call('/api/resource/Employee Checkin', {
      employee: data.employee,
      log_type: data.logType,
      time: data.time,
      skip_auto_attendance: data.skip_auto_attendance
    });
    return res.data;
  } catch (error) {
    console.error('Error creating checkin:', error);
    throw error;
  }
};

// ==========================================================================
// Update Checkin
// ==========================================================================
export const updateCheckinApi = async (checkinName, data) => {
  try {
    const res = await api.put(`/api/resource/Employee Checkin/${checkinName}`, {
      employee: data.employee,
      log_type: data.logType,
      time: data.time,
      skip_auto_attendance: data.skip_auto_attendance
    });
    return res.data.data;
  } catch (error) {
    console.error('Error updating checkin:', error);
    throw error;
  }
};

// ==========================================================================
// Delete Checkin
// ==========================================================================
export const deleteCheckinApi = async (checkinName) => {
  try {
    const res = await api.delete(`/api/resource/Employee Checkin/${checkinName}`);
    return res.data;
  } catch (error) {
    console.error('Error deleting checkin:', error);
    throw error;
  }
};

// ==========================================================================
// Mark Attendance from Checkins
// ==========================================================================
export const markAttendanceFromCheckinsApi = async (employee, attendance_date, status, checkinLogs) => {
  try {
    const res = await call('your_app.api.attendance.mark_attendance_and_link_log', {
      logs: checkinLogs,
      attendance_status: status,
      attendance_date: attendance_date,
      employee: employee
    });
    return res.data.message;
  } catch (error) {
    console.error('Error marking attendance:', error);
    throw error;
  }
};

// ==========================================================================
// Get Employee Attendance Summary
// ==========================================================================
export const getAttendanceSummaryApi = async (employee, month, year) => {
  try {
    const res = await call('your_app.api.attendance.get_monthly_attendance_summary', {
      params: {
        employee: employee,
        month: month,
        year: year
      }
    });
    return res.data.message || res.data;
  } catch (error) {
    console.error('Error fetching attendance summary:', error);
    throw error;
  }
};

// ==========================================================================
// Get Employee Attendance History
// ==========================================================================
export const getAttendanceHistoryApi = async (employee, from_date, to_date, limit = 30) => {
  try {
    const res = await call('your_app.api.attendance.get_employee_attendance_history', {
      params: {
        employee: employee,
        from_date: from_date,
        to_date: to_date,
        limit: limit
      }
    });
    return res.data.message || res.data;
  } catch (error) {
    console.error('Error fetching attendance history:', error);
    throw error;
  }
};

// ==========================================================================
// Get All Checkins (للصفحة الرئيسية)
// ==========================================================================
export const getAllCheckinsApi = async (filters = {}) => {
  try {
    const res = await call('/api/resource/Employee Checkin', {
      params: {
        fields: '["name", "employee", "employee_name", "log_type", "time", "attendance", "skip_auto_attendance"]',
        filters: JSON.stringify(filters),
        limit_page_length: 500
      }
    });
    return res.data.data;
  } catch (error) {
    console.error('Error fetching all checkins:', error);
    throw error;
  }
};

// ==========================================================================
// Bulk Mark Attendance
// ==========================================================================
export const bulkMarkAttendanceApi = async (data) => {
  try {
    const res = await call('your_app.api.attendance.bulk_mark_attendance', data);
    return res.data.message;
  } catch (error) {
    console.error('Error bulk marking attendance:', error);
    throw error;
  }
};

// ==========================================================================
// Check if Attendance Exists
// ==========================================================================
export const checkAttendanceExistsApi = async (employee, attendance_date) => {
  try {
    const res = await call('your_app.api.attendance.check_attendance_exists', {
      params: {
        employee: employee,
        attendance_date: attendance_date
      }
    });
    return res.data.message || res.data;
  } catch (error) {
    console.error('Error checking attendance:', error);
    throw error;
  }
};

// ==========================================================================
// Search Employee
// ==========================================================================
export const searchEmployeesApi = async (query) => {
  try {
    const res = await call('retail.retail.api.staff.search_employees', {
      params: {
        query: JSON.stringify(query),
      }
    });
    return res.data.message || res.data;
  } catch (error) {
    console.error('Error Search Employee:', error);
    throw error;
  }
};

// ==========================================================================
// API Process auto attendance
// ==========================================================================
export const processAutoAttendanceApi = async (shiftName) => {
  try {
    const res = await call(
      `retail.retail.api.shifts.process_auto_attendance_api`,
      {
        shift_name: shiftName
      }
    )

    return {
      status: res.status,
      data: res.data,
      message: 'تم معالجة حاضری بنجاح'
    }
  } catch (error) {
    console.error('Error processing auto attendance:', error)
    throw error
  }
}

// ==========================================================================
// Get all shift assignments with employee details
// ==========================================================================
export const fetchShiftAssignmentsApi = async (company = null) => {
  try {
    let filters = []

    if (company) {
      filters.push(['company', '=', company])
    }

    const res = await call('/api/resource/Shift Assignment', {
      params: {
        fields: JSON.stringify([
          'name',
          'employee',
          'employee_name',
          'shift_type',
          'status',
          'company',
          'department',
          'start_date',
          'end_date'
        ]),
        filters: JSON.stringify(filters),
        limit_page_length: 500
      }
    })

    // Transform response to match UI expectations
    const transformedData = res.data.data.map(assignment => ({
      id: assignment.name,
      employeeId: assignment.employee,
      employeeName: assignment.employee_name,
      shiftType: assignment.shift_type,
      status: assignment.status || 'مجدولة',
      company: assignment.company,
      department: assignment.department,
      startDate: assignment.start_date,
      endDate: assignment.end_date,
      date: assignment.start_date, // For compatibility
      // Default times based on shift type
      startTime: getShiftStartTime(assignment.shift_type),
      endTime: getShiftEndTime(assignment.shift_type),
      hours: calculateShiftHours(assignment.shift_type)
    }))

    return {
      status: 200,
      data: transformedData,
      message: 'تم تحميل الورديات بنجاح'
    }
  } catch (error) {
    console.error('Error fetching shift assignments:', error)
    throw error
  }
}

// ==========================================================================
// Create new shift assignment
// ==========================================================================
export const createShiftAssignmentApi = async (data) => {
  try {
    const payload = {
      doctype: 'Shift Assignment',
      employee: data.employee,
      shift_type: data.shiftType,
      start_date: data.startDate,
      end_date: data.endDate || null,
      company: data.company,
      status: data.status || 'Active'
    }
    console.log("payload",payload)
    const res = await call('/api/resource/Shift Assignment', payload)
    console.log("res aoi",res)
    return {
      status: res.status,
      data: res.data,
      message: 'تم إنشاء تعيين الوردية بنجاح'
    }
  } catch (error) {
    console.error('Error creating shift assignment:', error)
    throw error
  }
}

// ==========================================================================
// Update shift assignment
// ==========================================================================
export const updateShiftAssignmentApi = async (data) => {
  try {
    const payload = {
      shift_type: data.shiftType,
      end_date: data.endDate || null,
      status: data.status || 'Active'
    }

    const res = await api.put(
      `/api/resource/Shift Assignment/${encodeURIComponent(data.id)}`,
      payload
    )

    return {
      status: res.status,
      data: res.data,
      message: 'تم اپ ڈیٹ کریں تعيين الوردية بنجاح'
    }
  } catch (error) {
    console.error('Error updating shift assignment:', error)
    throw error
  }
}
// ==========================================================================
// Delete shift assignment
// ==========================================================================
export const deleteShiftAssignmentApi = async (assignmentId) => {
  try {

    const res = await call(
    'retail.retail.api.shifts.cancel_and_delete_shift_assignment',
    { name: assignmentId }
  )

  return {
    status: res.data.message.status,
    message: res.data.message.message
  }

  } catch (error) {
    console.error('Error deleting shift assignment:', error)
    throw error
  }
}
// ==========================================================================
// Get shift Type (start/end times)
// ==========================================================================
export const getShiftDetailsApi = async (shiftTypeName) => {
  try {
    const res = await call(
      `/api/resource/Shift Type/${encodeURIComponent(shiftTypeName)}`
    )

    return {
      status: res.status,
      data: res.data.data,
      message: 'تم تحميل بيانات الوردية بنجاح'
    }
  } catch (error) {
    console.error('Error fetching shift details:', error)
    throw error
  }
}
// ==========================================================================
// Helper functions for shift times
// ==========================================================================
function getShiftStartTime(shiftType) {
  const shiftTimes = {
    'صباحي': '06:00',
    'مسائي': '14:00',
    'ليلي': '22:00',
    'Morning': '06:00',
    'Evening': '14:00',
    'Night': '22:00'
  }
  return shiftTimes[shiftType] || '08:00'
}

function getShiftEndTime(shiftType) {
  const shiftTimes = {
    'صباحي': '14:00',
    'مسائي': '22:00',
    'ليلي': '06:00',
    'Morning': '14:00',
    'Evening': '22:00',
    'Night': '06:00'
  }
  return shiftTimes[shiftType] || '16:00'
}

function calculateShiftHours(shiftType) {
  const startTime = getShiftStartTime(shiftType)
  const endTime = getShiftEndTime(shiftType)

  const start = new Date(`2000-01-01 ${startTime}`)
  const end = new Date(`2000-01-01 ${endTime}`)

  let diff = (end - start) / (1000 * 60 * 60)
  if (diff < 0) diff += 24

  return parseFloat(diff.toFixed(2))
}

/* ==========================================================================
   Create - Add Leave Request with Mandatory Fields
========================================================================== */
export const createLeaveRequest = async (leaveData) => {
  try {
    const res = await call(
      'retail.retail.api.leaves.create_leave_request',
      {
        employee: leaveData.employeeId,
        employee_name: leaveData.employeeName,
        leave_type: leaveData.leaveType,
        company: leaveData.company,
        from_date: leaveData.fromDate,
        to_date: leaveData.toDate,
        number_of_days: leaveData.numberOfDays,
        reason: leaveData.reason || '',
        leave_approver: leaveData.leaveApproverId,
        leave_approver_name: leaveData.leaveApprover,
        status: leaveData.status || 'Pending'
      }
    )

    return {
      status: 'success',
      data: res.data.message.data || res.data.message,
      message: res.data.message.message || 'Leave request created successfully'
    }
  } catch (error) {
    console.error('Error creating leave request:', error)
    throw error
  }
}

/* ==========================================================================
   Update - Edit Leave Request with Mandatory Fields
========================================================================== */
export const updateLeaveRequest = async (leaveData) => {
  try {
    const res = await call(
      'retail.retail.api.leaves.update_leave_request',
      {
        name: leaveData.id,
        employee: leaveData.employeeId,
        employee_name: leaveData.employeeName,
        leave_type: leaveData.leaveType,
        company: leaveData.company,
        from_date: leaveData.fromDate,
        to_date: leaveData.toDate,
        number_of_days: leaveData.numberOfDays,
        reason: leaveData.reason || '',
        leave_approver: leaveData.leaveApproverId,
        leave_approver_name: leaveData.leaveApprover,
        status: leaveData.status
      }
    )

    return {
      status: 'success',
      data: res.data.message.data || res.data.message,
      message: res.data.message.message || 'Leave request updated successfully'
    }
  } catch (error) {
    console.error('Error updating leave request:', error)
    throw error
  }
}

/* ==========================================================================
   Read - Get All Leave Requests
========================================================================== */
export const getLeaveRequests = async (filters = {}) => {
  try {
    const params = new URLSearchParams()

    if (filters.employee) params.append('employee', filters.employee)
    if (filters.status) params.append('status', filters.status)
    if (filters.leave_type) params.append('leave_type', filters.leave_type)
    if (filters.company) params.append('company', filters.company)
    if (filters.from_date) params.append('from_date', filters.from_date)
    if (filters.to_date) params.append('to_date', filters.to_date)
    if (filters.leave_approver) params.append('leave_approver', filters.leave_approver)

    const queryString = params.toString()
    const url = queryString
      ? `retail.retail.api.leaves.get_leave_requests?${queryString}`
      : 'retail.retail.api.leaves.get_leave_requests'

    const res = await call(url)

    return {
      status: 'success',
      data: res.data.message?.data || res.data.message || [],
      message: 'Leave requests fetched successfully'
    }
  } catch (error) {
    console.error('Error fetching leave requests:', error)
    throw error
  }
}

/* ==========================================================================
   Delete - Single Leave Request
========================================================================== */
export const deleteLeaveRequest = async (leaveId) => {
  try {
    const res = await call(
      'retail.retail.api.leaves.delete_leave_request',
      { name: leaveId }
    )

    return {
      status: res.data.message.status || 'success',
      message: res.data.message.message || 'Leave request deleted successfully'
    }
  } catch (error) {
    console.error('Error deleting leave request:', error)
    throw error
  }
}

/* ==========================================================================
   Approve - Leave Request
========================================================================== */
export const approveLeaveRequest = async (leaveId) => {
  try {
    const res = await call(
      'retail.retail.api.leaves.approve_leave_request',
      { name: leaveId }
    )

    return {
      status: res.data.message.status || 'success',
      message: res.data.message.message || 'Leave request approved successfully'
    }
  } catch (error) {
    console.error('Error approving leave request:', error)
    throw error
  }
}

/* ==========================================================================
   Reject - Leave Request
========================================================================== */
export const rejectLeaveRequest = async (leaveId) => {
  try {
    const res = await call(
      'retail.retail.api.leaves.reject_leave_request',
      { name: leaveId }
    )

    return {
      status: res.data.message.status || 'success',
      message: res.data.message.message || 'Leave request rejected successfully'
    }
  } catch (error) {
    console.error('Error rejecting leave request:', error)
    throw error
  }
}

/* ==========================================================================
   Cancel - Leave Request
========================================================================== */
export const cancelLeaveRequest = async (leaveId) => {
  try {
    const res = await call(
      'retail.retail.api.leaves.cancel_leave_request',
      { name: leaveId }
    )

    return {
      status: res.data.message.status || 'success',
      message: res.data.message.message || 'Leave request cancelled successfully'
    }
  } catch (error) {
    console.error('Error cancelling leave request:', error)
    throw error
  }
}
/* ==========================================================================
   Get - Leave Balance by Employee
========================================================================== */
export const getLeaveBalance = async (employeeId) => {
  try {
    const res = await call(
      `retail.retail.api.leaves.get_leave_balance?employee=${employeeId}`
    )

    return {
      status: 'success',
      data: res.data.message?.data || res.data.message || {},
      message: 'Leave balance fetched successfully'
    }
  } catch (error) {
    console.error('Error fetching leave balance:', error)
    throw error
  }
}
/* ==========================================================================
   Get - Leave Statistics
========================================================================== */
export const getLeaveStatistics = async (filters = {}) => {
  try {
    const params = new URLSearchParams()

    if (filters.employee) params.append('employee', filters.employee)
    if (filters.company) params.append('company', filters.company)
    if (filters.start_date) params.append('start_date', filters.start_date)
    if (filters.end_date) params.append('end_date', filters.end_date)

    const queryString = params.toString()
    const url = queryString
      ? `retail.retail.api.leaves.get_leave_statistics?${queryString}`
      : 'retail.retail.api.leaves.get_leave_statistics'

    const res = await call(url)

    return {
      status: 'success',
      data: res.data.message?.data || res.data.message || {},
      message: 'Leave statistics fetched successfully'
    }
  } catch (error) {
    console.error('Error fetching leave statistics:', error)
    throw error
  }
}

const BASE = 'retail.retail.api'

/* ==========================================================================
   Address API - Create Address
========================================================================== */

// ─── Addresses ───────────────────────────────────────────────────────────────
// - getCustomerAddressesApi
// - create
// - delete

export const getCustomerAddressesApi = async (customer) => {
  const res = await call('' + BASE + '.address.get_customer_addresses', {
    params: { customer }
  })
  return res.data?.message ?? []
}
export const createAddressApi = async ({
  customer, title, line1, line2, city, state, country, pincode,
  is_primary_address, is_shipping_address
}) => {
  const res = await call('' + BASE + '.address.create_address', {
    customer, title, line1, line2: line2 || '',
    city, state: state || '', country: country || '',
    pincode: pincode || '',
    is_primary_address : is_primary_address  ? 1 : 0,
    is_shipping_address: is_shipping_address ? 1 : 0,
  })
  return res.data?.message
}
export const updateAddressApi = async (address_name, fields) => {
  const res = await call('' + BASE + '.address.update_address', {
    address_name,
    ...fields,
  })
  return res.data?.message
}

export const deleteAddressApi = async (address_name) => {
  const res = await call('' + BASE + '.address.delete_address', {
    address_name
  })
  return res.data?.message
}
// ─── Contacts ─────────────────────────────────────────────────────────────────

export const createContactApi = async ({
  customer, first_name, last_name, designation,
  is_primary, email_ids, phone_nos, address_name
}) => {
  const res = await call('' + BASE + '.contact.create_contact', {
    customer, first_name,
    last_name   : last_name    || '',
    designation : designation  || '',
    is_primary  : is_primary   ? 1 : 0,
    email_ids   : JSON.stringify(email_ids  || []),
    phone_nos   : JSON.stringify(phone_nos  || []),
    address_name: address_name || '',
  })
  return res.data?.message
}

export const updateContactApi = async (contact_name, {
  first_name, last_name, designation,
  is_primary, email_ids, phone_nos, address_name
}) => {
  const res = await call('' + BASE + '.contact.update_contact', {
    contact_name, first_name,
    last_name   : last_name    ?? '',
    designation : designation  ?? '',
    is_primary  : is_primary   ? 1 : 0,
    email_ids   : JSON.stringify(email_ids || []),
    phone_nos   : JSON.stringify(phone_nos || []),
    address_name: address_name ?? '',
  })
  return res.data?.message
}

export const deleteContactApi = async (contact_name) => {
  const res = await call('' + BASE + '.contact.delete_contact', {
    contact_name
  })
  return res.data?.message
}

export const linkAddressToContactApi = async (contact_name, address_name) => {
  const res = await call('' + BASE + '.contact.link_address_to_contact', {
    contact_name,
    address_name: address_name || '',
  })
  return res.data?.message
}


export const getInventoryBalance = async () => {
  try {
    const res = await call(
      'retail.retail.api.inventory.get_inventory_balance'
    )
    return {
      status:  'success',
      data:    res.data.message?.data || [],
      message: res.data.message?.message || 'Fetched successfully',
    }
  } catch (error) {
    console.error('Error fetching inventory balance:', error)
    return { status: 'error', data: [], message: String(error) }
  }
}

const BASE_PURCHASE_RECEIPTS = 'retail.retail.api.purchase_receipt'

// ✅ Get all receipts
export const getPurchaseReceipts = async () => {
  try {
    const res = await call(`${BASE_PURCHASE_RECEIPTS}.get_purchase_receipts`)
    console.log("getPurchaseReceipts",res)
    return res || []
  } catch (error) {
    console.error('Error fetching purchase receipts:', error)
    throw error
  }
}

// ✅ Get single receipt
export const getPurchaseReceipt = async (name) => {
  try {
    const res = await call(`${BASE_PURCHASE_RECEIPTS}.get_purchase_receipt`,
     { name }
    )
    return {
      status: 'success',
      data: res.data.message?.data || res.data.message || {},
      message: 'Receipt fetched successfully'
    }
  } catch (error) {
    console.error('Error fetching purchase receipt:', error)
    throw error
  }
}

// ✅ Create receipt
export const createPurchaseReceipt = async (receiptData) => {
  try {
    const res = await call(`${BASE_PURCHASE_RECEIPTS}.create_purchase_receipt`, {
      data: JSON.stringify(receiptData)
    })
    const result = res?.message || res?.data || res
    return {
      status: 'success',
      data: result,
      name: result?.name || result?.data?.name,
      message: 'Receipt created successfully'
    }
  } catch (error) {
    console.error('Error creating purchase receipt:', error)
    throw error
  }
}

// ✅ Update receipt
export const updatePurchaseReceipt = async (name, receiptData) => {
  try {
    const res = await call(`${BASE_PURCHASE_RECEIPTS}.update_purchase_receipt`, {
      name,
      data: JSON.stringify(receiptData)
    })
    return {
      status: 'success',
      data: res.data.message?.data || res.data.message || {},
      message: 'Receipt updated successfully'
    }
  } catch (error) {
    console.error('Error updating purchase receipt:', error)
    throw error
  }
}

// ✅ Delete receipt
export const deletePurchaseReceipt = async (name) => {
  try {
    const res = await call(`${BASE_PURCHASE_RECEIPTS}.delete_purchase_receipt`, { name })
    return {
      status: 'success',
      message: res.data.message?.message || 'Receipt deleted successfully'
    }
  } catch (error) {
    console.error('Error deleting purchase receipt:', error)
    throw error
  }
}

// ✅ Submit receipt (Draft → To Bill)
export const submitPurchaseReceipt = async (name) => {
  try {
    const res = await call(
      'retail.retail.api.purchase_receipt.submit_purchase_receipt',
      { name }
    )
    return {
      status: 'success',
      data: res.data.message?.data || {},
      message: res.data.message?.message || 'Receipt submitted successfully'
    }
  } catch (error) {
    console.error('Error submitting receipt:', error)
    throw error
  }
}

// ✅ Cancel receipt
export const cancelPurchaseReceipt = async (name) => {
  try {
    const res = await call(
      'retail.retail.api.purchase_receipt.cancel_purchase_receipt',
      { name }
    )
    return {
      status: 'success',
      message: res.data.message?.message || 'Receipt cancelled successfully'
    }
  } catch (error) {
    console.error('Error cancelling receipt:', error)
    throw error
  }
}

// ✅ Get all suppliers
export const getSuppliers = async () => {
  try {
    const res = await call(
      'retail.retail.api.purchase_receipt.get_suppliers'
    )
    return {
      status: 'success',
      data: res.data?.message?.data || [],
      message: 'Suppliers fetched successfully'
    }
  } catch (error) {
    console.error('Error fetching suppliers:', error)
    throw error
  }
}

export const createPurchaseInvoiceFromReceipt = async (receiptName, payload = {}) => {
  try {
    const res = await call(
      'retail.retail.api.purchase_receipt.create_purchase_invoice_from_receipt',
      {
        receipt_name:      receiptName,
        items:             payload.items ? JSON.stringify(payload.items) : undefined,
        posting_date:      payload.posting_date      || undefined,
        posting_time:      payload.posting_time      || undefined,
        set_posting_time:  payload.set_posting_time  || 0,
        remarks:           payload.remarks           || undefined,
      }
    )

    const result = res.data?.message   // Frappe wraps @whitelist return in .message

    if (result?.status === 'error') {
      throw new Error(result.message || 'Failed to create invoice')
    }

    return {
      status:  result?.status  || 'success',
      data:    result?.data    || {},
      message: result?.message || 'Invoice created successfully',
    }

  } catch (error) {
    console.error('Error creating purchase invoice:', error)
    throw error
  }
}

// ✅ Get invoices linked to receipt
export const getPurchaseInvoiceForReceipt = async (receiptName) => {
  try {
    const res = await call(
      'retail.retail.api.purchase_receipt.get_purchase_invoice_for_receipt',
       { receipt_name: receiptName }
    )
    return {
      status: 'success',
      data: res.data.message?.data || []
    }
  } catch (error) {
    console.error('Error fetching invoice:', error)
    throw error
  }
}

// ═══════════════════════════════════════════════════════
//  ITEM PRICE  —  api.js additions
// ═══════════════════════════════════════════════════════

const PRICE_LIST_BASE = 'retail.retail.api'

// ──────────────────────────────────────────────────────
//  PRICE LISTS
// ──────────────────────────────────────────────────────

/** Get ALL price lists (buying + selling) */
export const getAllPriceLists = async () => {
  try {
    const res = await call(`${PRICE_LIST_BASE}.item_price.get_all_price_lists`)
    return res?.data || []
  } catch (e) {
    console.error(e)
    return []
  }
}

/** Get the POS default price list */
export const getPOSPriceList = async () => {
    try{
        const res = await call(`${PRICE_LIST_BASE}.item_price.get_pos_price_list`)
        console.log("getPOSPriceList",res)
        return res.data || []
    } catch (e) {
        console.error(e)
        return []
    }
}
/**
 * Get price for a SINGLE item in a specific price list
 */
export const getItemPrices = async (filters = {}) => {
    console.log("filters",filters)
    try {
        const res = await call('retail.retail.api.item_price.get_item_price',
          { item_code: filters.item_code, price_list: filters.price_list }
          )
          console.log("getItemPrices",res)
          return res || []
      } catch (error) {
          console.error("❌ getItemPrice error:", error)
          throw error
      }
}

/**
 * Create a new Item Price record
 * @param {Object} data - { item_code, price_list, price_list_rate, currency, uom, valid_from, valid_upto }
 */
export const createItemPrice = (data) =>
  call(`${PRICE_LIST_BASE}.item_price.create_item_price`, data)

/**
 * Update an existing Item Price record
 * @param {string} name - e.g. "IP-00001"
 * @param {Object} data - { price_list_rate, currency, uom, valid_from, valid_upto }
 */
export const updateItemPrice = (name, data) =>
  api.put(`${PRICE_LIST_BASE}.item_price.update_item_price`, { name, ...data })

/**
 * Delete an Item Price record
 */
export const deleteItemPrice = (name) =>
  api.delete(`${PRICE_LIST_BASE}.item_price.delete_item_price`,{ name })


const onFiscalYearChange = async () => {
  if (!formData.value.fiscal_year || !formData.value.company) return
  try {
    const res = await call(
      'erpnext.accounts.doctype.period_closing_voucher.period_closing_voucher.get_period_start_end_date',
       { fiscal_year: formData.value.fiscal_year, company: formData.value.company }
    )
    const msg = res.data.message
    if (msg) {
      formData.value.period_start_date = msg[0] || ''
      formData.value.period_end_date   = msg[1] || ''
    }
  } catch (err) {
    toast.error('Could not fetch period dates')
  }
}


export const getDefaultCompany = async () => {
  try {
    const res = await call('retail.retail.api.common.get_default_company')
    return res.data.message || ''
  } catch (err) {
    console.error('Error loading default company:', err)
    return ''
  }
}

export const getCompanyBranding = async (companyName) => {
  if (!companyName) return {}
  try {
    const list = await getCompanies()
    const companies = Array.isArray(list) ? list : (list?.message || list?.data || [])
    const doc = (companies || []).find((c) => c.name === companyName) || {}
    return {
      name: doc.company_name || doc.name || companyName,
      logo: doc.company_logo || '',
    }
  } catch (err) {
    console.error('Error loading company branding:', err)
    return {}
  }
}

