import { defineStore } from 'pinia'
import { toRaw } from 'vue'
import { useSettingsStore } from './settings'
import {
  getCurrentUserInfoApi,
  processAutoAttendanceApi,
  fetchShiftAssignmentsApi,
  createShiftAssignmentApi,
  updateShiftAssignmentApi,
  deleteShiftAssignmentApi,
} from '@/services/api'
import {
  getAllShifts,
  fetchShiftsApi,
  make_closing_shift_from_opening_shift,
  loadHolidayListsApi,
  get_user_opening_shift,
  createShiftApi,
  updateShiftApi,
  deleteShiftApi,
  submit_closing_shift,
  get_shift_summary,
  getShiftStatistics,
  get_available_pos_profiles,
} from '@/composables/shift'
export const useShiftStore = defineStore('shift', {
  state: () => ({
    currentShift: null,
    CurrentUserInfo: null,
    pos_profile: null,
    pos_profile_name:null,
    pos_opening_shift: null,
    closingShift: null,
    currentCustomer: null,
    shifts: [],
    summary: null,
    isShiftOpen: false,
    statistics: {},
    users: [],
    showOpeningVoucherDialog: false, // ✨ نیا
    payment_methods: [],
    pos_profiles_list: []
  }),

  getters: {

    // Current shift info
    currentShiftInfo: (state) => {
      if (!state.currentShift) return null

      return {
        ...state.currentShift,
        duration: state.currentShift.period_start_date ?
          Date.now() - new Date(state.currentShift.period_start_date).getTime() : 0,
        isActive: state.isShiftOpen
      }
    },

    // Calculate expected cash
    expectedCash: (state) => {
      if (!state.currentShift) return 0

      return (state.currentShift.openingBalance || 0) +
        (state.currentShift.totalSales || 0)
    },

    // Calculate cash difference
    cashDifference: (state) => {
      if (!state.currentShift || !state.currentShift.closingBalance) return 0

      const expected = (state.currentShift.openingBalance || 0) +
        (state.currentShift.totalSales || 0)
      const actual = state.currentShift.closingBalance || 0

      return actual - expected
    },

    // Today's shifts
    todaysShifts: (state) => {
      const today = new Date().toDateString()
      return state.shifts.filter(shift =>
        new Date(shift.period_start_date).toDateString() === today
      )
    },

    // Shift statistics
    shiftStats: (state) => {
      if (!state.currentShift) return null

      return {
        transactionCount: state.currentShift.transactions?.length || 0,
        totalSales: state.currentShift.totalSales || 0,
        averageTransaction: state.currentShift.transactions?.length > 0 ?
          (state.currentShift.totalSales || 0) / state.currentShift.transactions.length : 0,
        duration: state.currentShift.period_start_date ?
          Date.now() - new Date(state.currentShift.period_start_date).getTime() : 0
      }
    }
  },

  actions: {
    async setCustomer(customer) {
      this.currentCustomer = customer || { name: 'Walk-in Customer', customer_name: 'Walk-in Customer' }
    },
    async setSupplier(supplier) {
      this.currentCustomer = supplier
    },
    async getAvailablePosprofiles(company, currency) {
      console.log("this.pos_profile.posa_allow_mpesa_reconcile_payments", this.pos_profile.posa_allow_mpesa_reconcile_payments)
      if (!this.pos_profile.posa_allow_mpesa_reconcile_payments) return;
      console.log("API get_available_pos_profiles")
      console.log("currency", currency)
      console.log("company", company)
      const posProfiles = await get_available_pos_profiles(company, currency)
      console.log("posProfiles", posProfiles)
      this.pos_profiles_list = posProfiles
    },
    async getCurrentUserInfo() {
      try {

        const CurrentUserInfo = await getCurrentUserInfoApi()
        if (!CurrentUserInfo || !CurrentUserInfo.user) {
          this.CurrentUserInfo = null
          return null
        }

        console.log("CurrentUserInfo", CurrentUserInfo)
        console.log("CurrentUserInfo of name", CurrentUserInfo.user)
        console.log("CurrentUserInfo of user", CurrentUserInfo.user)

        this.CurrentUserInfo = CurrentUserInfo
        return this.CurrentUserInfo
      } catch (error) {
        console.log(error)
      }

    },
    async checkActiveShift() {
      try {
        const currentUserInfo = await this.getCurrentUserInfo()
        const currentUser = currentUserInfo?.user
        if (!currentUser) {
          const hasLocalOpen = Boolean(this.pos_opening_shift && this.pos_profile)
          if (hasLocalOpen) {
            this.isShiftOpen = true
            this.showOpeningVoucherDialog = false
            return true
          }
          this.pos_opening_shift = null
          this.currentShift = null
          this.isShiftOpen = false
          this.showOpeningVoucherDialog = true
          return false
        }

        const result = await get_user_opening_shift(currentUser);

        if (result) {
          console.log('✅ Opening shift found:', result);
          // ✅ فيه shift مفتوح
          this.pos_profile = result.pos_profile || null
          this.pos_profile_name = result.pos_profile?.name || null
          this.pos_opening_shift = result.pos_opening_shift || null
          useSettingsStore().applyCurrencySettings(this.pos_profile?.currency)
          const shift = this.pos_opening_shift || {};
          const balanceDetails = shift.balance_details || [];
          const openingBalance = balanceDetails.reduce(
            (sum, b) => sum + (b.amount || 0),
            0
          );

          if (shift.name) {
            try {
              this.summary = await get_shift_summary(shift.name);
            } catch (summaryError) {
              console.warn('Shift summary unavailable, continuing with open shift:', summaryError);
              this.summary = null;
            }
          }

          const totalSales = this.summary?.total_sales || 0;
          const transactions = this.summary?.transactions || [];

          this.currentShift = {
            name: shift.name,
            user: shift.user,
            company: shift.company,
            pos_profile: shift.pos_profile,
            period_start_date: shift.period_start_date,
            period_end_date: shift.period_end_date || null,
            status: shift.status,
            posting_date: shift.posting_date,
            posting_time: shift.posting_time,
            all: shift,
            openingBalance,
            totalSales,
            closingBalance: 0,
            transactions,
            balance_details: balanceDetails
          };

          this.isShiftOpen = true
          this.showOpeningVoucherDialog = false // ✅ أغلق الـ dialog
          this.set_payment_methods() // ✅ حدّث payment methods
          this.getAvailablePosprofiles(this.pos_profile.company, this.pos_profile.currency)
          // if (!this.pos_profiles_list.includes(this.pos_profile.name)) {
          //   this.pos_profiles_list.push(this.pos_profile.name);
          // }
          console.log("this.pos_profiles_list", this.pos_profiles_list)
          console.log("this.pos_profile.company", this.pos_profile.company)
          console.log("this.pos_profile.currency", this.pos_profile.currency)
          console.log('✅ Current Shift (from backend):', this.currentShift);
          return true
        }
        else {
          // ❌ مفيش shift مفتوح
          this.pos_opening_shift = null;
          this.currentShift = null
          this.isShiftOpen = false;
          this.showOpeningVoucherDialog = true // ✅ افتح الـ dialog

          console.log('⚠️ No opening shift found for user');
          return false
        }
      } catch (error) {
        console.error('Error fetching opening shift:', error);
        const hasLocalOpen = Boolean(this.pos_opening_shift && this.pos_profile)
        if (hasLocalOpen) {
          this.isShiftOpen = true
          this.showOpeningVoucherDialog = false
          return true
        }
        this.pos_opening_shift = null;
        this.isShiftOpen = false
        return false
      }
    },
    set_payment_methods() {
      // get payment methods from pos profile
      // Always load payment methods from POS profile
      this.payment_methods = [];
      ;(this.pos_profile.payments || []).forEach((method) => {
        this.payment_methods.push({
          row_id: method.name,
          mode_of_payment: method.mode_of_payment,
          default: method.default,
          allow_in_returns: method.allow_in_returns,
          amount: 0
        });
      });
    },
    setShowOpeningVoucherDialog(value) {
      this.showOpeningVoucherDialog = value
    },
    async fetchShiftStatistics() {
      try {
        const stats = await getShiftStatistics()
        this.statistics = stats || {}
        return this.statistics
      } catch (error) {
        console.error('Error fetching shift statistics:', error)
      }
    },

  async loadShifts(filters = {}) {
  try {
    const response = await getAllShifts(filters)
    console.log("Shifts response:", response)

    if (response.status !== "success") {
      console.warn(response.message)
      this.shifts = []
      return { status: "error", data: [] }
    }

    const shifts = response.data || []

    this.shifts = shifts.map(shift => ({
      ...shift,
      duration: shift.start_datetime
        ? Math.floor((new Date(shift.end_datetime || Date.now()) - new Date(shift.start_datetime)) / 60000) + ' mins'
        : 'In Progress'
    }))

    return { status: "success", data: this.shifts }

  } catch (error) {
    console.error('Failed to load shifts:', error)
    this.shifts = []
    return { status: "error", data: [] }
  }
},

    async submitClosingShift(closingShift) {
      try {
        const res = await submit_closing_shift(JSON.stringify(closingShift))
        return res.message || res // بيرجع اسم الشيفت اللي اتقفل
      } catch (err) {
        console.error("Error submitting closing shift:", err)
        throw err
      }
    },
    async closingOpenShift(opening_shift) {
      try {
        const closing_shift = await make_closing_shift_from_opening_shift(opening_shift);
        console.log('Closing shift created:', closing_shift);
        this.pos_opening_shift = null   // 🟢 بعد ما تقفل، فضيه
        return closing_shift;
      } catch (error) {
        console.error('Error creating closing shift:', error);
        throw error;
      }
    },

    // Get shift by ID
    getShiftById(name) {
      return this.shifts.find(shift => shift.name === name)
    },

    // Get shifts by date range
    getShiftsByDateRange(startDate, endDate) {
      const start = new Date(startDate).getTime()
      const end = new Date(endDate).getTime()

      return this.shifts.filter(shift => {
        const shiftDate = new Date(shift.period_start_date).getTime()
        return shiftDate >= start && shiftDate <= end
      })
    },

    // Get shifts by user
    getShiftsByUser(userId) {
      return this.shifts.filter(shift => shift.userId === userId)
    },

    // Calculate shift duration
    getShiftDuration(shift) {
      const start = new Date(shift.period_start_date)
      const end = shift.period_end_date ? new Date(shift.period_end_date) : new Date()

      // getTIme return in Date ms
      // const diffMs = 10845000 // يعني حوالي 3 ساعات و 0 سےٹ و 45 سیکنڈ
      // const hours = Math.floor(diffMs / 3600000) // 3
      // const minutes = Math.floor((diffMs % 3600000) / 60000) // 0
      // const seconds = Math.floor((diffMs % 60000) / 1000) // 45
      // console.log(`${hours}h ${minutes}m ${seconds}s`)

      return end.getTime() - start.getTime()
    },

    // Format shift duration
    formatShiftDuration(shift) {
      const duration = this.getShiftDuration(shift)
      console.log('duration (ms):', duration)
      const hours = Math.floor(duration / (3600000))
      const minutes = Math.floor((duration % (3600000)) / (60000))
      const seconds = Math.floor((duration % (60000)) / 1000)
      return `${hours}h ${minutes}m ${seconds}s`
    },

    // Get user info
    getUserById(userId) {
      return this.users.find(user => user.id === userId)
    },

    // Validate shift operations
    validateShiftOperation(operation, data = {}) {
      const validations = {
        open: () => {
          if (this.isShiftOpen) {
            return { valid: false, message: 'There is already an open shift' }
          }
          if (data.openingBalance < 0) {
            return { valid: false, message: 'Opening balance cannot be negative' }
          }
          return { valid: true }
        },

        close: () => {
          if (!this.isShiftOpen) {
            return { valid: false, message: 'No active shift to close' }
          }
          if (data.closingBalance < 0) {
            return { valid: false, message: 'Closing balance cannot be negative' }
          }
          return { valid: true }
        }
      }

      return validations[operation] ? validations[operation]() : { valid: true }
    },

    // Export shift data
    async exportShiftData(shiftId = null) {
      try {
        const shiftsToExport = shiftId ?
          [this.getShiftById(shiftId)].filter(Boolean) :
          this.shifts

        const exportData = {
          shifts: shiftsToExport,
          exportedAt: new Date().toISOString(),
          exportedBy: this.currentShift?.userName || 'System',
          totalShifts: shiftsToExport.length,
          dateRange: {
            from: shiftsToExport.length > 0 ?
              shiftsToExport[shiftsToExport.length - 1].period_start_date : null,
            to: shiftsToExport.length > 0 ?
              shiftsToExport[0].period_start_date : null
          }
        }

        return exportData
      } catch (error) {
        console.error('Failed to export shift data:', error)
        throw error
      }
    },

    async fetchShifts(company){

      try{
        const response = await fetchShiftsApi(company)
        return response
      }
      catch(error){
        console.log(error)
      }

    },
      async createShift(data) {
     try{
       const response = await createShiftApi(data);
       return response

     }catch(error){
        console.log(error)
    }
  },
    // Update an existing shift
    async updateShift(data) {
      try {

        const response = await updateShiftApi(data)
        return {
          status: response.status === 200 ? 'success' : 'error',
          data: response.data || {},
          message: response.message || 'تم اپ ڈیٹ کریں الوردية بنجاح'
        }
      } catch (error) {
        console.error('Error updating shift:', error)
        return {
          status: 'error',
          data: {},
          message: error.response?.data?.message || 'حدث خطأ في اپ ڈیٹ کریں الوردية'
        }
      }
    },
     // Delete a shift
    async deleteShift(shiftName) {
      try {
        const response = await deleteShiftApi(shiftName)
        console.log("//respoonse",response)
        return {
          status: response.status === 200 ? 'success' : 'error',
          data: response.data || {},
          message: response.message
        }
      } catch (error) {
        console.error('Error deleting shift:', error)
        return {
          status: 'error',
          data: {},
          message: error.response?.data?.message
        }
      }
    },
     // Process auto attendance for a shift
    async processAutoAttendance(shiftName) {
      try {
        const response = await processAutoAttendanceApi(shiftName)
        return {
          status: response.status === 200 ? 'success' : 'error',
          data: response.data || {},
          message: response.message || 'تم معالجة حاضری بنجاح'
        }
      } catch (error) {
        console.error('Error processing auto attendance:', error)
        return {
          status: 'error',
          data: {},
          message: error.response?.data?.message || 'حدث خطأ في معالجة حاضری'
        }
      }
    },
    async loadHolidayLists() {
        try{
        const response = await loadHolidayListsApi();

        console.log("loadHolidayLists=>",response)
        return response

      }catch(error){
          console.log(error)
      }
    },
      async fetchShiftsAssignments(company = null) {
      try {

        const companyToUse = company
        const response = await fetchShiftAssignmentsApi(companyToUse)

        this.shifts = response.data || []

        return {
          status: 'success',
          data: response.data,
          message: response.message
        }
      } catch (error) {
        console.error('Error fetching shifts:', error)

        return {
          status: 'error',
          data: [],
          message: error.message || 'حدث خطأ في تحميل الورديات'
        }
      }
    },
    // Create new shift assignment
    async createShiftAssignment(data) {
      try {


        const response = await createShiftAssignmentApi({
          ...data,

        })

        // Refresh shifts list
        await this.fetchShifts()

        return {
          status: 'success',
          data: response.data,
          message: response.message
        }
      } catch (error) {
        console.error('Error creating shift assignment:', error)

        return {
          status: 'error',
          data: {},
          message: error.response?.data?.message || 'حدث خطأ في إنشاء تعيين الوردية'
        }
      }
    },

    // Update shift assignment
    async updateShiftAssignment(data) {
      try {
        const response = await updateShiftAssignmentApi(data)

        // Refresh shifts list
        await this.fetchShifts()

        return {
          status: 'success',
          data: response.data,
          message: response.message
        }
      } catch (error) {
        console.error('Error updating shift assignment:', error)

        return {
          status: 'error',
          data: {},
          message: error.response?.data?.message || 'حدث خطأ في اپ ڈیٹ کریں تعيين الوردية'
        }
      }
    },

    // Delete shift assignment
    async deleteShiftAssignment(assignmentId) {
      try {

        const response = await deleteShiftAssignmentApi(assignmentId)
        console.log("//respose delete ShiftAssignmentApi",response)
        return response
      } catch (error) {

        console.error('Error deleting shift assignment:', error)

        return {
          status: 'error',
          data: {},
          message: error.response?.data?.message || 'حدث خطأ في حذف کریں تعيين الوردية'
        }
      }
    }




  },
})
