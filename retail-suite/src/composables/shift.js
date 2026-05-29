import { call,createDocumentResource, createListResource } from 'frappe-ui'

// ====================================================================
//  Api Get Opening Dialog Data
// ====================================================================
export const get_opening_dialog_data = async () => {
    try {
        const response = await call('retail.retail.api.posapp.get_opening_dialog_data');
        console.log('Api Get Opening Dialog Data:', response);
        return response;
    }
    catch (error) {
        console.error('Error Api Get Opening Dialog Data:', error);
        throw error;
    }
}
// ====================================================================
//  Api Open Shift
// ====================================================================

export const open_shift = async (shiftData) => {
    try {

        const response = await call('retail.retail.api.posapp.create_opening_voucher',
            {
                pos_profile: shiftData.pos_profile,
                company: shiftData.company,
                balance_details: shiftData.balance_details
            }
        );
        console.log('Api Open Shift:', response);
        return response; // Assuming the new shift details are in response.data.message
    } catch (error) {
        console.error('Error Api opening shift:', error);
        throw error;
    }
}
// ====================================================================
//  Api Closing Shift
// ====================================================================

export const make_closing_shift_from_opening_shift = async (opening_shift) => {
    try {
        const response = await call('retail.retail.doctype.pos_closing_shift.pos_closing_shift.make_closing_shift_from_opening', {
            opening_shift: JSON.stringify(opening_shift)
        });
        console.log('Api Closing Shift:', response);
        return response;
    } catch (error) {
        console.error('Error Api Closing Shift:', error);
        throw error;
    }
}

// ====================================================================
//  Api Get User Opening Shift
// ====================================================================
export const get_user_opening_shift = async (user) => {
    try {
        const response = await call('retail.retail.api.posapp.check_opening_shift',
             {user: user}
            );
        console.log('Api Get User Opening Shift:', response);
        return response;
    } catch (error) {
        console.error('Error Api Get User Opening Shift:', error);
        throw error;
    }

}

// ==========================================================================
// Api Create a new shift
// ==========================================================================
export const createShiftApi = async (data) => {
  try {
    const payload = {
      doctype:'Shift Type',
      name: data.name,
      start_time: data.start_time,
      end_time: data.end_time,
      enable_auto_attendance: data.enable_auto_attendance || false,
      process_attendance_after: data.process_attendance_after || null,
      holiday_list: data.holiday_list || null,
      disabled: data.disabled || false
    }

    const shiftTypeDoc = createDocumentResource(payload)

    await shiftTypeDoc.insert()
    console.log('📦 shiftTypeDoc resource created:', shiftTypeDoc)

    return {
      status: "success",
      data: shiftTypeDoc,
      message: 'Api a new shift type is Created Successfully'
    }
  } catch (error) {
    console.error('Error Api Create a new shift:', error)
    throw error
  }
}

// ==========================================================================
// Update an existing shift
// ==========================================================================
export const updateShiftApi = async (data) => {
  try {
    const payload = {
      start_time: data.start_time,
      end_time: data.end_time,
      enable_auto_attendance: data.enable_auto_attendance || false,
      process_attendance_after: data.process_attendance_after || null,
      holiday_list: data.holiday_list || null,
      last_sync_of_checkin: data.last_sync_of_checkin || null
    }

    const res = await api.put(
      `/api/resource/Shift Type/${encodeURIComponent(data.name)}`,
      payload
    )

    return {
      status: res.status,
      data: res.data,
      message: 'تم اپ ڈیٹ کریں الوردية بنجاح'
    }
  } catch (error) {
    console.error('Error updating shift:', error)
    throw error
  }
}

// ==========================================================================
// Delete a shift
// ==========================================================================
export const deleteShiftApi = async (shiftName) => {
  try {
    const res = await api.delete(
      `/api/resource/Shift Type/${encodeURIComponent(shiftName)}`
    )

    console.log('Response Api', res)

    return {
      status: 'success',
      data: res.data,
      message: 'تم حذف کریں الوردية بنجاح'
    }

  } catch (error) {
    console.log('Error deleting shift:', error)

    // استخراج رسالة Frappe الحقيقية
    const frappeMessage =
      error?.response?.data?.exception ||
      error?.response?.data?.message ||
      error?.response?.data?._server_messages

    let message = 'فشل حذف کریں الوردية'

    // لو فيه server messages
    if (Array.isArray(frappeMessage)) {
      try {
        message = JSON.parse(frappeMessage[0]).message
      } catch {
        message = frappeMessage[0]
      }
    } else if (typeof frappeMessage === 'string') {
      message = frappeMessage
    }

    return {
      status: 'error',
      data: null,
      message
    }
  }
}
// ==========================================================================
// Api Fetch Shifts
// ==========================================================================

export const getAllShifts = async (filters = {}) => {
    try {
        const response = await call('retail.retail.api.shifts.get_shifts', {
                name: filters.name,
                status: filters.status || '',   // "Open" أو "Closed"
                order_by: 'creation desc'
          });

          return response
      } catch (error) {
          console.error('Error fetching shifts:', error);
          throw error;
      }
  }

