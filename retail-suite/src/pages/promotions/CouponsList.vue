<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">القسائم والكوبونات</h1>
        <p class="text-gray-600 mt-1">{{ coupons.length }} قسيمة</p>
      </div>
      <button
        @click="openCreateModal"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        قسيمة جديدة
      </button>
    </div>

    <!-- Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200 shadow">
        <p class="text-blue-600 text-sm font-semibold">إجمالي القسائم</p>
        <p class="text-3xl font-bold text-blue-900 mt-2">{{ coupons.length }}</p>
      </div>

      <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200 shadow">
        <p class="text-green-600 text-sm font-semibold">قسائم نشطة</p>
        <p class="text-3xl font-bold text-green-900 mt-2">{{ activeCoupons }}</p>
      </div>

      <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200 shadow">
        <p class="text-purple-600 text-sm font-semibold">المستخدمة</p>
        <p class="text-3xl font-bold text-purple-900 mt-2">{{ usedCoupons }}</p>
      </div>

      <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200 shadow">
        <p class="text-orange-600 text-sm font-semibold">المتبقية</p>
        <p class="text-3xl font-bold text-orange-900 mt-2">{{ unusedCoupons }}</p>
      </div>

      <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4 border border-red-200 shadow">
        <p class="text-red-600 text-sm font-semibold">منتهية الصلاحية</p>
        <p class="text-3xl font-bold text-red-900 mt-2">{{ expiredCoupons }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="ابحث بالكود..."
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />

        <select
          v-model="statusFilter"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">جميع الحالات</option>
          <option value="active">نشط</option>
          <option value="used">مستخدم</option>
          <option value="expired">منتهي</option>
        </select>

        <select
          v-model="discountTypeFilter"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">جميع الأنواع</option>
          <option value="percentage">نسبة</option>
          <option value="fixed">ثابت</option>
          <option value="freeShip">شحن مجاني</option>
        </select>

        <button
          @click="resetFilters"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          🔄 إعادة تعيين
        </button>
      </div>
    </div>

    <!-- Coupons Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-6 py-3 text-right text-sm font-semibold text-gray-900">الكود</th>
              <th class="px-6 py-3 text-right text-sm font-semibold text-gray-900">الخصم</th>
              <th class="px-6 py-3 text-right text-sm font-semibold text-gray-900">الحد الأدنى</th>
              <th class="px-6 py-3 text-right text-sm font-semibold text-gray-900">التاريخ</th>
              <th class="px-6 py-3 text-right text-sm font-semibold text-gray-900">الاستخدام</th>
              <th class="px-6 py-3 text-right text-sm font-semibold text-gray-900">الحالة</th>
              <th class="px-6 py-3 text-right text-sm font-semibold text-gray-900">الإجراءات</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="coupon in filteredCoupons" :key="coupon.id" class="hover:bg-gray-50 transition">
              <td class="px-6 py-4 text-sm font-medium text-gray-900 font-mono">{{ coupon.code }}</td>
              <td class="px-6 py-4 text-sm font-semibold text-gray-900">
                {{ coupon.discountType === 'percentage' ? coupon.discountValue + '%' : formatCurrency(coupon.discountValue) }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-600">{{ formatCurrency(coupon.minPurchase) }}</td>
              <td class="px-6 py-4 text-sm text-gray-600">
                {{ formatDate(coupon.startDate) }} - {{ formatDate(coupon.endDate) }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-600">{{ coupon.usedCount }} / {{ coupon.totalLimit || '∞' }}</td>
              <td class="px-6 py-4 text-sm">
                <span :class="getStatusClass(coupon.status)" class="px-2 py-1 rounded text-xs font-semibold">
                  {{ getStatusLabel(coupon.status) }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm space-x-2">
                <button @click="editCoupon(coupon)" class="text-blue-600 hover:text-blue-900">✏️</button>
                <button @click="copyCoupon(coupon.code)" class="text-green-600 hover:text-green-900">📋</button>
                <button @click="deleteCoupon(coupon.id)" class="text-red-600 hover:text-red-900">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredCoupons.length === 0" class="text-center py-12">
        <p class="text-gray-500">لا توجد قسائم مطابقة</p>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <button
        @click="generateRandomCoupons"
        class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
      >
        ✨ إنشاء قسائم عشوائية
      </button>
      <button
        @click="exportCoupons"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
      >
        📥 تصدير القسائم
      </button>
      <button
        @click="enableBulkDiscount"
        class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium"
      >
        🎁 خصم جماعي
      </button>
    </div>

    <!-- Modal -->
    <CouponModal
      v-if="showModal"
      :coupon="editingCoupon"
      @save="saveCoupon"
      @close="showModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import CouponModal from '@/components/modals/CouponModal.vue'

    const coupons = ref([
      {
        id: 1,
        code: 'SAVE30',
        discountType: 'percentage',
        discountValue: 30,
        minPurchase: 500,
        startDate: '2025-01-01',
        endDate: '2025-12-31',
        status: 'active',
        usedCount: 45,
        totalLimit: 100,
        description: 'خصم 30% على جميع المنتجات'
      },
      {
        id: 2,
        code: 'WELCOME50',
        discountType: 'fixed',
        discountValue: 50,
        minPurchase: 300,
        startDate: '2025-01-01',
        endDate: '2025-12-31',
        status: 'active',
        usedCount: 78,
        totalLimit: 200,
        description: 'خصم 50 جنيه للعملاء الجدد'
      },
      {
        id: 3,
        code: 'FREESHIP100',
        discountType: 'freeShip',
        discountValue: 0,
        minPurchase: 100,
        startDate: '2025-01-01',
        endDate: '2025-01-31',
        status: 'used',
        usedCount: 150,
        totalLimit: 150,
        description: 'شحن مجاني على الطلبات فوق 100 جنيه'
      },
      {
        id: 4,
        code: 'OLDYEAR25',
        discountType: 'percentage',
        discountValue: 25,
        minPurchase: 200,
        startDate: '2024-12-01',
        endDate: '2024-12-31',
        status: 'expired',
        usedCount: 340,
        totalLimit: 500,
        description: 'عرض رأس السنة - خصم 25%'
      }
    ])

    const searchQuery = ref('')
    const statusFilter = ref('')
    const discountTypeFilter = ref('')
    const showModal = ref(false)
    const editingCoupon = ref(null)

    const filteredCoupons = computed(() => {
      return coupons.value.filter(c => {
        const matchSearch = !searchQuery.value || c.code.includes(searchQuery.value.toUpperCase())
        const matchStatus = !statusFilter.value || c.status === statusFilter.value
        const matchType = !discountTypeFilter.value || c.discountType === discountTypeFilter.value
        return matchSearch && matchStatus && matchType
      })
    })

    const activeCoupons = computed(() => {
      return coupons.value.filter(c => c.status === 'active').length
    })

    const usedCoupons = computed(() => {
      return coupons.value.filter(c => c.status === 'used').length
    })

    const unusedCoupons = computed(() => {
      return coupons.value.filter(c => c.status === 'active' && c.usedCount === 0).length
    })

    const expiredCoupons = computed(() => {
      return coupons.value.filter(c => c.status === 'expired').length
    })

    const formatCurrency = (value) => {
      return new Intl.NumberFormat('ar-EG', {
        style: 'currency',
        currency: 'EGP'
      }).format(value)
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('ar-EG')
    }

    const getStatusClass = (status) => {
      const classes = {
        active: 'bg-green-100 text-green-800',
        used: 'bg-blue-100 text-blue-800',
        expired: 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }

    const getStatusLabel = (status) => {
      const labels = {
        active: 'نشط',
        used: 'مستخدم',
        expired: 'منتهي'
      }
      return labels[status] || status
    }

    const openCreateModal = () => {
      editingCoupon.value = null
      showModal.value = true
    }

    const editCoupon = (coupon) => {
      editingCoupon.value = { ...coupon }
      showModal.value = true
    }

    const saveCoupon = (coupon) => {
      if (coupon.id) {
        const index = coupons.value.findIndex(c => c.id === coupon.id)
        if (index >= 0) {
          coupons.value[index] = coupon
        }
      } else {
        coupon.id = Math.max(...coupons.value.map(c => c.id), 0) + 1
        coupons.value.push(coupon)
      }
      showModal.value = false
    }

    const deleteCoupon = (id) => {
      if (confirm('هل تريد حذف هذه القسيمة؟')) {
        coupons.value = coupons.value.filter(c => c.id !== id)
      }
    }

    const copyCoupon = (code) => {
      navigator.clipboard.writeText(code)
      alert(`✅ تم نسخ الكود: ${code}`)
    }

    const resetFilters = () => {
      searchQuery.value = ''
      statusFilter.value = ''
      discountTypeFilter.value = ''
    }

    const generateRandomCoupons = () => {
      const codes = ['SUMMER30', 'FLASH50', 'LUCKY25', 'WELCOME20', 'VIP40']
      const newCoupons = codes.map((code, idx) => ({
        id: Math.max(...coupons.value.map(c => c.id), 0) + idx + 1,
        code,
        discountType: ['percentage', 'fixed', 'freeShip'][idx % 3],
        discountValue: [30, 50, 25, 20, 40][idx],
        minPurchase: 100,
        startDate: new Date().toISOString().split('T')[0],
        endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        status: 'active',
        usedCount: 0,
        totalLimit: 100
      }))
      coupons.value.push(...newCoupons)
      alert('✅ تم إنشاء 5 قسائم جديدة!')
    }

    const exportCoupons = () => {
      const csv = [
        ['الكود', 'نوع الخصم', 'قيمة الخصم', 'الحد الأدنى', 'الحالة'],
        ...filteredCoupons.value.map(c => [
          c.code,
          c.discountType,
          c.discountValue,
          c.minPurchase,
          c.status
        ])
      ]
      const csvContent = csv.map(row => row.join(',')).join('\n')
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'coupons.csv'
      a.click()
    }

    const enableBulkDiscount = () => {
      window.$toast?.info('Opening bulk discount window')
    }

</script>
