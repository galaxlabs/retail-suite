<!-- UserProfile.vue -->
<template>

    <div class="w-full flex min-h-screen" style="font-size: 13px;" :style="{ background: 'var(--item-bg)' }">
      <main class="flex flex-col flex-1">

        <!-- ══════════════════ HEADER ══════════════════ -->
        <header
          class="mx-3 mt-3 sticky top-0 z-10 rounded-lg shadow-sm"
          :style="{
            background: 'var(--card-bg)',
            border: '1px solid var(--card-border)'
          }"
        >
          <div class="px-4 py-2 flex justify-between items-center">
            <div class="flex items-center gap-2">
              <button
                @click="goBack"
                class="p-1.5 rounded-md transition-colors"
                :style="{ color: 'var(--text-muted)' }"
                @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                @mouseleave="$event.currentTarget.style.background = 'transparent'"
              >
                <ArrowLeft class="w-4 h-4" />
              </button>

              <User class="w-5 h-5" style="color: #db2777;" />
              <div>
                <h1 class="text-sm font-bold" :style="{ color: 'var(--text-main)' }">
                  {{ viewingUser ? `${userProfile.name}'s Profile` : 'User Profile & Settings' }}
                </h1>
                <p class="text-xs" :style="{ color: 'var(--text-muted)' }">{{ viewingUser ? 'Viewing profile' : 'Editing profile' }}</p>
              </div>
            </div>
            </div>
        </header>

        <!-- ══════════════════ LOADING ══════════════════ -->
        <div v-if="loading" class="flex justify-center items-center py-12">
          <svg class="w-7 h-7 animate-spin" :style="{ color: 'var(--focus-ring)' }" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          <span class="ml-2 text-xs" :style="{ color: 'var(--text-muted)' }">Loading profile...</span>
        </div>

        <template v-else>

          <!-- ══════════════════ STATS ══════════════════ -->
          <section class="px-3 pt-3">
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-2">
              <StatsCard title="Your Role"   :value="userStats.role"       icon="Shield"      color="blue"   />
              <StatsCard title="Department"  :value="userStats.department"  icon="Building2"   color="green"  />
              <StatsCard title="Join Date"   :value="userStats.joinDate"    icon="Calendar"    color="purple" />
              <StatsCard title="Status"      :value="userStats.status"      icon="CheckCircle" color="green"  />
            </div>
          </section>

          <!-- ══════════════════ PROFILE & SETTINGS ══════════════════ -->
          <section class="px-3 pt-3">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">

              <!-- Profile Card -->
              <div class="lg:col-span-2">
                <div
                  class="rounded-lg shadow-sm p-4"
                  :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
                >
                  <!-- Avatar + Name -->
                  <div class="flex items-center gap-4 mb-4" :style="{ borderBottom: '1px solid var(--card-border)', paddingBottom: '16px' }">
                    <div class="w-16 h-16 rounded-full flex items-center justify-center overflow-hidden flex-shrink-0"
                      style="background: linear-gradient(135deg, #ec4899, #f43f5e);">
                      <img
                        v-if="userProfile.user_image"
                        :src="userProfile.user_image"
                        class="w-full h-full object-cover"
                      />
                      <span v-else class="text-2xl font-bold text-white">
                        {{ userProfile.name?.charAt(0)?.toUpperCase() || 'U' }}
                      </span>
                    </div>
                    <div>
                      <h2 class="text-sm font-bold" :style="{ color: 'var(--text-main)' }">{{ userProfile.name }}</h2>
                      <p class="text-xs mt-0.5" :style="{ color: 'var(--text-muted)' }">{{ userProfile.email }}</p>
                      <div class="flex flex-wrap gap-1 mt-1.5">
                        <span
                          v-for="role in userProfile.roles" :key="role"
                          class="px-2 py-0.5 rounded-full text-xs font-medium"
                          style="background: rgba(219, 39, 119, 0.1); color: #db2777;"
                        >
                          {{ role }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Info Grid -->
                  <div class="grid grid-cols-2 gap-2">
                    <div
                      v-for="(item, idx) in [
                        { label: 'Department', value: userProfile.department },
                        { label: 'Position',   value: userProfile.position   },
                        { label: 'Join Date',  value: userProfile.joinDate   },
                        { label: 'Status',     value: userProfile.status     },
                      ]" :key="idx"
                      class="rounded-md p-3"
                      :style="{ border: '1px solid var(--card-border)', background: 'var(--item-bg)' }"
                    >
                      <p class="text-xs mb-1" :style="{ color: 'var(--text-muted)' }">{{ item.label }}</p>
                      <p
                        class="text-xs font-semibold"
                        :style="{
                          color: item.label === 'Status'
                            ? (item.value === 'Active' ? 'var(--icon-color-green)' : '#ef4444')
                            : 'var(--text-main)'
                        }"
                      >
                        {{ item.value || 'N/A' }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Quick Settings Sidebar -->
              <div class="space-y-2">

                <!-- حالة 1: شايف بروفايل نفسه -->
                <template v-if="!viewingUser">

                  <!-- Account Settings -->
                  <div
                    class="rounded-lg shadow-sm p-3 cursor-pointer transition-all"
                    :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
                    @click="navigateTo('Settings')"
                    @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                    @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
                  >
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" :style="{ background: 'var(--info-bg)' }">
                        <Settings class="w-4 h-4" :style="{ color: 'var(--focus-ring)' }" />
                      </div>
                      <div>
                        <h3 class="text-xs font-semibold" :style="{ color: 'var(--text-main)' }">Account Settings</h3>
                        <p class="text-xs" :style="{ color: 'var(--text-muted)' }">Manage your account preferences</p>
                      </div>
                    </div>
                  </div>

                  <!-- Change Password -->
                  <div
                    class="rounded-lg shadow-sm p-3 cursor-pointer transition-all"
                    :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
                    @click="handleChangePassword"
                    @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                    @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
                  >
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" :style="{ background: 'var(--warning-bg)' }">
                        <Lock class="w-4 h-4" :style="{ color: 'var(--warning-border)' }" />
                      </div>
                      <div>
                        <h3 class="text-xs font-semibold" :style="{ color: 'var(--text-main)' }">Change Password</h3>
                        <p class="text-xs" :style="{ color: 'var(--text-muted)' }">Update your own password</p>
                      </div>
                    </div>
                  </div>

                  <!-- Logout -->
                  <div
                    class="rounded-lg shadow-sm p-3 cursor-pointer transition-all"
                    :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
                    @click="handleLogout"
                    @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                    @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
                  >
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style="background: #fef2f2;">
                        <LogOut class="w-4 h-4" style="color: #ef4444;" />
                      </div>
                      <div>
                        <h3 class="text-xs font-semibold" :style="{ color: 'var(--text-main)' }">Logout</h3>
                        <p class="text-xs" :style="{ color: 'var(--text-muted)' }">Sign out from your account</p>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- حالة 2: System Manager بيشوف بروفايل حد تاني -->
                <template v-if="viewingUser && isSystemManager">

                  <!-- Reset by Email -->
                  <div
                    class="rounded-lg shadow-sm p-3 cursor-pointer transition-all"
                    :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
                    @click="handleResetPassword"
                    @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                    @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
                  >
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" :style="{ background: 'var(--warning-bg)' }">
                        <KeyRound class="w-4 h-4" :style="{ color: 'var(--warning-border)' }" />
                      </div>
                      <div>
                        <h3 class="text-xs font-semibold" :style="{ color: 'var(--text-main)' }">Reset Password</h3>
                        <p class="text-xs" :style="{ color: 'var(--text-muted)' }">Send reset email to user</p>
                      </div>
                    </div>
                  </div>

                  <!-- Set New Password -->
                  <div
                    class="rounded-lg shadow-sm p-3 cursor-pointer transition-all"
                    :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
                    @click="showPasswordModal = true"
                    @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                    @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
                  >
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" :style="{ background: 'var(--icon-bg-purple)' }">
                        <Lock class="w-4 h-4" :style="{ color: 'var(--icon-color-purple)' }" />
                      </div>
                      <div>
                        <h3 class="text-xs font-semibold" :style="{ color: 'var(--text-main)' }">Set New Password</h3>
                        <p class="text-xs" :style="{ color: 'var(--text-muted)' }">Set password directly for this user</p>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- حالة 3: User عادي يشوف بروفايل حد تاني -->
                <template v-if="viewingUser && !isSystemManager">
                  <div
                    class="rounded-lg shadow-sm p-3"
                    :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
                  >
                    <p class="text-xs text-center" :style="{ color: 'var(--text-muted)' }">No actions available</p>
                  </div>
                </template>

              </div>
            </div>
          </section>

          <!-- ══════════════════ RECENT ACTIVITY ══════════════════ -->
          <section class="px-3 pt-3 pb-4">
            <div
              class="rounded-lg shadow-sm p-4"
              :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
            >
              <h2 class="text-xs font-bold mb-3" :style="{ color: 'var(--text-main)' }">Account Activity</h2>
              <div class="space-y-2">
                <div
                  v-for="activity in recentActivities" :key="activity.id"
                  class="flex items-center justify-between py-2"
                  :style="{ borderBottom: '1px solid var(--card-border)' }"
                >
                  <div class="flex items-center gap-3">
                    <div :class="['w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0', activity.bgColor]">
                      <component :is="activity.icon" class="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <p class="text-xs font-medium" :style="{ color: 'var(--text-main)' }">{{ activity.title }}</p>
                      <p class="text-xs" :style="{ color: 'var(--text-muted)' }">{{ activity.timestamp }}</p>
                    </div>
                  </div>
                  <span
                    class="text-xs font-medium px-2 py-0.5 rounded-full"
                    :class="activity.badgeClass"
                  >
                    {{ activity.status }}
                  </span>
                </div>
              </div>
            </div>
          </section>

        </template>

        <!-- ══════════════════ PASSWORD MODAL ══════════════════ -->
        <div
          v-if="showPasswordModal"
          class="fixed inset-0 flex items-center justify-center z-50 p-4"
          style="background: rgba(0,0,0,0.5);"
          @click.self="closePasswordModal"
        >
          <div
            class="w-full max-w-md rounded-xl shadow-2xl"
            :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
          >
            <!-- Modal Header -->
            <div
              class="flex items-center justify-between px-5 py-3"
              :style="{ borderBottom: '1px solid var(--card-border)' }"
            >
              <h3 class="text-sm font-semibold" :style="{ color: 'var(--text-main)' }">Set New Password</h3>
              <button
                @click="closePasswordModal"
                class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                :style="{ color: 'var(--text-muted)' }"
                @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                @mouseleave="$event.currentTarget.style.background = 'transparent'"
              >
                <X class="w-4 h-4" />
              </button>
            </div>

            <!-- Modal Body -->
            <div class="p-5 space-y-3">
              <p class="text-xs" :style="{ color: 'var(--text-muted)' }">
                Setting new password for:
                <span class="font-semibold" :style="{ color: 'var(--text-main)' }">{{ userProfile.name }}</span>
              </p>

              <!-- New Password -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">New Password *</label>
                <div class="relative">
                  <input
                    v-model="passwordForm.new_password"
                    :type="showNewPass ? 'text' : 'password'"
                    placeholder="Enter new password"
                    class="w-full px-3 py-1.5 pr-9 rounded-md text-xs focus:outline-none"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                  />
                  <button
                    type="button"
                    @click="showNewPass = !showNewPass"
                    class="absolute right-2.5 top-2 transition-colors"
                    :style="{ color: 'var(--text-muted)' }"
                  >
                    <Eye v-if="!showNewPass" class="w-3.5 h-3.5" />
                    <EyeOff v-else class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <!-- Confirm Password -->
              <div>
                <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Confirm Password *</label>
                <div class="relative">
                  <input
                    v-model="passwordForm.confirm_password"
                    :type="showConfirmPass ? 'text' : 'password'"
                    placeholder="Confirm new password"
                    class="w-full px-3 py-1.5 pr-9 rounded-md text-xs focus:outline-none"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                  />
                  <button
                    type="button"
                    @click="showConfirmPass = !showConfirmPass"
                    class="absolute right-2.5 top-2 transition-colors"
                    :style="{ color: 'var(--text-muted)' }"
                  >
                    <Eye v-if="!showConfirmPass" class="w-3.5 h-3.5" />
                    <EyeOff v-else class="w-3.5 h-3.5" />
                  </button>
                </div>
                <p v-if="passwordForm.confirm_password && !passwordsMatch" class="text-xs mt-1" style="color: #ef4444;">
                  Passwords do not match
                </p>
                <p v-if="passwordForm.confirm_password && passwordsMatch" class="text-xs mt-1" :style="{ color: 'var(--icon-color-green)' }">
                  ✓ Passwords match
                </p>
              </div>

              <!-- Error -->
              <div v-if="passwordError" class="rounded-md p-3 text-xs" style="background: #fef2f2; color: #ef4444; border: 1px solid #fecaca;">
                {{ passwordError }}
              </div>

              <!-- Success -->
              <div v-if="passwordSuccess" class="rounded-md p-3 text-xs" :style="{ background: 'var(--icon-bg-green)', color: 'var(--icon-color-green)', border: '1px solid var(--icon-color-green)' }">
                ✅ Password changed successfully!
              </div>
            </div>

            <!-- Modal Footer -->
            <div
              class="flex justify-end gap-2 px-5 py-3"
              :style="{ borderTop: '1px solid var(--card-border)' }"
            >
              <button
                type="button"
                @click="closePasswordModal"
                class="px-4 py-1.5 text-xs rounded-md transition-colors"
                :style="{
                  background: 'var(--item-bg)',
                  color: 'var(--text-sub)',
                  border: '1px solid var(--item-border)'
                }"
                @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                @mouseleave="$event.currentTarget.style.background = 'var(--item-bg)'"
              >
                Cancel
              </button>
              <button
                @click="handleSetNewPassword"
                :disabled="!passwordsMatch || !passwordForm.new_password || isSavingPassword"
                class="px-4 py-1.5 text-xs text-white rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                :style="{ background: 'var(--icon-color-purple)' }"
              >
                {{ isSavingPassword ? 'Saving...' : 'Change Password' }}
              </button>
            </div>
          </div>
        </div>

      </main>
    </div>

