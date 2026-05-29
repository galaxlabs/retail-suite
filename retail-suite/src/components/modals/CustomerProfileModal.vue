<!-- CustomerProfileModal.vue -->
<template>
  <div class="fixed inset-0 bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-gradient-to-r from-cyan-600 to-blue-600 text-white px-6 py-6 flex items-center justify-between border-b border-cyan-700">
        <div>
          <h2 class="text-2xl font-bold">{{ customer.name }}</h2>
          <p class="text-cyan-100 text-sm mt-1">{{ customer.email }} • {{ customer.phone }}</p>
        </div>
        <button
          @click="$emit('close')"
          class="text-white hover:bg-white hover:bg-opacity-20 p-2 rounded-lg transition"
        >
          ✕
        </button>
      </div>

      <div class="p-6 space-y-6">
        <!-- Statistics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard title="کل خریداری" :value="formatCurrency(customer.totalPurchases)" color="green" />
          <StatCard title="باقی قرض" :value="formatCurrency(customer.debt)" color="red" />
          <StatCard title="آرڈرز کی تعداد" :value="purchases.length" color="blue" />
          <StatCard title="اوسط آرڈر" :value="formatCurrency(averageOrder)" color="purple" />
        </div>

        <!-- Tab Navigation -->
        <div class="border-b border-gray-200 bg-gray-50 -mx-6 px-6">
          <div class="flex gap-8">
            <button
              @click="activeTab = 'info'"
              :class="['py-4 font-medium border-b-2 transition', activeTab === 'info' ? 'border-cyan-600 text-cyan-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
            >
              📋 المعلومات
            </button>
            <button
              @click="activeTab = 'purchases'"
              :class="['py-4 font-medium border-b-2 transition', activeTab === 'purchases' ? 'border-cyan-600 text-cyan-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
            >
              🛍️ خریداری کا ریکارڈ
            </button>
            <button
              @click="activeTab = 'transactions'"
              :class="['py-4 font-medium border-b-2 transition', activeTab === 'transactions' ? 'border-cyan-600 text-cyan-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
            >
              📊 اکاونٹ سٹیٹسےٹ
            </button>
          </div>
        </div>

        <!-- Tab Content -->
        <!-- Info Tab -->
        <div v-if="activeTab === 'info'" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Personal Information -->
            <div class="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">👤 ذاتی معلومات</h3>
              <div class="space-y-4">
                <InfoItem label="نام" :value="customer.name" />
                <InfoItem label="ای میل" :value="customer.email" />
                <InfoItem label="فون نمبر" :value="customer.phone" />
                <InfoItem label="پتہ" :value="customer.address" />
              </div>
            </div>

            <!-- Financial Information -->
            <div class="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">💰 مالی معلومات</h3>
              <div class="space-y-3">
                <InfoRow label="کریڈٹ لمٹ" :value="formatCurrency(customer.creditLimit || 0)" />
                <InfoRow label="ڈسکاونٹ" :value="`${customer.discount || 0}%`" />
                <InfoRow label="شروط ادائیگی" :value="`${customer.paymentTerms || 0} دن`" />
                <div class="flex justify-between items-center p-3 bg-white rounded border border-gray-200">
                  <span class="text-sm text-gray-600 font-semibold">حیثیت</span>
                  <span :class="getStatusClass(customer.status)" class="px-3 py-1 rounded text-xs font-semibold">
                    {{ getStatusLabel(customer.status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Notes -->
          <div class="bg-blue-50 rounded-lg p-6 border border-blue-200">
            <h3 class="font-semibold text-gray-900 mb-2">📝 ملاحظات</h3>
            <p class="text-gray-700">{{ customer.notes || 'کوئی نوٹس نہیں' }}</p>
          </div>
        </div>

        <!-- Purchases Tab -->
        <div v-if="activeTab === 'purchases'" class="space-y-4">
          <div v-if="purchases.length > 0" class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="px-4 py-3 text-right font-semibold text-gray-900">رقم انوائس</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-900">تاریخ</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-900">رقم</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-900">حیثیت</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="purchase in purchases" :key="purchase.id" class="hover:bg-gray-50 transition">
                  <td class="px-4 py-3 font-medium text-gray-900">#{{ purchase.id }}</td>
                  <td class="px-4 py-3 text-gray-600">{{ purchase.date }}</td>
                  <td class="px-4 py-3 font-bold">{{ formatCurrency(purchase.amount) }}</td>
                  <td class="px-4 py-3">
                    <span :class="getPurchaseStatusClass(purchase.status)" class="px-2 py-1 rounded text-xs font-semibold">
                      {{ purchase.statusLabel }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-8 text-gray-500">
            کوئی خریداری نہیں
          </div>
        </div>

        <!-- Transactions Tab -->
        <div v-if="activeTab === 'transactions'" class="space-y-4">
          <div class="flex items-center gap-4 mb-4">
            <div class="flex-1">
              <label class="text-sm text-gray-600 font-semibold block mb-1">سے</label>
              <input
                v-model="dateFilterFrom"
                type="date"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
              />
            </div>
            <div class="flex-1">
              <label class="text-sm text-gray-600 font-semibold block mb-1">تک</label>
              <input
                v-model="dateFilterTo"
                type="date"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
              />
            </div>
          </div>

          <div v-if="transactions.length > 0" class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="px-4 py-3 text-right font-semibold text-gray-900">تاریخ</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-900">تفصیل</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-900">ڈیبٹ</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-900">کریڈٹ</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-900">بیلنس</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="(trans, idx) in transactions" :key="idx" class="hover:bg-gray-50 transition">
                  <td class="px-4 py-3 text-gray-600">{{ trans.date }}</td>
                  <td class="px-4 py-3 text-gray-900">{{ trans.description }}</td>
                  <td class="px-4 py-3 font-medium text-red-600">{{ trans.debit ? formatCurrency(trans.debit) : '-' }}</td>
                  <td class="px-4 py-3 font-medium text-green-600">{{ trans.credit ? formatCurrency(trans.credit) : '-' }}</td>
                  <td class="px-4 py-3 font-bold" :class="trans.balance >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatCurrency(trans.balance) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Summary -->
          <div class="grid grid-cols-3 gap-4 mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <p class="text-sm text-gray-600 font-semibold">إجمالي الڈیبٹ</p>
              <p class="text-lg font-bold text-red-600 mt-2">{{ formatCurrency(totalDebit) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 font-semibold">إجمالي الکریڈٹ</p>
              <p class="text-lg font-bold text-green-600 mt-2">{{ formatCurrency(totalCredit) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600 font-semibold">بیلنس النهائي</p>
              <p :class="['text-lg font-bold mt-2', (totalDebit - totalCredit) <= 0 ? 'text-green-600' : 'text-red-600']">
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
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition font-medium"
        >
          🖨️ پرنٹ کریں
        </button>
        <button
          @click="$emit('close')"
          class="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition font-medium"
        >
          بند کریں
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const StatCard = {
  props: ['title', 'value', 'color'],
  template: `
    <div :class="['bg-gradient-to-br rounded-lg p-4 border', getGradient(color)]">
      <p :class="['text-sm font-semibold mb-1', getTextColor(color)]">{{ title }}</p>
      <p :class="['text-2xl font-bold', getValueColor(color)]">{{ value }}</p>
    </div>
  `,
  methods: {
    getGradient(color) {
      const gradients = {
        green: 'from-green-50 to-green-100 border-green-200',
        red: 'from-red-50 to-red-100 border-red-200',
        blue: 'from-blue-50 to-blue-100 border-blue-200',
        purple: 'from-purple-50 to-purple-100 border-purple-200'
      }
      return gradients[color] || gradients.blue
    },
    getTextColor(color) {
      const colors = { green: 'text-green-600', red: 'text-red-600', blue: 'text-blue-600', purple: 'text-purple-600' }
      return colors[color] || colors.blue
    },
    getValueColor(color) {
      const colors = { green: 'text-green-900', red: 'text-red-900', blue: 'text-blue-900', purple: 'text-purple-900' }
      return colors[color] || colors.blue
    }
  }
}

const InfoItem = {
  props: ['label', 'value'],
  template: `
    <div>
      <p class="text-sm text-gray-600 font-semibold">{{ label }}</p>
      <p class="text-gray-900 mt-1 font-medium">{{ value }}</p>
    </div>
  `
}

const InfoRow = {
  props: ['label', 'value'],
  template: `
    <div class="flex justify-between items-center p-3 bg-white rounded border border-gray-200">
      <span class="text-sm text-gray-600 font-semibold">{{ label }}</span>
      <span class="text-gray-900 font-bold">{{ value }}</span>
    </div>
  `
}

  const props = defineProps({
    customer: {
      type: Object,
      required: true
    }
  })
 const emit = defineEmits(['close'])
    const activeTab = ref('info')
    const dateFilterFrom = ref('2025-01-01')
    const dateFilterTo = ref('2025-01-31')

    const purchases = ref([
      { id: 1001, date: '2025-01-25', amount: 1500, status: 'paid', statusLabel: 'ادا شدہ' },
      { id: 1002, date: '2025-01-20', amount: 2000, status: 'paid', statusLabel: 'ادا شدہ' },
      { id: 1003, date: '2025-01-15', amount: 1200, status: 'pending', statusLabel: 'زیر التوا' }
    ])

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
      return purchases.value.reduce((sum, p) => sum + p.amount, 0) / purchases.value.length
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

    const getStatusClass = (status) => ({
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      blocked: 'bg-red-100 text-red-800'
    }[status] || 'bg-gray-100 text-gray-800')

    const getStatusLabel = (status) => ({
      active: 'فعال',
      inactive: 'غير فعال',
      blocked: 'بلاک شدہ'
    }[status] || status)

    const getPurchaseStatusClass = (status) => ({
      paid: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      cancelled: 'bg-red-100 text-red-800'
    }[status] || 'bg-gray-100 text-gray-800')

    const printStatement = () => {
      window.print()
    }

</script>
