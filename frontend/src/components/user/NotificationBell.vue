<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { isAxiosError } from 'axios'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

interface Notification {
  id: number
  title: string
  message: string
  type: string
  is_read: boolean
  created_at: string
  related_id: number | null
}

interface BookingInviteDetails {
  invite_id: number
  booking_id: number
  code: string
  status: string
  court_name: string
  location: string
  booking_date: string
  start_time: string
  end_time: string
  total_price: number | null
  inviter_name: string
  invitee_name: string | null
}

const authStore = useAuthStore()
const toast = useToast()
const notifications = ref<Notification[]>([])
const unreadCount = ref(0)
const showDropdown = ref(false)
const triggerRef = ref<HTMLElement | null>(null)
const dropdownStyle = ref<Record<string, string>>({})
const handledFriendRequestIds = ref<number[]>([])
const processingFriendRequestId = ref<number | null>(null)
const handledBookingInviteIds = ref<number[]>([])
const processingBookingInviteId = ref<number | null>(null)
const showDetailsModal = ref(false)
const loadingDetailsInviteId = ref<number | null>(null)
const bookingInviteDetails = ref<BookingInviteDetails | null>(null)
let pollingInterval: ReturnType<typeof setInterval> | null = null

const updateDropdownPosition = () => {
  if (!triggerRef.value) return

  const rect = triggerRef.value.getBoundingClientRect()
  const dropdownWidth = Math.min(380, window.innerWidth - 20)
  const left = Math.max(
    10,
    Math.min(rect.right - dropdownWidth, window.innerWidth - dropdownWidth - 10),
  )

  dropdownStyle.value = {
    position: 'fixed',
    top: `${rect.bottom + 8}px`,
    left: `${left}px`,
    width: `${dropdownWidth}px`,
    maxHeight: '500px',
    zIndex: '20000',
  }
}

const fetchNotifications = async () => {
  const token = localStorage.getItem('token')
  if (!authStore.user || !token) return

  try {
    const [notifResponse, countResponse] = await Promise.all([
      axiosInstance.get<Notification[]>('/notifications?limit=10'),
      axiosInstance.get('/notifications/unread-count'),
    ])
    notifications.value = notifResponse.data
    unreadCount.value = countResponse.data.count
  } catch (error) {
    const err = error as { response?: { status?: number } }
    if (err?.response?.status === 401) return
  }
}

const markAsRead = async (notificationId: number) => {
  try {
    await axiosInstance.put(`/notifications/${notificationId}/read`)
    const notification = notifications.value.find((item) => item.id === notificationId)
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
    notifications.value.forEach((item) => {
      item.is_read = true
    })
    unreadCount.value = 0
  } catch {
    // Silent fail
  }
}

const handleNotificationClick = async (notification: Notification) => {
  if (
    notification.type === 'friend_request_received' ||
    notification.type === 'booking_invite_received'
  )
    return
  await markAsRead(notification.id)
}

