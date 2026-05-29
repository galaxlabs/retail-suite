<template>
  <div class="fixed inset-0 bg-opacity-50 flex items-center justify-center z-50 p-4">
    <!-- Modal Background -->
    <div
      class="absolute inset-0"
      @click="handleBackgroundClick"
    ></div>

    <!-- Modal Content -->
    <div class="relative bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 transform transition-all">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-green-50 to-emerald-50">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 rounded-lg mr-3">
              <PlayIcon class="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">Open Shift</h3>
              <p class="text-sm text-gray-600">Start a new cashier shift</p>
            </div>


          </div>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition-colors duration-200 p-1"
            :disabled="isLoading"
          >
            <CloseIcon class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Form Content -->
      <form @submit.prevent="submit_dialog" class="px-6 py-6 space-y-6">
        <!-- User Selection -->
        <div>
            <!-- Company Selection -->
            <label class="block text-sm font-medium text-gray-700 mb-2">
            Company *
            </label>
            <select
                v-model="company"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200"
                :disabled="isLoading"
                required
                >
            <option value="" disabled>Select Company</option>
                <option
                    v-for="company in companies"
                    :key="company"
                    :value="company"
                >
                    {{ company }}
                </option>
                </select>
            <label class="block text-sm font-medium text-gray-700 mb-2">
            Pos Profile *
            </label>
              <!-- Select POS Profile -->
            <select
                 v-model="pos_profile"
                 class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200"
                 :disabled="!pos_profiles.length">
                <option value="" disabled>Select POS Profile</option>
                <option v-for="p in pos_profiles" :key="p" :value="p">
                {{ p }}
                </option>
            </select>
            <!-- <label class="block text-sm font-medium text-gray-700 mb-2">
                Cashier / User *
                {{ user }}
            </label>

            <p>  {{ form.userId }}</p> -->
          <!-- <select
            v-model="form.userId"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200"
            :disabled="isLoading"
          >
            <option value="" disabled> {{ form.userId }}</option> -->
            <!-- <option
              v-for="user in shiftStore.users"
              :key="user.id"
              :value="user.id"
            >
              {{ form.value.userId }} - {{ user.role }}
            </option> -->
          <!-- </select> -->
          <!-- <p class="text-xs text-gray-500 mt-1">
            Choose the cashier who will operate this shift
          </p> -->
        </div>

        <!-- Opening Balance -->

        <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
                Opening Balance
                <span class="text-gray-500 font-normal">(per payment method)</span>
            </label>

            <div v-for="m in payments_methods" :key="m.mode_of_payment" class="mb-3">
                <div class="flex items-center">
                <!-- Label -->
                <span class="w-32 text-gray-700 text-sm">
                    {{ m.mode_of_payment }} ({{ m.currency }})
                </span>

                <!-- Input -->
                <input
                    v-model.number="m.amount"
                    type="number"
                    min="0"
                    step="1"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200"
                    :disabled="isLoading"
                    placeholder="0"
                />
                </div>
            </div>

            <p class="text-xs text-gray-500 mt-1">
                Enter opening balance for each payment method
            </p>
        </div>

        <!-- Optional Validation Toggle -->
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div>
            <label class="text-sm font-medium text-gray-700">
              Require Opening Balance
            </label>
            <p class="text-xs text-gray-500">
              Make opening balance mandatory
            </p>
          </div>
          <ToggleSwitch v-model="requireBalance" />
        </div>

        <!-- Notes -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Notes <span class="text-gray-500 font-normal">(Optional)</span>
          </label>
          <textarea
            v-model="form.notes"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200 resize-none"
            rows="3"
            :disabled="isLoading"
            placeholder="Any notes about this shift..."
          ></textarea>
        </div>

        <!-- Current Time Display -->
        <div class="flex items-center justify-center p-3 bg-blue-50 rounded-lg">
          <ClockIcon class="w-5 h-5 text-blue-600 mr-2" />
          <span class="text-sm font-medium text-blue-900">
            Shift will start at: {{ currentTime }}
          </span>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="p-3 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-center">
            <AlertIcon class="w-5 h-5 text-red-600 mr-2" />
            <span class="text-sm text-red-800">{{ errorMessage }}</span>
          </div>
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="p-3 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-center">
            <CheckIcon class="w-5 h-5 text-green-600 mr-2" />
            <span class="text-sm text-green-800">{{ successMessage }}</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            @click="$emit('close')"
            class="flex-1 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200"
            :disabled="isLoading"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="!canSubmit || isLoading"
            class="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <LoadingSpinner v-if="isLoading" class="w-4 h-4 mr-2" />
            <PlayIcon v-else class="w-4 h-4 mr-2" />
            {{ isLoading ? 'Opening...' : 'Open Shift' }}
          </button>
        </div>
      </form>
    </div>
  </div>

</template>



