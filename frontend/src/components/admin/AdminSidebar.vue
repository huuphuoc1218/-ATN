<template>
  <div class="admin-sidebar">
    <div class="sidebar-header">
      <div class="logo-container">
        <img
          src="/Logo.png"
          alt="Logo"
          class="logo-icon"
          style="
            height: 40px;
            width: auto;
            filter: drop-shadow(0 4px 8px rgba(65, 105, 225, 0.4));
            animation: pulse 3s ease-in-out infinite;
          "
        />
        <div class="logo-text">
          <span class="logo-brand">NP SPORTCLUB</span>
          <span class="logo-subtitle">Admin Portal</span>
        </div>
      </div>
    </div>

    <nav class="sidebar-nav">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: currentRoute === item.path }"
      >
        <div class="nav-icon-wrapper">
          <img
            v-if="item.iconImage"
            :src="item.iconImage"
            :alt="item.label"
            class="nav-icon-image"
          />
          <span v-else class="nav-icon">{{ item.icon }}</span>
        </div>
        <span class="nav-label">{{ item.label }}</span>
        <span class="nav-arrow" v-if="currentRoute === item.path">›</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <div class="admin-badge">
        <span class="badge-icon">👤</span>
        <span class="badge-text">{{ authStore.user?.full_name || 'Admin' }}</span>
      </div>
      <button class="logout-btn" @click="handleLogout">
        <span class="logout-icon">🚪</span>
        <span class="logout-label">Logout</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const currentRoute = computed(() => route.path)

const menuItems = [
  { path: '/admin/profile', label: 'Profile', icon: '👤' },
  { path: '/admin/users', label: 'Users', icon: '👥' },
  { path: '/admin/courts', label: 'Court', iconImage: '/logo-pickball.webp' },
  { path: '/admin/requests', label: 'Request', icon: '📋' },
]

const handleLogout = () => {
  authStore.logout()
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-sidebar {
  width: 280px;
  height: 100vh;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f1729 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
  z-index: 1000;
}

.sidebar-header {
  padding: 30px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  font-size: 40px;
  filter: drop-shadow(0 4px 8px rgba(65, 105, 225, 0.4));
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.logo-brand {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 1.5px;
  background: linear-gradient(135deg, #fff 0%, #a8b9ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-subtitle {
  font-size: 11px;
  color: #8899bb;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.sidebar-nav {
  flex: 1;
  padding: 30px 16px;
  overflow-y: auto;
}

.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  color: #9ca3af;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border-radius: 12px;
  margin-bottom: 8px;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #4169e1 0%, #5a7fee 100%);
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.nav-item:hover {
  background: rgba(65, 105, 225, 0.15);
  color: #fff;
  transform: translateX(4px);
}

.nav-item:hover::before {
  transform: scaleY(1);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(65, 105, 225, 0.25) 0%, rgba(90, 127, 238, 0.2) 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(65, 105, 225, 0.3);
}

.nav-item.active::before {
  transform: scaleY(1);
}

.nav-icon-wrapper {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  margin-right: 14px;
  transition: all 0.3s ease;
}

.nav-item:hover .nav-icon-wrapper,
.nav-item.active .nav-icon-wrapper {
  background: rgba(65, 105, 225, 0.3);
  transform: scale(1.1);
}

.nav-icon {
  font-size: 20px;
}

.nav-icon-image {
  width: 20px;
  height: 20px;
  object-fit: contain;
  display: block;
}

.nav-label {
  font-size: 15px;
  font-weight: 500;
  flex: 1;
}

.nav-arrow {
  font-size: 18px;
  font-weight: bold;
  color: #4169e1;
  margin-left: auto;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.admin-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  margin-bottom: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.badge-icon {
  font-size: 20px;
}

.badge-text {
  font-size: 13px;
  font-weight: 600;
  color: #e0e7ff;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px 20px;
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 15px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.logout-btn:hover {
  background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(220, 38, 38, 0.4);
}

.logout-btn:active {
  transform: translateY(0);
}

.logout-icon {
  font-size: 18px;
}

.logout-label {
  font-weight: 600;
}

@media (max-width: 1024px) {
  .admin-sidebar {
    width: 100%;
    height: auto;
    position: relative;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
  }

  .sidebar-header {
    padding: 14px 16px;
  }

  .logo-brand {
    font-size: 16px;
  }

  .sidebar-nav {
    padding: 10px 12px;
    display: flex;
    gap: 8px;
    overflow-x: auto;
    overflow-y: hidden;
    white-space: nowrap;
  }

  .nav-item {
    margin-bottom: 0;
    min-width: max-content;
    padding: 10px 12px;
  }

  .nav-item:hover {
    transform: none;
  }

  .nav-icon-wrapper {
    width: 34px;
    height: 34px;
    margin-right: 8px;
  }

  .nav-label {
    font-size: 13px;
  }

  .sidebar-footer {
    display: none;
  }
}

@media (max-width: 640px) {
  .sidebar-header {
    padding: 10px 12px;
  }

  .logo-container {
    gap: 10px;
  }

  .logo-icon {
    height: 30px !important;
  }

  .logo-subtitle {
    display: none;
  }

  .sidebar-nav {
    padding: 8px 10px;
  }
}
</style>