const respondFriendRequest = async (notification: Notification, action: 'accept' | 'reject') => {
  if (!notification.related_id) return
  if (processingFriendRequestId.value === notification.related_id) return

  try {
    processingFriendRequestId.value = notification.related_id
    await axiosInstance.post(`/friends/requests/${notification.related_id}/respond`, { action })

    if (!handledFriendRequestIds.value.includes(notification.related_id)) {
      handledFriendRequestIds.value = [...handledFriendRequestIds.value, notification.related_id]
    }

    const targetNotification = notifications.value.find((item) => item.id === notification.id)
    if (targetNotification) {
      targetNotification.type = 'friend_request_result'
      targetNotification.title =
        action === 'accept' ? 'Friend request accepted' : 'Friend request rejected'
      targetNotification.message =
        action === 'accept'
          ? 'You accepted this friend request.'
          : 'You rejected this friend request.'
      if (!targetNotification.is_read) {
        targetNotification.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    }

    toast.success(action === 'accept' ? 'Friend request accepted' : 'Friend request rejected')
    window.dispatchEvent(new CustomEvent('friends-updated'))
  } catch (error: unknown) {
    const message = isAxiosError(error)
      ? error.response?.data?.detail || 'Unable to process friend request'
      : 'Unable to process friend request'
    toast.error(message)
  } finally {
    processingFriendRequestId.value = null
  }
}

const canShowFriendRequestActions = (notification: Notification) => {
  return (
    notification.type === 'friend_request_received' &&
    !notification.is_read &&
    Boolean(notification.related_id) &&
    !handledFriendRequestIds.value.includes(notification.related_id as number)
  )
}

const respondBookingInvite = async (notification: Notification, action: 'accept' | 'reject') => {
  if (!notification.related_id) return
  if (processingBookingInviteId.value === notification.related_id) return

  try {
    processingBookingInviteId.value = notification.related_id
    await axiosInstance.post(`/bookings/invite-codes/${notification.related_id}/respond`, {
      action,
    })

    if (!handledBookingInviteIds.value.includes(notification.related_id)) {
      handledBookingInviteIds.value = [...handledBookingInviteIds.value, notification.related_id]
    }

    const targetNotification = notifications.value.find((item) => item.id === notification.id)
    if (targetNotification) {
      targetNotification.type = 'booking_invite_result'
      targetNotification.title =
        action === 'accept' ? 'Booking invite accepted' : 'Booking invite rejected'
      targetNotification.message =
        action === 'accept'
          ? 'You accepted this booking invitation.'
          : 'You rejected this booking invitation.'
      if (!targetNotification.is_read) {
        targetNotification.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    }

    toast.success(action === 'accept' ? 'Booking invite accepted' : 'Booking invite rejected')
  } catch (error: unknown) {
    const message = isAxiosError(error)
      ? error.response?.data?.detail || 'Unable to process booking invite'
      : 'Unable to process booking invite'
    toast.error(message)
  } finally {
    processingBookingInviteId.value = null
  }
}

const canShowBookingInviteActions = (notification: Notification) => {
  return (
    notification.type === 'booking_invite_received' &&
    !notification.is_read &&
    Boolean(notification.related_id) &&
    !handledBookingInviteIds.value.includes(notification.related_id as number)
  )
}

const openBookingInviteDetails = async (notification: Notification) => {
  if (!notification.related_id) return
  if (loadingDetailsInviteId.value === notification.related_id) return

  loadingDetailsInviteId.value = notification.related_id
  try {
    const response = await axiosInstance.get<BookingInviteDetails>(
      `/bookings/invite-codes/${notification.related_id}/details`,
    )
    bookingInviteDetails.value = response.data
    showDetailsModal.value = true
  } catch (error: unknown) {
    const message = isAxiosError(error)
      ? error.response?.data?.detail || 'Unable to load booking details'
      : 'Unable to load booking details'
    toast.error(message)
  } finally {
    loadingDetailsInviteId.value = null
  }
}

const closeBookingInviteDetails = () => {
  showDetailsModal.value = false
  bookingInviteDetails.value = null
}

const formatDetailsDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const formatPrice = (price: number | null) => {
  if (price === null || Number.isNaN(price)) {
    return 'N/A'
  }
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(price)
}

const getInviteStatusClass = (status: string) => {
  if (status === 'accepted') return 'accepted'
  if (status === 'rejected') return 'rejected'
  return 'pending'
}

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
  if (showDropdown.value) {
    fetchNotifications()
    nextTick(updateDropdownPosition)
  }
}

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'friend_request_received':
      return '🤝'
    case 'friend_request_result':
      return '💬'
    case 'booking_invite_received':
      return '🎫'
    case 'booking_invite_result':
      return '📨'
    case 'request_created':
      return '📝'
    case 'request_approved':
      return '✅'
    case 'request_rejected':
      return '❌'
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

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (
    !target.closest('.notification-bell-container') &&
    !target.closest('.notification-dropdown')
  ) {
    showDropdown.value = false
  }
}

