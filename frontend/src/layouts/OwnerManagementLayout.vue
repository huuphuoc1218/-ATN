<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppHeader from '@/components/layout/AppHeader.vue'
import NotificationBell from '@/components/owner/NotificationBell.vue'
const route = useRoute()
const authStore = useAuthStore()

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
    id: 'revenue',
    label: 'Revenue Statistics',
    icon: 'chart-bar',
    path: '/owner/management/revenue',
  },
  {
    id: 'courts',
    label: 'Upload Court',
    icon: 'building-stadium',
    path: '/owner/management/courts',
  },
  {
    id: 'court-list',
    label: 'Court List',
    icon: 'list-bullet',
    path: '/owner/management/court-list',
  },
  {
    id: 'bookings',
    label: 'Booking Schedule',
    icon: 'calendar',
    path: '/owner/management/bookings',
  },
]

const isActive = (path: string) => {
  return route.path === path
}

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
  <div class="owner-management-layout">
    <!-- Header -->
    <AppHeader :showManagement="true" />

    <div v-if="isMobileView && isSidebarOpen" class="sidebar-backdrop" @click="closeSidebar"></div>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: !isSidebarOpen }">
      <div class="sidebar-header">
        <div class="logo-section">
          <div class="logo-icon">
            <img src="/Logo.png" alt="Logo" />
          </div>
          <transition name="fade">
            <div v-if="isSidebarOpen" class="logo-text">
              <span class="logo-title">Owner Panel</span>
              <span class="logo-subtitle">Management</span>
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
              v-if="item.icon === 'chart-bar'"
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
                d="M3 3v18h18"
              />
              <rect x="7" y="13" width="3" height="5" rx="1" fill="#fbbf24" />
              <rect x="12" y="9" width="3" height="9" rx="1" fill="#10b981" />
              <rect x="17" y="5" width="3" height="13" rx="1" fill="#3b82f6" />
            </svg>
            <svg
              v-else-if="item.icon === 'building-stadium'"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              width="24"
              height="24"
            >
              <rect x="4" y="10" width="16" height="8" rx="2" fill="#10b981" />
              <rect x="7" y="6" width="10" height="4" rx="2" fill="#fbbf24" />
              <rect x="9" y="2" width="6" height="4" rx="2" fill="#3b82f6" />
            </svg>
            <svg
              v-else-if="item.icon === 'list-bullet'"
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
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
            <svg
              v-else-if="item.icon === 'calendar'"
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
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </span>
          <transition name="fade">
            <span v-if="isSidebarOpen" class="nav-label">{{ item.label }}</span>
          </transition>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="main-wrapper">
      <!-- Top Bar -->
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
          <h1>{{ menuItems.find((item) => isActive(item.path))?.label || 'Management' }}</h1>
        </div>

        <NotificationBell />

        <div class="user-info">
          <div class="user-avatar">
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
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </div>
          <div class="user-details">
            <span class="user-name">{{ authStore.user?.full_name }}</span>
            <span class="user-role">Owner</span>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.owner-management-layout {
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

/* Sidebar */
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

/* Navigation */
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
  background: #fbbf24;
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

.nav-item.active::before {
  transform: scaleY(1);
}

.nav-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.nav-label {
  font-weight: 600;
  font-size: 0.95rem;
}

/* Main Wrapper */
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

/* Top Bar */
.top-bar {
  background: white;
  padding: 20px 32px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  min-width: 0;
  overflow: visible;
  position: sticky;
  top: 0;
  z-index: 900;
}

@media (max-width: 1440px) {
  .top-bar {
    padding: 16px 24px;
    gap: 16px;
  }
}

.toggle-btn {
  width: 40px;
  height: 40px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background: #e5e7eb;
}

.toggle-btn svg {
  width: 20px;
  height: 20px;
  color: #374151;
}

.top-bar-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.top-bar-title h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 1440px) {
  .top-bar-title h1 {
    font-size: 1.2rem;
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: #f9fafb;
  border-radius: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar svg {
  width: 24px;
  height: 24px;
  color: white;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #1f2937;
}

.user-role {
  font-size: 0.75rem;
  color: #6b7280;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 32px;
}

/* Fade Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .sidebar {
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

  .main-wrapper {
    margin-left: 0;
  }

  .sidebar.collapsed ~ .main-wrapper {
    margin-left: 0;
  }

  .user-details {
    display: none;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 240px;
    top: 0;
    padding-top: 0;
  }

  .sidebar.collapsed {
    width: 240px;
  }

  .main-wrapper {
    margin-left: 0;
  }

  .top-bar {
    padding: 16px 20px;
  }

  .top-bar-title h1 {
    font-size: 1.2rem;
  }

  .main-content {
    padding: 20px;
  }

  .top-bar {
    gap: 12px;
  }
}

@media (max-width: 640px) {
  .top-bar {
    padding: 12px;
  }

  .top-bar-title h1 {
    font-size: 1rem;
  }

  .sidebar,
  .sidebar.collapsed {
    width: 220px;
    top: 0;
    padding-top: 0;
  }
}
</style>
