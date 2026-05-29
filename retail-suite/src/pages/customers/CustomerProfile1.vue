<!-- CustomerProfile.vue -->
<template>
  <div class="p-6 space-y-6">
    <CuromerProfileModal
      :customer="customer"
    />
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-800">{{ error }}</p>
    </div>

    <!-- Customer Profile -->
    <div v-else class="space-y-6">
      <!-- Header with Back Button -->
      <div class="flex items-center gap-4 mb-6">
        <router-link to="/customers" class="p-2 hover:bg-gray-100 rounded-lg transition">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 12H5m7 7l-7-7 7-7" />
          </svg>
        </router-link>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">{{ customer.name }}</h1>
          <p class="text-gray-600">{{ customer.email }} • {{ customer.phone }}</p>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200 shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-green-600 text-sm font-semibold">إجمالي المشتريات</p>
              <p class="text-3xl font-bold text-green-900 mt-2">{{ formatCurrency(customer.totalPurchases) }}</p>
            </div>
            <div class="text-4xl opacity-30">💰</div>
          </div>
        </div>

        <div :class="['bg-gradient-to-br rounded-lg p-6 border shadow', customer.debt > 0 ? 'from-red-50 to-red-100 border-red-200' : 'from-green-50 to-green-100 border-green-200']">
          <div class="flex items-center justify-between">
            <div>
              <p :class="['text-sm font-semibold', customer.debt > 0 ? 'text-red-600' : 'text-green-600']">الديون المتبقية</p>
              <p :class="['text-3xl font-bold mt-2', customer.debt > 0 ? 'text-red-900' : 'text-green-900']">{{ formatCurrency(customer.debt) }}</p>
            </div>
            <div class="text-4xl opacity-30">📊</div>
          </div>
        </div>

        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200 shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-blue-600 text-sm font-semibold">عدد الطلبات</p>
              <p class="text-3xl font-bold text-blue-900 mt-2">{{ purchases.length }}</p>
            </div>
            <div class="text-4xl opacity-30">📦</div>
          </div>
        </div>

        <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200 shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-purple-600 text-sm font-semibold">متوسط الطلب</p>
              <p class="text-3xl font-bold text-purple-900 mt-2">{{ formatCurrency(averageOrder) }}</p>
            </div>
            <div class="text-4xl opacity-30">📈</div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="bg-white rounded-lg shadow border border-gray-200">
        <div class="border-b border-gray-200 flex flex-wrap">
          <button
            @click="activeTab = 'info'"
            :class="['px-6 py-4 font-medium border-b-2 transition', activeTab === 'info' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
          >
            📋 المعلومات
          </button>
          <button
            @click="activeTab = 'purchases'"
            :class="['px-6 py-4 font-medium border-b-2 transition', activeTab === 'purchases' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
          >
            🛍️ سجل المشتريات
          </button>
          <button
            @click="activeTab = 'transactions'"
            :class="['px-6 py-4 font-medium border-b-2 transition', activeTab === 'transactions' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
          >
            📊 كشف الحساب
          </button>
          <button
            @click="activeTab = 'documents'"
            :class="['px-6 py-4 font-medium border-b-2 transition', activeTab === 'documents' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
          >
            📄 الوثائق
          </button>
        </div>

        <!-- Tab Content -->
        <div class="p-6">
          <!-- Info Tab -->
          <div v-if="activeTab === 'info'" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Personal Information -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-900 border-b pb-2">👤 المعلومات الشخصية</h3>

                <div class="space-y-3">
                  <div>
                    <p class="text-sm text-gray-600 font-semibold">الاسم الكامل</p>
                    <p class="text-gray-900 mt-1">{{ customer.name }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600 font-semibold">البريد الإلكتروني</p>
                    <p class="text-gray-900 mt-1">{{ customer.email }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600 font-semibold">رقم الهاتف</p>
                    <p class="text-gray-900 mt-1">{{ customer.phone }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600 font-semibold">العنوان</p>
                    <p class="text-gray-900 mt-1">{{ customer.address }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600 font-semibold">نوع العميل</p>
                    <p class="text-gray-900 mt-1">{{ getCustomerTypeLabel(customer.customerType) }}</p>
                  </div>
                </div>
              </div>

              <!-- Financial Information -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-900 border-b pb-2">💰 المعلومات المالية</h3>

                <div class="space-y-3">
                  <div class="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span class="text-sm text-gray-600 font-semibold">حد الائتمان</span>
                    <span class="text-gray-900 font-bold">{{ formatCurrency(customer.creditLimit || 0) }}</span>
                  </div>
                  <div class="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span class="text-sm text-gray-600 font-semibold">الخصم</span>
                    <span class="text-gray-900 font-bold">{{ customer.discount || 0 }}%</span>
                  </div>
                  <div class="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span class="text-sm text-gray-600 font-semibold">شروط الدفع</span>
                    <span class="text-gray-900 font-bold">{{ customer.paymentTerms || 0 }} أيام</span>
                  </div>
                  <div class="flex justify-between items-center p-3 bg-blue-50 rounded border border-blue-200">
                    <span class="text-sm text-blue-600 font-semibold">الحالة</span>
                    <span :class="getStatusClass(customer.status)" class="px-3 py-1 rounded text-xs font-semibold">
                      {{ getStatusLabel(customer.status) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Notes Section -->
            <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h3 class="font-semibold text-gray-900 mb-2">📝 ملاحظات</h3>
              <p class="text-gray-700">{{ customer.notes || 'لا توجد ملاحظات' }}</p>
            </div>

            <!-- Action Buttons -->
            <div class="flex gap-2 pt-4 border-t">
              <router-link :to="`/customers/${customer.id}/edit`" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                ✏️ تعديل
              </router-link>
              <button @click="printProfile" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                🖨️ طباعة
              </button>
            </div>
          </div>

          <!-- Purchases Tab -->
          <div v-if="activeTab === 'purchases'" class="space-y-4">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold">سجل الشراء ({{ purchases.length }} طلب)</h3>
              <input
                v-model="purchaseFilter"
                type="text"
                placeholder="ابحث في الفواتير..."
                class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div v-if="purchases.length > 0" class="overflow-x-auto">
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
                  <tr v-for="purchase in purchases" :key="purchase.id" class="hover:bg-gray-50 transition">
                    <td class="px-4 py-3 font-medium text-gray-900">#{{ purchase.id }}</td>
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
                      <button class="text-blue-600 hover:text-blue-900 transition text-sm">عرض</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              لا توجد عمليات شراء
            </div>
          </div>

          <!-- Transactions Tab (Account Statement) -->
          <div v-if="activeTab === 'transactions'" class="space-y-4">
            <div class="flex gap-4 mb-4">
              <div>
                <label class="text-sm text-gray-600 font-semibold">من</label>
                <input
                  v-model="dateFilterFrom"
                  type="date"
                  class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mt-1"
                />
              </div>
              <div>
                <label class="text-sm text-gray-600 font-semibold">إلى</label>
                <input
                  v-model="dateFilterTo"
                  type="date"
                  class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mt-1"
                />
              </div>
              <div class="flex items-end">
                <button @click="applyDateFilter" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                  تطبيق
                </button>
              </div>
            </div>

            <div v-if="transactions.length > 0" class="overflow-x-auto">
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
                  <tr v-for="(trans, idx) in transactions" :key="idx" class="hover:bg-gray-50 transition">
                    <td class="px-4 py-3 text-gray-600">{{ trans.date }}</td>
                    <td class="px-4 py-3 text-gray-900">{{ trans.description }}</td>
                    <td class="px-4 py-3 font-bold text-red-600">{{ trans.debit ? formatCurrency(trans.debit) : '-' }}</td>
                    <td class="px-4 py-3 font-bold text-green-600">{{ trans.credit ? formatCurrency(trans.credit) : '-' }}</td>
                    <td class="px-4 py-3 font-bold" :class="trans.balance >= 0 ? 'text-green-600' : 'text-red-600'">
                      {{ formatCurrency(Math.abs(trans.balance)) }}
                      <span class="text-xs" :class="trans.balance >= 0 ? 'text-green-600' : 'text-red-600'">
                        {{ trans.balance >= 0 ? '(له)' : '(عليه)' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Summary -->
            <div class="grid grid-cols-3 gap-4 mt-6 p-6 bg-gray-50 rounded-lg border border-gray-200">
              <div>
                <p class="text-sm text-gray-600 font-semibold">إجمالي المدين</p>
                <p class="text-2xl font-bold text-red-600 mt-2">{{ formatCurrency(totalDebit) }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600 font-semibold">إجمالي الدائن</p>
                <p class="text-2xl font-bold text-green-600 mt-2">{{ formatCurrency(totalCredit) }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600 font-semibold">الرصيد النهائي</p>
                <p :class="['text-2xl font-bold mt-2', (totalDebit - totalCredit) <= 0 ? 'text-green-600' : 'text-red-600']">
                  {{ formatCurrency(Math.abs(totalDebit - totalCredit)) }}
                </p>
              </div>
            </div>
          </div>

          <!-- Documents Tab -->
          <div v-if="activeTab === 'documents'" class="space-y-4">
            <div class="flex items-center gap-2 mb-4">
              <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                📤 رفع وثيقة
              </button>
            </div>

            <div v-if="documents.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div v-for="doc in documents" :key="doc.id" class="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:shadow transition">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-semibold text-gray-900">{{ doc.name }}</h4>
                  <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">{{ doc.type }}</span>
                </div>
                <p class="text-sm text-gray-600 mb-3">{{ doc.uploadedAt }}</p>
                <div class="flex gap-2">
                  <button class="flex-1 text-blue-600 hover:text-blue-900 text-sm transition">📥 تحميل</button>
                  <button class="flex-1 text-red-600 hover:text-red-900 text-sm transition">🗑️ حذف</button>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              لا توجد وثائق مرفقة
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCustomersStore } from '@/stores/customers'
import CuromerProfileModal from '@/components/modals/CustomerProfileModal.vue'

    const route = useRoute()
    const customersStore = useCustomersStore()

    const customer = ref({})
    const purchases = ref([])
    const transactions = ref([])
    const documents = ref([])
    const loading = ref(false)
    const error = ref(null)
    const activeTab = ref('info')
    const purchaseFilter = ref('')
    const dateFilterFrom = ref('2025-01-01')
    const dateFilterTo = ref('2025-01-31')

    // Sample data for demo
    const sampleCustomer = {
      id: 1,
      name: 'أحمد محمد',
      phone: '01234567890',
      email: 'ahmed@example.com',
      address: 'القاهرة - مصر',
      customerType: 'individual',
      debt: 500,
      totalPurchases: 5000,
      status: 'active',
      creditLimit: 10000,
      discount: 5,
      paymentTerms: 30,
      notes: 'عميل موثوق - يدفع في الوقت المحدد'
    }

    const samplePurchases = [
      { id: 1001, date: '2025-01-25', amount: 1500, paid: 1500, remaining: 0, status: 'paid', statusLabel: 'ادا شدہ' },
      { id: 1002, date: '2025-01-20', amount: 2000, paid: 0, remaining: 2000, status: 'pending', statusLabel: 'قيد الانتظار' },
      { id: 1003, date: '2025-01-15', amount: 1200, paid: 700, remaining: 500, status: 'partial', statusLabel: 'جزوی' }
    ]

    const sampleTransactions = [
      { date: '2025-01-01', description: 'رصيد افتتاحي', debit: 500, credit: 0, balance: 500 },
      { date: '2025-01-05', description: 'شراء #1001', debit: 1500, credit: 0, balance: 2000 },
      { date: '2025-01-10', description: 'دفع نقدي', debit: 0, credit: 1000, balance: 1000 },
      { date: '2025-01-15', description: 'شراء #1002', debit: 2000, credit: 0, balance: 3000 },
      { date: '2025-01-20', description: 'شراء #1003', debit: 1200, credit: 0, balance: 4200 },
      { date: '2025-01-25', description: 'دفع بشيك', debit: 0, credit: 2000, balance: 2200 }
    ]

    const sampleDocuments = [
      { id: 1, name: 'العقد التجاري', type: 'PDF', uploadedAt: '2025-01-10' },
      { id: 2, name: 'هوية شخصية', type: 'Image', uploadedAt: '2025-01-05' },
      { id: 3, name: 'رخصة عمل', type: 'PDF', uploadedAt: '2025-01-01' }
    ]

    const loadCustomer = async () => {
      loading.value = true
      try {
        // استبدل بـ API الفعلي
        const customerId = route.params.id || 1
        // const customer = await customersStore.getCustomer(customerId)
        customer.value = sampleCustomer
        purchases.value = samplePurchases
        transactions.value = sampleTransactions
        documents.value = sampleDocuments
        error.value = null
      } catch (err) {
        error.value = 'خطأ في تحميل بيانات العميل'
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    const averageOrder = computed(() => {
      if (purchases.value.length === 0) return 0
      const total = purchases.value.reduce((sum, p) => sum + p.amount, 0)
      return total / purchases.value.length
    })

    const totalDebit = computed(() => {
      return transactions.value.reduce((sum, t) => sum + (t.debit || 0), 0)
    })

    const totalCredit = computed(() => {
      return transactions.value.reduce((sum, t) => sum + (t.credit || 0), 0)
    })

    const formatCurrency = (value) => {
      return new Intl.NumberFormat('ar-EG', {
        style: 'currency',
        currency: 'EGP'
      }).format(value)
    }

    const getStatusClass = (status) => {
      const classes = {
        active: 'bg-green-100 text-green-800',
        inactive: 'bg-gray-100 text-gray-800',
        blocked: 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }

    const getStatusLabel = (status) => {
      const labels = {
        active: 'نشط',
        inactive: 'غير نشط',
        blocked: 'محظور'
      }
      return labels[status] || status
    }

    const getCustomerTypeLabel = (type) => {
      const labels = {
        individual: 'فرد',
        business: 'تجاري',
        corporate: 'شركة'
      }
      return labels[type] || type
    }

    const getPurchaseStatusClass = (status) => {
      const classes = {
        paid: 'bg-green-100 text-green-800',
        pending: 'bg-yellow-100 text-yellow-800',
        partial: 'bg-blue-100 text-blue-800',
        cancelled: 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }

    const getPurchaseStatusLabel = (status) => {
      const labels = {
        paid: 'ادا شدہ',
        pending: 'قيد الانتظار',
        partial: 'جزوی',
        cancelled: 'ملغى'
      }
      return labels[status] || status
    }

    const applyDateFilter = () => {
      // تطبيق الفلتر على المعاملات
      console.log(`تصفية من ${dateFilterFrom.value} إلى ${dateFilterTo.value}`)
    }

    const printProfile = () => {
      window.print()
    }

    onMounted(() => {
      loadCustomer()
    })

</script>

<style scoped>
/* Print styles */
@media print {
  .no-print {
    display: none !important;
  }
}
</style>
