import { createRouter, createWebHistory } from 'vue-router'
import { session, checkSession } from '@/services/auth'
import config from '@/config/frappe'

const MobileScan = () => import('@/pages/MobileScan.vue')
import POS from '@/pages/POS.vue'
const Pay = () => import('@/pages/Pay.vue')
const NewPayment = () => import('@/pages/NewPayment.vue')
const Setting = () => import('@/pages/Setting.vue')
import Login from '@/pages/Login.vue'
const InvoicesList = () => import('@/pages/invoices/InvoicesList.vue')
const SuppliersInvoicesList = () => import('@/pages/invoices/SuppliersInvoices.vue')
const Archive = () => import('@/pages/Archive.vue')
const shiftsList = () => import('@/pages/Shifts/ShiftsList.vue')
const ShiftShow = () => import('@/pages/Shifts/ShiftShow.vue')
const InventoryDashboard = () => import('@/pages/inventory/Dashboard.vue')

const ItemPrice = () => import('@/pages/inventory/ItemPrice.vue')
const PurchaseReceipt = () => import('@/pages/inventory/PurchaseReceipt.vue')
const Barcodesunified = () => import('@/pages/inventory/Barcodesunified.vue')

const InventoryTransfer = () => import('@/pages/inventory/Transfer.vue')
const InventoryTracking = () => import('@/pages/inventory/InventoryTracking.vue')
const InventoryBalance = () => import('@/pages/inventory/InventoryBalance.vue')

const CustomersList = () => import('@/pages/customers/CustomersList.vue')
const CustomerProfile = () => import('@/pages/customers/CustomerProfile.vue')

const SuppliersList = () => import('@/pages/suppliers/SuppliersList.vue')
const SupplierProfile = () => import('@/pages/suppliers/SupplierProfile.vue')

const StaffDashboard = () => import('@/pages/staff/StaffDashboard.vue')
const StaffList = () => import('@/pages/staff/StaffList.vue')
const StaffProfile = () => import('@/pages/staff/StaffProfile.vue')
const StaffManagementControl = () => import('@/pages/staff/StaffManagementControl.vue')

const SalesAnalytics = () => import('@/pages/reports/SalesAnalytics.vue')
const IncomeStatement = () => import('@/pages/reports/IncomeStatement.vue')
const AccountsPayable = () => import('@/pages/reports/AccountsPayable.vue')
const AccountsReceivable = () => import('@/pages/reports/AccountsReceivable.vue')
const BalanceSheet = () => import('@/pages/reports/BalanceSheet.vue')
const CashFlowStatement = () => import('@/pages/reports/CashFlowStatement.vue')
const Expenses = () => import('@/pages/reports/Expenses.vue')

const Accounting = () => import('@/pages/accounting/Accounting.vue')
const AccountingDashboard = () => import('@/pages/accounting/AccountingDashboard.vue')

const PromotionsList = () => import('@/pages/promotions/PromotionsList.vue')
const CouponsList = () => import('@/pages/promotions/CouponsList.vue')
const DiscountRules = () => import('@/pages/promotions/DiscountRules.vue')
const LoyaltyProgram = () => import('@/pages/promotions/LoyaltyProgram.vue')

const AttendanceList = () => import('@/pages/attendance/AttendanceList.vue')
const LeaveManagement = () => import('@/pages/attendance/LeaveManagement.vue')
const ShiftSchedule = () => import('@/pages/attendance/ShiftSchedule.vue')
const CheckinList = () => import('@/pages/attendance/CheckinList.vue')

const UserProfile = () => import('@/pages/users/UserProfile.vue')
const NotificationCenter = () => import('@/pages/alerts/NotificationCenter.vue')

const ShiftType = () => import('@/pages/attendance/ShiftType.vue')
import DashboardHome from '@/pages/DashboardHome.vue'
import NonPage from '@/pages/NonPage.vue'
import ForbiddenView from '@/pages/ForbiddenView.vue'