</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'

import StatsCard from '@/layout/StatsCard.vue'
import { useRouter, useRoute } from 'vue-router'
import { call } from 'frappe-ui'
import { getCurrentUserInfo, getAllUsers, changeUserPasswordApi } from '@/composables/user'
import {
  User, ArrowLeft, Settings, Lock, LogOut,
  CheckCircle, Eye, EyeOff, KeyRound, X
} from 'lucide-vue-next'

const router = useRouter()
const route  = useRoute()
const loading = ref(false)

const viewingUser = computed(() => route.query.user || null)

const userStats = reactive({ role: 'N/A', department: 'N/A', joinDate: 'N/A', status: 'N/A' })

const userProfile = reactive({
  name: '', email: '', department: '', position: '',
  status: 'Active', user_image: '', roles: [], joinDate: 'N/A',
})

const loadProfile = async () => {
  loading.value = true
  try {
    if (viewingUser.value) {
      const res = await getAllUsers()
      const found = (res.data || []).find(u => u.name === viewingUser.value)
      if (found) fillProfile(found)
    } else {
      const res = await getCurrentUserInfo()
      if (res.data) fillProfile(res.data)
    }
  } catch (e) {
    console.error('Error loading profile:', e)
  } finally {
    loading.value = false
  }
}

const fillProfile = (data) => {
  userProfile.name       = data.full_name || data.name
  userProfile.email      = data.email
  userProfile.department = data.department || 'N/A'
  userProfile.position   = data.designation || data.position || 'N/A'
  userProfile.status     = data.enabled === undefined ? (data.status || 'Active') : (data.enabled ? 'Active' : 'Inactive')
  userProfile.user_image = data.user_image || ''
  userProfile.roles      = data.roles || []
  userProfile.joinDate   = data.join_date || data.creation?.split(' ')[0] || 'N/A'
  userStats.role         = data.roles?.[0] || 'N/A'
  userStats.department   = data.department || 'N/A'
  userStats.joinDate     = userProfile.joinDate
  userStats.status       = userProfile.status
}

