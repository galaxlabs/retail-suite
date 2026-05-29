<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">قوانين الخصم</h1>
        <p class="text-gray-600 mt-1">إدارة قوانين الخصم التلقائي</p>
      </div>
      <button
        @click="openCreateModal"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        قانون جديد
      </button>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <div class="flex gap-4">
        <button
          @click="activeTab = 'quantity'"
          :class="['px-4 py-3 font-medium border-b-2 transition', activeTab === 'quantity' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
        >
          📦 خصم حسب الكمية
        </button>
        <button
          @click="activeTab = 'tiered'"
          :class="['px-4 py-3 font-medium border-b-2 transition', activeTab === 'tiered' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
        >
          📊 خصم متدرج
        </button>
        <button
          @click="activeTab = 'category'"
          :class="['px-4 py-3 font-medium border-b-2 transition', activeTab === 'category' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
        >
          🏷️ خصم حسب الفئة
        </button>
        <button
          @click="activeTab = 'time'"
          :class="['px-4 py-3 font-medium border-b-2 transition', activeTab === 'time' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
        >
          ⏰ خصم حسب الوقت
        </button>
      </div>
    </div>

    <!-- Quantity Discounts -->
    <div v-if="activeTab === 'quantity'" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-6">خصم حسب الكمية</h2>

      <div class="space-y-4">
        <div v-for="rule in quantityRules" :key="rule.id" class="border border-gray-200 rounded-lg p-4 flex items-center justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-4">
              <div class="bg-blue-100 text-blue-800 px-3 py-1 rounded text-sm font-semibold">
                من {{ rule.minQty }} إلى {{ rule.maxQty }}
              </div>
              <div class="text-lg font-bold text-green-600">
                خصم {{ rule.discountType === 'percentage' ? rule.discountValue + '%' : formatCurrency(rule.discountValue) }}
              </div>
              <p class="text-sm text-gray-600">{{ rule.description }}</p>
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="editRule(rule)" class="text-blue-600 hover:text-blue-900">✏️</button>
            <button @click="deleteRule(rule.id)" class="text-red-600 hover:text-red-900">🗑️</button>
          </div>
        </div>

        <button
          @click="addQuantityRule"
          class="w-full px-4 py-2 border-2 border-dashed border-gray-300 text-gray-600 rounded-lg hover:border-blue-500 hover:text-blue-600 transition"
        >
          ➕ إضافة قاعدة جديدة
        </button>
      </div>
    </div>

    <!-- Tiered Discounts -->
    <div v-if="activeTab === 'tiered'" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-6">خصم متدرج</h2>

      <div class="space-y-4">
        <div v-for="rule in tieredRules" :key="rule.id" class="border border-gray-200 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-900">{{ rule.name }}</h3>
            <div class="flex gap-2">
              <button @click="editRule(rule)" class="text-blue-600 hover:text-blue-900">✏️</button>
              <button @click="deleteRule(rule.id)" class="text-red-600 hover:text-red-900">🗑️</button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div v-for="tier in rule.tiers" :key="tier.tier" class="bg-gray-50 rounded p-3">
              <p class="text-xs text-gray-600 font-semibold">المستوى {{ tier.tier }}</p>
              <p class="text-sm font-bold text-gray-900 mt-1">من {{ formatCurrency(tier.amount) }}</p>
              <p class="text-lg font-bold text-green-600 mt-1">{{ tier.discount }}%</p>
            </div>
          </div>
        </div>

        <button
          @click="addTieredRule"
          class="w-full px-4 py-2 border-2 border-dashed border-gray-300 text-gray-600 rounded-lg hover:border-blue-500 hover:text-blue-600 transition"
        >
          ➕ إضافة قاعدة متدرجة
        </button>
      </div>
    </div>

    <!-- Category Discounts -->
    <div v-if="activeTab === 'category'" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-6">خصم حسب الفئة</h2>

      <div class="space-y-4">
        <div v-for="rule in categoryRules" :key="rule.id" class="border border-gray-200 rounded-lg p-4 flex items-center justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-4">
              <div class="bg-purple-100 text-purple-800 px-3 py-1 rounded text-sm font-semibold">
                {{ rule.category }}
              </div>
              <div class="text-lg font-bold text-green-600">
                خصم {{ rule.discount }}%
              </div>
              <p class="text-sm text-gray-600">{{ rule.description }}</p>
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="editRule(rule)" class="text-blue-600 hover:text-blue-900">✏️</button>
            <button @click="deleteRule(rule.id)" class="text-red-600 hover:text-red-900">🗑️</button>
          </div>
        </div>

        <button
          @click="addCategoryRule"
          class="w-full px-4 py-2 border-2 border-dashed border-gray-300 text-gray-600 rounded-lg hover:border-blue-500 hover:text-blue-600 transition"
        >
          ➕ إضافة خصم فئة
        </button>
      </div>
    </div>

    <!-- Time-Based Discounts -->
    <div v-if="activeTab === 'time'" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-6">خصم حسب الوقت</h2>

      <div class="space-y-4">
        <div v-for="rule in timeRules" :key="rule.id" class="border border-gray-200 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-900">{{ rule.name }}</h3>
            <div class="flex gap-2">
              <button @click="editRule(rule)" class="text-blue-600 hover:text-blue-900">✏️</button>
              <button @click="deleteRule(rule.id)" class="text-red-600 hover:text-red-900">🗑️</button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-gray-50 rounded p-3">
              <p class="text-xs text-gray-600 font-semibold">📅 الأيام</p>
              <p class="text-sm font-bold text-gray-900 mt-1">{{ rule.days.join(', ') }}</p>
            </div>
            <div class="bg-gray-50 rounded p-3">
              <p class="text-xs text-gray-600 font-semibold">⏰ الوقت</p>
              <p class="text-sm font-bold text-gray-900 mt-1">{{ rule.startTime }} - {{ rule.endTime }}</p>
            </div>
            <div class="bg-gray-50 rounded p-3">
              <p class="text-xs text-gray-600 font-semibold">🎁 الخصم</p>
              <p class="text-lg font-bold text-green-600 mt-1">{{ rule.discount }}%</p>
            </div>
          </div>
        </div>

        <button
          @click="addTimeRule"
          class="w-full px-4 py-2 border-2 border-dashed border-gray-300 text-gray-600 rounded-lg hover:border-blue-500 hover:text-blue-600 transition"
        >
          ➕ إضافة خصم زمني
        </button>
      </div>
    </div>

    <!-- Modal -->
    <DiscountRuleModal
      v-if="showModal"
      :rule="editingRule"
      :rule-type="activeTab"
      @save="saveRule"
      @close="showModal = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import DiscountRuleModal from '@/components/modals/DiscountRuleModal.vue'

    const activeTab = ref('quantity')
    const showModal = ref(false)
    const editingRule = ref(null)

    const quantityRules = ref([
      {
        id: 1,
        minQty: 1,
        maxQty: 10,
        discountType: 'percentage',
        discountValue: 5,
        description: 'خصم صغير للكميات القليلة'
      },
      {
        id: 2,
        minQty: 11,
        maxQty: 50,
        discountType: 'percentage',
        discountValue: 10,
        description: 'خصم متوسط'
      },
      {
        id: 3,
        minQty: 51,
        maxQty: 999999,
        discountType: 'percentage',
        discountValue: 20,
        description: 'خصم كبير للكميات الكبيرة'
      }
    ])

    const tieredRules = ref([
      {
        id: 1,
        name: 'الخصم المتدرج حسب المبلغ',
        tiers: [
          { tier: 1, amount: 0, discount: 0 },
          { tier: 2, amount: 500, discount: 5 },
          { tier: 3, amount: 1000, discount: 10 },
          { tier: 4, amount: 2000, discount: 15 }
        ]
      }
    ])

    const categoryRules = ref([
      {
        id: 1,
        category: 'المشروبات',
        discount: 15,
        description: 'خصم على جميع المشروبات'
      },
      {
        id: 2,
        category: 'الحلويات',
        discount: 10,
        description: 'خصم على الحلويات'
      },
      {
        id: 3,
        category: 'الساندويتش',
        discount: 8,
        description: 'خصم على الساندويتش'
      }
    ])

    const timeRules = ref([
      {
        id: 1,
        name: 'خصم ساعة الذروة',
        days: ['السبت', 'الأحد', 'الاثنين'],
        startTime: '12:00',
        endTime: '14:00',
        discount: 20
      },
      {
        id: 2,
        name: 'خصم الليل',
        days: ['الجمعة', 'السبت'],
        startTime: '20:00',
        endTime: '23:59',
        discount: 25
      }
    ])

    const formatCurrency = (value) => {
      return new Intl.NumberFormat('ar-EG', {
        style: 'currency',
        currency: 'EGP'
      }).format(value)
    }

    const openCreateModal = () => {
      editingRule.value = null
      showModal.value = true
    }

    const editRule = (rule) => {
      editingRule.value = { ...rule }
      showModal.value = true
    }

    const deleteRule = (id) => {
      if (confirm('هل تريد حذف هذه القاعدة؟')) {
        // حذف من القائمة المناسبة
        if (activeTab.value === 'quantity') {
          quantityRules.value = quantityRules.value.filter(r => r.id !== id)
        } else if (activeTab.value === 'tiered') {
          tieredRules.value = tieredRules.value.filter(r => r.id !== id)
        } else if (activeTab.value === 'category') {
          categoryRules.value = categoryRules.value.filter(r => r.id !== id)
        } else if (activeTab.value === 'time') {
          timeRules.value = timeRules.value.filter(r => r.id !== id)
        }
      }
    }

    const saveRule = (rule) => {
      if (rule.id) {
        // تحديث
        if (activeTab.value === 'quantity') {
          const idx = quantityRules.value.findIndex(r => r.id === rule.id)
          if (idx >= 0) quantityRules.value[idx] = rule
        }
      } else {
        // إنشاء جديد
        rule.id = Date.now()
        if (activeTab.value === 'quantity') {
          quantityRules.value.push(rule)
        }
      }
      showModal.value = false
    }

    const addQuantityRule = () => {
      openCreateModal()
    }

    const addTieredRule = () => {
      window.$toast?.info('مرحلہ وار ڈسکاونٹ بنانے کی ونڈو کھل رہی ہے')
    }

    const addCategoryRule = () => {
      window.$toast?.info('کیٹیگری ڈسکاونٹ بنانے کی ونڈو کھل رہی ہے')
    }

    const addTimeRule = () => {
      window.$toast?.info('وقتی ڈسکاونٹ بنانے کی ونڈو کھل رہی ہے')
    }


</script>
