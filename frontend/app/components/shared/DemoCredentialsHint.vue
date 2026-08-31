<script setup lang="ts">
import { ref } from 'vue'

const { t } = useI18n()
const { public: { demoMode } } = useRuntimeConfig()
const toast = useToast()
const auth = useAuth()

const DEMO_EMAIL = 'admin@demo.clinic'
const DEMO_PASSWORD = 'demo1234'

const loadingEmail = ref<string | null>(null)

const roles = [
  {
    email: 'admin@demo.clinic',
    labelKey: 'settings.roles.admin',
    icon: 'i-lucide-crown',
    color: 'primary' as const,
    class: 'col-span-2'
  },
  {
    email: 'dentist@demo.clinic',
    labelKey: 'settings.roles.dentist',
    icon: 'i-lucide-stethoscope',
    color: 'neutral' as const,
    class: ''
  },
  {
    email: 'receptionist@demo.clinic',
    labelKey: 'settings.roles.receptionist',
    icon: 'i-lucide-contact',
    color: 'neutral' as const,
    class: ''
  },
  {
    email: 'hygienist@demo.clinic',
    labelKey: 'settings.roles.hygienist',
    icon: 'i-lucide-sparkles',
    color: 'neutral' as const,
    class: ''
  },
  {
    email: 'assistant@demo.clinic',
    labelKey: 'settings.roles.assistant',
    icon: 'i-lucide-user-check',
    color: 'neutral' as const,
    class: ''
  }
]

async function copy(value: string) {
  if (!import.meta.client) return
  try {
    await navigator.clipboard.writeText(value)
    toast.add({
      title: t('common.success'),
      description: t('demo.copied'),
      color: 'success'
    })
  } catch {
    // Clipboard may be unavailable (insecure context). Silent.
  }
}

async function quickLogin(email: string) {
  if (loadingEmail.value) return
  loadingEmail.value = email
  try {
    await auth.login({
      email,
      password: 'demo1234'
    })
    toast.add({
      title: t('auth.loginSuccess'),
      color: 'success'
    })
    await navigateTo('/')
  } catch (error: unknown) {
    console.error('Quick login error:', error)
    toast.add({
      title: t('common.error'),
      description: t('auth.invalidCredentials'),
      color: 'danger'
    })
  } finally {
    loadingEmail.value = null
  }
}
</script>

<template>
  <div
    v-if="demoMode"
    class="alert-surface-info rounded-token-md px-4 py-3 mt-4 space-y-3"
  >
    <div class="flex items-center gap-2">
      <UIcon
        name="i-lucide-info"
        class="w-4 h-4 shrink-0"
        :style="{ color: 'var(--color-info-accent)' }"
      />
      <span class="text-ui font-medium">
        {{ t('demo.credentialsTitle') }}
      </span>
    </div>
    <div class="space-y-1 text-body">
      <button
        type="button"
        class="flex items-center gap-2 w-full text-left hover:bg-surface rounded-token-sm px-2 py-1 transition-colors"
        :aria-label="t('demo.copyEmail')"
        @click="copy(DEMO_EMAIL)"
      >
        <span class="text-subtle w-20 shrink-0">{{ t('auth.email') }}:</span>
        <code class="font-mono text-default flex-1">{{ DEMO_EMAIL }}</code>
        <UIcon
          name="i-lucide-copy"
          class="w-3.5 h-3.5 text-subtle shrink-0"
        />
      </button>
      <button
        type="button"
        class="flex items-center gap-2 w-full text-left hover:bg-surface rounded-token-sm px-2 py-1 transition-colors"
        :aria-label="t('demo.copyPassword')"
        @click="copy(DEMO_PASSWORD)"
      >
        <span class="text-subtle w-20 shrink-0">{{ t('auth.password') }}:</span>
        <code class="font-mono text-default flex-1">{{ DEMO_PASSWORD }}</code>
        <UIcon
          name="i-lucide-copy"
          class="w-3.5 h-3.5 text-subtle shrink-0"
        />
      </button>
    </div>
    <p class="text-caption text-subtle">
      {{ t('demo.credentialsNote') }}
    </p>

    <!-- Divider -->
    <div class="border-t border-info/20 my-2"></div>

    <!-- Quick Login Section -->
    <div class="space-y-2">
      <div class="flex items-center gap-2">
        <UIcon
          name="i-lucide-zap"
          class="w-4 h-4 shrink-0 text-amber-500"
        />
        <span class="text-ui font-medium">
          {{ t('demo.quickLogin') }}
        </span>
      </div>
      <p class="text-caption text-subtle">
        {{ t('demo.quickLoginNote') }}
      </p>
      <div class="grid grid-cols-2 gap-2 pt-1">
        <UButton
          v-for="role in roles"
          :key="role.email"
          variant="soft"
          :color="role.color"
          :icon="role.icon"
          :class="role.class"
          :loading="loadingEmail === role.email"
          :disabled="!!loadingEmail"
          size="sm"
          @click="quickLogin(role.email)"
        >
          {{ t(role.labelKey) }}
        </UButton>
      </div>
    </div>
  </div>
</template>
