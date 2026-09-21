<template>
  <AdminDashboardLayout>
    <template #title>Users Management</template>

    <div class="users-page">
      <!-- Stats Row -->
      <div class="stats-row">
        <div class="stat-item">
          <div class="stat-icon blue">👥</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalUsers }}</div>
            <div class="stat-label">Total Users</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon green">✓</div>
          <div class="stat-info">
            <div class="stat-value">{{ activeUsers }}</div>
            <div class="stat-label">Active</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon orange">👤</div>
          <div class="stat-info">
            <div class="stat-value">{{ inactiveUsers }}</div>
            <div class="stat-label">Inactive</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon purple">📊</div>
          <div class="stat-info">
            <div class="stat-value">{{ users.length }}</div>
            <div class="stat-label">On This Page</div>
          </div>
        </div>
      </div>

      <div class="users-table-card">
        <div class="card-header">
          <h2 class="card-title">👥 All Users</h2>
          <div class="card-actions">
            <button class="filter-btn" @click="loadUsers">
              <span>🔄</span>
              <span>Refresh</span>
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading users...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error-state">
          <span class="error-icon">⚠️</span>
          <p>{{ error }}</p>
          <button class="retry-btn" @click="loadUsers">Retry</button>
        </div>

        <!-- Empty State -->
        <div v-else-if="users.length === 0" class="empty-state">
          <span class="empty-icon">👥</span>
          <p>No users found</p>
        </div>

        <!-- Users Table -->
        <div v-else>
          <table class="users-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Role</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="table-row">
                <td>
                  <div class="user-name">
                    <div class="user-avatar">
                      <span class="avatar-text">{{ getUserInitials(user.full_name) }}</span>
                    </div>
                    <div class="user-details">
                      <div class="name">{{ user.full_name }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="email-text">{{ user.email }}</span>
                </td>
                <td>
                  <span class="phone-text">{{ user.phone_number || 'N/A' }}</span>
                </td>
                <td>
                  <span :class="['role-tag', getRoleClass(user.role)]">{{
                    getRoleDisplay(user.role)
                  }}</span>
                </td>
                <td>
                  <span :class="['status-badge', user.is_active ? 'active' : 'inactive']">
                    {{ user.is_active ? '✓ Active' : '✗ Inactive' }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button
                      class="action-btn delete-btn"
                      title="Delete"
                      @click="confirmDelete(user)"
                      :disabled="user.role === 'admin'"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <div class="pagination" v-if="totalPages > 1">
            <button class="page-btn prev-btn" @click="prevPage" :disabled="currentPage === 1">
              ‹
            </button>
            <button
              v-for="page in totalPages"
              :key="page"
              class="page-btn"
              :class="{ active: currentPage === page }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
            <button
              class="page-btn next-btn"
              @click="nextPage"
              :disabled="currentPage === totalPages"
            >
              ›
            </button>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <transition name="modal">
        <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
          <div class="modal-content">
            <div class="modal-header">
              <h2>⚠️ Confirm Deletion</h2>
              <button class="close-btn" @click="closeDeleteModal">✕</button>
            </div>
            <div class="modal-body">
              <p>
                Are you sure you want to delete user
                <strong>{{ userToDelete?.full_name }}</strong
                >?
              </p>
              <p class="warning-text">This action cannot be undone.</p>
            </div>
            <div class="modal-footer">
              <button class="cancel-btn" @click="closeDeleteModal">Cancel</button>
              <button class="confirm-delete-btn" @click="deleteUser" :disabled="isDeleting">
                {{ isDeleting ? 'Deleting...' : 'Delete' }}
              </button>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </AdminDashboardLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AdminDashboardLayout from '@/layouts/AdminDashboardLayout.vue'
import axiosInstance from '@/utils/axios'

interface User {
  id: number
  email: string
  full_name: string
  phone_number?: string | null
  role: string
  is_active: boolean
}

const users = ref<User[]>([])
const total = ref(0)
const isLoading = ref(false)
const error = ref('')
const currentPage = ref(1)
const pageSize = ref(5)

// Delete modal state
const showDeleteModal = ref(false)
const userToDelete = ref<User | null>(null)
const isDeleting = ref(false)

// Computed
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const totalUsers = computed(() => total.value)
const activeUsers = computed(() => users.value.filter((u) => u.is_active).length)
const inactiveUsers = computed(() => users.value.filter((u) => !u.is_active).length)

// Functions
const getUserInitials = (fullName: string) => {
  const names = fullName.split(' ')
  if (names.length >= 2) {
    return (names[0][0] + names[names.length - 1][0]).toUpperCase()
  }
  return fullName.substring(0, 2).toUpperCase()
}

const getRoleDisplay = (role: string) => {
  const roleMap: Record<string, string> = {
    admin: 'Admin',
    user: 'User',
    owner: 'Owner',
    enterprise: 'Enterprise',
  }
  return roleMap[role] || role
}

const getRoleClass = (role: string) => {
  const classMap: Record<string, string> = {
    admin: 'role-admin',
    user: 'role-user',
    owner: 'role-owner',
    enterprise: 'role-enterprise',
  }
  return classMap[role] || 'role-user'
}

const loadUsers = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const response = await axiosInstance.get('/users', {
      params: {
        skip,
        limit: pageSize.value,
      },
    })

    if (response.data) {
      // Backend đã lọc bỏ admin rồi, chỉ cần hiển thị
      users.value = response.data.users
      total.value = response.data.total
      console.log('✅ Loaded users (excluding admins):', users.value.length)
    }
  } catch (err: unknown) {
    console.error('❌ Load users error:', err)
    error.value = 'Failed to load users. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const goToPage = (page: number) => {
  currentPage.value = page
  loadUsers()
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadUsers()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadUsers()
  }
}

