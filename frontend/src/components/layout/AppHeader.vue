<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import UserDropdown from './UserDropdown.vue'

const route = useRoute()

const authStore = useAuthStore()

// Props để custom header
interface Props {
  showManagement?: boolean
  showAdvertisement?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showManagement: false,
  showAdvertisement: false,
})

const currentTime = ref('')
const currentDate = ref('')
const currentDay = ref('')
const isScrolled = ref(false)
let timeInterval: number | null = null

// Check authentication
const isAuthenticated = computed(() => !!authStore.user)
const isUser = computed(() => authStore.user?.role === 'user')

// Compute home link based on user role
const homeLink = computed(() => {
  if (!authStore.user) {
    return '/'
  }

  const role = authStore.user.role

  // Map role to home page
  switch (role) {
    case 'user':
      return '/user/home'
    case 'owner':
      return '/owner/home'
    case 'enterprise':
      return '/enterprise/home'
    case 'admin':
      return '/admin/profile'
    default:
      return '/'
  }
})

const updateDateTime = () => {
  const now = new Date()

  // Update time with seconds for real-time display
  currentTime.value = now.toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })

  // Update date
  currentDate.value = now.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })

  // Update day of week
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  currentDay.value = days[now.getDay()]
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

onMounted(() => {
  updateDateTime()
  // Update every second for real-time clock
  timeInterval = window.setInterval(updateDateTime, 1000)
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <header class="app-header" :class="{ scrolled: isScrolled }">
    <div class="header-container">
      <!-- Logo -->
      <div class="logo-section">
        <div class="logo-icon">
          <img src="/Logo.png" alt="Logo" />
        </div>
        <div class="logo-text">
          <span class="pickleball">Pickleball</span>
          <span class="brand">NP SPORTCLUB</span>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="main-nav">
        <router-link :to="homeLink" class="nav-link">HOME</router-link>
        <router-link to="/court" class="nav-link">COURT</router-link>
        <router-link
          v-if="isUser"
          to="/user/streaks/friends"
          class="nav-link"
          :class="{ 'router-link-active': route.path.startsWith('/user/streaks') }"
        >
          STREAKS
        </router-link>

        <!-- Management link for Owner -->
        <router-link
          v-if="props.showManagement"
          to="/owner/management/revenue"
          class="nav-link"
          :class="{ 'router-link-active': route.path.startsWith('/owner/management') }"
        >
          MANAGEMENT
        </router-link>

        <!-- Advertisement link for Enterprise -->
        <router-link
          v-if="props.showAdvertisement"
          to="/enterprise/advertisements/list"
          class="nav-link"
          :class="{ 'router-link-active': route.path.startsWith('/enterprise/advertisements') }"
        >
          ADVERTISEMENT
        </router-link>
      </nav>

      <!-- Time & Date -->
      <div class="datetime-section">
        <div class="datetime-card">
          <div class="datetime-row">
            <svg
              class="datetime-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div class="datetime-info">
              <div class="datetime-label">Time</div>
              <div class="datetime-value time-value">{{ currentTime }}</div>
            </div>
          </div>
        </div>

        <div class="datetime-divider"></div>

        <div class="datetime-card">
          <div class="datetime-row">
            <svg
              class="datetime-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <div class="datetime-info">
              <div class="datetime-label">{{ currentDay }}</div>
              <div class="datetime-value">{{ currentDate }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- User Info or Sign In Button -->
      <UserDropdown v-if="isAuthenticated" />

      <router-link v-else to="/login" class="sign-in-btn">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          class="icon"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
          />
        </svg>
        <span>Sign In</span>
      </router-link>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: linear-gradient(135deg, #2d5016 0%, #3d6620 50%, #4a7c2c 100%);
  padding: 18px 48px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: all 0.3s ease;
  border-bottom: 3px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
}

@media (max-width: 1440px) {
  .app-header {
    padding: 14px 24px;
  }

  .app-header.scrolled {
    padding: 12px 24px;
  }
}

.app-header.scrolled {
  padding: 14px 48px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #243e11 0%, #2d5016 50%, #3d6620 100%);
}

.header-container {
  max-width: 1600px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  align-items: center;
  gap: 20px;
}

@media (max-width: 1440px) {
  .header-container {
    gap: 16px;
  }
}

/* Logo Section */
.logo-section {
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  border: 2px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.logo-section:hover {
  transform: scale(1.05);
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow:
    0 6px 20px rgba(0, 0, 0, 0.25),
    0 0 30px rgba(255, 255, 255, 0.1);
}

.logo-icon {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 4px 12px rgba(255, 255, 255, 0.3)) drop-shadow(0 2px 8px rgba(0, 0, 0, 0.4));
  animation: float 3s ease-in-out infinite;
  transition: transform 0.3s ease;
}

@media (max-width: 1440px) {
  .logo-icon {
    width: 70px;
    height: 70px;
  }
}

.logo-icon:hover {
  transform: scale(1.1);
}

.logo-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: brightness(1.1);
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-5px);
  }
}

.logo-text {
  display: flex;
  flex-direction: column;
  color: white;
  line-height: 1.3;
}

