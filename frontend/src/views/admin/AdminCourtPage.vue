<template>
  <AdminDashboardLayout>
    <template #title>Courts Management</template>

    <div class="court-page">
      <!-- Stats Row -->
      <div class="stats-row">
        <div class="stat-item">
          <div class="stat-icon green">
            <img src="/logo-pickball.webp" alt="Court" class="court-public-icon stat" />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ totalCourts }}</div>
            <div class="stat-label">Total Courts</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon blue">✓</div>
          <div class="stat-info">
            <div class="stat-value">{{ activeCourts }}</div>
            <div class="stat-label">Active</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon orange">⏸️</div>
          <div class="stat-info">
            <div class="stat-value">{{ inactiveCourts }}</div>
            <div class="stat-label">Inactive</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon purple">📈</div>
          <div class="stat-info">
            <div class="stat-value">+{{ courtsThisMonth }}</div>
            <div class="stat-label">This Month</div>
          </div>
        </div>
      </div>

      <div class="court-table-card">
        <div class="card-header">
          <h2 class="card-title">
            <img src="/logo-pickball.webp" alt="Court" class="court-public-icon title" />
            <span>All Courts</span>
          </h2>
          <div class="card-actions">
            <button class="filter-btn">
              <span>🔍</span>
              <span>Filter</span>
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="loading-container">
          <div class="spinner"></div>
          <p>Loading courts...</p>
        </div>

        <!-- Courts Table -->
        <table v-else-if="courts.length > 0" class="court-table">
          <thead>
            <tr>
              <th>Court Name</th>
              <th>Location</th>
              <th>Phone Number</th>
              <th>Courts</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="court in paginatedCourts" :key="court.id" class="table-row">
              <td>
                <div class="court-name">
                  <div class="court-icon-wrapper">
                    <img src="/logo-pickball.webp" alt="Court" class="court-public-icon table" />
                  </div>
                  <div class="court-details">
                    <div class="name">{{ court.name }}</div>
                    <div class="court-type">{{ court.court_quantity }} courts available</div>
                  </div>
                </div>
              </td>
              <td>
                <div class="location-text">
                  <img src="/images.png" alt="Location" class="location-icon-image" />
                  <span>{{ getLocation(court) }}</span>
                </div>
              </td>
              <td>
                <div class="phone-text">
                  <img src="/pngtree-phone.jpg" alt="Phone" class="phone-icon-image" />
                  <span>{{ court.contact_phone }}</span>
                </div>
              </td>
              <td>
                <div class="quantity-badge">
                  {{ court.court_quantity }}
                </div>
              </td>
              <td>
                <span
                  :class="['status-badge', court.is_active ? 'active' : 'inactive']"
                  @click="toggleCourtStatus(court)"
                  style="cursor: pointer"
                  :title="'Click to toggle status'"
                >
                  {{ getStatus(court) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="action-btn view-btn" title="View" @click="viewCourt(court.id)">
                    👁️
                  </button>
                  <button
                    class="action-btn delete-btn"
                    title="Delete"
                    @click="confirmDelete(court)"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- No Courts State -->
        <div v-else class="no-courts">
          <p>No courts found.</p>
        </div>

        <!-- Pagination -->
        <div v-if="courts.length > itemsPerPage" class="pagination">
          <button class="page-btn prev-btn" @click="previousPage" :disabled="currentPage === 1">
            ‹
          </button>
          <button
            v-for="page in totalPages"
            :key="page"
            class="page-btn"
            :class="{ active: page === currentPage }"
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

      <!-- Court Details Modal -->
      <transition name="modal">
        <div v-if="showModal" class="modal-overlay" @click="closeModal">
          <div class="modal-container" @click.stop>
            <div class="modal-header">
              <h2>Court Details</h2>
              <button class="modal-close-btn" @click="closeModal">✕</button>
            </div>

            <div v-if="selectedCourt" class="modal-body">
              <!-- Basic Info -->
              <div class="info-section">
                <h3 class="section-title">Basic Information</h3>
                <div class="info-grid">
                  <div class="info-item">
                    <label>Court Name</label>
                    <p>{{ selectedCourt.name }}</p>
                  </div>
                  <div class="info-item">
                    <label>Number of Courts</label>
                    <p>{{ selectedCourt.court_quantity }}</p>
                  </div>
                  <div class="info-item">
                    <label>Address</label>
                    <p>{{ selectedCourt.address }}</p>
                  </div>
                  <div class="info-item">
                    <label>Ward</label>
                    <p>Ward {{ selectedCourt.ward }}</p>
                  </div>
                  <div class="info-item">
                    <label>City</label>
                    <p>{{ selectedCourt.city }}</p>
                  </div>
                  <div class="info-item">
                    <label>Opening Hours</label>
                    <p>{{ selectedCourt.opening_time }} - {{ selectedCourt.closing_time }}</p>
                  </div>
                </div>

                <div class="info-item full-width">
                  <label>Description</label>
                  <p>{{ selectedCourt.description || 'No description' }}</p>
                </div>
              </div>

              <!-- Contact Info -->
              <div class="info-section">
                <h3 class="section-title">Contact Information</h3>
                <div class="info-grid">
                  <div class="info-item">
                    <label>Phone Number</label>
                    <p>{{ selectedCourt.contact_phone }}</p>
                  </div>
                  <div class="info-item">
                    <label>Email</label>
                    <p>{{ selectedCourt.contact_email || 'N/A' }}</p>
                  </div>
                </div>
              </div>

              <!-- Facilities -->
              <div
                class="info-section"
                v-if="selectedCourt.facilities && selectedCourt.facilities.length > 0"
              >
                <h3 class="section-title">Amenities</h3>
                <div class="facilities-list">
                  <span
                    v-for="facility in selectedCourt.facilities"
                    :key="facility"
                    class="facility-badge"
                  >
                    {{ getFacilityLabel(facility) }}
                  </span>
                </div>
              </div>

              <!-- Time Slots -->
              <div
                class="info-section"
                v-if="selectedCourt.time_slots && selectedCourt.time_slots.length > 0"
              >
                <h3 class="section-title">Time Slots & Pricing</h3>
                <div class="time-slots-list">
                  <div
                    v-for="(slot, index) in selectedCourt.time_slots"
                    :key="index"
                    class="time-slot-item"
                  >
                    <span class="time-range">{{ slot.start_time }} - {{ slot.end_time }}</span>
                    <span class="price">{{ formatPrice(slot.price) }}</span>
                  </div>
                </div>
              </div>

              <!-- Images -->
              <div
                class="info-section"
                v-if="selectedCourt.images && selectedCourt.images.length > 0"
              >
                <h3 class="section-title">Images</h3>
                <div class="images-grid">
                  <img
                    v-for="(image, index) in selectedCourt.images"
                    :key="index"
                    :src="resolveImageUrl(image)"
                    :alt="`Court image ${index + 1}`"
                    class="court-image"
                  />
                </div>
              </div>

              <!-- Status -->
              <div class="info-section">
                <h3 class="section-title">Status</h3>
                <div class="info-grid">
                  <div class="info-item">
                    <label>Status</label>
                    <span
                      :class="['status-badge', selectedCourt.is_active ? 'active' : 'inactive']"
                    >
                      {{ getStatus(selectedCourt) }}
                    </span>
                  </div>
                  <div class="info-item">
                    <label>Created Date</label>
                    <p>{{ new Date(selectedCourt.created_at).toLocaleDateString('en-GB') }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn-close" @click="closeModal">Close</button>
            </div>
          </div>
        </div>
      </transition>

      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>⚠️ Confirm Deletion</h2>
            <button class="close-btn" @click="closeDeleteModal">✕</button>
          </div>
          <div class="modal-body">
            <p>
              Are you sure you want to delete court <strong>{{ courtToDelete?.name }}</strong
              >?
            </p>
            <p class="warning-text">This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="closeDeleteModal">Cancel</button>
            <button class="confirm-delete-btn" @click="deleteCourt" :disabled="isDeleting">
              {{ isDeleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </AdminDashboardLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AdminDashboardLayout from '@/layouts/AdminDashboardLayout.vue'
import axiosInstance from '@/utils/axios'

const backendOrigin = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(
  /\/api\/?$/,
  '',
)

const resolveImageUrl = (imagePath: string) => {
  if (!imagePath) return ''
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) return imagePath
  if (imagePath.startsWith('/')) return `${backendOrigin}${imagePath}`
  return `${backendOrigin}/${imagePath}`
}

interface TimeSlot {
  start_time: string
  end_time: string
  price: number
}

interface Court {
  id: number
  name: string
  address: string
  ward: string
  city: string
  description: string
  court_quantity: number
  opening_time: string
  closing_time: string
  images: string[]
  is_active: boolean
  owner_id: number
  facilities?: string[]
  time_slots?: TimeSlot[]
  contact_phone: string
  contact_email?: string
  created_at: string
  updated_at?: string
}

const courts = ref<Court[]>([])
const isLoading = ref(false)
const showModal = ref(false)
const selectedCourt = ref<Court | null>(null)

// Delete modal state
const showDeleteModal = ref(false)
const courtToDelete = ref<Court | null>(null)
const isDeleting = ref(false)

// Pagination
const currentPage = ref(1)
const itemsPerPage = 5

// Fetch courts from API
const fetchCourts = async () => {
  isLoading.value = true
  try {
    const response = await axiosInstance.get('/courts')
    courts.value = response.data
  } catch (error) {
    console.error('Error fetching courts:', error)
  } finally {
    isLoading.value = false
  }
}

// Calculate stats from real data
const totalCourts = computed(() => courts.value.length)

const activeCourts = computed(() => courts.value.filter((court) => court.is_active).length)

const inactiveCourts = computed(() => courts.value.filter((court) => !court.is_active).length)

// Calculate courts added this month
const courtsThisMonth = computed(() => {
  const now = new Date()
  const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)

  return courts.value.filter((court) => {
    const createdAt = new Date(court.created_at)
    return createdAt >= firstDayOfMonth
  }).length
})

// Pagination computed
const totalPages = computed(() => Math.ceil(courts.value.length / itemsPerPage))

const paginatedCourts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return courts.value.slice(start, end)
})

// Format location
const getLocation = (court: Court) => {
  return `${court.address}, Ward ${court.ward}, ${court.city}`
}

// Get status text
const getStatus = (court: Court) => {
  return court.is_active ? 'Active' : 'Inactive'
}

// View court details in modal
const viewCourt = (courtId: number) => {
  selectedCourt.value = courts.value.find((c) => c.id === courtId) || null
  if (selectedCourt.value) {
    showModal.value = true
  }
}

// Close modal
const closeModal = () => {
  showModal.value = false
  selectedCourt.value = null
}

// Format price
const formatPrice = (price: number) => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(price)
}

