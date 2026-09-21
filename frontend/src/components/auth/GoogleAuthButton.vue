<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'

type GoogleButtonText = 'signin_with' | 'signup_with' | 'continue_with'
type AccountRole = 'user' | 'owner' | 'enterprise'

interface GoogleIdentityButtonOptions {
  theme?: 'outline' | 'filled_blue' | 'filled_black'
  size?: 'large' | 'medium' | 'small'
  text?: GoogleButtonText
  shape?: 'rectangular' | 'pill' | 'circle' | 'square'
  width?: number
}

interface GoogleIdentityCredentialResponse {
  credential?: string
}

interface GoogleIdentityService {
  accounts: {
    id: {
      initialize: (options: {
        client_id: string
        callback: (response: GoogleIdentityCredentialResponse) => void | Promise<void>
      }) => void
      renderButton: (element: HTMLElement, options: GoogleIdentityButtonOptions) => void
      cancel?: () => void
    }
  }
}

interface GoogleIdentityWindow extends Window {
  google?: GoogleIdentityService
}

const props = withDefaults(
  defineProps<{
    label: string
    redirectTo?: string
    buttonText?: GoogleButtonText
    selectedRole?: AccountRole | null
    requireRoleSelection?: boolean
  }>(),
  {
    redirectTo: undefined,
    buttonText: 'continue_with',
    selectedRole: null,
    requireRoleSelection: false,
  },
)

const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const buttonContainer = ref<HTMLDivElement | null>(null)
const isProcessing = ref(false)
const scriptError = ref('')
const googleScaleX = ref(1)
const googleScaleY = ref(1.25)

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim() || ''

let googleScriptPromise: Promise<void> | null = null

const getRoleHomePath = (role?: string | null) => {
  if (role === 'owner') {
    return '/owner/home'
  }
  if (role === 'enterprise') {
    return '/enterprise/home'
  }
  return '/user/home'
}

const loadGoogleScript = () => {
  if ((window as GoogleIdentityWindow).google) {
    return Promise.resolve()
  }

  if (googleScriptPromise) {
    return googleScriptPromise
  }

  googleScriptPromise = new Promise<void>((resolve, reject) => {
    const existingScript = document.querySelector<HTMLScriptElement>(
      'script[data-google-identity-script="true"]',
    )

    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(), { once: true })
      existingScript.addEventListener(
        'error',
        () => reject(new Error('Failed to load Google script')),
        {
          once: true,
        },
      )
      return
    }

    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.dataset.googleIdentityScript = 'true'
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load Google script'))
    document.head.appendChild(script)
  })

  return googleScriptPromise
}

const renderButton = async () => {
  scriptError.value = ''

  if (!googleClientId) {
    scriptError.value = 'Set VITE_GOOGLE_CLIENT_ID in frontend .env to enable Google sign-in.'
    return
  }

  if (!buttonContainer.value) {
    return
  }

  try {
    await loadGoogleScript()

    const google = (window as GoogleIdentityWindow).google
    if (!google?.accounts?.id) {
      throw new Error('Google Identity Services is unavailable')
    }

    google.accounts.id.initialize({
      client_id: googleClientId,
      callback: async (response: { credential?: string }) => {
        if (!response.credential) {
          return
        }

        if (props.requireRoleSelection && !props.selectedRole) {
          toast.error('❌ Please select a role before Google sign-up.', { timeout: 4000 })
          return
        }

        isProcessing.value = true

        try {
          const result = await authStore.loginWithGoogle(
            response.credential,
            props.selectedRole || undefined,
          )

          if (result.success) {
            // Only enforce role-match for signup (requireRoleSelection=true)
            // For login (requireRoleSelection=false), allow any existing account
            if (
              props.requireRoleSelection &&
              props.selectedRole &&
              authStore.user?.role !== props.selectedRole
            ) {
              authStore.logout()
              toast.error('❌ Account role does not match the selected role.', { timeout: 4000 })
              return
            }

            toast.success(`✅ ${props.label} successful!`, { timeout: 2000 })
            const redirectPath = props.redirectTo || getRoleHomePath(authStore.user?.role || null)
            await router.push(redirectPath)
            return
          }

          const errorMessage = result.error || 'Google sign-in failed. Please try again.'
          toast.error(`❌ ${errorMessage}`, { timeout: 4000 })
        } catch {
          toast.error('❌ Google sign-in failed. Please try again.', { timeout: 4000 })
        } finally {
          isProcessing.value = false
        }
      },
    })

    const desiredWidth = Math.floor(buttonContainer.value.getBoundingClientRect().width) || 430
    const renderedWidth = Math.min(desiredWidth, 400)
    googleScaleX.value = desiredWidth / renderedWidth

    google.accounts.id.renderButton(buttonContainer.value, {
      theme: 'outline',
      size: 'large',
      text: props.buttonText,
      shape: 'pill',
      width: renderedWidth,
    })
  } catch (error) {
    console.error('Google sign-in initialization failed:', error)
    scriptError.value = 'Google sign-in is unavailable right now.'
  }
}

onMounted(() => {
  void renderButton()
})

onBeforeUnmount(() => {
  const google = (window as GoogleIdentityWindow).google
  google?.accounts?.id?.cancel?.()
})
</script>

<template>
  <div class="google-auth-section">
    <div class="or-divider">
      <span>OR</span>
    </div>

    <div class="google-button-wrap">
      <div
        v-if="googleClientId"
        ref="buttonContainer"
        class="google-button-container"
        :style="{
          '--google-scale-x': String(googleScaleX),
          '--google-scale-y': String(googleScaleY),
        }"
      ></div>
      <button v-else type="button" class="google-fallback-btn" disabled>
        Continue with Google
      </button>
      <p v-if="isProcessing" class="google-loading">Processing Google sign-in...</p>
    </div>

    <p v-if="!googleClientId" class="google-config-hint">
      Set <strong>VITE_GOOGLE_CLIENT_ID</strong> in frontend .env to enable Google sign-in.
    </p>

    <p v-if="scriptError" class="google-config-hint">{{ scriptError }}</p>
  </div>
</template>

<style scoped>
.google-auth-section {
  margin-top: 18px;
}

.or-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  color: #7a7a7a;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.or-divider::before,
.or-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(45, 80, 22, 0.25), transparent);
}

.google-button-wrap {
  display: grid;
  gap: 10px;
}

.google-button-container {
  width: 100%;
  min-height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: scaleX(var(--google-scale-x, 1)) scaleY(var(--google-scale-y, 1));
  transform-origin: center;
}

.google-fallback-btn {
  width: 100%;
  min-height: 52px;
  border: 1px solid rgba(45, 80, 22, 0.2);
  border-radius: 999px;
  background: #f7f9f5;
  color: #6b7280;
  font: inherit;
  font-weight: 600;
  cursor: not-allowed;
}

.google-loading,
.google-config-hint {
  margin: 0;
  font-size: 0.88rem;
  color: #5f6a5f;
  line-height: 1.45;
}

.google-config-hint strong {
  color: #2d5016;
}
</style>