const currentUserRoles = ref([])
const isSystemManager  = computed(() =>
  currentUserRoles.value.includes('System Manager') ||
  currentUserRoles.value.includes('Administrator')
)

const loadCurrentUserRoles = async () => {
  try {
    const res = await getCurrentUserInfo()
    currentUserRoles.value = res.data?.roles || []
  } catch (e) { console.error(e) }
}

const navigateTo       = (name) => router.push({ name })
const handleChangePassword = () => router.push({ name: 'change-password' })
const handleLogout = async () => {
  try { await call('logout') } finally { router.push({ name: 'Login' }) }
}

const handleResetPassword = async () => {
  if (!confirm(`Send password reset email to ${userProfile.email}?`)) return
  try {
    await call('frappe.core.doctype.user.user.reset_password', { user: viewingUser.value })
    window.$toast?.success('Reset email sent successfully')
  } catch (e) { window.$toast?.error('Error sending reset email') }
}

const showPasswordModal  = ref(false)
const isSavingPassword   = ref(false)
const passwordError      = ref('')
const passwordSuccess    = ref(false)
const showNewPass        = ref(false)
const showConfirmPass    = ref(false)
const passwordForm       = reactive({ new_password: '', confirm_password: '' })
const passwordsMatch     = computed(() => passwordForm.new_password && passwordForm.new_password === passwordForm.confirm_password)