// Get facility label
const getFacilityLabel = (facility: string) => {
  const labels: Record<string, string> = {
    parking: 'Parking',
    wifi: 'Free WiFi',
    shower: 'Shower',
    locker: 'Locker',
    drinks: 'Drinks',
    equipment: 'Equipment Rental',
  }
  return labels[facility] || facility
}

// Delete court functions
const confirmDelete = (court: Court) => {
  courtToDelete.value = court
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  courtToDelete.value = null
}

const deleteCourt = async () => {
  if (!courtToDelete.value) return

  isDeleting.value = true

  try {
    await axiosInstance.delete(`/courts/${courtToDelete.value.id}`)
    alert('Court deleted successfully')
    closeDeleteModal()
    fetchCourts() // Refresh list
  } catch (error) {
    console.error('Error deleting court:', error)
    alert('Unable to delete court')
  } finally {
    isDeleting.value = false
  }
}

// Toggle court status
const toggleCourtStatus = async (court: Court) => {
  try {
    await axiosInstance.put(`/courts/${court.id}`, {
      ...court,
      is_active: !court.is_active,
    })
    alert('Court status updated successfully')
    fetchCourts() // Refresh list
  } catch (error) {
    console.error('Error updating court status:', error)
    alert('Failed to update court status')
  }
}

