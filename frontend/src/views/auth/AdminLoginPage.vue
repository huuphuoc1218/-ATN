<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

// Form state
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)

// UI state
const errorMessage = ref('')
const isSubmitting = computed(() => authStore.isLoading)

// Handle admin login
const handleAdminLogin = async () => {
  // Clear previous error
  errorMessage.value = ''

  // Validation
  if (!email.value || !password.value) {
    const msg = 'Please enter all required information'
    errorMessage.value = msg
    toast.error(`❌ ${msg}`)
    return
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    const msg = 'Invalid email'
    errorMessage.value = msg
    toast.error(`❌ ${msg}`)
    return
  }

  try {
    const result = await authStore.login({
      email: email.value,
      password: password.value,
    })

    if (result.success) {
      // Get actual user role from auth store
      const actualRole = authStore.user?.role

      // CHECK ROLE: Must be admin
      if (actualRole !== 'admin') {
        // Logout user
        authStore.logout()

        const msg = `Only Admin accounts can access this page!`
        errorMessage.value = msg
        toast.error(`❌ ${msg}`, {
          timeout: 4000,
        })
        return
      }

      // Admin role matched - proceed with login
      toast.success('✅ Admin login successful!', {
        timeout: 2000,
      })

      // Redirect to admin dashboard
      setTimeout(() => {
        router.push('/admin/profile')
      }, 1000)
    } else {
      const error = result.error || 'Login failed. Please try again!'
      errorMessage.value = error
      toast.error(`❌ ${error}`, {
        timeout: 4000,
      })
    }
  } catch {
    const errorMsg = 'An unexpected error occurred. Please try again!'
    errorMessage.value = errorMsg
    toast.error(`❌ ${errorMsg}`)
  }
}

// Navigate back to user login
const goToUserLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="admin-login-page">
    <div class="admin-login-container">
      <!-- Left Side - Image with Admin Theme -->
      <div class="image-section">
        <img
          src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200"
          alt="Admin Dashboard"
          class="background-image"
        />
        <div class="image-overlay">
          <div class="overlay-content">
            <div class="shield-icon">🛡️</div>
            <h2 class="overlay-title">Admin Portal</h2>
            <p class="overlay-text">Secure Access for System Administrators</p>
            <div class="security-badges">
              <div class="badge">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
                <span>Secure Access</span>
              </div>
              <div class="badge">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
                <span>Encrypted</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - Admin Login Form -->
      <div class="form-section">
        <div class="form-container">
          <!-- Logo with Admin Badge -->
          <div class="logo-section">
            <div class="logo-icon">
              <img
                src="/Logo.png"
                alt="NP SPORTCLUB Logo"
                style="width: 60px; height: 60px; object-fit: contain"
              />
            </div>
            <div class="logo-text">
              <span class="pickleball">Pickleball</span>
              <span class="brand">NP SPORTCLUB</span>
            </div>
            <div class="admin-badge">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
              <span>ADMIN</span>
            </div>
          </div>

          <!-- Welcome Text -->
          <div class="welcome-section">
            <h1 class="welcome-title">ADMIN ACCESS</h1>
            <p class="welcome-subtitle">System Administrator Login</p>
          </div>

          <!-- Security Notice -->
          <div class="security-notice">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>For system administrators only.</span>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="error-message">
            <span class="error-icon">⚠️</span>
            {{ errorMessage }}
          </div>

          <!-- Admin Login Form -->
          <form @submit.prevent="handleAdminLogin" class="admin-login-form">
            <!-- Email Input -->
            <div class="input-group">
              <svg
                class="input-icon-left"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              <input
                v-model="email"
                type="email"
                placeholder="Admin Email"
                class="form-input"
                required
                :disabled="isSubmitting"
              />
            </div>

            <!-- Password Input -->
            <div class="input-group">
              <svg
                class="input-icon-left"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Admin Password"
                class="form-input"
                required
                :disabled="isSubmitting"
              />
              <button
                type="button"
                class="input-icon-right clickable"
                @click="showPassword = !showPassword"
                :disabled="isSubmitting"
              >
                <svg
                  v-if="showPassword"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                  />
                </svg>
              </button>
            </div>

            <!-- Remember -->
            <div class="form-options">
              <label class="remember-checkbox">
                <input v-model="rememberMe" type="checkbox" :disabled="isSubmitting" />
                <span class="checkbox-text">Keep me signed in</span>
              </label>
            </div>

            <!-- Submit Button -->
            <button type="submit" class="submit-btn" :disabled="isSubmitting">
              <svg
                v-if="!isSubmitting"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
              <span v-if="isSubmitting" class="spinner">⏳</span>
              <span v-else>SECURE LOGIN</span>
            </button>
          </form>

          <!-- Back to User Login -->
          <div class="back-section">
            <a @click="goToUserLogin" class="back-link">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              <span>Back to User Login</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  padding: 20px;
}

.admin-login-container {
  width: 100%;
  max-width: 1200px;
  min-height: 700px;
  background: #1a1a2e;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  display: grid;
  grid-template-columns: 45% 55%;
  border: 2px solid rgba(220, 38, 38, 0.3);
}

