<template>
  <AdminDashboardLayout>
    <template #title>Profile</template>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ editModalTitle }}</h2>
          <button class="close-btn" @click="closeEditModal">✕</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveChanges">
            <div v-if="editField === 'full_name'" class="form-group">
              <label>Full Name</label>
              <input v-model="editValue" type="text" placeholder="Enter your full name" required />
            </div>

            <div v-else-if="editField === 'email'" class="form-group">
              <label>Email Address</label>
              <input v-model="editValue" type="email" placeholder="Enter your email" required />
            </div>

            <div v-else-if="editField === 'phone_number'" class="form-group">
              <label>Phone Number</label>
              <input
                v-model="editValue"
                type="tel"
                placeholder="Enter your phone number"
                required
              />
            </div>

            <div v-else-if="editField === 'password'" class="form-group">
              <label>New Password</label>
              <input
                v-model="editValue"
                type="password"
                placeholder="Enter new password"
                required
                minlength="6"
              />
              <small>Password must be at least 6 characters</small>
            </div>

            <div v-if="updateError" class="error-message">{{ updateError }}</div>

            <div class="modal-actions">
              <button type="button" class="cancel-btn" @click="closeEditModal">Cancel</button>
              <button type="submit" class="save-btn" :disabled="isUpdating">
                {{ isUpdating ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div class="profile-page">
      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue">👥</div>
          <div class="stat-content">
            <div class="stat-value">{{ isLoadingStats ? '...' : totalUsers }}</div>
            <div class="stat-label">Total Users</div>
          </div>
          <div class="stat-trend up">{{ activeUsers + inactiveUsers }}</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon green">✓</div>
          <div class="stat-content">
            <div class="stat-value">{{ isLoadingStats ? '...' : activeUsers }}</div>
            <div class="stat-label">Active Users</div>
          </div>
          <div class="stat-trend up">
            {{
              isLoadingStats || totalUsers === 0
                ? '-'
                : Math.round((activeUsers / totalUsers) * 100) + '%'
            }}
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon orange">👤</div>
          <div class="stat-content">
            <div class="stat-value">{{ isLoadingStats ? '...' : inactiveUsers }}</div>
            <div class="stat-label">Inactive Users</div>
          </div>
          <div class="stat-trend">
            {{
              isLoadingStats || totalUsers === 0
                ? '-'
                : Math.round((inactiveUsers / totalUsers) * 100) + '%'
            }}
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon purple">
            <img src="/logo-pickball.webp" alt="Court" class="stat-icon-image" />
          </div>
          <div class="stat-content">
            <div class="stat-value">0</div>
            <div class="stat-label">Total Courts</div>
          </div>
          <div class="stat-trend">-</div>
        </div>
      </div>

      <!-- Profile Card -->
      <div class="profile-card">
        <div class="card-header">
          <h2 class="card-title">👤 Admin Profile</h2>
          <button class="edit-profile-btn">
            <span>✏️</span>
            <span>Edit Profile</span>
          </button>
        </div>

        <div class="profile-content">
          <div class="profile-avatar-section">
            <div class="avatar-container">
              <div class="avatar-circle">
                <span class="avatar-icon">{{ userInitials }}</span>
              </div>
            </div>
          </div>

          <div class="profile-info-section">
            <h1 class="profile-greeting">Hello {{ firstName }}! 👋</h1>
            <p class="profile-subtitle">Welcome back to your admin dashboard</p>

            <div class="info-grid">
              <div class="info-card">
                <div class="info-header">
                  <span class="info-icon">👤</span>
                  <span class="info-title">Full Name</span>
                </div>
                <div class="info-value">{{ authStore.user?.full_name || 'N/A' }}</div>
                <button class="info-edit-btn" @click="openEditModal('full_name', 'Edit Full Name')">
                  <span>✏️</span>
                </button>
              </div>

              <div class="info-card">
                <div class="info-header">
                  <img
                    src="/pngtree-email-icon-design-png-image_2413695.jpg"
                    alt="Email"
                    class="info-icon-image"
                  />
                  <span class="info-title">Email Address</span>
                </div>
                <div class="info-value">{{ authStore.user?.email || 'N/A' }}</div>
                <button class="info-edit-btn" @click="openEditModal('email', 'Edit Email')">
                  <span>✏️</span>
                </button>
              </div>

              <div class="info-card">
                <div class="info-header">
                  <img src="/pngtree-phone.jpg" alt="Phone" class="info-icon-image" />
                  <span class="info-title">Phone Number</span>
                </div>
                <div class="info-value">{{ authStore.user?.phone_number || 'Not set' }}</div>
                <button
                  class="info-edit-btn"
                  @click="openEditModal('phone_number', 'Edit Phone Number')"
                >
                  <span>✏️</span>
                </button>
              </div>

              <div class="info-card">
                <div class="info-header">
                  <img
                    src="/pngtree-vector-lock-icon-png-image_515444.jpg"
                    alt="Password"
                    class="info-icon-image"
                  />
                  <span class="info-title">Password</span>
                </div>
                <div class="info-value">••••••••••</div>
                <button class="info-edit-btn" @click="openEditModal('password', 'Change Password')">
                  <span>✏️</span>
                </button>
              </div>

              <div class="info-card">
                <div class="info-header">
                  <span class="info-icon">🛡️</span>
                  <span class="info-title">Role</span>
                </div>
                <div class="info-value">
                  <span class="role-badge">{{ getRoleDisplay(authStore.user?.role) }}</span>
                </div>
              </div>

              <div class="info-card">
                <div class="info-header">
                  <span class="info-icon">📅</span>
                  <span class="info-title">Account Status</span>
                </div>
                <div class="info-value">
                  <span
                    :class="['status-badge', authStore.user?.is_active ? 'active' : 'inactive']"
                  >
                    {{ authStore.user?.is_active ? '✓ Active' : '✗ Inactive' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Activity Card -->
      <div class="activity-card">
        <div class="card-header">
          <h2 class="card-title">📊 Recent Activity</h2>
          <a href="/admin/requests" class="view-all-link">View All →</a>
        </div>
        <div class="activity-list">
          <div v-if="isLoadingActivities" class="activity-empty">Loading recent activity...</div>
          <div v-else-if="recentActivities.length === 0" class="activity-empty">
            No recent activity yet.
          </div>
          <div
            v-else
            v-for="activity in recentActivities"
            :key="activity.key"
            class="activity-item"
          >
            <div class="activity-icon" :class="activity.color">{{ activity.icon }}</div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-time">{{ formatTimeAgo(activity.occurred_at) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminDashboardLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AdminDashboardLayout from '@/layouts/AdminDashboardLayout.vue'
import { useAuthStore } from '@/stores/auth'
import axiosInstance from '@/utils/axios'

const authStore = useAuthStore()

// Modal state
const showEditModal = ref(false)
const editField = ref('')
const editModalTitle = ref('')
const editValue = ref('')
const isUpdating = ref(false)
const updateError = ref('')

// Stats state
const totalUsers = ref(0)
const activeUsers = ref(0)
const inactiveUsers = ref(0)
const isLoadingStats = ref(false)
const recentActivities = ref<ActivityItem[]>([])
const isLoadingActivities = ref(false)

// Computed properties
const userInitials = computed(() => {
  const fullName = authStore.user?.full_name || 'Admin'
  const names = fullName.split(' ')
  if (names.length >= 2) {
    return (names[0][0] + names[names.length - 1][0]).toUpperCase()
  }
  return fullName.substring(0, 2).toUpperCase()
})

const firstName = computed(() => {
  const fullName = authStore.user?.full_name || 'Admin'
  return fullName.split(' ')[0]
})

const getRoleDisplay = (role?: string) => {
  const roleMap: Record<string, string> = {
    admin: 'Admin',
    user: 'User',
    owner: 'Owner',
    enterprise: 'Enterprise',
  }
  return roleMap[role || 'admin'] || 'Admin'
}

// Modal functions
const openEditModal = (field: string, title: string) => {
  editField.value = field
  editModalTitle.value = title
  updateError.value = ''

  // Set current value
  if (field === 'password') {
    editValue.value = ''
  } else if (field === 'full_name') {
    editValue.value = authStore.user?.full_name || ''
  } else if (field === 'email') {
    editValue.value = authStore.user?.email || ''
  } else if (field === 'phone_number') {
    editValue.value = authStore.user?.phone_number || ''
  }

  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editField.value = ''
  editValue.value = ''
  updateError.value = ''
}

const saveChanges = async () => {
  if (!authStore.user?.id) {
    updateError.value = 'User ID does not exist'
    return
  }

  isUpdating.value = true
  updateError.value = ''

  try {
    const updateData: Record<string, string> = {}
    updateData[editField.value] = editValue.value

    console.log('🔄 Updating field:', editField.value, 'with value:', editValue.value)
    console.log('📤 Update data:', updateData)

    const result = await authStore.updateProfile(authStore.user.id, updateData)

    console.log('📥 Result:', result)

    if (result.success) {
      closeEditModal()
      console.log('✅ Profile updated successfully')
    } else {
      updateError.value = result.error || 'Update failed'
    }
  } catch (error) {
    console.error('❌ Update error:', error)
    updateError.value = 'An error occurred. Please try again.'
  } finally {
    isUpdating.value = false
  }
}

// Interface for user
interface User {
  id: number
  email: string
  full_name: string
  role: string
  is_active: boolean
}

interface RecentActivityItem {
  type: string
  title: string
  description?: string
  occurred_at: string
  icon: string
  color: string
}

interface ActivityItem {
  key: string
  type: string
  title: string
  occurred_at: string
  icon: string
  color: 'blue' | 'green' | 'orange'
}

// Load statistics
const loadStats = async () => {
  console.log('🔄 Starting loadStats...')
  isLoadingStats.value = true

  try {
    console.log('📤 Calling API /users...')
    // Load tất cả users để tính toán chính xác
    // API đã lọc bỏ admin rồi
    const response = await axiosInstance.get('/users', {
      params: {
        skip: 0,
        limit: 100, // Backend giới hạn tối đa 100
      },
    })

    console.log('📥 API Response:', response.data)

    if (response.data) {
      const users: User[] = response.data.users
      const total = response.data.total

      console.log('Processing users:', users)

      totalUsers.value = total

      // Tính số lượng active và inactive từ danh sách users nhận được
      activeUsers.value = users.filter((u: User) => u.is_active).length
      inactiveUsers.value = users.filter((u: User) => !u.is_active).length

      console.log('✅ Stats loaded successfully:', {
        totalUsers: totalUsers.value,
        activeUsers: activeUsers.value,
        inactiveUsers: inactiveUsers.value,
        usersLength: users.length,
      })
    } else {
      console.warn('⚠️ No data in response')
    }
  } catch (error) {
    console.error('❌ Load stats error:', error)
    totalUsers.value = 0
    activeUsers.value = 0
    inactiveUsers.value = 0
  } finally {
    isLoadingStats.value = false
    console.log('✅ loadStats completed. Final values:', {
      totalUsers: totalUsers.value,
      activeUsers: activeUsers.value,
      inactiveUsers: inactiveUsers.value,
    })
  }
}

const formatTimeAgo = (value: string) => {
  const date = new Date(value)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()

  if (diffMs < 0) {
    return date.toLocaleString('vi-VN')
  }

  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  if (diffMinutes < 1) return 'Just now'
  if (diffMinutes < 60) return `${diffMinutes} minutes ago`

  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return `${diffHours} hours ago`

  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 30) return `${diffDays} days ago`

  return date.toLocaleDateString('vi-VN')
}

const loadRecentActivities = async () => {
  isLoadingActivities.value = true

  try {
    const response = await axiosInstance.get('/users/admin/recent-activity', {
      params: { limit: 8 },
    })

    const items: RecentActivityItem[] = response.data?.items || []
    recentActivities.value = items.map((item, index) => {
      const color = item.color === 'green' || item.color === 'orange' ? item.color : 'blue'
      return {
        key: `${item.type}-${item.occurred_at}-${index}`,
        type: item.type,
        title: item.title,
        occurred_at: item.occurred_at,
        icon: item.icon || '📌',
        color,
      }
    })
  } catch (error) {
    console.error('❌ Load recent activity error:', error)
    recentActivities.value = []
  } finally {
    isLoadingActivities.value = false
  }
}

// Load stats on mount
onMounted(() => {
  loadStats()
  loadRecentActivities()
})
</script>

<style scoped>
.profile-page {
  max-width: 1400px;
  margin: 0 auto;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.stat-icon-image {
  width: 28px;
  height: 28px;
  object-fit: contain;
  display: block;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.stat-icon.green {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.stat-icon.orange {
  background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
}

.stat-icon.purple {
  background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #1f2937;
  line-height: 1;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.stat-trend {
  font-size: 13px;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 8px;
  background: #f3f4f6;
  color: #6b7280;
}

.stat-trend.up {
  background: #d1fae5;
  color: #059669;
}

/* Profile Card */
.profile-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 32px;
  border: 1px solid #f0f0f0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f3f4f6;
}

.card-title {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.edit-profile-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #4169e1 0%, #5a7fee 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(65, 105, 225, 0.3);
}

.edit-profile-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(65, 105, 225, 0.4);
}

.profile-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 48px;
  align-items: start;
}

.profile-avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.avatar-circle {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);
  border: 6px solid #fff;
}

.avatar-icon {
  font-size: 90px;
}

.profile-info-section {
  flex: 1;
}

.profile-greeting {
  font-size: 36px;
  font-weight: 800;
  margin: 0 0 8px 0;
  color: #1f2937;
}

.profile-subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 0 0 32px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.info-card {
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  position: relative;
}

.info-card:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.info-icon {
  font-size: 20px;
}

.info-icon-image {
  width: 20px;
  height: 20px;
  object-fit: contain;
  border-radius: 4px;
  flex-shrink: 0;
}

.info-title {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  padding-right: 40px;
}

.role-badge {
  display: inline-block;
  padding: 6px 14px;
  background: linear-gradient(135deg, #4169e1 0%, #5a7fee 100%);
  color: #fff;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(65, 105, 225, 0.3);
}

.status-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
}

.status-badge.active {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.status-badge.inactive {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.info-edit-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 32px;
  height: 32px;
  background: #fff;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.info-edit-btn:hover {
  background: #f3f4f6;
  border-color: #4169e1;
  transform: scale(1.1);
}

/* Activity Card */
.activity-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
}

.view-all-link {
  color: #4169e1;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: color 0.3s ease;
}

.view-all-link:hover {
  color: #3155c4;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: #f3f4f6;
}

.activity-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.activity-icon-image {
  width: 22px;
  height: 22px;
  object-fit: contain;
  display: block;
}

.activity-icon.blue {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.activity-icon.green {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.activity-icon.orange {
  background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
}

.activity-content {
  flex: 1;
}

.activity-empty {
  padding: 18px;
  border-radius: 12px;
  background: #f9fafb;
  color: #6b7280;
  font-size: 14px;
}

.activity-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 13px;
  color: #6b7280;
}

@media (max-width: 1024px) {
  .profile-content {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .profile-greeting {
    font-size: 28px;
  }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 32px;
  border-bottom: 2px solid #f3f4f6;
}

.modal-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #f3f4f6;
  border-radius: 8px;
  font-size: 20px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.modal-body {
  padding: 32px;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  font-size: 15px;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-group input:focus {
  outline: none;
  border-color: #4169e1;
  box-shadow: 0 0 0 3px rgba(65, 105, 225, 0.1);
}

.form-group small {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
}

.error-message {
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn,
.save-btn {
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.save-btn {
  background: linear-gradient(135deg, #4169e1 0%, #5a7fee 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(65, 105, 225, 0.3);
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(65, 105, 225, 0.4);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
