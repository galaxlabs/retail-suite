import { createRouter, createWebHistory } from 'vue-router'
import { session, checkSession } from '@/services/auth'
import config from '@/config/frappe'

import MobileScan from '@/pages/MobileScan.vue'
import POS from '@/pages/POS.vue'
import Pay from '@/pages/Pay.vue'
import NewPayment from '@/pages/NewPayment.vue'
import Setting from '@/pages/Setting.vue'
import Login from '@/pages/Login.vue'
import InvoicesList from '@/pages/invoices/InvoicesList.vue'
import SuppliersInvoicesList from '@/pages/invoices/SuppliersInvoices.vue'
import Archive from '@/pages/Archive.vue'
import shiftsList from '@/pages/Shifts/ShiftsList.vue'
import ShiftShow from '@/pages/Shifts/ShiftShow.vue'
import InventoryDashboard from '@/pages/inventory/Dashboard.vue'

import ItemPrice from '@/pages/inventory/ItemPrice.vue'
import PurchaseReceipt from '@/pages/inventory/PurchaseReceipt.vue'
import Barcodesunified from '@/pages/inventory/Barcodesunified.vue'

import InventoryTransfer from '@/pages/inventory/Transfer.vue'
import InventoryTracking from '@/pages/inventory/InventoryTracking.vue'
import InventoryBalance from '@/pages/inventory/InventoryBalance.vue'

import CustomersList from '@/pages/customers/CustomersList.vue'
import CustomerProfile from '@/pages/customers/CustomerProfile.vue'

import SuppliersList from '@/pages/suppliers/SuppliersList.vue'
import SupplierProfile from '@/pages/suppliers/SupplierProfile.vue'

import StaffDashboard from '@/pages/staff/StaffDashboard.vue'
import StaffList from '@/pages/staff/StaffList.vue'
import StaffProfile from '@/pages/staff/StaffProfile.vue'
import StaffManagementControl from '@/pages/staff/StaffManagementControl.vue'

import SalesAnalytics from '@/pages/reports/SalesAnalytics.vue'
import IncomeStatement from '@/pages/reports/IncomeStatement.vue'
import AccountsPayable from '@/pages/reports/AccountsPayable.vue'
import AccountsReceivable from '@/pages/reports/AccountsReceivable.vue'
import BalanceSheet from '@/pages/reports/BalanceSheet.vue'
import CashFlowStatement from '@/pages/reports/CashFlowStatement.vue'
import Expenses from '@/pages/reports/Expenses.vue'

import Accounting from '@/pages/accounting/Accounting.vue'
import AccountingDashboard from '@/pages/accounting/AccountingDashboard.vue'

import PromotionsList from '@/pages/promotions/PromotionsList.vue'
import CouponsList from '@/pages/promotions/CouponsList.vue'
import DiscountRules from '@/pages/promotions/DiscountRules.vue'
import LoyaltyProgram from '@/pages/promotions/LoyaltyProgram.vue'

import AttendanceList from '@/pages/attendance/AttendanceList.vue'
import LeaveManagement from '@/pages/attendance/LeaveManagement.vue'
import ShiftSchedule from '@/pages/attendance/ShiftSchedule.vue'
import CheckinList from '@/pages/attendance/CheckinList.vue'

import UserProfile from '@/pages/users/UserProfile.vue'
import NotificationCenter from '@/pages/alerts/NotificationCenter.vue'

import ShiftType from '@/pages/attendance/ShiftType.vue'
import NonPage from '@/pages/NonPage.vue'
import ForbiddenView from '@/pages/ForbiddenView.vue'

const appBase = window.location.pathname.startsWith('/retail_suite/') ? '/retail_suite/' : (import.meta.env.BASE_URL || '/')

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login, meta: { requiresAuth: false, layout: 'none' } },
  { path: '/pos', name: 'POS', component: POS, meta: { requiresAuth: false, layout: 'none' } },
  { path: '/settings', name: 'Settings', component: Setting, meta: { requiresAuth: true } },
  { path: '/archive', name: 'Archive', component: Archive, meta: { requiresAuth: true } },
  { path: '/payment', name: 'Payment', component: Pay, meta: { requiresAuth: true } },
  { path: '/newpayment', name: 'Newpayment', component: NewPayment, meta: { requiresAuth: true } },
  { path: '/notification-center', name: 'NotificationCenter', component: NotificationCenter, meta: { requiresAuth: true } },
  { path: '/mobile-scan', name: 'MobileScan', component: MobileScan, meta: { requiresAuth: false, layout: 'none' } },
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

let sessionChecked = false
router.beforeEach(async (to, from, next) => {
  if (!sessionChecked) {
    await checkSession()
    sessionChecked = true
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