.pickleball {
  font-size: 0.85rem;
  font-weight: 500;
  opacity: 0.95;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.brand {
  font-size: 1.75rem;
  font-weight: 900;
  letter-spacing: 3px;
  text-shadow:
    0 2px 12px rgba(0, 0, 0, 0.4),
    0 0 20px rgba(255, 255, 255, 0.2);
  background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 50%, #ffffff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@media (max-width: 1440px) {
  .brand {
    font-size: 1.3rem;
    letter-spacing: 2px;
  }

  .pickleball {
    font-size: 0.75rem;
  }
}

/* Navigation */
.main-nav {
  display: flex;
  gap: 12px;
  justify-content: center;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: 1px;
  padding: 12px 28px;
  border-radius: 10px;
  transition: all 0.3s ease;
  position: relative;
  background: transparent;
  text-transform: uppercase;
  white-space: nowrap;
}

@media (max-width: 1440px) {
  .nav-link {
    font-size: 0.9rem;
    padding: 10px 20px;
  }
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* DateTime Section */
.datetime-section {
  display: flex;
  align-items: center;
  gap: 0;
  background: rgba(255, 255, 255, 0.12);
  padding: 12px 20px;
  border-radius: 14px;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.datetime-section:hover {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.datetime-card {
  display: flex;
  align-items: center;
}

.datetime-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.datetime-icon {
  width: 32px;
  height: 32px;
  color: white;
  opacity: 0.95;
  flex-shrink: 0;
}

.datetime-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  color: white;
}

.datetime-label {
  font-size: 0.7rem;
  font-weight: 500;
  opacity: 0.85;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.datetime-value {
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  font-family: 'Courier New', monospace;
}

.time-value {
  font-size: 1.1rem;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.datetime-divider {
  width: 2px;
  height: 36px;
  background: rgba(255, 255, 255, 0.25);
  margin: 0 16px;
}

/* Sign In Button */
.sign-in-btn {
  background: white;
  color: #2d5016;
  border: none;
  padding: 12px 32px;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sign-in-btn .icon {
  width: 20px;
  height: 20px;
}

.sign-in-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  background: #f8f8f8;
}

.sign-in-btn:active {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

/* Responsive Design */
@media (max-width: 1400px) {
  .datetime-label {
    font-size: 0.65rem;
  }

  .datetime-value {
    font-size: 0.9rem;
  }

  .time-value {
    font-size: 1rem;
  }
}

@media (max-width: 1366px) {
  .datetime-section {
    display: none;
  }

  .header-container {
    grid-template-columns: auto 1fr auto;
    gap: 20px;
  }
}

@media (max-width: 968px) {
  .app-header {
    padding: 16px 24px;
  }

  .header-container {
    gap: 20px;
  }

  .main-nav {
    gap: 4px;
  }

  .nav-link {
    padding: 10px 16px;
    font-size: 0.9rem;
  }
}

@media (max-width: 968px) {
  .datetime-section {
    display: none;
  }

  .header-container {
    grid-template-columns: auto 1fr auto;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: 12px 12px;
  }

  .header-container {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 10px;
    align-items: center;
  }

  .logo-section {
    flex: 0 0 auto;
    padding: 6px 10px;
    gap: 8px;
    border-radius: 12px;
  }

  .logo-icon {
    width: 42px;
    height: 42px;
  }

  .logo-icon img {
    width: 100%;
    height: 100%;
  }

  .logo-text {
    display: flex;
  }

  .brand {
    font-size: 1rem;
    letter-spacing: 1.2px;
  }

  .pickleball {
    font-size: 0.7rem;
  }

  .main-nav {
    grid-column: 1 / -1;
    width: 100%;
    justify-content: flex-start;
    order: 3;
    gap: 6px;
    flex-wrap: nowrap;
    overflow-x: auto;
    scrollbar-width: thin;
    padding-bottom: 2px;
  }

  .nav-link {
    padding: 7px 12px;
    font-size: 0.85rem;
    flex: 0 0 auto;
  }

  .sign-in-btn {
    padding: 9px 14px;
    font-size: 0.85rem;
  }
}

@media (max-width: 640px) {
  .logo-section {
    padding: 5px 8px;
    gap: 6px;
  }

  .logo-icon {
    width: 34px;
    height: 34px;
  }

  .brand {
    font-size: 0.82rem;
    letter-spacing: 0.6px;
  }

  .pickleball {
    font-size: 0.65rem;
  }

  .nav-link {
    padding: 7px 10px;
    font-size: 0.76rem;
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: 10px 8px;
  }

  .logo-section {
    padding: 4px 6px;
    gap: 6px;
  }

  .logo-icon {
    width: 30px;
    height: 30px;
  }

  .logo-text {
    display: none;
  }

  .main-nav {
    gap: 4px;
  }

  .nav-link {
    padding: 6px 9px;
    font-size: 0.7rem;
    letter-spacing: 0.3px;
    border-radius: 8px;
  }

  .sign-in-btn span {
    display: none;
  }

  .sign-in-btn {
    padding: 10px;
    width: 44px;
    height: 44px;
    justify-content: center;
  }

  .sign-in-btn .icon {
    width: 20px;
    height: 20px;
  }
}
</style>