const appBase = window.location.pathname.startsWith('/retail_suite/') ? '/retail_suite/' : (import.meta.env.BASE_URL || '/')

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login, meta: { requiresAuth: false, layout: 'none' }, beforeEnter: () => { stopSessionCheck(); return true } },
  { path: '/pos', name: 'POS', component: POS, meta: { requiresAuth: true, layout: 'none' } },
  { path: '/settings', name: 'Settings', component: Setting, meta: { requiresAuth: true } },
  { path: '/archive', name: 'Archive', component: Archive, meta: { requiresAuth: true } },
  { path: '/payment', name: 'Payment', component: Pay, meta: { requiresAuth: true } },
  { path: '/newpayment', name: 'Newpayment', component: NewPayment, meta: { requiresAuth: true } },
  { path: '/notification-center', name: 'NotificationCenter', component: NotificationCenter, meta: { requiresAuth: true } },
  { path: '/mobile-scan', name: 'MobileScan', component: MobileScan, meta: { requiresAuth: false, layout: 'none' } },
  { path: '/dashboard', name: 'Dashboard', component: DashboardHome, meta: { requiresAuth: true } },
  { path: '/403', name: 'Forbidden', component: ForbiddenView },
  { path: '/inventory', name: 'inventory-dashboard', component: InventoryDashboard, meta: { title: 'Inventory Dashboard', requiresAuth: true } },
  { path: '/inventory/purchase-receipt', name: 'purchase-receipt', component: PurchaseReceipt, meta: { title: 'Purchase Receipts', requiresAuth: true } },
  { path: '/inventory-tracking', name: 'inventory-tracking', component: InventoryTracking, meta: { title: 'Inventory Tracking', requiresAuth: true } },
  { path: '/inventory-balance', name: 'inventory-balance', component: InventoryBalance, meta: { title: 'Inventory Balance', requiresAuth: true } },
  { path: '/inventory-transfer', name: 'inventory-transfer', component: InventoryTransfer, meta: { title: 'Inventory Transfer', requiresAuth: true } },
  { path: '/inventory/item-price', name: 'Item-Price', component: ItemPrice, meta: { title: 'Item Price', requiresAuth: true } },
  { path: '/inventory/Barcodesunified', name: 'inventory-Barcodesunified', component: Barcodesunified, meta: { title: 'Barcodesunified', requiresAuth: true } },
  { path: '/accounting-reports', name: 'AccountingReposts', component: Accounting, meta: { title: 'Accounts', requiresAuth: true } },
  { path: '/accounting-dashboard', name: 'Accounting-Dashboard', component: AccountingDashboard, meta: { title: 'Accounting-Dashboard', requiresAuth: true } },
  { path: '/customers', name: 'CustomersList', component: CustomersList, meta: { title: 'Customers', requiresAuth: true } },
  { path: '/customers/:customer_name', name: 'CustomerProfile', component: CustomerProfile, meta: { title: 'Customer Profile', requiresAuth: true } },
  { path: '/invoices', name: 'Invoices', component: InvoicesList, meta: { requiresAuth: true } },
  { path: '/suppliers-invoices', name: 'SuppliersInvoices', component: SuppliersInvoicesList, meta: { requiresAuth: true } },
  { path: '/suppliers', name: 'SuppliersList', component: SuppliersList, meta: { title: 'Suppliers', requiresAuth: true } },
  { path: '/suppliers/:supplier_name', name: 'SupplierProfile', component: SupplierProfile, meta: { title: 'Supplier Profile', requiresAuth: true } },
  { path: '/promotions', name: 'Promotions', component: PromotionsList, meta: { requiresAuth: true } },
  { path: '/coupons', name: 'Coupons', component: CouponsList, meta: { requiresAuth: true } },
  { path: '/discount-rules', name: 'DiscountRules', component: DiscountRules, meta: { requiresAuth: true } },
  { path: '/loyalty', name: 'LoyaltyProgram', component: LoyaltyProgram, meta: { requiresAuth: true } },
  { path: '/staff-dashboard', name: 'StaffDashboard', component: StaffDashboard, meta: { requiresAuth: true } },
  { path: '/staff', name: 'StaffList', component: StaffList, meta: { title: 'Staff', requiresAuth: true } },
  { path: '/StaffProfile/:staff_name', name: 'StaffProfile', component: StaffProfile, meta: { title: 'Employee Profile', requiresAuth: true } },
  { path: '/Staff/StaffManagementControl', name: 'StaffManagementControl', component: StaffManagementControl, meta: { title: 'StaffManagementControl', requiresAuth: true } },
  { path: '/staff/:id/edit', name: 'EditStaff', component: StaffList, meta: { title: 'Edit Employee', requiresAuth: true } },
  { path: '/shifts', name: 'Shifts', component: shiftsList, meta: { requiresAuth: true } },
  { path: '/shifts/:id', name: 'ShiftShow', component: ShiftShow, props: true, meta: { requiresAuth: true } },
  { path: '/shifts-schedule', name: 'ShiftSchedule', component: ShiftSchedule, meta: { requiresAuth: true } },
  { path: '/attendance', name: 'Attendance', component: AttendanceList, meta: { requiresAuth: true } },
  { path: '/leave-management', name: 'LeaveManagement', component: LeaveManagement, meta: { requiresAuth: true } },
  { path: '/Checkin-List', name: 'CheckinList', component: CheckinList, meta: { requiresAuth: true } },
  { path: '/Shift-Type', name: 'ShiftType', component: ShiftType, meta: { requiresAuth: true } },
  { path: '/user-profile', name: 'user-profile', component: UserProfile, meta: { requiresAuth: true } },
  { path: '/sales-analytics', name: 'SalesAnalytics', component: SalesAnalytics, meta: { title: 'Sales Analytics Reports', requiresAuth: true } },
  { path: '/reports/income-statement', name: 'IncomeStatement', component: IncomeStatement, meta: { requiresAuth: true } },
  { path: '/reports/accounts-payable', name: 'AccountsPayable', component: AccountsPayable, meta: { requiresAuth: true } },
  { path: '/reports/accounts-receivable', name: 'AccountsReceivable', component: AccountsReceivable, meta: { requiresAuth: true } },
  { path: '/reports/balance-sheet', name: 'BalanceSheet', component: BalanceSheet, meta: { requiresAuth: true } },
  { path: '/reports/cashflow-statement', name: 'CashFlowStatement', component: CashFlowStatement, meta: { requiresAuth: true } },
  { path: '/reports/expenses', name: 'Expenses', component: Expenses, meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NonPage, meta: { requiresAuth: false } },
]