.image-section {
  position: relative;
  overflow: hidden;
}

.background-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.3;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(220, 38, 38, 0.85) 0%, rgba(153, 27, 27, 0.9) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.overlay-content {
  text-align: center;
  color: white;
  padding: 40px;
}

.shield-icon {
  font-size: 5rem;
  margin-bottom: 24px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.overlay-title {
  font-size: 2.5rem;
  font-weight: 900;
  margin: 0 0 12px 0;
  letter-spacing: 2px;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.overlay-text {
  font-size: 1.1rem;
  opacity: 0.95;
  margin: 0 0 32px 0;
  font-weight: 500;
}

.security-badges {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.15);
  padding: 12px 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.badge svg {
  width: 24px;
  height: 24px;
}

.badge span {
  font-weight: 600;
  font-size: 0.9rem;
}

.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px 60px;
  background: #16213e;
}

.form-container {
  width: 100%;
  max-width: 480px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
  position: relative;
}

.logo-icon {
  font-size: 2.5rem;
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.pickleball {
  font-size: 1rem;
  font-weight: 500;
  color: #9ca3af;
}

.brand {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: 2px;
  color: white;
}

.admin-badge {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  padding: 8px 16px;
  border-radius: 8px;
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 1px;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
}

.admin-badge svg {
  width: 16px;
  height: 16px;
}

.welcome-section {
  margin-bottom: 20px;
}

.welcome-title {
  font-size: 2.2rem;
  font-weight: 900;
  color: white;
  margin: 0 0 8px 0;
  letter-spacing: 2px;
  text-shadow: 0 2px 8px rgba(220, 38, 38, 0.5);
}

.welcome-subtitle {
  font-size: 1rem;
  color: #9ca3af;
  margin: 0;
}

.security-notice {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  color: #fca5a5;
  font-size: 0.85rem;
}

.security-notice svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.error-message {
  background: rgba(220, 38, 38, 0.15);
  color: #fca5a5;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  border: 1px solid rgba(220, 38, 38, 0.3);
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.admin-login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input {
  width: 100%;
  padding: 14px 50px 14px 50px;
  border: 2px solid #2d3748;
  border-radius: 12px;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.3s;
  background: #1a202c;
  color: white;
  font-family: inherit;
}

.form-input::placeholder {
  color: #6b7280;
}

.form-input:focus {
  border-color: #dc2626;
  box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.2);
  background: #252d3d;
}

.input-icon-left {
  position: absolute;
  left: 18px;
  width: 20px;
  height: 20px;
  color: #6b7280;
  transition: color 0.3s;
  pointer-events: none;
}

.form-input:focus ~ .input-icon-left,
.input-group:hover .input-icon-left {
  color: #dc2626;
}

.input-icon-right {
  position: absolute;
  right: 18px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-icon-right svg {
  width: 20px;
  height: 20px;
  color: #6b7280;
  transition: color 0.3s;
}

.input-icon-right:hover svg {
  color: #dc2626;
}

.form-options {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-top: -4px;
}

.remember-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  color: #9ca3af;
}

.remember-checkbox input[type='checkbox'] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #dc2626;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 8px;
  box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.submit-btn svg {
  width: 20px;
  height: 20px;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(220, 38, 38, 0.5);
}

.submit-btn:active {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1s linear infinite;
  display: inline-block;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.back-section {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #9ca3af;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
  font-weight: 600;
}

.back-link svg {
  width: 18px;
  height: 18px;
  transition: transform 0.3s;
}

.back-link:hover {
  color: white;
}

.back-link:hover svg {
  transform: translateX(-4px);
}

@media (max-width: 1024px) {
  .admin-login-container {
    grid-template-columns: 1fr;
    height: auto;
    min-height: auto;
  }

  .image-section {
    display: none;
  }

  .form-section {
    padding: 40px 20px;
  }
}

@media (max-width: 640px) {
  .welcome-title {
    font-size: 1.8rem;
  }

  .form-section {
    padding: 30px 20px;
  }

  .admin-badge {
    position: absolute;
    top: -10px;
    right: 0;
  }

  .logo-section {
    margin-bottom: 40px;
  }
}

@media (max-width: 480px) {
  .admin-login-page {
    padding: 12px;
  }

  .admin-login-container {
    border-radius: 16px;
    min-height: auto;
  }

  .form-section {
    padding: 20px 12px;
  }

  .form-container {
    max-width: 100%;
  }

  .welcome-title {
    font-size: 1.5rem;
    letter-spacing: 1px;
  }

  .welcome-subtitle {
    font-size: 0.9rem;
  }

  .security-notice {
    padding: 10px 12px;
    font-size: 0.8rem;
  }

  .form-input {
    padding: 12px 42px 12px 42px;
    font-size: 0.9rem;
  }

  .input-icon-left {
    left: 14px;
    width: 18px;
    height: 18px;
  }

  .input-icon-right {
    right: 12px;
  }

  .submit-btn {
    padding: 12px;
    font-size: 0.9rem;
    letter-spacing: 1px;
  }

  .back-section {
    margin-top: 16px;
    padding-top: 14px;
  }
}
</style>
