<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <h2 class="text-xl font-bold text-gray-900">
          {{ rule ? 'ترمیم کریں القاعدة' : 'قاعدة خصم نیاة' }}
        </h2>
        <button
          @click="$emit('close')"
          class="text-gray-500 hover:text-gray-700 text-2xl"
        >
          ✕
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
        <!-- Quantity Discount Form -->
        <div v-if="ruleType === 'quantity'" class="space-y-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">خصم حسب مقدار</h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">مقدار الدنيا *</label>
              <input
                v-model.number="form.minQty"
                type="number"
                min="0"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="0"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">مقدار العليا *</label>
              <input
                v-model.number="form.maxQty"
                type="number"
                min="1"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="999999"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">نوع ڈسکاونٹ *</label>
            <select
              v-model="form.discountType"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">اختر قسم</option>
              <option value="percentage">فیصد (%)</option>
              <option value="fixed">مقررہ رقم</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              قيمة ڈسکاونٹ *
              <span class="text-gray-500 text-xs">({{ form.discountType === 'percentage' ? '%' : 'ج.م' }})</span>
            </label>
            <input
              v-model.number="form.discountValue"
              type="number"
              min="0"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="0"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">تفصیل</label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="وصف القاعدة"
            ></textarea>
          </div>
        </div>

        <!-- Tiered Discount Form -->
        <div v-if="ruleType === 'tiered'" class="space-y-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">مرحلہ وار ڈسکاونٹ</h3>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">اصول کا نام *</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="مثال: ڈسکاونٹ المتدرج حسب رقم"
            />
          </div>

          <div class="space-y-4">
            <label class="block text-sm font-medium text-gray-700">سطحیں *</label>
            <div
              v-for="(tier, idx) in form.tiers"
              :key="idx"
              class="border border-gray-200 rounded-lg p-4 space-y-3"
            >
              <div class="flex items-center justify-between">
                <h4 class="font-semibold text-gray-900">سطح {{ idx + 1 }}</h4>
                <button
                  v-if="form.tiers.length > 1"
                  @click="removeTier(idx)"
                  type="button"
                  class="text-red-600 hover:text-red-900"
                >
                  🗑️
                </button>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label class="text-xs font-medium text-gray-700">رقم الأدنى (ج.م) *</label>
                  <input
                    v-model.number="tier.amount"
                    type="number"
                    min="0"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label class="text-xs font-medium text-gray-700">ڈسکاونٹ (%) *</label>
                  <input
                    v-model.number="tier.discount"
                    type="number"
                    min="0"
                    max="100"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            <button
              @click="addTier"
              type="button"
              class="w-full px-4 py-2 border-2 border-dashed border-gray-300 text-gray-600 rounded-lg hover:border-blue-500 hover:text-blue-600 transition"
            >
              ➕ شامل کریں مستوى
            </button>
          </div>
        </div>

        <!-- Category Discount Form -->
        <div v-if="ruleType === 'category'" class="space-y-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">کیٹیگری ڈسکاونٹ</h3>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">کیٹیگری سےتخب کریں *</label>
            <select
              v-model="form.category"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">کیٹیگری سےتخب کریں</option>
              <option value="beverages">مشروبات</option>
              <option value="food">کھانا</option>
              <option value="desserts">میٹھائیاں</option>
              <option value="snacks">اسنیکس</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">نسبة ڈسکاونٹ (%) *</label>
            <input
              v-model.number="form.discount"
              type="number"
              min="0"
              max="100"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="0"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">تفصیل</label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="وصف ڈسکاونٹ"
            ></textarea>
          </div>
        </div>

        <!-- Time-Based Discount Form -->
        <div v-if="ruleType === 'time'" class="space-y-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">خصم حسب وقت</h3>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">اسم ڈسکاونٹ الزسےي *</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="مثال: خصم ساعة الذروة"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">دن سےتخب کریں *</label>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
              <label
                v-for="day in daysOfWeek"
                :key="day"
                class="flex items-center gap-2 cursor-pointer"
              >
                <input
                  :value="day"
                  v-model="form.days"
                  type="checkbox"
                  class="w-4 h-4 text-blue-600 rounded"
                />
                <span class="text-sm text-gray-700">{{ day }}</span>
              </label>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">شروع کا وقت *</label>
              <input
                v-model="form.startTime"
                type="time"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">اختتام کا وقت *</label>
              <input
                v-model="form.endTime"
                type="time"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">نسبة ڈسکاونٹ (%) *</label>
            <input
              v-model.number="form.discount"
              type="number"
              min="0"
              max="100"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="0"
            />
          </div>
        </div>

        <!-- Actions -->
        <div class="border-t pt-6 flex items-center justify-end gap-4">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            سےسوخ کریں
          </button>
          <button
            type="submit"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            {{ rule ? 'اپ ڈیٹ کریں' : 'شامل کریں' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps( {
    rule: {
      type: Object,
      default: null
    },
    ruleType: {
      type: String,
      required: true
    }
})
const emit = defineEmits(['save', 'close'])

  const daysOfWeek = ['ہفتہ', 'اتوار', 'پیر', 'سےگل', 'بدھ', 'جمعرات', 'جمعہ']

  const form = ref({
    // Quantity
    minQty: 0,
    maxQty: 999999,
    discountType: 'percentage',
    discountValue: 0,

    // Tiered
    name: '',
    tiers: [
      { tier: 1, amount: 0, discount: 0 }
    ],

    // Category
    category: '',

    // Time
    days: ['ہفتہ'],
    startTime: '09:00',
    endTime: '17:00',

    // Common
    discount: 0,
    description: '',
    id: null
  })

  watch(() => props.rule, (newRule) => {
    if (newRule) {
      form.value = { ...newRule }
    } else {
      resetForm()
    }
  }, { immediate: true })

  const resetForm = () => {
    form.value = {
      minQty: 0,
      maxQty: 999999,
      discountType: 'percentage',
      discountValue: 0,
      name: '',
      tiers: [{ tier: 1, amount: 0, discount: 0 }],
      category: '',
      days: ['ہفتہ'],
      startTime: '09:00',
      endTime: '17:00',
      discount: 0,
      description: '',
      id: null
    }
  }

  const addTier = () => {
    const newTier = {
      tier: form.value.tiers.length + 1,
      amount: 0,
      discount: 0
    }
    form.value.tiers.push(newTier)
  }

  const removeTier = (idx) => {
    form.value.tiers.splice(idx, 1)
  }

  const handleSubmit = () => {
    if (validateForm()) {
      emit('save', { ...form.value })
    }
  }

  const validateForm = () => {
    if (props.ruleType === 'quantity') {
      if (!form.value.minQty && form.value.minQty !== 0) {
        alert('براہ کرم کم از کم مقدار درج کریں')
        return false
      }
      if (!form.value.maxQty) {
        alert('براہ کرم زیادہ سے زیادہ مقدار درج کریں')
        return false
      }
      if (form.value.minQty > form.value.maxQty) {
        alert('کم از کم مقدار زیادہ سے زیادہ مقدار سے کم ہونی چاہیے')
        return false
      }
    }

    if (props.ruleType === 'tiered') {
      if (!form.value.name) {
        alert('براہ کرم اصول کا نام درج کریں')
        return false
      }
    }

    if (props.ruleType === 'category') {
      if (!form.value.category) {
        alert('براہ کرم کیٹیگری منتخب کریں')
        return false
      }
    }

    if (props.ruleType === 'time') {
      if (!form.value.name) {
        alert('براہ کرم نام درج کریں')
        return false
      }
      if (form.value.days.length === 0) {
        alert('براہ کرم کم از کم ایک دن منتخب کریں')
        return false
      }
    }

    return true
  }


</script>