export const fetchShiftsApi = async (company) => {
  try {
    const res = await call('retail.retail.api.shifts.get_shifts',
       {company: JSON.stringify(company),}
    );
    return res;
  } catch (error) {
    console.error('Error Search Employee:', error);
    throw error;
  }
};
// ==========================================================================
// API Holiday List
// ==========================================================================
export const loadHolidayListsApi = async () => {
  try {
    const resource = createListResource({
      doctype: 'Holiday List',
      fields: ['*'],
      pageLength: 500,
      auto: true,
    })
    await resource.list.promise
    console.log("API Holiday List: ", resource.data)
    return resource.data
  } catch (err) {
    console.error('Error API Holiday List:', err)
  }
}
// ==========================================================================
// API Get Shift Summary
// ==========================================================================
export async function get_shift_summary(pos_opening_shift) {
    try {
        const shiftParam =
            typeof pos_opening_shift === 'string'
                ? pos_opening_shift
                : pos_opening_shift.name;

        const response = await call(
            'retail.retail.doctype.pos_closing_shift.pos_closing_shift.get_shift_summary',
            { pos_opening_shift_name: shiftParam }

        );

        console.log('API Get Shift Summary:', response);
        return response;
    } catch (error) {
        console.error('Error API Get Shift Summary:', error);
        throw error;
    }
}

// ==========================================================================
// API Get Shift Dtails
// ==========================================================================
export const getShiftDetails = async (shift_id) => {
    try {
        const response = await call('retail.retail.api.shifts.get_shift_details',
            { shift_id }
        );
        console.log('API Get Shift Dtails:', response);
        return response;

    } catch (error) {
        console.error('Error API Get Shift Dtails:', error);
        throw error;
    }

}

// ==========================================================================
// API Submit Closing Shift
// ==========================================================================
export const submit_closing_shift = async (closingShift) => {
    try {
        const response = await call(
            'retail.retail.doctype.pos_closing_shift.pos_closing_shift.submit_closing_shift',
            {closing_shift: closingShift}
        )
        console.log("API Submit Closing Shift: ", response.data)
        return response.data
    } catch (error) {
        console.error("Error API Submit Closing Shift: ", error)
        throw error
    }
}
// ==========================================================================
// API Get Shift Payment Summary
// ==========================================================================
export const get_shift_payment_summary = async (pos_opening_shift) => {
    try {

        const response = await call(
          'retail.retail.doctype.pos_closing_shift.pos_closing_shift.get_shift_payment_summary',
          { opening_shift_name: pos_opening_shift }
        )
        console.log("Api Get Shift Payment Summary:", response)
        return response?.message
    } catch (error) {
        console.error("Error Api Get Shift Payment Summary:", error)
        throw error
    }
}
// ==========================================================================
// API Get Shift Satatistics
// ==========================================================================
export const getShiftStatistics = async () => {
    try {
        const response = await call('retail.retail.api.shifts.get_shift_statistics');

        return response; // Assuming the statistics are in response.data.message

    } catch (error) {
        console.error('Error fetching shifts statistics:', error);
        throw error;
    }
}
// =========================================================
// Get Availabe POS Profile
// =========================================================
export const get_available_pos_profiles = async (company, currency) => {

    try {
        const response = await call('retail.retail.api.payment_entry.get_available_pos_profiles',
           {company,currency}
        )
        console.log("api Availabe POS Profile", response)
        return response
    }
    catch (error) {
        console.error("❌ Process Payment error:", error)
    }
}
// ======================================================================
// API BeginningCash Balance
// ======================================================================
export const getBeginningCashBalance = async (filters = {}) => {
  try {
    const response = await call(
      'retail.retail.api.reports.get_beginning_cash_balance',
      { ...filters }
    )

    console.log('✅ API BeginningCash Balance', response)
    return response
  } catch (error) {
    console.error('❌ ERRO API BeginningCash Balance', error)
    throw error
  }
}
// ======================================================================
// API Create Create Update Customer in Frappe DB
// ======================================================================
export const createUpdateCustomerInFrappeDB = async (args) => {
  const {
    method = 'create',
    customer_id,
    customer_name,
    pos_profile_doc,
    company,
    first_mobile,
    second_mobile,
    email_id,
    city,
    address_line1,
    address_line2,
    state,
    country,
    pincode,
    first_name,
    last_name,
    customer_group,
    territory,
    customer_type,
    gender,
    note,
  } = args
  try{
    const res = await call('retail.retail.api.posapp.create_customer', {
      method,
      customer_id    : customer_id   || '',
      customer_name,
      pos_profile_doc: typeof pos_profile_doc === 'string'
                        ? pos_profile_doc
                        : JSON.stringify(pos_profile_doc || {}),
      company        : company       || '',
      first_mobile   : first_mobile  || '',
      second_mobile  : second_mobile || '',
      email_id       : email_id      || '',
      city           : city          || '',
      address_line1  : address_line1 || '',
      address_line2  : address_line2 || '',
      state          : state         || '',
      country        : country       || 'Egypt',
      pincode        : pincode       || '',
      first_name     : first_name    || '',
      last_name      : last_name     || '',
      customer_group : customer_group || '',
      territory      : territory      || '',
      customer_type  : customer_type  || 'Individual',
      gender         : gender         || '',
      note           : note           || '',
    })
    console.log("✅ API Create Update Customer in Frappe DB:", res)
    return res

  }catch (e){
    console.error("❌ Error Api Create Update Customer in Frappe DB:", e)
  }
}
// ======================================================================
// API Get Customers from Frappe DB
// ======================================================================
export const getCustomersFromFrappeDB = async (pos_profile) => {
    try {
        const response = await call('retail.retail.api.posapp.get_customer_names',
             { pos_profile }
        )
        console.log("API Get Customers from Frappe DB", response)
        return response
    }
    catch (error) {
        console.error("❌ Error API Get Customers from Frappe DB:", error)
    }
}