const router = createRouter({
  history: createWebHistory(appBase),
  routes,
})


let sessionCheckInterval = null

const startSessionCheck = () => {
  if (sessionCheckInterval) return
  sessionCheckInterval = setInterval(async () => {
    if (window.location.hash.startsWith("#/login") || window.location.hash.startsWith("#/403")) return
    try {
      const ok = await checkSession()
      if (ok === false) {
        clearInterval(sessionCheckInterval)
        sessionCheckInterval = null
        localStorage.removeItem("api_key")
        localStorage.removeItem("api_secret")
        sessionStorage.setItem("session_expired", "1")
        window.location.hash = "#/login"
      }
    } catch(e) {
      // Silently ignore session check failures
    }
  }, 120000)
}

const stopSessionCheck = () => {
  if (sessionCheckInterval) {
    clearInterval(sessionCheckInterval)
    sessionCheckInterval = null
  }
}

let sessionChecked = false
router.beforeEach(async (to, from, next) => {
  if (!sessionChecked) {
    await checkSession()
    sessionChecked = true
  startSessionCheck()
  }

  const isAuth = !!session.user
  console.log('🔀 Guard:', to.path)
  console.log('👤 session.user:', session.user)
  console.log('✅ isAuth:', isAuth)
  console.log('✅  to.meta.requiresAuth:', to.meta.requiresAuth)

  if (to.path === '/' && !isAuth) {
    return next('/login')
  }

  if (to.path === '/login' && isAuth) {
    return next('/pos')
  }

  if (to.meta.requiresAuth && !isAuth) {
    return next('/login')
  }

  if (to.meta.roles && to.meta.roles.length > 0) {
    const userRoles = session.roles || []
    const hasAccess = to.meta.roles.some(role => userRoles.includes(role))
    if (!hasAccess) return next({ name: 'Forbidden' })
  }

  next()
})
export default router
