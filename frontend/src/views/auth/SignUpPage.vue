<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import GoogleAuthButton from '@/components/auth/GoogleAuthButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()

const userType = ref<'user' | 'enterprise' | 'owner' | null>(null)

// Check if role is passed via query parameter
onMounted(() => {
  const roleParam = route.query.role as string
  if (roleParam === 'enterprise' || roleParam === 'owner') {
    userType.value = roleParam
  }
})
const name = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const errorMessage = ref('')
const isSubmitting = computed(() => authStore.isLoading)

const handleSignUp = async () => {
  errorMessage.value = ''

  // Validation
  if (!name.value || !email.value || !password.value || !confirmPassword.value) {
    errorMessage.value = 'Please fill in all required information'
    toast.error('Please fill in all required information')
    return
  }

  if (password.value.length < 6) {
    errorMessage.value = 'Password must be at least 6 characters'
    toast.error('Password must be at least 6 characters')
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Password confirmation does not match'
    toast.error('Password confirmation does not match')
    return
  }

  if (!userType.value) {
    errorMessage.value = 'Please select your role before signing up'
    toast.error('Please select your role before signing up')
    return
  }

  const result = await authStore.signup({
    email: email.value,
    password: password.value,
    full_name: name.value,
    phone_number: phone.value || undefined,
    role: userType.value,
  })

  if (result.success) {
    // Hiển thị thông báo thành công
    toast.success('🎉 Account created successfully!', {
      timeout: 2000,
    })

    // Chuyển hướng về trang login sau 2 giây
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } else {
    errorMessage.value = result.error || 'Registration failed'
    toast.error(errorMessage.value)
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="signup-page">
    <div class="signup-container">
      <!-- Left Side - Form -->
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

          <!-- Title -->
          <div class="title-section">
            <h1 class="page-title">SIGN UP</h1>
            <p class="page-subtitle">Create your account</p>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="error-message">
            <span class="error-icon">⚠️</span>
            {{ errorMessage }}
          </div>

          <!-- User Type Label -->
          <div class="who-label">Who are you ?</div>

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

          <!-- Sign Up Form -->
          <form @submit.prevent="handleSignUp" class="signup-form">
            <!-- Name Input -->
            <div class="input-group">
              <input
                v-model="name"
                type="text"
                placeholder="Full Name"
                class="form-input"
                required
                :disabled="isSubmitting"
              />
            </div>

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

            <!-- Confirm Password Input -->
            <div class="input-group">
              <input
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="Confirm Password"
                class="form-input"
                required
                :disabled="isSubmitting"
              />
              <button
                type="button"
                class="input-icon clickable"
                @click="showConfirmPassword = !showConfirmPassword"
                :disabled="isSubmitting"
              >
                <svg
                  v-if="showConfirmPassword"
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

            <!-- Submit Button -->
            <button type="submit" class="submit-btn" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner">⏳</span>
              <span v-else>CREATE</span>
            </button>
          </form>

          <GoogleAuthButton
            label="Google sign-up"
            button-text="signup_with"
            :selected-role="userType"
            :require-role-selection="true"
          />

          <!-- Login Link -->
          <div class="login-section">
            <span class="login-text">Already have an account? </span>
            <a @click="goToLogin" class="login-link">Login!</a>
          </div>
        </div>
      </div>

      <!-- Right Side - Image -->
      <div class="image-section">
        <img
          src="https://i.pinimg.com/1200x/04/59/35/045935827b1f4a5772159ce76a6b1880.jpg?fbclid=IwY2xjawPE08NleHRuA2FlbQIxMABicmlkETFJdHVUV2R4NmFBbVNTTVNhc3J0YwZhcHBfaWQQMjIyMDM5MTc4ODIwMDg5MgABHnIB4EjUurB58YP1y_wyKtnyvtutiuEcJ36ETXMK7hqF6Djr2L6XOsMN5iMD_aem_7geijhvrXz2pUk8ci7VUJQ"
          alt="Pickleball Balls"
          class="background-image"
        />
        <div class="image-overlay"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.signup-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  padding: 20px;
}

.signup-container {
  width: 100%;
  max-width: 1200px;
  min-height: 750px;
  background: white;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  display: grid;
  grid-template-columns: 55% 45%;
}

.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px 60px;
  background: #f8f9fa;
  overflow-y: auto;
}

.form-container {
  width: 100%;
  max-width: 480px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
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

.title-section {
  margin-bottom: 20px;
}

.page-title {
  font-size: 2.2rem;
  font-weight: 900;
  color: #2d5016;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.page-subtitle {
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
  margin-bottom: 14px;
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

.who-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #2d5016;
  margin-bottom: 10px;
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

.signup-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
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
  margin-top: 6px;
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

.login-section {
  text-align: center;
  margin-top: 16px;
  font-size: 0.9rem;
  padding-bottom: 8px;
}

.login-text {
  color: #666;
}

.login-link {
  color: #2d5016;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.3s;
}

.login-link:hover {
  color: #4a7c2c;
  text-decoration: underline;
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
  background: linear-gradient(135deg, rgba(74, 124, 44, 0.5) 0%, rgba(45, 80, 22, 0.7) 100%);
}

@media (max-width: 1024px) {
  .signup-container {
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

  .page-title {
    font-size: 2.25rem;
  }
}

@media (max-width: 768px) {
  .form-section {
    padding: 30px 20px;
  }

  .page-title {
    font-size: 2rem;
  }

  .page-subtitle {
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

  .form-grid {
    gap: 16px;
  }
}

@media (max-width: 640px) {
  .form-section {
    padding: 24px 16px;
  }

  .logo-section {
    margin-bottom: 20px;
  }

  .logo-section h1 {
    font-size: 1.75rem;
  }

  .title-section {
    margin-bottom: 16px;
  }

  .page-title {
    font-size: 1.75rem;
  }

  .page-subtitle {
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

  .form-grid {
    grid-template-columns: 1fr;
    gap: 14px;
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

  .login-prompt {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.5rem;
  }

  .logo-section h1 {
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
