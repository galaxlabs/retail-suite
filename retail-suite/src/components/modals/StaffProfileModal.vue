<template>
  <div
    class="fixed inset-0 bg-opacity-50 z-50 flex items-center justify-center p-4"
  >
    <div
      class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto"
    >
      <!-- Header -->
      <div
        class="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-6 flex items-center justify-between"
      >
        <div>
          <h2 class="text-2xl font-bold">{{ staff.name }}</h2>
          <p class="text-blue-100 text-sm mt-1">
            #{{ staff.name }} • {{ staff.designation }} في
            {{ getDepartmentLabel(staff.department) }}
          </p>
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
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200"
          >
            <p class="text-green-600 text-sm font-semibold mb-1">
              بنیادی تنخواہ
            </p>
            <p class="text-2xl font-bold text-green-900">
              {{ formatCurrency(staff.salary) }}
            </p>
          </div>

          <div
            class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200"
          >
            <p class="text-blue-600 text-sm font-semibold mb-1">
              خالص مہینہي
            </p>
            <p class="text-2xl font-bold text-blue-900">
              {{ formatCurrency(netSalary) }}
            </p>
          </div>

          <div
            :class="[
              'bg-gradient-to-br rounded-lg p-4 border',
              staff.status === 'active'
                ? 'from-green-50 to-green-100 border-green-200'
                : 'from-gray-50 to-gray-100 border-gray-200',
            ]"
          >
            <p
              :class="[
                'text-sm font-semibold mb-1',
                staff.status === 'active' ? 'text-green-600' : 'text-gray-600',
              ]"
            >
              Status
            </p>
            <p
              :class="[
                'text-2xl font-bold',
                staff.status === 'active' ? 'text-green-900' : 'text-gray-900',
              ]"
            >
              {{ getStatusLabel(staff.status) }}
            </p>
          </div>
        </div>

        <!-- Tabs -->
        <div class="border-b border-gray-200">
          <div class="flex gap-4">
            <button
              @click="activeTab = 'info'"
              :class="[
                'px-4 py-3 font-medium border-b-2 transition',
                activeTab === 'info'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900',
              ]"
            >
              المعلومات
            </button>
            <button
              @click="activeTab = 'salary'"
              :class="[
                'px-4 py-3 font-medium border-b-2 transition',
                activeTab === 'salary'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900',
              ]"
            >
              تنخواہیں
            </button>
            <button
              @click="activeTab = 'attendance'"
              :class="[
                'px-4 py-3 font-medium border-b-2 transition',
                activeTab === 'attendance'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900',
              ]"
            >
              حاضری
            </button>
            <button
              @click="activeTab = 'performance'"
              :class="[
                'px-4 py-3 font-medium border-b-2 transition',
                activeTab === 'performance'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900',
              ]"
            >
              کارکردگی
            </button>
          </div>
        </div>

        <!-- Tab Content -->
        <!-- Info Tab -->
        <div v-if="activeTab === 'info'" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Personal Info -->
            <div class="bg-gray-50 rounded-lg p-4 space-y-3">
              <h3 class="font-semibold text-gray-900 mb-4">
                ذاتی معلومات
              </h3>
              <div>
                <p class="text-sm text-gray-600">نام</p>
                <p class="font-medium text-gray-900">{{ staff.employee_name }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">ای میل</p>
                <p class="font-medium text-gray-900">{{ staff.company_email }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">الهاتف</p>
                <p class="font-medium text-gray-900">{{ staff.cell_number }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">پتہ</p>
                <p class="font-medium text-gray-900">{{ staff.address }}</p>
              </div>
            </div>

            <!-- Job Info -->
            <div class="bg-gray-50 rounded-lg p-4 space-y-3">
              <h3 class="font-semibold text-gray-900 mb-4">
                ملازمت کی معلومات
              </h3>
              <div>
                <p class="text-sm text-gray-600">ملازم نمبر</p>
                <p class="font-medium text-gray-900">#{{ staff.name }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">عہدہ</p>
                <p class="font-medium text-gray-900">{{ staff.designation }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">شعبہ</p>
                <p class="font-medium text-gray-900">
                  {{ getDepartmentLabel(staff.department) }}
                </p>
              </div>
              <div>
                <p class="text-sm text-gray-600"> Date of Joining</p>
                <p class="font-medium text-gray-900">
                  {{ formatDate(staff.date_of_joining) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Salary Tab -->
        <div v-if="activeTab === 'salary'" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p class="text-blue-600 text-sm font-semibold">بنیادی تنخواہ</p>
              <p class="text-2xl font-bold text-blue-900 mt-2">
                {{ formatCurrency(staff.salary) }}
              </p>
            </div>
            <div class="bg-green-50 rounded-lg p-4 border border-green-200">
              <p class="text-green-600 text-sm font-semibold">الاونس</p>
              <p class="text-2xl font-bold text-green-900 mt-2">
                {{ formatCurrency(staff.bonus || 0) }}
              </p>
            </div>
            <div class="bg-red-50 rounded-lg p-4 border border-red-200">
              <p class="text-red-600 text-sm font-semibold">کٹوتیاں</p>
              <p class="text-2xl font-bold text-red-900 mt-2">
                {{ formatCurrency(staff.deductions || 0) }}
              </p>
            </div>
          </div>

          <!-- Salary History -->
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h4 class="font-semibold text-gray-900 mb-4">سجل تنخواہیں</h4>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead class="bg-gray-100 border-b border-gray-200">
                  <tr>
                    <th class="px-4 py-2 text-right font-semibold">مہینہ</th>
                    <th class="px-4 py-2 text-right font-semibold">الراتب</th>
                    <th class="px-4 py-2 text-right font-semibold">الاونس</th>
                    <th class="px-4 py-2 text-right font-semibold">کٹوتیاں</th>
                    <th class="px-4 py-2 text-right font-semibold">خالص</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr
                    v-for="(record, idx) in salaryHistory"
                    :key="idx"
                    class="hover:bg-white transition"
                  >
                    <td class="px-4 py-2 text-gray-600">{{ record.month }}</td>
                    <td class="px-4 py-2 font-semibold text-gray-900">
                      {{ formatCurrency(record.salary) }}
                    </td>
                    <td class="px-4 py-2 text-green-600">
                      {{ formatCurrency(record.bonus) }}
                    </td>
                    <td class="px-4 py-2 text-red-600">
                      {{ formatCurrency(record.deductions) }}
                    </td>
                    <td class="px-4 py-2 font-bold text-gray-900">
                      {{ formatCurrency(record.net) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Attendance Tab -->
        <div v-if="activeTab === 'attendance'" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-green-50 rounded-lg p-4 border border-green-200">
              <p class="text-green-600 text-sm font-semibold">دن حاضری</p>
              <p class="text-3xl font-bold text-green-900 mt-2">
                {{ attendanceStats.present }}
              </p>
            </div>
            <div class="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <p class="text-yellow-600 text-sm font-semibold">غیر حاضری کے دن</p>
              <p class="text-3xl font-bold text-yellow-900 mt-2">
                {{ attendanceStats.absent }}
              </p>
            </div>
            <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p class="text-blue-600 text-sm font-semibold">معدل حاضری</p>
              <p class="text-3xl font-bold text-blue-900 mt-2">
                {{ attendanceStats.percentage }}%
              </p>
            </div>
          </div>
        </div>

        <!-- Performance Tab -->
        <div v-if="activeTab === 'performance'" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p class="text-blue-600 text-sm font-semibold mb-2">
                تقييم کارکردگی
              </p>
              <div class="flex items-center gap-2">
                <div class="flex gap-1">
                  <span
                    v-for="n in 5"
                    :key="n"
                    :class="[
                      'text-xl',
                      n <= performance.rating
                        ? 'text-yellow-400'
                        : 'text-gray-300',
                    ]"
                    >★</span
                  >
                </div>
                <span class="text-xl font-bold text-blue-900"
                  >{{ performance.rating }}/5</span
                >
              </div>
            </div>

            <div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
              <p class="text-purple-600 text-sm font-semibold mb-2">
                المبيعات هذا مہینہ
              </p>
              <p class="text-2xl font-bold text-purple-900">
                {{ formatCurrency(performance.sales) }}
              </p>
            </div>
          </div>

          <!-- Performance Notes -->
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h4 class="font-semibold text-gray-900 mb-2">ملاحظات</h4>
            <p class="text-gray-700">{{ performance.notes }}</p>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div
        class="border-t border-gray-200 bg-gray-50 px-6 py-4 flex items-center justify-end gap-4"
      >
        <button
          @click="printProfile"
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
import { ref, computed } from "vue"

/* =========================
   Props & Emits
========================= */
const props = defineProps({
  staff: {
    type: Object,
    required: true,
  },
  salaryHistory: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(["close"])

/* =========================
   State
========================= */
const activeTab = ref("info")

const attendanceStats = ref({
  present: 28,
  absent: 2,
  percentage: 93,
})

const performance = ref({
  rating: 4,
  sales: 150000,
  notes: "موظف متفاني ويعمل بجد، أداء ممتاز هذا مہینہ",
})

/* =========================
   Computed
========================= */
const netSalary = computed(() => {
  return (
    (props.staff.salary || 0) +
    (props.staff.bonus || 0) -
    (props.staff.deductions || 0)
  )
})

/* =========================
   Helpers
========================= */
const formatCurrency = (value) => {
  return new Intl.NumberFormat("ar-EG", {
    style: "currency",
    currency: "EGP",
  }).format(value || 0)
}

const getDepartmentLabel = (dept) => {
  const labels = {
    sales: "المبيعات",
    warehouse: "المستودع",
    cashier: "کیشیرز",
    management: "الإدارة",
  }
  return labels[dept] || dept
}

const getStatusLabel = (status) => {
  const labels = {
    Active: "فعال",
    Inactive: "غير فعال",
    Suspended: "موقوف",
    Left: "مغادر",
  }
  return labels[status] || status
}

const formatDate = (date) => {
  return date ? new Date(date).toLocaleDateString("ar-EG") : "-"
}

const printProfile = () => {
  window.print()
}
</script>