<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useShiftStore } from '@/stores/shift'
import { useSettingsStore } from '@/stores/settings'
import { get_opening_dialog_data, open_shift } from '@/composables/shift'
import ClockIcon from '@/components/icons/ClockIcon.svg'
import PlayIcon from '@/components/icons/PlayIcon.svg'
import LoadingSpinner from '@/components/icons/LoadingSpinner.vue'
import ToggleSwitch from '@/components/icons/ToggleSwitch.vue'
import CheckIcon from '@/components/icons/CheckIcon.svg'
import CloseIcon from '@/components/icons/CloseIcon.svg'
import AlertIcon from '@/components/icons/AlertIcon.svg'


  const emit = defineEmits(['close', 'success', 'error'])

    const shiftStore = useShiftStore()
    const settingsStore = useSettingsStore()
    const companies_data = ref([])
    const companies = ref([])
    const company = ref('')
    const pos_profiles_data = ref([])
    const payments_method_data = ref([])
    const pos_profile = ref('')
    const payments_methods = ref([])
    const pos_profiles = ref([])

    const selectedCurrency = () =>
        pos_profiles_data.value.find(el => el.name === pos_profile.value)?.currency ||
        companies_data.value.find(el => el.name === company.value)?.default_currency ||
        settingsStore.settings.pricing.currency

    const syncProfilesForCompany = (selectedCompany) => {
        // Show all profiles regardless of company
        pos_profiles.value = pos_profiles_data.value
            .map(el => el.name)

        // Pre-select first profile matching the company if possible
        const matching = pos_profiles_data.value.filter(el => el.company === selectedCompany)
        pos_profile.value = matching.length
            ? matching[0].name
            : (pos_profiles.value.length ? pos_profiles.value[0] : '')
    }

    watch(company, syncProfilesForCompany)
    watch(pos_profile, (val) => {
        payments_methods.value = payments_method_data.value
            .filter(el => el.parent === val)
            .map(el => ({
                mode_of_payment: el.mode_of_payment,
                amount: 0,
                currency: el.currency
            }))

        if (val) {
            settingsStore.applyCurrencySettings(selectedCurrency())
        }
    })

        // Form state
        const form = ref({
            userId: '',
            openingBalance: 0,
            notes: ''
        })

    const requireBalance = ref(false)
    const isLoading = ref(false)
    const errorMessage = ref('')
    const successMessage = ref('')
    const currentTime = ref('')

    // Computed properties
    const canSubmit = computed(() => {
      if (!company.value || !pos_profile.value) return false
      if (requireBalance.value && (!form.value.openingBalance || form.value.openingBalance < 0)) {
        return false
      }
      return !isLoading.value
    })

    const selectedUser = computed(() => {
      return shiftStore.users.find(user => user.id === form.value.userId)
    })

    // Update current time
    const updateCurrentTime = () => {
      currentTime.value = new Date().toLocaleString('en-US', {
          timeZone: 'Asia/Riyadh',
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
      })

    }

    let timeInterval
    onMounted(async() => {

      updateCurrentTime()
      timeInterval = setInterval(updateCurrentTime, 1000)

      // Auto-select first user if only one available
      if (shiftStore.users.length === 1) {
        console.log("Auto-selecting user:", shiftStore.users[0])
        form.value.userId = shiftStore.users[0].id
      }
        // Fetch additional data if needed
        const data  = await get_opening_dialog_data()
        console.log("Open Dialog Data", data)

        companies_data.value = data.companies || []
        companies.value = companies_data.value.map(el => el.name)
        console.log("companies", companies)

        pos_profiles_data.value = data.pos_profiles_data || []
        payments_method_data.value = data.payments_method || []

        const defaultCompany = pos_profiles_data.value[0]?.company || companies.value[0] || ''
        if (defaultCompany) {
            company.value = defaultCompany
            syncProfilesForCompany(defaultCompany)
        }


    })
    onMounted(() => {
        getCurrentUserData();
    });
    onUnmounted(() => {
      if (timeInterval) {
        clearInterval(timeInterval)
      }
    })
    const submit_dialog = async() => {
        try {
            // isLoading = true;
            clearMessages()
            if (!payments_methods.value.length || !company.value || !pos_profile.value) {
                return;
            }
            const validation = shiftStore.validateShiftOperation('open', form.value)
            if (!validation.valid) {
                errorMessage.value = validation.message
                return
            }
            const shiftData = {
                            pos_profile: pos_profile.value,
                            company: company.value,
                            balance_details: JSON.stringify(payments_methods.value)
                        }

            const newShift = await open_shift(shiftData)
            if (newShift) {
            settingsStore.applyCurrencySettings(newShift.pos_profile?.currency || selectedCurrency())
            shiftStore.isShiftOpen = true
            console.log('After set in modal:', shiftStore.isShiftOpen)
            console.log("r.message:", newShift)
            setTimeout(() => {
            emit('success', newShift)
            emit('close')
            }, 1000)
            successMessage.value = 'Shift opened successfully!'

            }

        } catch (error) {
            console.error('Failed to create opening voucher:', error);
            errorMessage.value = error.message || 'Failed to open shift. Please try again.'
        } finally {
            // isLoading = false;
        }

    }
    // Clear messages
    const clearMessages = () => {
      errorMessage.value = ''
      successMessage.value = ''
    }

    // Handle background click
    const handleBackgroundClick = () => {
      if (!isLoading.value) {
        emit('close')
      }
    }

    const getCurrentUserData = async () => {
        try {
            const currentUserInfo = await shiftStore.getCurrentUserInfo();
            if (!currentUserInfo || !currentUserInfo.user) {
                form.value.userId = "";
                return;
            }
            form.value.userId = currentUserInfo.user; // Set the userId in the form
            console.log("Current User in Modal:", currentUserInfo);

        } catch (error) {
            console.error('Error fetching current user:', error);
        }

    };

</script>

<style scoped>
/* Animation classes */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Focus states */
input:focus, select:focus, textarea:focus {
  outline: none;
}

/* Disabled states */
input:disabled, select:disabled, textarea:disabled, button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Gradient background */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

.from-green-50 {
  --tw-gradient-from: #f0fdf4;
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(240, 253, 244, 0));
}

.to-emerald-50 {
  --tw-gradient-to: #ecfdf5;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .max-w-md {
    max-width: calc(100vw - 2rem);
  }
}
</style>
