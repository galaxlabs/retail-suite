<!-- CustomerProfileModal.vue -->
<template>
  <div class="fixed inset-0 bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-6 flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold">{{ customer.name }}</h2>
          <p class="text-blue-100 text-sm mt-1">{{ customer.email }} • {{ customer.phone }}</p>
        </div>
        <button
          @click="$emit('close')"
          class="text-white hover:bg-white hover:bg-opacity-20 p-2 rounded transition"
        >
          ✕
        </button>
      </div>

      <div class="p-6 space-y-6">
        <!-- Statistics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
            <p class="text-green-600 text-sm font-semibold mb-1">کل خریداری</p>
            <p class="text-2xl font-bold text-green-900">{{ formatCurrency(customer.totalPurchases) }}</p>
          </div>

          <div :class="['bg-gradient-to-br rounded-lg p-4 border', customer.debt > 0 ? 'from-red-50 to-red-100 border-red-200' : 'from-green-50 to-green-100 border-green-200']">
            <p :class="['text-sm font-semibold mb-1', customer.debt > 0 ? 'text-red-600' : 'text-green-600']">باقی قرض</p>
            <p :class="['text-2xl font-bold', customer.debt > 0 ? 'text-red-900' : 'text-green-900']">{{ formatCurrency(customer.debt) }}</p>
          </div>

          <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
            <p class="text-blue-600 text-sm font-semibold mb-1">آرڈرز کی تعداد</p>
            <p class="text-2xl font-bold text-blue-900">{{ purchases.length }}</p>
          </div>

          <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
            <p class="text-purple-600 text-sm font-semibold mb-1">اوسط آرڈر</p>
            <p class="text-2xl font-bold text-purple-900">{{ formatCurrency(averageOrder) }}</p>
          </div>
        </div>

        <!-- Tabs -->
        <div class="border-b border-gray-200">
          <div class="flex gap-4">
            <button
              @click="activeTab = 'info'"
              :class="['px-4 py-3 font-medium border-b-2 transition', activeTab === 'info' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
            >
              المعلومات
            </button>
            <button
              @click="activeTab = 'purchases'"
              :class="['px-4 py-3 font-medium border-b-2 transition', activeTab === 'purchases' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
            >
              خریداری کا ریکارڈ
            </button>
            <button
              @click="activeTab = 'transactions'"
              :class="['px-4 py-3 font-medium border-b-2 transition', activeTab === 'transactions' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
            >
              اکاونٹ سٹیٹسےٹ
            </button>
          </div>
        </div>

        <!-- Tab Content -->
        <!-- Info Tab -->
        <div v-if="activeTab === 'info'" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Personal Info -->
            <div class="bg-gray-50 rounded-lg p-4 space-y-3">
              <h3 class="font-semibold text-gray-900 mb-4">ذاتی معلومات</h3>
              <div>
                <p class="text-sm text-gray-600">نام</p>
                <p class="font-medium text-gray-900">{{ customer.name }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">ای میل</p>
                <p class="font-medium text-gray-900">{{ customer.email }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">فون نمبر</p>
                <p class="font-medium text-gray-900">{{ customer.phone }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">پتہ</p>
                <p class="font-medium text-gray-900">{{ customer.address }}</p>
              </div>
            </div>

            <!-- Financial Info -->
            <div class="bg-gray-50 rounded-lg p-4 space-y-3">
              <h3 class="font-semibold text-gray-900 mb-4">مالی معلومات</h3>
              <div>
                <p class="text-sm text-gray-600">کریڈٹ لمٹ</p>
                <p class="font-medium text-gray-900">{{ formatCurrency(customer.creditLimit || 0) }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">ڈسکاونٹ</p>
                <p class="font-medium text-gray-900">{{ customer.discount || 0 }}%</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">شروط ادائیگی</p>
                <p class="font-medium text-gray-900">{{ customer.paymentTerms || 0 }} دن</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">حیثیت</p>
                <span :class="getStatusClass(customer.status)" class="px-2 py-1 rounded text-xs font-semibold">
                  {{ getStatusLabel(customer.status) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Notes -->
          <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <h3 class="font-semibold text-gray-900 mb-2">ملاحظات</h3>
            <p class="text-gray-700">{{ customer.notes || 'کوئی نوٹس نہیں' }}</p>
          </div>
        </div>

        <!-- Purchases Tab -->
        <div v-if="activeTab === 'purchases'" class="space-y-4">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="px-4 py-2 text-right font-semibold text-gray-900">رقم انوائس</th>
                  <th class="px-4 py-2 text-right font-semibold text-gray-900">تاریخ</th>
                  <th class="px-4 py-2 text-right font-semibold text-gray-900">رقم</th>
                  <th class="px-4 py-2 text-right font-semibold text-gray-900">حیثیت</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="purchase in purchases" :key="purchase.id" class="hover:bg-gray-50">
                  <td class="px-4 py-2 font-medium text-gray-900">#{{ purchase.id }}</td>
                  <td class="px-4 py-2 text-gray-600">{{ purchase.date }}</td>
                  <td class="px-4 py-2 font-medium">{{ formatCurrency(purchase.amount) }}</td>
                  <td class="px-4 py-2">
                    <span :class="getPurchaseStatusClass(purchase.status)" class="px-2 py-1 rounded text-xs font-semibold">
                      {{ purchase.statusLabel }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Transactions Tab (Account Statement) -->
        <div v-if="activeTab === 'transactions'" class="space-y-4">
          <div class="flex items-center gap-4">
            <input
              v-model="dateFilterFrom"
              type="date"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <span class="text-gray-600">تک</span>
            <input
              v-model="dateFilterTo"
              type="date"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="px-4 py-2 text-right font-semibold text-gray-900">تاریخ</th>
                  <th class="px-4 py-2 text-right font-semibold text-gray-900">تفصیل</th>
                  <th class="px-4 py-2 text-right font-semibold text-gray-900">ڈیبٹ</th>
                  <th class="px-4 py-2 text-right font-semibold text-gray-900">کریڈٹ</th>
                  <th class="px-4 py-2 text-right font-semibold text-gray-900">بیلنس</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="(trans, idx) in transactions" :key="idx" class="hover:bg-gray-50">
                  <td class="px-4 py-2 text-gray-600">{{ trans.date }}</td>
                  <td class="px-4 py-2 text-gray-900">{{ trans.description }}</td>
                  <td class="px-4 py-2 font-medium text-red-600">{{ trans.debit ? formatCurrency(trans.debit) : '-' }}</td>
                  <td class="px-4 py-2 font-medium text-green-600">{{ trans.credit ? formatCurrency(trans.credit) : '-' }}</td>
                  <td class="px-4 py-2 font-bold" :class="trans.balance >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatCurrency(trans.balance) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Summary -->
          <div class="grid grid-cols-3 gap-4 mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <p class="text-sm text-gray-600">إجمالي الڈیبٹ</p>
              <p class="text-lg font-bold text-red-600">{{ formatCurrency(totalDebit) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">إجمالي الکریڈٹ</p>
              <p class="text-lg font-bold text-green-600">{{ formatCurrency(totalCredit) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">بیلنس النهائي</p>
              <p :class="['text-lg font-bold', (totalDebit - totalCredit) <= 0 ? 'text-green-600' : 'text-red-600']">
                {{ formatCurrency(totalDebit - totalCredit) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="border-t border-gray-200 bg-gray-50 px-6 py-4 flex items-center justify-between">
        <button
          @click="printStatement"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition"
        >
          🖨️ پرنٹ کریں
        </button>
        <button
          @click="$emit('close')"
          class="px-4 py-2 bg-gray-300 text-gray-900 rounded-lg hover:bg-gray-400 transition"
        >
          بند کریں
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

  const props = defineProps( {
    customer: {
      type: Object,
      required: true
    }
  })
  const emit = defineEmits(['close'])

    const activeTab = ref('info')
    const dateFilterFrom = ref('2025-01-01')
    const dateFilterTo = ref('2025-01-31')

    // Sample purchases
    const purchases = ref([
      { id: 1001, date: '2025-01-25', amount: 1500, status: 'paid', statusLabel: 'ادا شدہ' },
      { id: 1002, date: '2025-01-20', amount: 2000, status: 'paid', statusLabel: 'ادا شدہ' },
      { id: 1003, date: '2025-01-15', amount: 1200, status: 'pending', statusLabel: 'زیر التوا' }
    ])

    // Sample transactions for account statement
    const transactions = ref([
      { date: '2025-01-01', description: 'ابتدائی بیلنس', debit: 500, credit: 0, balance: 500 },
      { date: '2025-01-05', description: 'خریداری #1001', debit: 1500, credit: 0, balance: 2000 },
      { date: '2025-01-10', description: 'نقد ادائیگی', debit: 0, credit: 1000, balance: 1000 },
      { date: '2025-01-15', description: 'خریداری #1002', debit: 2000, credit: 0, balance: 3000 },
      { date: '2025-01-20', description: 'خریداری #1003', debit: 1200, credit: 0, balance: 4200 },
      { date: '2025-01-25', description: 'دفع بشيك', debit: 0, credit: 2000, balance: 2200 }
    ])

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
        active: 'فعال',
        inactive: 'غير فعال',
        blocked: 'بلاک شدہ'
      }
      return labels[status] || status
    }

    const getPurchaseStatusClass = (status) => {
      const classes = {
        paid: 'bg-green-100 text-green-800',
        pending: 'bg-yellow-100 text-yellow-800',
        cancelled: 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }

    const printStatement = () => {
      window.print()
    }

</script>
