<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppHeader from '@/components/layout/AppHeader.vue'
import NotificationBell from '@/components/user/NotificationBell.vue'

const route = useRoute()
const authStore = useAuthStore()

const backendOrigin = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(
  /\/api\/?$/,
  '',
)

const avatarSrc = computed(() => {
  const raw = authStore.user?.avatar_url
  if (!raw) return ''
  if (raw.startsWith('http://') || raw.startsWith('https://')) return raw
  if (raw.startsWith('/')) return `${backendOrigin}${raw}`
  return `${backendOrigin}/${raw}`
})

const MOBILE_BREAKPOINT = 1024
const isSidebarOpen = ref(true)
const isMobileView = ref(false)

const updateViewportState = () => {
  const isMobile = window.innerWidth <= MOBILE_BREAKPOINT
  isMobileView.value = isMobile
  isSidebarOpen.value = !isMobile
}

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const closeSidebar = () => {
  if (isMobileView.value) {
    isSidebarOpen.value = false
  }
}

const handleNavClick = () => {
  closeSidebar()
}

const menuItems = [
  {
    id: 'friends',
    label: 'Friends',
    icon: 'users',
    path: '/user/streaks/friends',
  },
  {
    id: 'streaks',
    label: 'Streaks',
    icon: 'streaks-image',
    path: '/user/streaks/overview',
  },
]

const isActive = (path: string) => route.path === path

watch([isSidebarOpen, isMobileView], ([open, mobile]) => {
  document.body.style.overflow = mobile && open ? 'hidden' : ''
})

onMounted(() => {
  updateViewportState()
  window.addEventListener('resize', updateViewportState)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateViewportState)
  document.body.style.overflow = ''
})
</script>

<template>
  <div class="user-streaks-layout">
    <AppHeader />

    <div v-if="isMobileView && isSidebarOpen" class="sidebar-backdrop" @click="closeSidebar"></div>

    <aside class="sidebar" :class="{ collapsed: !isSidebarOpen }">
      <div class="sidebar-header">
        <div class="logo-section">
          <div class="logo-icon">
            <img src="/Logo.png" alt="Logo" />
          </div>
          <transition name="fade">
            <div v-if="isSidebarOpen" class="logo-text">
              <span class="logo-title">User Panel</span>
              <span class="logo-subtitle">Friends & Streaks</span>
            </div>
          </transition>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.id"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
          @click="handleNavClick"
        >
          <span class="nav-icon">
            <svg
              v-if="item.icon === 'users'"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              width="24"
              height="24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 20h5v-2a4 4 0 00-4-4h-1M9 20H4v-2a4 4 0 014-4h1m4-4a4 4 0 100-8 4 4 0 000 8zm-6 0a3 3 0 110-6 3 3 0 010 6zm12 0a3 3 0 110-6 3 3 0 010 6z"
              />
            </svg>
            <svg
              v-else-if="item.icon === 'fire'"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              width="24"
              height="24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 3c0 3.5-3 5-3 8a3 3 0 106 0c0-1.5-.6-2.7-1.7-3.9M9 14a3 3 0 006 0c0 1.7-1.3 3-3 3s-3-1.3-3-3z"
              />
            </svg>
            <img
              v-else-if="item.icon === 'streaks-image'"
              src="/streaks.jpg"
              alt="Streaks"
              class="nav-icon-image"
            />
          </span>
          <transition name="fade">
            <span v-if="isSidebarOpen" class="nav-label">{{ item.label }}</span>
          </transition>
        </router-link>
      </nav>
    </aside>

    <div class="main-wrapper">
      <header class="top-bar">
        <button class="toggle-btn" @click="toggleSidebar">
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
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <div class="top-bar-title">
          <h1>{{ menuItems.find((item) => isActive(item.path))?.label || 'Streaks' }}</h1>
        </div>

        <div class="top-bar-right">
          <NotificationBell />

          <div class="user-info">
            <div class="user-avatar">
              <img v-if="avatarSrc" :src="avatarSrc" alt="User avatar" class="user-avatar-image" />
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
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <div class="user-details">
              <span class="user-name">{{ authStore.user?.full_name }}</span>
              <span class="user-role">User</span>
            </div>
          </div>
        </div>
      </header>

      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.user-streaks-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f8fafc;
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  z-index: 1100;
}

.sidebar {
  width: 280px;
  background: linear-gradient(180deg, #2d5016 0%, #1a3009 100%);
  color: white;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.1);
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  height: 100dvh;
  padding-top: 130px;
  z-index: 800;
}

@media (max-width: 1440px) {
  .sidebar {
    width: 240px;
    padding-top: 110px;
  }

  .sidebar.collapsed {
    width: 70px;
  }
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 70px;
  height: 70px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 2px 6px rgba(255, 255, 255, 0.2));
  transition: transform 0.3s ease;
}

.logo-icon:hover {
  transform: scale(1.1);
}

.logo-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 1.2rem;
  font-weight: 700;
  line-height: 1.2;
}

.logo-subtitle {
  font-size: 0.8rem;
  opacity: 0.8;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #22c55e;
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.nav-item.active::before {
  transform: scaleY(1);
}

.nav-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.nav-icon-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.nav-label {
  font-weight: 600;
  font-size: 0.95rem;
}

.main-wrapper {
  flex: 1;
  margin-left: 280px;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sidebar.collapsed ~ .main-wrapper {
  margin-left: 80px;
}

@media (max-width: 1440px) {
  .main-wrapper {
    margin-left: 240px;
  }

  .sidebar.collapsed ~ .main-wrapper {
    margin-left: 70px;
  }
}

.top-bar {
  height: 80px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  padding: 0 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.top-bar-title {
  flex: 1;
  text-align: center;
}

.toggle-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: #f3f4f6;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background: #22c55e;
  color: white;
}

.toggle-btn svg {
  width: 22px;
  height: 22px;
}

.top-bar-title h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-left: auto;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px 8px 8px;
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
}

.user-avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e5e7eb;
  border: 1px solid #d1d5db;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.user-avatar svg {
  width: 20px;
  height: 20px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1;
}

.user-role {
  font-size: 12px;
  color: #6b7280;
  line-height: 1;
}

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 1024px) {
  .sidebar {
    display: flex;
    width: 260px;
    top: 0;
    bottom: 0;
    height: 100dvh;
    padding-top: 0;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 1200;
  }

  .sidebar.collapsed {
    width: 260px;
    transform: translateX(-100%);
  }

  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }

  .main-wrapper,
  .sidebar.collapsed ~ .main-wrapper {
    margin-left: 0;
  }

  .top-bar {
    padding: 0 16px;
  }

  .top-bar-title h1 {
    font-size: 1.1rem;
  }

  .toggle-btn {
    display: flex;
  }

  .top-bar-right {
    gap: 10px;
  }

  .main-content {
    padding: 16px;
  }
}

@media (max-width: 640px) {
  .top-bar {
    height: 68px;
    padding: 0 12px;
  }

  .top-bar-title h1 {
    font-size: 1rem;
  }

  .user-details {
    display: none;
  }

  .sidebar {
    top: 0;
    width: 240px;
    padding-top: 0;
  }

  .sidebar.collapsed {
    width: 240px;
  }
}
</style>
