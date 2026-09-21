<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import UserProfileModal from '@/components/user/UserProfileModal.vue'
import BookingHistoryModal from '@/components/user/BookingHistoryModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)
const showProfileModal = ref(false)
const showBookingModal = ref(false)

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

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
  isOpen.value = false
}

const goToProfile = () => {
  showProfileModal.value = true
  isOpen.value = false
}

const goToBookingHistory = () => {
  showBookingModal.value = true
  isOpen.value = false
}

// Close dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="user-dropdown" ref="dropdownRef">
    <button class="dropdown-trigger" @click="toggleDropdown">
      <div class="user-avatar">
        <img v-if="avatarSrc" :src="avatarSrc" alt="User avatar" class="avatar-image" />
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
      <span class="user-name">{{ authStore.user?.full_name }}</span>
      <svg
        class="chevron"
        :class="{ open: isOpen }"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <transition name="dropdown">
      <div v-if="isOpen" class="dropdown-menu">
        <div class="dropdown-header">
          <div class="user-info">
            <div class="user-avatar-large">
              <img v-if="avatarSrc" :src="avatarSrc" alt="User avatar" class="avatar-large-image" />
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
              <div class="user-full-name">{{ authStore.user?.full_name }}</div>
              <div class="user-email">{{ authStore.user?.email }}</div>
            </div>
          </div>
        </div>

        <div class="dropdown-divider"></div>

        <div class="dropdown-body">
          <button class="dropdown-item" @click="goToProfile">
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
            <span>Profile</span>
          </button>

          <button class="dropdown-item" @click="goToBookingHistory">
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
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <span>Booking History</span>
          </button>
        </div>

        <div class="dropdown-divider"></div>

        <div class="dropdown-footer">
          <button class="dropdown-item logout" @click="handleLogout">
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
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
            <span>Log out</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- Modals -->
    <UserProfileModal :is-open="showProfileModal" @close="showProfileModal = false" />
    <BookingHistoryModal :is-open="showBookingModal" @close="showBookingModal = false" />
  </div>
</template>

<style scoped>
.user-dropdown {
  position: relative;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.25);
  padding: 10px 16px;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  font-weight: 600;
  font-size: 0.95rem;
}

.dropdown-trigger:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar svg {
  width: 20px;
  height: 20px;
  color: white;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chevron {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.chevron.open {
  transform: rotate(180deg);
}

/* Dropdown Menu */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  min-width: 280px;
  overflow: hidden;
  z-index: 11000;
}

.dropdown-header {
  padding: 16px;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-large {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-large-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar-large svg {
  width: 28px;
  height: 28px;
  color: white;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-full-name {
  color: white;
  font-weight: 700;
  font-size: 1rem;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-email {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
}

.dropdown-body,
.dropdown-footer {
  padding: 8px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #374151;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.dropdown-item:hover {
  background: #f3f4f6;
  color: #2d5016;
}

.dropdown-item svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.dropdown-item.logout {
  color: #dc2626;
}

.dropdown-item.logout:hover {
  background: #fee2e2;
  color: #b91c1c;
}

/* Transition */
.dropdown-enter-active {
  animation: dropdown-fade-in 0.3s ease;
}

.dropdown-leave-active {
  animation: dropdown-fade-out 0.2s ease;
}

@keyframes dropdown-fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes dropdown-fade-out {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

@media (max-width: 768px) {
  .user-name {
    display: none;
  }

  .dropdown-trigger {
    padding: 10px;
  }

  .dropdown-menu {
    min-width: 260px;
  }
}

@media (max-width: 480px) {
  .dropdown-menu {
    right: -8px;
    min-width: min(92vw, 260px);
  }

  .dropdown-item {
    padding: 10px 12px;
    font-size: 0.9rem;
  }

  .dropdown-header {
    padding: 12px;
  }

  .user-full-name {
    font-size: 0.95rem;
  }

  .user-email {
    font-size: 0.8rem;
  }
}
</style>