onMounted(() => {
  fetchNotifications()
  pollingInterval = setInterval(fetchNotifications, 30000)
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('resize', updateDropdownPosition)
  window.addEventListener('scroll', updateDropdownPosition, true)
})

onUnmounted(() => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
  }
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', updateDropdownPosition)
  window.removeEventListener('scroll', updateDropdownPosition, true)
})
</script>

<template>
  <div class="notification-bell-container">
    <button
      ref="triggerRef"
      class="notification-bell"
      :class="{ active: showDropdown }"
      @click="toggleDropdown"
    >
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

    <Teleport to="body">
      <transition name="dropdown">
        <div v-if="showDropdown" class="notification-dropdown" :style="dropdownStyle">
          <div class="dropdown-header">
            <h3>Notifications</h3>
            <button v-if="unreadCount > 0" class="mark-all-btn" @click="markAllAsRead">
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
                  <div v-if="canShowFriendRequestActions(notification)" class="actions">
                    <button
                      type="button"
                      class="action-btn accept"
                      :disabled="processingFriendRequestId === notification.related_id"
                      @click.stop="respondFriendRequest(notification, 'accept')"
                    >
                      Accept
                    </button>
                    <button
                      type="button"
                      class="action-btn reject"
                      :disabled="processingFriendRequestId === notification.related_id"
                      @click.stop="respondFriendRequest(notification, 'reject')"
                    >
                      Reject
                    </button>
                  </div>
                  <div v-if="canShowBookingInviteActions(notification)" class="actions">
                    <button
                      type="button"
                      class="action-btn details"
                      :disabled="loadingDetailsInviteId === notification.related_id"
                      @click.stop="openBookingInviteDetails(notification)"
                    >
                      {{
                        loadingDetailsInviteId === notification.related_id
                          ? 'Loading...'
                          : 'Details'
                      }}
                    </button>
                    <button
                      type="button"
                      class="action-btn accept"
                      :disabled="processingBookingInviteId === notification.related_id"
                      @click.stop="respondBookingInvite(notification, 'accept')"
                    >
                      Accept
                    </button>
                    <button
                      type="button"
                      class="action-btn reject"
                      :disabled="processingBookingInviteId === notification.related_id"
                      @click.stop="respondBookingInvite(notification, 'reject')"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            </template>

            <div v-else class="empty-state">
              <p>No notifications</p>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>

    <Teleport to="body">
      <transition name="dropdown">
        <div
          v-if="showDetailsModal"
          class="details-overlay"
          @click.self="closeBookingInviteDetails"
        >
          <div class="details-modal" v-if="bookingInviteDetails">
            <div class="details-header">
              <div class="details-title-block">
                <span class="details-kicker">INVITATION DETAILS</span>
                <h3>Booking Invite</h3>
                <p class="details-subtitle">Review full booking information before you respond.</p>
              </div>
              <button type="button" class="details-close" @click="closeBookingInviteDetails">
                Close
              </button>
            </div>

            <div class="details-top-row">
              <div class="details-pill code">Code: {{ bookingInviteDetails.code }}</div>
              <div
                class="details-pill status"
                :class="getInviteStatusClass(bookingInviteDetails.status)"
              >
                {{ bookingInviteDetails.status }}
              </div>
            </div>

            <div class="details-section">
              <h4>Booking</h4>
              <div class="details-grid">
                <div class="details-item wide">
                  <span class="label">Court</span>
                  <strong>{{ bookingInviteDetails.court_name }}</strong>
                </div>
                <div class="details-item wide">
                  <span class="label">Location</span>
                  <strong>{{ bookingInviteDetails.location }}</strong>
                </div>
                <div class="details-item">
                  <span class="label">Date</span>
                  <strong>{{ formatDetailsDate(bookingInviteDetails.booking_date) }}</strong>
                </div>
                <div class="details-item">
                  <span class="label">Time</span>
                  <strong
                    >{{ bookingInviteDetails.start_time }} -
                    {{ bookingInviteDetails.end_time }}</strong
                  >
                </div>
                <div class="details-item">
                  <span class="label">Total Price</span>
                  <strong>{{ formatPrice(bookingInviteDetails.total_price) }}</strong>
                </div>
              </div>
            </div>

            <div class="details-section">
              <h4>People</h4>
              <div class="people-grid">
                <div class="person-card inviter">
                  <span class="role">Inviter</span>
                  <strong>{{ bookingInviteDetails.inviter_name }}</strong>
                </div>
                <div class="person-card invitee">
                  <span class="role">Invitee</span>
                  <strong>{{ bookingInviteDetails.invitee_name || 'Pending' }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<style scoped>
.notification-bell-container {
  position: relative;
  z-index: 1;
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
  border-color: #2d5016;
  background: #f0fdf4;
}

.notification-bell svg {
  width: 24px;
  height: 24px;
  color: #374151;
}

.notification-bell:hover svg,
.notification-bell.active svg {
  color: #2d5016;
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
  max-height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  z-index: 20000;
  overflow: hidden;
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

.actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.action-btn {
  border: none;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-btn.accept {
  background: #dcfce7;
  color: #166534;
}

.action-btn.reject {
  background: #fee2e2;
  color: #991b1b;
}

.action-btn.details {
  background: #dbeafe;
  color: #1d4ed8;
}

.details-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30000;
  padding: 20px;
}

.details-modal {
  width: min(620px, 100%);
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 18px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.details-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.details-kicker {
  display: inline-block;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 700;
  color: #1d4ed8;
}

.details-header h3 {
  margin: 0;
  color: #0f172a;
  font-size: 1.3rem;
}

.details-subtitle {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 0.9rem;
}

.details-close {
  border: none;
  border-radius: 10px;
  padding: 8px 12px;
  background: #eef2ff;
  color: #3730a3;
  font-weight: 700;
  cursor: pointer;
}

.details-top-row {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.details-pill {
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.details-pill.code {
  background: #dbeafe;
  color: #1d4ed8;
}

.details-pill.status {
  background: #e5e7eb;
  color: #334155;
}

.details-pill.status.accepted {
  background: #dcfce7;
  color: #166534;
}

.details-pill.status.rejected {
  background: #fee2e2;
  color: #991b1b;
}

.details-pill.status.pending {
  background: #fef3c7;
  color: #92400e;
}

.details-section {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px;
  background: white;
}

.details-section + .details-section {
  margin-top: 10px;
}

.details-section h4 {
  margin: 0 0 10px;
  color: #1f2937;
  font-size: 0.98rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 14px;
}

.details-item {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px;
  background: #f8fafc;
}

.details-item.wide {
  grid-column: 1 / -1;
}

.details-item .label {
  display: block;
  color: #64748b;
  font-size: 0.76rem;
  margin-bottom: 4px;
}

.details-item strong {
  color: #0f172a;
  font-size: 0.92rem;
}

.people-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.person-card {
  border-radius: 10px;
  padding: 10px;
  border: 1px solid #e5e7eb;
}

.person-card.inviter {
  background: #f0f9ff;
  border-color: #bae6fd;
}

.person-card.invitee {
  background: #fefce8;
  border-color: #fde68a;
}

.person-card .role {
  display: block;
  color: #64748b;
  font-size: 0.76rem;
  margin-bottom: 4px;
}

.person-card strong {
  color: #0f172a;
}

@media (max-width: 768px) {
  .details-grid {
    grid-template-columns: 1fr;
  }

  .details-item.wide {
    grid-column: auto;
  }

  .people-grid {
    grid-template-columns: 1fr;
  }
}

.empty-state {
  padding: 30px 20px;
  text-align: center;
  color: #9ca3af;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