const handleSetNewPassword = async () => {
  passwordError.value = ''; passwordSuccess.value = false
  if (!passwordForm.new_password)          { passwordError.value = 'Password is required'; return }
  if (passwordForm.new_password.length < 6) { passwordError.value = 'Password must be at least 6 characters'; return }
  if (!passwordsMatch.value)               { passwordError.value = 'Passwords do not match'; return }
  isSavingPassword.value = true
  try {
    await changeUserPasswordApi({ user: viewingUser.value, new_password: passwordForm.new_password })
    passwordSuccess.value = true
    setTimeout(() => closePasswordModal(), 2000)
  } catch (e) {
    passwordError.value = e?.response?.data?.message || 'Error changing password'
  } finally {
    isSavingPassword.value = false
  }
}

const closePasswordModal = () => {
  showPasswordModal.value = false; passwordError.value = ''; passwordSuccess.value = false
  showNewPass.value = false; showConfirmPass.value = false
  passwordForm.new_password = ''; passwordForm.confirm_password = ''
}

const recentActivities = ref([
  { id: 1, title: 'Profile updated',   timestamp: '2 hours ago', status: 'Updated', bgColor: 'bg-blue-500',    icon: User,         badgeClass: 'bg-blue-100 text-blue-800'    },
  { id: 2, title: 'Password changed',  timestamp: '1 day ago',   status: 'Changed', bgColor: 'bg-green-500',   icon: Lock,         badgeClass: 'bg-green-100 text-green-800'  },
  { id: 3, title: 'Login successful',  timestamp: '2 days ago',  status: 'Success', bgColor: 'bg-emerald-500', icon: CheckCircle,  badgeClass: 'bg-emerald-100 text-emerald-800' },
])

const goBack = () => { router.back() }
onMounted(() => { loadProfile(); loadCurrentUserRoles() })
</script>
