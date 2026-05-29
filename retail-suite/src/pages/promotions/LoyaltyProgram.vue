<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">برنامج الولاء والنقاط</h1>
        <p class="text-gray-600 mt-1">إدارة برنامج النقاط والمكافآت</p>
      </div>
      <button
        @click="showSettings = true"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        ⚙️ إعدادات البرنامج
      </button>
    </div>

    <!-- Program Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200 shadow">
        <p class="text-blue-600 text-sm font-semibold">إجمالي الأعضاء</p>
        <p class="text-3xl font-bold text-blue-900 mt-2">{{ totalMembers }}</p>
      </div>

      <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200 shadow">
        <p class="text-green-600 text-sm font-semibold">النقاط الموزعة</p>
        <p class="text-3xl font-bold text-green-900 mt-2">{{ totalPointsDistributed }}</p>
      </div>

      <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200 shadow">
        <p class="text-purple-600 text-sm font-semibold">النقاط المستخدمة</p>
        <p class="text-3xl font-bold text-purple-900 mt-2">{{ totalPointsUsed }}</p>
      </div>

      <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200 shadow">
        <p class="text-orange-600 text-sm font-semibold">العضويات الذهبية</p>
        <p class="text-3xl font-bold text-orange-900 mt-2">{{ goldMembers }}</p>
      </div>

      <div class="bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg p-4 border border-pink-200 shadow">
        <p class="text-pink-600 text-sm font-semibold">المكافآت المستحقة</p>
        <p class="text-3xl font-bold text-pink-900 mt-2">{{ pendingRewards }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <div class="flex gap-4">
        <button
          @click="activeTab = 'tiers'"
          :class="['px-4 py-3 font-medium border-b-2 transition', activeTab === 'tiers' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
        >
          ⭐ مستويات العضوية
        </button>
        <button
          @click="activeTab = 'members'"
          :class="['px-4 py-3 font-medium border-b-2 transition', activeTab === 'members' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
        >
          👥 الأعضاء
        </button>
        <button
          @click="activeTab = 'rewards'"
          :class="['px-4 py-3 font-medium border-b-2 transition', activeTab === 'rewards' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
        >
          🎁 المكافآت
        </button>
        <button
          @click="activeTab = 'history'"
          :class="['px-4 py-3 font-medium border-b-2 transition', activeTab === 'history' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900']"
        >
          📜 السجل
        </button>
      </div>
    </div>

    <!-- Membership Tiers -->
    <div v-if="activeTab === 'tiers'" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-6">مستويات العضوية</h2>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div v-for="tier in membershipTiers" :key="tier.id" class="border-2 rounded-lg p-6 text-center" :class="tier.borderClass">
          <div class="text-4xl mb-2">{{ tier.icon }}</div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">{{ tier.name }}</h3>

          <div class="bg-gray-50 rounded p-3 mb-4">
            <p class="text-xs text-gray-600">الحد الأدنى للنقاط</p>
            <p class="text-2xl font-bold text-gray-900">{{ tier.minPoints }}</p>
          </div>

          <div class="space-y-2 text-sm mb-4">
            <p v-for="benefit in tier.benefits" :key="benefit" class="text-gray-600">✓ {{ benefit }}</p>
          </div>

          <p class="text-2xl font-bold text-gray-900 mb-4">
            <span :class="tier.colorClass">{{ tier.memberCount }} عضو</span>
          </p>

          <button class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
            تعديل
          </button>
        </div>
      </div>
    </div>

    <!-- Members -->
    <div v-if="activeTab === 'members'" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-6">الأعضاء</h2>

      <div class="mb-4 flex gap-4">
        <input
          v-model="memberSearch"
          type="text"
          placeholder="ابحث عن عميل..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
        <select
          v-model="tierFilter"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">جميع المستويات</option>
          <option value="bronze">برونزي</option>
          <option value="silver">فضي</option>
          <option value="gold">ذهبي</option>
          <option value="platinum">بلاتيني</option>
        </select>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-6 py-3 text-right text-sm font-semibold">الاسم</th>
              <th class="px-6 py-3 text-right text-sm font-semibold">المستوى</th>
              <th class="px-6 py-3 text-right text-sm font-semibold">النقاط</th>
              <th class="px-6 py-3 text-right text-sm font-semibold">الهاتف</th>
              <th class="px-6 py-3 text-right text-sm font-semibold">تاريخ الانضمام</th>
              <th class="px-6 py-3 text-right text-sm font-semibold">الإجراءات</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="member in members" :key="member.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 text-sm text-gray-900 font-medium">{{ member.name }}</td>
              <td class="px-6 py-4 text-sm">
                <span :class="getTierClass(member.tier)" class="px-2 py-1 rounded text-xs font-semibold">
                  {{ getTierLabel(member.tier) }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm font-bold text-gray-900">{{ member.points }}</td>
              <td class="px-6 py-4 text-sm text-gray-600">{{ member.phone }}</td>
              <td class="px-6 py-4 text-sm text-gray-600">{{ formatDate(member.joinDate) }}</td>
              <td class="px-6 py-4 text-sm space-x-2">
                <button @click="editMember(member)" class="text-blue-600 hover:text-blue-900">✏️</button>
                <button @click="viewMemberDetails(member)" class="text-green-600 hover:text-green-900">👁️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Rewards -->
    <div v-if="activeTab === 'rewards'" class="bg-white rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-lg font-semibold text-gray-900">المكافآت المتاحة</h2>
        <button
          @click="openRewardModal"
          class="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
        >
          ➕ إضافة مكافأة
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="reward in rewards" :key="reward.id" class="border border-gray-200 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-900">{{ reward.name }}</h3>
            <span class="text-2xl">{{ reward.icon }}</span>
          </div>

          <p class="text-sm text-gray-600 mb-3">{{ reward.description }}</p>

          <div class="bg-blue-50 rounded p-3 mb-3">
            <p class="text-xs text-blue-600 font-semibold">النقاط المطلوبة</p>
            <p class="text-2xl font-bold text-blue-900">{{ reward.pointsRequired }}</p>
          </div>

          <p class="text-xs text-gray-600 mb-3">متبقي: {{ reward.stock }} من {{ reward.totalStock }}</p>

          <div class="flex gap-2">
            <button @click="editReward(reward)" class="flex-1 text-blue-600 hover:text-blue-900 py-1">✏️</button>
            <button @click="deleteReward(reward.id)" class="flex-1 text-red-600 hover:text-red-900 py-1">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- History -->
    <div v-if="activeTab === 'history'" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-6">سجل النقاط والمكافآت</h2>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-6 py-3 text-right text-sm font-semibold">التاريخ</th>
              <th class="px-6 py-3 text-right text-sm font-semibold">العميل</th>
              <th class="px-6 py-3 text-right text-sm font-semibold">النوع</th>
              <th class="px-6 py-3 text-right text-sm font-semibold">النقاط</th>
              <th class="px-6 py-3 text-right text-sm font-semibold">الوصف</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="record in history" :key="record.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 text-sm text-gray-600">{{ formatDate(record.date) }}</td>
              <td class="px-6 py-4 text-sm text-gray-900 font-medium">{{ record.customerName }}</td>
              <td class="px-6 py-4 text-sm">
                <span :class="record.type === 'earn' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-1 rounded text-xs font-semibold">
                  {{ record.type === 'earn' ? 'كسب' : 'استخدام' }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm font-bold" :class="record.type === 'earn' ? 'text-green-600' : 'text-red-600'">
                {{ record.type === 'earn' ? '+' : '-' }}{{ record.points }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-600">{{ record.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

    const activeTab = ref('tiers')
    const showSettings = ref(false)
    const memberSearch = ref('')
    const tierFilter = ref('')

    const membershipTiers = ref([
      {
        id: 1,
        name: 'برونزي',
        icon: '🥉',
        borderClass: 'border-orange-300',
        minPoints: 0,
        memberCount: 245,
        colorClass: 'text-orange-600',
        benefits: ['خصم 2%', 'عروض حصرية', 'دعم الأولوية']
      },
      {
        id: 2,
        name: 'فضي',
        icon: '🥈',
        borderClass: 'border-gray-300',
        minPoints: 1000,
        memberCount: 89,
        colorClass: 'text-gray-600',
        benefits: ['خصم 5%', 'عروض أسبوعية', 'شحن مجاني']
      },
      {
        id: 3,
        name: 'ذهبي',
        icon: '🥇',
        borderClass: 'border-yellow-300',
        minPoints: 5000,
        memberCount: 23,
        colorClass: 'text-yellow-600',
        benefits: ['خصم 10%', 'هدايا شهرية', 'دعم VIP']
      },
      {
        id: 4,
        name: 'بلاتيني',
        icon: '💎',
        borderClass: 'border-blue-300',
        minPoints: 10000,
        memberCount: 5,
        colorClass: 'text-blue-600',
        benefits: ['خصم 15%', 'هدايا حصرية', 'مدير حساب شخصي']
      }
    ])

    const members = ref([
      {
        id: 1,
        name: 'أحمد محمد',
        tier: 'gold',
        points: 7500,
        phone: '01234567890',
        joinDate: '2024-06-15'
      },
      {
        id: 2,
        name: 'فاطمة علي',
        tier: 'silver',
        points: 3200,
        phone: '01111111111',
        joinDate: '2024-09-20'
      },
      {
        id: 3,
        name: 'محمود حسن',
        tier: 'bronze',
        points: 450,
        phone: '01555555555',
        joinDate: '2024-11-10'
      }
    ])

    const rewards = ref([
      {
        id: 1,
        name: 'خصم 100 جنيه',
        icon: '🎟️',
        description: 'استخدم النقاط للحصول على خصم',
        pointsRequired: 1000,
        stock: 45,
        totalStock: 100
      },
      {
        id: 2,
        name: 'قهوة مجانية',
        icon: '☕',
        description: 'احصل على قهوة لاتيه مجانية',
        pointsRequired: 500,
        stock: 78,
        totalStock: 100
      },
      {
        id: 3,
        name: 'وجبة شاملة',
        icon: '🍔',
        description: 'وجبة برجر مع مشروب وحلوى',
        pointsRequired: 1500,
        stock: 12,
        totalStock: 50
      }
    ])

    const history = ref([
      {
        id: 1,
        date: '2025-01-28',
        customerName: 'أحمد محمد',
        type: 'earn',
        points: 250,
        description: 'شراء من المتجر'
      },
      {
        id: 2,
        date: '2025-01-27',
        customerName: 'فاطمة علي',
        type: 'redeem',
        points: 500,
        description: 'استخدام قسيمة'
      },
      {
        id: 3,
        date: '2025-01-26',
        customerName: 'محمود حسن',
        type: 'earn',
        points: 120,
        description: 'مكافأة العضوية'
      }
    ])

    const totalMembers = computed(() => members.value.length)
    const totalPointsDistributed = computed(() => members.value.reduce((sum, m) => sum + m.points, 0))
    const totalPointsUsed = computed(() => history.value.filter(h => h.type === 'redeem').reduce((sum, h) => sum + h.points, 0))
    const goldMembers = computed(() => members.value.filter(m => m.tier === 'gold' || m.tier === 'platinum').length)
    const pendingRewards = computed(() => rewards.value.reduce((sum, r) => sum + (r.stock - Math.floor(r.stock / 2)), 0))

    const formatDate = (date) => new Date(date).toLocaleDateString('ar-EG')

    const getTierClass = (tier) => {
      const classes = {
        bronze: 'bg-orange-100 text-orange-800',
        silver: 'bg-gray-100 text-gray-800',
        gold: 'bg-yellow-100 text-yellow-800',
        platinum: 'bg-blue-100 text-blue-800'
      }
      return classes[tier] || 'bg-gray-100 text-gray-800'
    }

    const getTierLabel = (tier) => {
      const labels = {
        bronze: 'برونزي',
        silver: 'فضي',
        gold: 'ذهبي',
        platinum: 'بلاتيني'
      }
      return labels[tier] || tier
    }

    const editMember = (member) => {
      window.$toast?.info('Editing ' + member.name)
    }

    const viewMemberDetails = (member) => {
      window.$toast?.info('Viewing ' + member.name)
    }

    const openRewardModal = () => {
      window.$toast?.info('Opening new reward window')
    }

    const editReward = (reward) => {
      window.$toast?.info('Editing ' + reward.name)
    }

    const deleteReward = (id) => {
      window.$toast?.warning('Deleting reward')
    }


</script>
