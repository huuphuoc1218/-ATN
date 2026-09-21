<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import GoogleAuthButton from '@/components/auth/GoogleAuthButton.vue'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

// Form state
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const userType = ref<'user' | 'enterprise' | 'owner'>('user')

// UI state
const errorMessage = ref('')
const isSubmitting = computed(() => authStore.isLoading)

// Handle login
const handleLogin = async () => {
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

      // CHECK ROLE: So sánh role thực tế với role đã chọn
      if (actualRole !== userType.value) {
        // Logout user
        authStore.logout()

        const msg = `Account does not exist. Please check again.`
        errorMessage.value = msg
        toast.error(`❌ ${msg}`, {
          timeout: 4000,
        })
        return
      }

      // Role matched - proceed with login
      toast.success('✅ Login successful!', {
        timeout: 2000,
      })

      // Redirect based on role
      setTimeout(() => {
        let redirectPath = '/user/home'

        if (actualRole === 'owner') {
          redirectPath = '/owner/home'
        } else if (actualRole === 'enterprise') {
          redirectPath = '/enterprise/home'
        }

        router.push(redirectPath)
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

// Navigate to sign up page
const goToSignUp = () => {
  router.push('/signup')
}
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Left Side - Image -->
      <div class="image-section">
        <img
          src="https://i.pinimg.com/1200x/ff/ec/83/ffec834246af54637385878acc35aae4.jpg?fbclid=IwY2xjawPE0zJleHRuA2FlbQIxMABicmlkETFJdHVUV2R4NmFBbVNTTVNhc3J0YwZhcHBfaWQQMjIyMDM5MTc4ODIwMDg5MgABHhR48rePQTmDRICQZ6sXKziKjptBXdAHAjwPzh2biolIzVlngov2-u4ibBa3_aem_PW5Sy3jx965tnsM0p6KdjQ"
          alt="Pickleball Equipment"
          class="background-image"
        />
        <div class="image-overlay"></div>
      </div>

      <!-- Right Side - Login Form -->
      <div class="form-section">
        <div class="form-container">
          <!-- Logo -->
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
          </div>

          <!-- Welcome Text -->
          <div class="welcome-section">
            <h1 class="welcome-title">WELCOME BACK</h1>
            <p class="welcome-subtitle">Login into your account</p>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="error-message">
            <span class="error-icon">⚠️</span>
            {{ errorMessage }}
          </div>

          <!-- User Type Selection -->
          <div class="user-type-section">
            <button
              type="button"
              class="type-btn"
              :class="{ active: userType === 'user' }"
              @click="userType = 'user'"
            >
              <span class="type-dot"></span>
              User
            </button>
            <button
              type="button"
              class="type-btn"
              :class="{ active: userType === 'enterprise' }"
              @click="userType = 'enterprise'"
            >
              <span class="type-dot"></span>
              Enterprise
            </button>
            <button
              type="button"
              class="type-btn"
              :class="{ active: userType === 'owner' }"
              @click="userType = 'owner'"
            >
              <span class="type-dot"></span>
              Owner
            </button>
          </div>

          <!-- Login Form -->
          <form @submit.prevent="handleLogin" class="login-form">
            <!-- Email Input -->
            <div class="input-group">
              <input
                v-model="email"
                type="email"
                placeholder="Email"
                class="form-input"
                required
                :disabled="isSubmitting"
              />
              <span class="input-icon">👤</span>
            </div>

            <!-- Password Input -->
            <div class="input-group">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Password"
                class="form-input"
                required
                :disabled="isSubmitting"
              />
              <button
                type="button"
                class="input-icon clickable"
                @click="showPassword = !showPassword"
                :disabled="isSubmitting"
              >
                <svg
                  v-if="showPassword"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  class="icon-svg"
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
                  class="icon-svg"
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
                <span class="checkbox-text">Remember</span>
              </label>
            </div>

            <!-- Submit Button -->
            <button type="submit" class="submit-btn" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner">⏳</span>
              <span v-else>LOG IN</span>
            </button>
          </form>

          <GoogleAuthButton
            label="Google sign-in"
            button-text="signin_with"
            :selected-role="userType"
          />

          <!-- Sign Up Link -->
          <div class="signup-section">
            <div class="signup-row">
              <span class="signup-text">Don't have an account? </span>
              <a @click="goToSignUp" class="signup-link">Sign up!</a>
            </div>
            <div class="admin-row">
              <span class="signup-text">If you are admin? </span>
              <router-link to="/admin/login" class="admin-link">Sign in!</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 1200px;
  min-height: 700px;
  background: white;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  display: grid;
  grid-template-columns: 45% 55%;
}

.image-section {
  position: relative;
  overflow: hidden;
}

.background-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(45, 80, 22, 0.7) 0%, rgba(74, 124, 44, 0.5) 100%);
}

