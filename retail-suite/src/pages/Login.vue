<template>
  <div class="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
    <div class="w-full max-w-md rounded-2xl border border-white/10 bg-slate-900/95 p-8 shadow-2xl">
      <div class="mb-6">
        <p class="text-sm uppercase tracking-wide text-slate-400">Retail Suite</p>
        <h1 class="mt-2 text-2xl font-semibold">Sign in to POS</h1>
        <p class="mt-2 text-sm text-slate-400">Use your Frappe user to open the POS workspace.</p>
      </div>

      <form class="space-y-4" @submit.prevent="submitLogin">
        <label class="block">
          <span class="mb-2 block text-sm text-slate-300">Username</span>
          <input
            v-model="username"
            autocomplete="username"
            type="email"
            class="w-full rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none ring-0 focus:border-cyan-400"
            placeholder="retail.gromax.cashier@example.com"
          />
        </label>

        <label class="block">
          <span class="mb-2 block text-sm text-slate-300">Password</span>
          <input
            v-model="password"
            autocomplete="current-password"
            type="password"
            class="w-full rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none ring-0 focus:border-cyan-400"
            placeholder="••••••••"
          />
        </label>

        <button
          type="submit"
          :disabled="session.login.loading"
          class="w-full rounded-xl bg-cyan-500 px-4 py-3 font-medium text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {{ session.login.loading ? 'Signing in...' : 'Continue' }}
        </button>
      </form>

      <p v-if="errorMessage" class="mt-4 text-sm text-red-300">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { session } from '@/services/auth'

const username = ref('')
const password = ref('')
const errorMessage = ref('')

async function submitLogin() {
  errorMessage.value = ''
  try {
    await session.login.submit({ username: username.value, password: password.value })
  } catch (err) {
    errorMessage.value = err?.message || 'Login failed'
  }
}
</script>