const confirmDelete = (user: User) => {
  userToDelete.value = user
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  userToDelete.value = null
}

const deleteUser = async () => {
  if (!userToDelete.value) return

  isDeleting.value = true

  try {
    await axiosInstance.delete(`/users/${userToDelete.value.id}`)
    console.log('✅ User deleted successfully')

    // Reload users
    await loadUsers()

    closeDeleteModal()
  } catch (err: unknown) {
    console.error('❌ Delete user error:', err)
    alert('Failed to delete user. Please try again.')
  } finally {
    isDeleting.value = false
  }
}

// Load users on mount
onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-page {
  max-width: 1400px;
  margin: 0 auto;
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 28px;
}

.stat-item {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
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

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #1f2937;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
}

/* Table Card */
.users-table-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  overflow-x: auto;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f3f4f6;
}

.card-title {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: #f3f4f6;
  color: #374151;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}

/* Loading, Error, Empty States */
.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f4f6;
  border-top-color: #4169e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p,
.error-state p,
.empty-state p {
  font-size: 16px;
  color: #6b7280;
  margin: 10px 0;
}

.error-icon,
.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.retry-btn {
  margin-top: 16px;
  padding: 10px 20px;
  background: #4169e1;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.retry-btn:hover {
  background: #3155c4;
}

/* Table */
.users-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-bottom: 28px;
}

.users-table thead {
  background: #f9fafb;
}

.users-table th {
  text-align: left;
  padding: 16px 20px;
  font-size: 13px;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e5e7eb;
}

.users-table tbody .table-row {
  border-bottom: 1px solid #f3f4f6;
  transition: all 0.2s ease;
}

.users-table tbody .table-row:hover {
  background: #f9fafb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.users-table tbody .table-row:last-child {
  border-bottom: none;
}

.users-table td {
  padding: 20px;
  font-size: 15px;
  color: #1f2937;
  vertical-align: middle;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 14px;
}

.user-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #4169e1 0%, #5a7fee 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(65, 105, 225, 0.25);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-details .name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1;
}

.role-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  width: fit-content;
}

.role-tag.role-admin {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
}

.role-tag.role-user {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
}

.role-tag.role-owner {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
}

.role-tag.role-enterprise {
  background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%);
  color: #6b21a8;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
}

.status-badge.active {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
}

.status-badge.inactive {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #991b1b;
}

.email-text,
.phone-text {
  color: #6b7280;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1.5px solid #e5e7eb;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.delete-btn:hover:not(:disabled) {
  background: #fee2e2;
  border-color: #ef4444;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding-top: 8px;
}

.page-btn {
  min-width: 40px;
  height: 40px;
  border: 1.5px solid #e5e7eb;
  background: #fff;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  color: #6b7280;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #d1d5db;
  color: #374151;
}

.page-btn.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-color: #3b82f6;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  padding: 0 16px;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
}

/* Modal */
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

.modal-content {
  background: #fff;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
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
  font-size: 20px;
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
}

.close-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.modal-body {
  padding: 24px 32px;
}

.modal-body p {
  font-size: 15px;
  color: #374151;
  margin: 0 0 12px 0;
  line-height: 1.6;
}

.warning-text {
  color: #ef4444;
  font-weight: 600;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px 32px;
  border-top: 2px solid #f3f4f6;
}

.cancel-btn,
.confirm-delete-btn {
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

.confirm-delete-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.confirm-delete-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
}

.confirm-delete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modal Animation */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.9);
}

@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .card-header h2 {
    font-size: 1.35rem;
  }

  .users-table {
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 1.75rem;
  }

  .stat-label {
    font-size: 0.85rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .card-header h2 {
    font-size: 1.25rem;
  }

  .card-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .filter-btn,
  .refresh-btn {
    flex: 1;
    min-width: 120px;
  }

  .users-table {
    font-size: 13px;
    min-width: 720px;
  }

  .users-table th,
  .users-table td {
    padding: 10px 8px;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
    font-size: 12px;
  }

  .user-name {
    font-size: 0.9rem;
  }

  .user-email {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.5rem;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .stat-label {
    font-size: 0.8rem;
  }

  .card-header h2 {
    font-size: 1.1rem;
  }

  .filter-btn,
  .refresh-btn {
    font-size: 0.85rem;
    padding: 8px 14px;
  }

  .users-table {
    font-size: 12px;
    min-width: 640px;
  }

  .users-table th,
  .users-table td {
    padding: 8px 6px;
  }

  .user-avatar {
    width: 32px;
    height: 32px;
    font-size: 11px;
  }
}
</style>
