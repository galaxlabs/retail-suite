<!-- CustomerProfile.vue -->
<template>

    <div class="w-full flex min-h-screen bg-gray-50">
      <main class="flex flex-col flex-1 min-h-screen">

        <!-- Header -->
        <header class="mx-3 mt-3 sticky top-0 z-10 bg-white rounded-xl shadow-sm border-b border-gray-200">
          <div class="px-6 py-4 flex justify-between items-center">
            <div class="flex items-center gap-4">
              <router-link to="/customers" class="p-2 hover:bg-gray-100 rounded-lg transition">
                <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 12H5m7 7l-7-7 7-7" />
                </svg>
              </router-link>
              <div>
                <h1 class="text-lg font-bold text-gray-900">{{ customer.customer_name || customerName }}</h1>
                <p class="text-sm text-gray-500 mt-1">{{ primaryEmail }} • {{ primaryPhone }}</p>
              </div>
            </div>
            <div class="flex gap-2">
              <router-link
                :to="`/customers/${customerName}/edit`"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium"
              >
                ✏️ تعديل
              </router-link>
              <button
                @click="printProfile"
                class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-sm font-medium"
              >
                🖨️ طباعة
              </button>
            </div>
          </div>
        </header>

        <!-- Loading State -->
        <div v-if="loading" class="flex items-center justify-center py-12 px-6">
          <div class="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="mx-6 mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p class="text-red-800">{{ error }}</p>
        </div>

        <!-- Main Content -->
        <div v-else class="flex-1 px-6 py-8 space-y-6">

          <!-- Statistics Cards -->
          <section class="flex-shrink-0">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatsCard title="إجمالي المشتريات" :value="formatCurrency(customer.totalPurchases || 0)" icon="ShoppingCart" color="green" />
              <StatsCard title="الديون المتبقية"   :value="formatCurrency(customer.debt || 0)"           icon="AlertCircle"   color="red" />
              <StatsCard title="عدد الطلبات"        :value="purchases.length"                             icon="Package"       color="blue" />
              <StatsCard title="متوسط الطلب"        :value="formatCurrency(averageOrder)"                 icon="TrendingUp"    color="purple" />
            </div>
          </section>

          <!-- Main Card with Tabs -->
          <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">

            <!-- Tab Navigation -->
            <div class="border-b border-gray-200 bg-gray-50">
              <div class="px-6 flex flex-wrap gap-8">
                <button
                  v-for="tab in tabs"
                  :key="tab.key"
                  @click="activeTab = tab.key"
                  :class="['py-4 font-medium border-b-2 transition',
                    activeTab === tab.key
                      ? 'border-cyan-600 text-cyan-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900']"
                >
                  {{ tab.label }}
                </button>
              </div>
            </div>

            <!-- Tab Content -->
            <div class="p-6">

              <!-- =================== Info Tab =================== -->
              <div v-if="activeTab === 'info'" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

                  <!-- Personal Information -->
                  <div class="bg-gray-50 rounded-lg p-6 border border-gray-200">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <span class="text-2xl">👤</span> المعلومات الشخصية
                    </h3>
                    <div class="space-y-4">
                      <InfoField label="الاسم الكامل"      :value="customer.customer_name" />
                      <InfoField label="البريد الإلكتروني" :value="primaryEmail" />
                      <InfoField label="رقم الهاتف"        :value="primaryPhone" />
                      <InfoField label="المدينة"           :value="customer.custom_city" />
                      <InfoField label="نوع العميل"        :value="getCustomerTypeLabel(customer.customer_type)" />
                    </div>
                  </div>

                  <!-- Financial Information -->
                  <div class="bg-gray-50 rounded-lg p-6 border border-gray-200">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <span class="text-2xl">💰</span> المعلومات المالية
                    </h3>
                    <div class="space-y-3">
                      <div class="flex justify-between items-center p-3 bg-white rounded border border-gray-200">
                        <span class="text-sm text-gray-600 font-semibold">حد الائتمان</span>
                        <span class="text-gray-900 font-bold">{{ formatCurrency(customer.credit_limit || 0) }}</span>
                      </div>
                      <div class="flex justify-between items-center p-3 bg-white rounded border border-gray-200">
                        <span class="text-sm text-gray-600 font-semibold">الخصم</span>
                        <span class="text-gray-900 font-bold">{{ customer.posa_discount || 0 }}%</span>
                      </div>
                      <div class="flex justify-between items-center p-3 bg-white rounded border border-gray-200">
                        <span class="text-sm text-gray-600 font-semibold">شروط الدفع</span>
                        <span class="text-gray-900 font-bold">{{ customer.payment_terms || '—' }}</span>
                      </div>
                      <div class="flex justify-between items-center p-3 bg-white rounded border border-gray-200">
                        <span class="text-sm text-gray-600 font-semibold">الحالة</span>
                        <span :class="getStatusClass(customerStatus)" class="px-3 py-1 rounded text-xs font-semibold">
                          {{ getStatusLabel(customerStatus) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Notes Section -->
                <div class="bg-blue-50 rounded-lg p-6 border border-blue-200">
                  <h3 class="font-semibold text-gray-900 mb-2">📝 ملاحظات</h3>
                  <p class="text-gray-700">{{ customer.custom_note || 'لا توجد ملاحظات' }}</p>
                </div>
              </div>

              <!-- =================== Purchases Tab =================== -->
              <div v-if="activeTab === 'purchases'" class="space-y-4">
                <div class="flex justify-between items-center mb-4">
                  <h3 class="text-lg font-semibold">سجل الشراء ({{ filteredPurchases.length }} طلب)</h3>
                  <input
                    v-model="purchaseFilter"
                    type="text"
                    placeholder="ابحث في الفواتير..."
                    class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                  />
                </div>

                <div v-if="filteredPurchases.length > 0" class="overflow-x-auto">
                  <table class="w-full text-sm">
                    <thead class="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">رقم الفاتورة</th>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">التاريخ</th>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">المبلغ</th>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">الادا شدہ</th>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">المتبقي</th>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">الحالة</th>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">الإجراءات</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                      <tr v-for="purchase in filteredPurchases" :key="purchase.id" class="hover:bg-gray-50 transition">
                        <td class="px-4 py-3 font-medium text-gray-900">{{ purchase.invoice_name }}</td>
                        <td class="px-4 py-3 text-gray-600">{{ purchase.date }}</td>
                        <td class="px-4 py-3 font-bold text-gray-900">{{ formatCurrency(purchase.amount) }}</td>
                        <td class="px-4 py-3 text-green-600 font-semibold">{{ formatCurrency(purchase.paid || 0) }}</td>
                        <td class="px-4 py-3 text-red-600 font-semibold">{{ formatCurrency(purchase.remaining || 0) }}</td>
                        <td class="px-4 py-3">
                          <span :class="getPurchaseStatusClass(purchase.status)" class="px-2 py-1 rounded text-xs font-semibold">
                            {{ getPurchaseStatusLabel(purchase.status) }}
                          </span>
                        </td>
                        <td class="px-4 py-3">
                          <button class="text-cyan-600 hover:text-cyan-900 transition text-sm font-medium">عرض</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div v-else class="text-center py-8 text-gray-500">
                  لا توجد نتائج
                </div>
              </div>

              <!-- =================== Transactions Tab =================== -->
              <div v-if="activeTab === 'transactions'" class="space-y-4">
                <div class="flex gap-4 mb-4 items-end">
                  <div>
                    <label class="text-sm text-gray-600 font-semibold">من</label>
                    <input
                      v-model="dateFilterFrom"
                      type="date"
                      class="block px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent mt-1"
                    />
                  </div>
                  <div>
                    <label class="text-sm text-gray-600 font-semibold">إلى</label>
                    <input
                      v-model="dateFilterTo"
                      type="date"
                      class="block px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent mt-1"
                    />
                  </div>
                  <button @click="applyDateFilter" class="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition font-medium">
                    تطبيق
                  </button>
                  <button v-if="dateFilterFrom || dateFilterTo" @click="resetDateFilter" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition font-medium">
                    إعادة تعيين
                  </button>
                </div>

                <div v-if="filteredTransactions.length > 0" class="overflow-x-auto">
                  <table class="w-full text-sm">
                    <thead class="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">التاريخ</th>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">الوصف</th>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">مدين (عليه)</th>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">دائن (له)</th>
                        <th class="px-4 py-3 text-right font-semibold text-gray-900">الرصيد</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                      <tr v-for="(trans, idx) in filteredTransactions" :key="idx" class="hover:bg-gray-50 transition">
                        <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ trans.date }}</td>
                        <td class="px-4 py-3 text-gray-900 whitespace-pre-line">{{ trans.description }}</td>
                        <td class="px-4 py-3 font-bold text-red-600">{{ trans.debit ? formatCurrency(trans.debit) : '—' }}</td>
                        <td class="px-4 py-3 font-bold text-green-600">{{ trans.credit ? formatCurrency(trans.credit) : '—' }}</td>
                        <td class="px-4 py-3 font-bold" :class="trans.balance <= 0 ? 'text-red-600' : 'text-green-600'">
                          {{ formatCurrency(Math.abs(trans.balance)) }}
                          <span class="text-xs">({{ trans.balance <= 0 ? 'عليه' : 'له' }})</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div v-else class="text-center py-8 text-gray-500">
                  لا توجد معاملات في هذا النطاق
                </div>

                <!-- Summary -->
                <div class="grid grid-cols-3 gap-4 mt-6 p-6 bg-gray-50 rounded-lg border border-gray-200">
                  <div>
                    <p class="text-sm text-gray-600 font-semibold">إجمالي المدين</p>
                    <p class="text-2xl font-bold text-red-600 mt-2">{{ formatCurrency(filteredTotalDebit) }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600 font-semibold">إجمالي الدائن</p>
                    <p class="text-2xl font-bold text-green-600 mt-2">{{ formatCurrency(filteredTotalCredit) }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600 font-semibold">الرصيد النهائي</p>
                    <p :class="['text-2xl font-bold mt-2', filteredBalance <= 0 ? 'text-red-600' : 'text-green-600']">
                      {{ formatCurrency(Math.abs(filteredBalance)) }}
                      <span class="text-sm font-normal">({{ filteredBalance <= 0 ? 'عليه' : 'له' }})</span>
                    </p>
                  </div>
                </div>
              </div>

              <!-- =================== Documents Tab =================== -->
              <div v-if="activeTab === 'documents'" class="space-y-4">
                <div class="flex items-center gap-2 mb-4">
                  <button class="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition font-medium">
                    📤 رفع وثيقة
                  </button>
                </div>

                <div v-if="documents.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div v-for="doc in documents" :key="doc.id" class="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:shadow transition">
                    <div class="flex items-center justify-between mb-2">
                      <h4 class="font-semibold text-gray-900">{{ doc.name }}</h4>
                      <span class="text-xs bg-cyan-100 text-cyan-800 px-2 py-1 rounded">{{ doc.type }}</span>
                    </div>
                    <p class="text-sm text-gray-600 mb-3">{{ doc.uploadedAt }}</p>
                    <div class="flex gap-2">
                      <button class="flex-1 text-cyan-600 hover:text-cyan-900 text-sm transition font-medium">📥 تحميل</button>
                      <button class="flex-1 text-red-600 hover:text-red-900 text-sm transition font-medium">🗑️ حذف</button>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-8 text-gray-500">
                  لا توجد وثائق مرفقة
                </div>
              </div>

            </div>
          </section>
        </div>
      </main>
    </div>

</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import StatsCard from '@/layout/StatsCard.vue'
import InfoField from '@/components/modals/InfoField.vue'
import { useCustomersStore } from '@/stores/customers.js'
import { formatCurrency } from '@/utils/formatters.js'

// ─── Route ───────────────────────────────────────────────────────────────────
const route = useRoute()
const customerName = route.params.customer_name

// ─── Store ────────────────────────────────────────────────────────────────────
const customerStore = useCustomersStore()

// ─── State ────────────────────────────────────────────────────────────────────
const customer     = ref({})
const purchases    = ref([])
const transactions = ref([])
const documents    = ref([])

const loading        = ref(false)
const error          = ref(null)
const activeTab      = ref('info')
const purchaseFilter = ref('')
const dateFilterFrom = ref('')
const dateFilterTo   = ref('')
const dateFilterActive = ref(false)

// ─── Tabs definition ──────────────────────────────────────────────────────────
const tabs = [
  { key: 'info',         label: '📋 المعلومات' },
  { key: 'purchases',    label: '🛍️ سجل المشتريات' },
  { key: 'transactions', label: '📊 كشف الحساب' },
  { key: 'documents',    label: '📄 الوثائق' },
]

// ─── Computed: customer ───────────────────────────────────────────────────────

/** contact_details is an ARRAY — pick the primary one */
const primaryContact = computed(() => {
  const contacts = customer.value?.contact_details
  if (Array.isArray(contacts) && contacts.length) {
    return contacts.find(c => c.is_primary_contact) || contacts[0]
  }
  return null
})

const primaryEmail = computed(() =>
  primaryContact.value?.email_id || customer.value?.email_id || '—'
)

const primaryPhone = computed(() =>
  primaryContact.value?.mobile_no ||
  customer.value?.mobile_no ||
  customer.value?.custom_first_mobile ||
  '—'
)

const primaryAddress = computed(() => {
  const addr = customer.value?.address_details
  if (!addr || !Object.keys(addr).length) return '—'
  return [addr.address_line1, addr.city, addr.country].filter(Boolean).join(' - ')
})

const customerStatus = computed(() =>
  customer.value?.disabled ? 'inactive' : 'active'
)

// ─── Computed: purchases ──────────────────────────────────────────────────────

const averageOrder = computed(() => {
  if (!purchases.value.length) return 0
  const total = purchases.value.reduce((sum, p) => sum + (p.amount || 0), 0)
  return total / purchases.value.length
})

const filteredPurchases = computed(() => {
  if (!purchaseFilter.value) return purchases.value
  const q = purchaseFilter.value.toLowerCase()
  return purchases.value.filter(p =>
    p.invoice_name?.toLowerCase().includes(q) ||
    p.date?.includes(q)
  )
})

// ─── Computed: transactions ───────────────────────────────────────────────────

const filteredTransactions = computed(() => {
  if (!dateFilterActive.value) return transactions.value
  return transactions.value.filter(t => {
    const d = t.date
    if (dateFilterFrom.value && d < dateFilterFrom.value) return false
    if (dateFilterTo.value   && d > dateFilterTo.value)   return false
    return true
  })
})

const filteredTotalDebit = computed(() =>
  filteredTransactions.value.reduce((s, t) => s + (t.debit || 0), 0)
)

const filteredTotalCredit = computed(() =>
  filteredTransactions.value.reduce((s, t) => s + (t.credit || 0), 0)
)

/** Positive = له (customer owes us) | Negative = عليه (we owe customer) */
const filteredBalance = computed(() => filteredTotalDebit.value - filteredTotalCredit.value)

// ─── Helpers ──────────────────────────────────────────────────────────────────

const getStatusClass = (status) => ({
  active:   'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  blocked:  'bg-red-100 text-red-800',
}[status] ?? 'bg-gray-100 text-gray-800')

const getStatusLabel = (status) => ({
  active:   'نشط',
  inactive: 'غير نشط',
  blocked:  'محظور',
}[status] ?? status)

const getPurchaseStatusClass = (status) => ({
  paid:      'bg-green-100 text-green-800',
  pending:   'bg-yellow-100 text-yellow-800',
  partial:   'bg-blue-100 text-blue-800',
  cancelled: 'bg-red-100 text-red-800',
}[status] ?? 'bg-gray-100 text-gray-800')

const getPurchaseStatusLabel = (status) => ({
  paid:      'ادا شدہ',
  pending:   'قيد الانتظار',
  partial:   'جزوی',
  cancelled: 'ملغى',
}[status] ?? status)

const getCustomerTypeLabel = (type) => ({
  Individual: 'فرد',
  Business:   'تجاري',
  Company:    'شركة',
}[type] ?? type ?? '—')

// ─── Actions ──────────────────────────────────────────────────────────────────

const applyDateFilter = () => {
  dateFilterActive.value = true
}

const resetDateFilter = () => {
  dateFilterFrom.value   = ''
  dateFilterTo.value     = ''
  dateFilterActive.value = false
}

const printProfile = () => {
  window.print()
}

// ─── Load Data ────────────────────────────────────────────────────────────────

const loadCustomerFullData = async () => {
  try {
    loading.value = true
    error.value   = null

    const response = await customerStore.fetchCustomerProfile(customerName)

    // API returns a flat object — map each key correctly
    customer.value = {
      ...response.customer_data,
      contact_details: response.contact_details || [],
      address_details: response.address_details || {},
      totalPurchases:  response.totalPurchases   ?? 0,
      debt:            response.debt             ?? 0,
    }

    purchases.value    = response.purchases    || []
    transactions.value = response.transactions || []
    documents.value    = response.documents    || []

  } catch (err) {
    console.error(err)
    error.value = 'حدث خطأ أثناء تحميل بيانات العميل'
  } finally {
    loading.value = false
  }
}

onMounted(loadCustomerFullData)
</script>
