<!-- PromotionModal.vue -->
<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <h2 class="text-xl font-bold text-gray-900">
          {{ promotion ? 'ترمیم کریں الدیکھیں' : 'دیکھیں ترويجي نیا' }}
        </h2>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">اسم الدیکھیں *</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="مثال: خصم جمعہ البيضاء"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">نوع الدیکھیں *</label>
            <select
              v-model="form.type"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">اختر قسم</option>
              <option value="percentage">فیصد ڈسکاونٹ</option>
              <option value="fixed">مقررہ ڈسکاونٹ</option>
              <option value="bundle">دیکھیں مجمع</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">تفصیل</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="وصف الدیکھیں"
          ></textarea>
        </div>

        <div v-if="form.type !== 'bundle'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              قيمة الدیکھیں *
              <span class="text-gray-500 text-xs">({{ form.type === 'percentage' ? '%' : 'ج.م' }})</span>
            </label>
            <input
              v-model.number="form.value"
              type="number"
              min="0"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">کم از کم رقم</label>
            <input
              v-model.number="form.minAmount"
              type="number"
              min="0"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="0"
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

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">استعمال کی حد</label>
            <input
              v-model.number="form.usageLimit"
              type="number"
              min="-1"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="-1 لـ لامحدود"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">شامل اشیاء *</label>
            <select
              v-model="form.applicableProducts"
              multiple
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">تمام اشیاء</option>
              <option value="beverages">مشروبات</option>
              <option value="food">کھانا</option>
              <option value="desserts">میٹھائیاں</option>
            </select>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <input v-model="form.status" value="active" type="radio" id="active" class="w-4 h-4" />
          <label for="active" class="text-sm font-medium text-gray-700">فعال</label>

          <input v-model="form.status" value="inactive" type="radio" id="inactive" class="w-4 h-4" />
          <label for="inactive" class="text-sm font-medium text-gray-700">غیر فعال</label>
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
            {{ promotion ? 'اپ ڈیٹ کریں' : 'شامل کریں' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
  const props = defineProps( {
    promotion: {
      type: Object,
      default: null
    }
  })
  const emit = defineEmits(['save', 'close'])

    const form = ref({
      id: null,
      name: '',
      description: '',
      type: 'percentage',
      value: 0,
      minAmount: 0,
      startDate: new Date().toISOString().split('T')[0],
      endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      status: 'active',
      usageLimit: 100,
      usageCount: 0,
      applicableProducts: ['all']
    })

    watch(() => props.promotion, (newPromo) => {
      if (newPromo) {
        form.value = { ...newPromo }
      } else {
        resetForm()
      }
    }, { immediate: true })

    const resetForm = () => {
      form.value = {
        id: null,
        name: '',
        description: '',
        type: 'percentage',
        value: 0,
        minAmount: 0,
        startDate: new Date().toISOString().split('T')[0],
        endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        status: 'active',
        usageLimit: 100,
        usageCount: 0,
        applicableProducts: ['all']
      }
    }

    const handleSubmit = () => {
      if (!form.value.name) {
        alert('براہ کرم پروموشن کا نام درج کریں')
        return
      }
      if (!form.value.type) {
        alert('براہ کرم پروموشن کی قسم منتخب کریں')
        return
      }
      emit('save', { ...form.value })
    }
</script>

---
