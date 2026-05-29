<template>
<div class="fixed inset-0 flex items-center justify-center z-50 p-4"
:style="{ background: 'var(--item-bg)' }">
  <div class=" rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
   :style="{
            background: 'var(--card-bg)',
            borderColor: 'var(--card-border)'
          }">
      <!-- Header -->
      <div class="sticky top-0 bg-gray-800 border-b border-gray-700 px-6 py-4 flex justify-between items-center">
        <h2 class="text-2xl font-bold text-white">
          {{ shift ? 'Edit Shift' : 'New Shift' }}
        </h2>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-white transition"
        >
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-6">

        <!-- Shift Name -->
        <FormField label="Shift Name" required>
          <input
            v-model="formData.name"
            type="text"
            :disabled="!!shift"
            placeholder="Example: Morning, Evening"
            class="w-full px-4 py-2 rounded-lg border focus:outline-none transition"
            :style="{
              background: 'var(--input-bg)',
              color: 'var(--text-main)',
              borderColor: 'var(--input-border)',
              placeholderColor: 'var(--text-sub)'
            }"
          />
        </FormField>

        <!-- Time Range -->
        <div class="grid grid-cols-2 gap-4">
          <FormField label="Start Time" required>
            <input
              v-model="formData.start_time"
              type="time"
              class="w-full px-4 py-2 rounded-lg border focus:outline-none transition"
              :style="{
                background: 'var(--input-bg)',
                color: 'var(--text-main)',
                borderColor: 'var(--input-border)',
                placeholderColor: 'var(--text-sub)'
              }"
            />
          </FormField>

          <FormField label="End Time" required>
            <input
              v-model="formData.end_time"
              type="time"
              class="w-full px-4 py-2 rounded-lg border focus:outline-none transition"
              :style="{
                background: 'var(--input-bg)',
                color: 'var(--text-main)',
                borderColor: 'var(--input-border)',
                placeholderColor: 'var(--text-sub)'
              }"
            />
          </FormField>
        </div>

        <!-- Holiday List -->
        <FormField label="Holiday List">
          <select
            v-model="formData.holiday_list"
            class="w-full px-4 py-2 rounded-lg border focus:outline-none transition"
            :style="{
              background: 'var(--input-bg)',
              color: 'var(--text-main)',
              borderColor: 'var(--input-border)',
              placeholderColor: 'var(--text-sub)'
            }"
          >
            <option disabled value="">-- No Holiday List --</option>
            <option
              v-for="holiday in holidayLists"
              :key="holiday.name"
              :value="holiday.name"
            >
              {{ holiday.name }}
            </option>
          </select>
        </FormField>

        <!-- Auto Attendance Section -->
        <div class="border-t border-gray-700 pt-6">
          <div class="flex items-center gap-3 mb-4">
            <label class="flex items-center gap-3 mb-4 cursor-pointer">
              <input
                v-model="formData.enable_auto_attendance"
                type="checkbox"
                :true-value="1"
                :false-value="0"
                class=" px-4 py-2 rounded-lg border focus:outline-none transition"
                  :style="{
                    background: 'var(--input-bg)',
                    color: 'var(--text-main)',
                    borderColor: 'var(--input-border)',
                    placeholderColor: 'var(--text-sub)'
                  }"
              />
              <span class="text-white font-semibold">
                Enable Auto Attendance
              </span>
            </label>
          </div>

          <!-- Process Attendance After -->
          <Transition name="fade">
            <FormField
              v-if="formData.enable_auto_attendance"
              label="Process Attendance After"
              :required="formData.enable_auto_attendance"
            >
              <input
                v-model="formData.process_attendance_after"
                type="date"
                class="w-full px-4 py-2 rounded-lg border focus:outline-none transition"
                :style="{
                  background: 'var(--input-bg)',
                  color: 'var(--text-main)',
                  borderColor: 'var(--input-border)',
                  placeholderColor: 'var(--text-sub)'
                }"
              />
              <p class="text-gray-400 text-sm mt-2">
                Check-in and check-out records will be processed starting from this date
              </p>
            </FormField>
          </Transition>
        </div>

        <!-- Last Sync -->
        <div class="border-t border-gray-700 pt-6">
          <div class="flex items-center gap-3 mb-4">
            <input
              v-model="formData.last_sync_of_checkin"
              type="datetime-local"
              class="w-full px-4 py-2 rounded-lg border focus:outline-none transition"
              :style="{
                background: 'var(--input-bg)',
                color: 'var(--text-main)',
                borderColor: 'var(--input-border)',
                placeholderColor: 'var(--text-sub)'
              }"
            />
          </div>
          <p class="text-gray-400 text-sm mt-2">Last Sync Date</p>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="p-4 bg-red-700 border border-red-600 rounded-lg">
          <p class="text-red-100 text-sm">{{ error }}</p>
        </div>

        <!-- Actions -->
        <div class="flex gap-3 pt-6 border-t border-gray-700">
          <button
            type="button"
            @click="$emit('close')"
            class="flex-1 px-4 py-2 text-gray-300 border border-gray-600 rounded-lg hover:bg-gray-700 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
          >
            <Loader v-if="loading" class="w-4 h-4 animate-spin" />
            {{ loading ? 'Saving...' : 'Save Shift' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { X, Loader } from 'lucide-vue-next'
import FormField from '@/components/modals/FormField.vue'
/* ========================
   Props & Emits
======================== */
const props = defineProps({
  shift: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  holidayLists:{
    type: Array,
    default: () => [],
  }
})

const emit = defineEmits(['save', 'close'])

/* ========================
   State
======================== */
const formData = reactive({
  name: '',
  start_time: '',
  end_time: '',
  enable_auto_attendance: false,
  process_attendance_after: null,
  holiday_list: '',
  last_sync_of_checkin:null
})


const error = ref('')

/* ========================
   Computed
======================== */
const isFormValid = computed(() => {
  return (
    formData.name &&
    formData.start_time &&
    formData.end_time &&
    (!formData.enable_auto_attendance || formData.process_attendance_after)
  )
})

/* ========================
   Methods
======================== */

const handleSubmit = () => {
  if (!isFormValid.value) {
    error.value = 'براہ کرم تمام مطلوبہ فیلڈز پُر کریں'
    return
  }

  error.value = ''
  emit('save', { ...formData })
}

/* ========================
   Watchers
======================== */
watch(
  () => props.shift,
  (newShift) => {
    if (newShift) {
      Object.assign(formData, newShift)
    } else {
      Object.assign(formData, {
        name: '',
        start_time: '',
        end_time: '',
        enable_auto_attendance: false,
        process_attendance_after: null,
        holiday_list: '',
        last_sync_of_checkin:null
      })
    }
  },
  { immediate: true }
)

/* ========================
   Lifecycle
======================== */
const formatTime = (time) => {
  if (!time) return '-'
  try {
    const [hours, minutes] = time.split(':')
    return `${hours}:${minutes}`
  } catch {
    return time
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