// Pagination methods
const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

onMounted(() => {
  fetchCourts()
})
</script>

<style scoped>
.court-page {
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
.court-table-card {
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
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.court-public-icon {
  object-fit: contain;
  display: block;
}

.court-public-icon.stat {
  width: 26px;
  height: 26px;
}

.court-public-icon.title {
  width: 24px;
  height: 24px;
}

.court-public-icon.table {
  width: 22px;
  height: 22px;
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

/* Table */
.court-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-bottom: 28px;
}

.court-table thead {
  background: #f9fafb;
}

.court-table th {
  text-align: left;
  padding: 16px 20px;
  font-size: 13px;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e5e7eb;
}

.court-table tbody .table-row {
  border-bottom: 1px solid #f3f4f6;
  transition: all 0.2s ease;
}

.court-table tbody .table-row:hover {
  background: #f9fafb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.court-table tbody .table-row:last-child {
  border-bottom: none;
}

.court-table td {
  padding: 20px;
  font-size: 15px;
  color: #1f2937;
  vertical-align: middle;
}

.court-name {
  display: flex;
  align-items: center;
  gap: 14px;
}

.court-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25);
}

.court-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.court-details .name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1;
}

.court-type {
  display: inline-block;
  padding: 3px 10px;
  background: #d1fae5;
  color: #065f46;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  width: fit-content;
}