.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px 60px;
  background: #f8f9fa;
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
  color: #666;
}

.brand {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: 2px;
  color: #2d5016;
}

.welcome-section {
  margin-bottom: 20px;
}

.welcome-title {
  font-size: 2.2rem;
  font-weight: 900;
  color: #2d5016;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.welcome-subtitle {
  font-size: 1rem;
  color: #666;
  margin: 0;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  border: 1px solid #ef5350;
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

.user-type-section {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.type-btn {
  flex: 1;
  padding: 12px 16px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.type-dot {
  width: 12px;
  height: 12px;
  border: 2px solid #ccc;
  border-radius: 50%;
  transition: all 0.3s;
}

.type-btn.active {
  border-color: #2d5016;
  background: #f1f8e9;
  color: #2d5016;
}

.type-btn.active .type-dot {
  background: #2d5016;
  border-color: #2d5016;
}

.type-btn:hover {
  border-color: #4a7c2c;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 14px 50px 14px 18px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.3s;
  background: white;
  font-family: inherit;
}

.form-input:focus {
  border-color: #4a7c2c;
  box-shadow: 0 0 0 4px rgba(74, 124, 44, 0.1);
}

.input-icon {
  position: absolute;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  color: #999;
  transition: color 0.3s;
}

.input-icon.clickable {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-icon.clickable .icon-svg {
  width: 20px;
  height: 20px;
  color: #999;
  transition: color 0.3s;
}

.input-icon.clickable:hover .icon-svg {
  color: #4a7c2c;
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
  color: #666;
}

.remember-checkbox input[type='checkbox'] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #4a7c2c;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 8px;
  box-shadow: 0 4px 15px rgba(45, 80, 22, 0.3);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(45, 80, 22, 0.4);
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

.signup-section {
  text-align: center;
  margin-top: 20px;
  font-size: 0.9rem;
  padding-bottom: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.signup-row,
.admin-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
}

.signup-text {
  color: #666;
}

.signup-link {
  color: #2d5016;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.3s;
}

.signup-link:hover {
  color: #4a7c2c;
  text-decoration: underline;
}

.admin-link {
  color: #dc2626;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.3s;
}

.admin-link:hover {
  color: #b91c1c;
  text-decoration: underline;
}

@media (max-width: 1024px) {
  .login-container {
    grid-template-columns: 1fr;
    height: auto;
    min-height: auto;
  }

  .image-section {
    display: none;
  }

  .form-section {
    padding: 40px 30px;
  }

  .welcome-title {
    font-size: 2.25rem;
  }
}

@media (max-width: 768px) {
  .form-section {
    padding: 30px 20px;
  }

  .welcome-title {
    font-size: 2rem;
  }

  .welcome-text {
    font-size: 0.95rem;
  }

  .user-type-card {
    padding: 14px;
  }

  .user-type-icon {
    width: 40px;
    height: 40px;
  }

  .user-type-title {
    font-size: 0.95rem;
  }

  .user-type-description {
    font-size: 0.8rem;
  }

  .input-group label {
    font-size: 0.9rem;
  }

  .input-wrapper input {
    padding: 12px 45px 12px 12px;
    font-size: 0.95rem;
  }

  .btn-primary {
    padding: 12px;
    font-size: 0.95rem;
  }
}

@media (max-width: 640px) {
  .form-section {
    padding: 24px 16px;
  }

  .welcome-title {
    font-size: 1.75rem;
  }

  .welcome-text {
    font-size: 0.9rem;
  }

  .user-type-section {
    flex-direction: column;
    gap: 10px;
  }

  .user-type-card {
    padding: 12px;
  }

  .user-type-icon {
    width: 36px;
    height: 36px;
  }

  .user-type-title {
    font-size: 0.9rem;
  }

  .user-type-description {
    font-size: 0.75rem;
  }

  .input-wrapper input {
    padding: 10px 40px 10px 10px;
    font-size: 0.9rem;
  }

  .toggle-password {
    right: 10px;
  }

  .btn-primary {
    padding: 11px;
    font-size: 0.9rem;
  }

  .divider-text {
    font-size: 0.8rem;
  }

  .signup-prompt {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .welcome-title {
    font-size: 1.5rem;
  }

  .user-type-card {
    padding: 10px;
  }

  .input-wrapper input {
    font-size: 0.85rem;
  }

  .btn-primary {
    font-size: 0.85rem;
  }
}
</style>
