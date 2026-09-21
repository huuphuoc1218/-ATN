<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axiosInstance from '@/utils/axios'

interface Notification {
  id: number
  title: string
  message: string
  type: string
  is_read: boolean
  created_at: string
  related_id: number | null
}

const router = useRouter()
const authStore = useAuthStore()
const notifications = ref<Notification[]>([])
const unreadCount = ref(0)
const showDropdown = ref(false)
let pollingInterval: ReturnType<typeof setInterval> | null = null

const fetchNotifications = async () => {
  // Only fetch if user is authenticated
  const token = localStorage.getItem('token')
  if (!authStore.user || !token) {
    return
  }

  try {
    const [notifResponse, countResponse] = await Promise.all([
      axiosInstance.get<Notification[]>('/notifications?limit=10'),
      axiosInstance.get('/notifications/unread-count'),
    ])
    notifications.value = notifResponse.data
    unreadCount.value = countResponse.data.count
  } catch (error) {
    const err = error as { response?: { status?: number } }
    // Silent fail for 401 errors
    if (err?.response?.status === 401) {
      return
    }
  }
}

const markAsRead = async (notificationId: number) => {
  try {
    await axiosInstance.put(`/notifications/${notificationId}/read`)
    const notification = notifications.value.find((n) => n.id === notificationId)
    if (notification && !notification.is_read) {
      notification.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  } catch {
    // Silent fail
  }
}

const markAllAsRead = async () => {
  try {
    await axiosInstance.post('/notifications/mark-all-read')
    notifications.value.forEach((n) => (n.is_read = true))
    unreadCount.value = 0
  } catch {
    // Silent fail
  }
}

const handleNotificationClick = async (notification: Notification) => {
  await markAsRead(notification.id)
  showDropdown.value = false

  // Navigate based on notification type for admin
  if (notification.type === 'request_created' && notification.related_id) {
    router.push('/admin/request')
  }
}

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
  if (showDropdown.value) {
    fetchNotifications()
  }
}

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'request_created':
      return '📝'
    case 'request_approved':
      return '✅'
    case 'request_rejected':
      return '❌'
    case 'booking_created':
      return '📅'
    case 'booking_cancelled':
      return '🚫'
    default:
      return '🔔'
  }
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} minutes ago`
  if (hours < 24) return `${hours} hours ago`
  return `${days} days ago`
}

// Close dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.notification-bell-container')) {
    showDropdown.value = false
  }
}

onMounted(() => {
  // Initial fetch
  fetchNotifications()

  // Poll for new notifications every 30 seconds
  pollingInterval = setInterval(fetchNotifications, 30000)

  // Close dropdown when clicking outside
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  // Clear interval on unmount
  if (pollingInterval) {
    clearInterval(pollingInterval)
  }
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="notification-bell-container">
    <button class="notification-bell" @click="toggleDropdown" :class="{ active: showDropdown }">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
    </button>

    <transition name="dropdown">
      <div v-if="showDropdown" class="notification-dropdown">
        <div class="dropdown-header">
          <h3>Notifications</h3>
          <button v-if="unreadCount > 0" @click="markAllAsRead" class="mark-all-btn">
            Mark all as read
          </button>
        </div>

        <div class="notification-list">
          <template v-if="notifications.length > 0">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              class="notification-item"
              :class="{ unread: !notification.is_read }"
              @click="handleNotificationClick(notification)"
            >
              <div class="notification-icon">{{ getNotificationIcon(notification.type) }}</div>
              <div class="notification-content">
                <h4>{{ notification.title }}</h4>
                <p>{{ notification.message }}</p>
                <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
              </div>
            </div>
          </template>

          <div v-else class="empty-state">
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
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
              />
            </svg>
            <p>No notifications</p>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.notification-bell-container {
  position: relative;
  z-index: 10000;
}

.notification-bell {
  position: relative;
  padding: 8px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.notification-bell:hover,
.notification-bell.active {
  border-color: #4169e1;
  background: #eff6ff;
}

.notification-bell svg {
  width: 24px;
  height: 24px;
  color: #374151;
}

.notification-bell:hover svg,
.notification-bell.active svg {
  color: #4169e1;
}

.badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 0.7rem;
  font-weight: 700;
  min-width: 20px;
  text-align: center;
}

.notification-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 380px;
  max-height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  overflow: hidden;
}

@media (max-width: 768px) {
  .notification-dropdown {
    position: fixed;
    top: 60px;
    right: 10px;
    left: 10px;
    width: auto;
  }
}

@media (max-width: 480px) {
  .notification-dropdown {
    top: 52px;
    right: 6px;
    left: 6px;
    max-height: calc(100vh - 64px);
  }

  .dropdown-header {
    padding: 12px 14px;
  }

  .dropdown-header h3 {
    font-size: 1rem;
  }

  .notification-item {
    padding: 12px 14px;
  }
}

.dropdown-header {
  padding: 16px 20px;
  border-bottom: 2px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dropdown-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
}

.mark-all-btn {
  padding: 6px 12px;
  background: #f3f4f6;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mark-all-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 16px 20px;
  display: flex;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid #f3f4f6;
}

.notification-item:hover {
  background: #f9fafb;
}

.notification-item.unread {
  background: #eff6ff;
}

.notification-item.unread:hover {
  background: #dbeafe;
}

.notification-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-content h4 {
  margin: 0 0 4px 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1f2937;
}

.notification-content p {
  margin: 0 0 6px 0;
  font-size: 0.85rem;
  color: #6b7280;
  line-height: 1.4;
}

.notification-time {
  font-size: 0.75rem;
  color: #9ca3af;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #9ca3af;
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 0.9rem;
}

/* Dropdown animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Scrollbar styling */
.notification-list::-webkit-scrollbar {
  width: 6px;
}

.notification-list::-webkit-scrollbar-track {
  background: #f3f4f6;
}

.notification-list::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.notification-list::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