.location-text,
.phone-text {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #6b7280;
  font-size: 14px;
}

.location-text span:last-child,
.phone-text span:last-child {
  word-wrap: break-word;
  max-width: 300px;
}

.location-icon,
.phone-icon {
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
}

.location-icon-image {
  width: 16px;
  height: 16px;
  object-fit: contain;
  border-radius: 4px;
  flex-shrink: 0;
  margin-top: 2px;
}

.phone-icon-image {
  width: 16px;
  height: 16px;
  object-fit: contain;
  border-radius: 4px;
  flex-shrink: 0;
  margin-top: 2px;
}

.status-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  transition: all 0.3s ease;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.active:hover {
  background: #a7f3d0;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.inactive:hover {
  background: #fecaca;
}

/* Quantity Badge */
.quantity-badge {
  display: inline-block;
  padding: 6px 12px;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-container p {
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
}

/* No Courts State */
.no-courts {
  text-align: center;
  padding: 60px 20px;
  color: #9ca3af;
  font-size: 14px;
  font-weight: 500;
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

.view-btn:hover {
  background: #dbeafe;
  border-color: #3b82f6;
}

.edit-btn:hover {
  background: #fef3c7;
  border-color: #f59e0b;
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
  gap: 6px;
  padding-top: 24px;
  margin-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.page-btn {
  min-width: 40px;
  height: 40px;
  border: 1.5px solid #e5e7eb;
  background: #fff;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.page-btn.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-color: #3b82f6;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-dots {
  color: #9ca3af;
  font-weight: 600;
  padding: 0 8px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  overflow-y: auto;
}

.modal-container {
  background: white;
  border-radius: 20px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 32px;
  border-bottom: 2px solid #f3f4f6;
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
  border-radius: 20px 20px 0 0;
}

.modal-header h2 {
  font-size: 24px;
  font-weight: 800;
  color: #1f2937;
  margin: 0;
}

.modal-close-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #f3f4f6;
  color: #6b7280;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
  transform: rotate(90deg);
}

.modal-body {
  padding: 32px;
}

.info-section {
  margin-bottom: 32px;
}

.info-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #f3f4f6;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item p {
  font-size: 15px;
  color: #1f2937;
  margin: 0;
  font-weight: 500;
  line-height: 1.6;
}

.facilities-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.facility-badge {
  padding: 8px 16px;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.time-slots-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
}

.time-slot-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  transition: all 0.3s;
}

.time-slot-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.time-range {
  font-size: 14px;
  font-weight: 600;
  color: #4b5563;
}

.price {
  font-size: 15px;
  font-weight: 700;
  color: #059669;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.court-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 12px;
  border: 2px solid #e5e7eb;
  transition: all 0.3s;
}

.court-image:hover {
  transform: scale(1.05);
  border-color: #3b82f6;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 24px 32px;
  border-top: 2px solid #f3f4f6;
  background: #f9fafb;
  border-radius: 0 0 20px 20px;
  position: sticky;
  bottom: 0;
}

.btn-close {
  padding: 12px 32px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-close:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  color: #1f2937;
}

/* Modal Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container,
.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container,
.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.9);
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

/* Delete Modal Styles */
.modal-content {
  background: #fff;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

.modal-content .modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 32px;
  border-bottom: 2px solid #f3f4f6;
}

.modal-content .modal-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.modal-content .modal-body {
  padding: 24px 32px;
}

.modal-content .modal-body p {
  font-size: 15px;
  color: #374151;
  margin: 0 0 12px 0;
  line-height: 1.6;
}

.modal-content .modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px 32px;
  border-top: 2px solid #f3f4f6;
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

.warning-text {
  color: #ef4444;
  font-weight: 600;
  font-size: 14px;
  margin-top: 8px;
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

@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .card-header h2 {
    font-size: 1.35rem;
  }

  .court-table {
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

  .court-table {
    font-size: 13px;
    min-width: 720px;
  }

  .court-table th,
  .court-table td {
    padding: 10px 8px;
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

  .court-table {
    font-size: 12px;
    min-width: 640px;
  }

  .court-table th,
  .court-table td {
    padding: 8px 6px;
  }
}
</style>
