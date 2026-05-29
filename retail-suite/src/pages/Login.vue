<template>
  <div class="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
    <div class="w-full max-w-md rounded-2xl border border-white/10 bg-slate-900/95 p-8 shadow-2xl">
      <div class="mb-6">
        <p class="text-sm uppercase tracking-wide text-slate-400">Retail Suite</p>
        <h1 class="mt-2 text-2xl font-semibold">Sign in to POS</h1>
        <p class="mt-2 text-sm text-slate-400">Use your Frappe user to open the POS workspace.</p>
      </div>

      <div class="mb-5 rounded-xl border px-3 py-2 text-xs"
           :class="backendOnline ? 'border-emerald-400/30 bg-emerald-500/10 text-emerald-200' : 'border-amber-400/30 bg-amber-500/10 text-amber-200'">
        <p class="font-medium">Backend: {{ backendOnline ? 'Connected' : 'Unavailable' }}</p>
        <p class="mt-1 break-all opacity-90">{{ backendBaseUrl }}</p>
      </div>

      <form class="space-y-4" @submit.prevent="submitLogin">
        <label class="block">
          <span class="mb-2 block text-sm text-slate-300">Username</span>
          <input
            v-model.trim="username"
            autocomplete="username"
            type="email"
            class="w-full rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none ring-0 focus:border-cyan-400"
            placeholder="retail.gromax.cashier@example.com"
            required
          />
        </label>

        <label class="block">
          <span class="mb-2 block text-sm text-slate-300">Password</span>
          <div class="relative">
            <input
              v-model="password"
              autocomplete="current-password"
              :type="showPassword ? 'text' : 'password'"
              class="w-full rounded-xl border border-white/10 bg-slate-950 px-4 py-3 pr-20 text-white outline-none ring-0 focus:border-cyan-400"
              placeholder="••••••••"
              required
            />
            <button
              type="button"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-300 hover:text-white"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
        </label>

        <button
          type="submit"
          :disabled="session.login.loading || !canSubmit || !backendOnline"
          class="w-full rounded-xl bg-cyan-500 px-4 py-3 font-medium text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {{ session.login.loading ? 'Signing in...' : 'Continue' }}
        </button>
      </form>

      <p v-if="errorMessage" class="mt-4 text-sm text-red-300">{{ errorMessage }}</p>
      <p class="mt-4 text-xs text-slate-500">Tip: use Ctrl + Shift + R after each new Vercel deploy.</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { session } from '@/services/auth'
import { API_BASE_URL, resolveBackendUrl } from '@/config/runtime'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const errorMessage = ref('')
const backendOnline = ref(false)

const backendBaseUrl = API_BASE_URL || window.location.origin
const canSubmit = computed(() => username.value.length > 3 && password.value.length > 0)

async function checkBackendHealth() {
  try {
    const response = await fetch(resolveBackendUrl('/api/method/ping'), {
      method: 'GET',
      credentials: 'include',
    })
    backendOnline.value = response.ok
  } catch (err) {
    backendOnline.value = false
  }
}

async function submitLogin() {
  errorMessage.value = ''

  if (!backendOnline.value) {
    errorMessage.value = 'Backend is not reachable. Check environment URL and CORS settings.'
    return
  }

  try {
    await session.login.submit({ username: username.value, password: password.value })
  } catch (err) {
    errorMessage.value = err?.message || 'Login failed'
  }
}

onMounted(() => {
  checkBackendHealth()
})
</script>
