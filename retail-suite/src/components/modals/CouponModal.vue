
<!-- CouponModal.vue -->
<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <h2 class="text-xl font-bold text-gray-900">
          {{ coupon ? 'ترمیم کریں القسيمة' : 'قسيمة نیاة' }}
        </h2>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">کوپن کوڈ *</label>
            <input
              v-model="form.code"
              type="text"
              required
              :disabled="!!coupon"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent uppercase disabled:bg-gray-100"
              placeholder="مثال: SAVE30"
            />
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
              <option value="freeShip">مفت شپنگ</option>
            </select>
          </div>
        </div>

        <div v-if="form.discountType !== 'freeShip'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">الحد الأدنى للخریداری (ج.م)</label>
            <input
              v-model.number="form.minPurchase"
              type="number"
              min="0"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="0"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">استعمال کی کل اجازت</label>
            <input
              v-model.number="form.totalLimit"
              type="number"
              min="-1"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="-1 لـ لامحدود"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">شروع کرنے کی تاریخ *</label>
            <input
              v-model="form.startDate"
              type="date"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">ختم ہونے کی تاریخ *</label>
            <input
              v-model="form.endDate"
              type="date"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">تفصیل</label>
          <textarea
            v-model="form.description"
            rows="2"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="کوپن کی تفصیل"
          ></textarea>
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
            {{ coupon ? 'اپ ڈیٹ کریں' : 'شامل کریں' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

  const props = defineProps({
    coupon: {
      type: Object,
      default: null
    }
  })
  const emit = defineEmits( ['save', 'close'])

    const form = ref({
      id: null,
      code: '',
      discountType: 'percentage',
      discountValue: 0,
      minPurchase: 0,
      startDate: new Date().toISOString().split('T')[0],
      endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      status: 'active',
      usedCount: 0,
      totalLimit: 100,
      description: ''
    })

    watch(() => props.coupon, (newCoupon) => {
      if (newCoupon) {
        form.value = { ...newCoupon }
      } else {
        resetForm()
      }
    }, { immediate: true })

    const resetForm = () => {
      form.value = {
        id: null,
        code: '',
        discountType: 'percentage',
        discountValue: 0,
        minPurchase: 0,
        startDate: new Date().toISOString().split('T')[0],
        endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        status: 'active',
        usedCount: 0,
        totalLimit: 100,
        description: ''
      }
    }

    const handleSubmit = () => {
      if (!form.value.code) {
        alert('براہ کرم کوپن کوڈ درج کریں')
        return
      }
      emit('save', { ...form.value })
    }




</script>
