<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from '@/utils/axios'
import { useToast } from 'vue-toastification'
import type { AxiosError } from 'axios'

const toast = useToast()

interface Advertisement {
  id: number
  name: string
  description: string
  image_url: string
  detail_url: string
  click_count?: number
  created_at: string
  updated_at: string
}

const advertisements = ref<Advertisement[]>([])
const pendingCount = ref(0)
const isLoading = ref(true)
const error = ref<string>('')
const deleteConfirmId = ref<number | null>(null)
const isDeleting = ref(false)
const backendBaseUrl = String(axios.defaults.baseURL || '').replace(/\/api\/?$/, '')

const loadAdvertisements = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const [approvedResponse, requestResponse] = await Promise.all([
      axios.get('/enterprise/advertisements'),
      axios.get('/enterprise/advertisement-requests'),
    ])

    advertisements.value = approvedResponse.data.data || approvedResponse.data || []

    const requests = requestResponse.data.data || requestResponse.data || []
    pendingCount.value = requests.filter(
      (item: { status?: string }) => item.status === 'pending',
    ).length
  } catch (err) {
    const error_msg =
      (err as AxiosError<{ detail: string }>)?.response?.data?.detail ||
      (err as Error)?.message ||
      'Failed to load advertisements'
    error.value = error_msg
    toast.error(error_msg)
  } finally {
    isLoading.value = false
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const resolveImageUrl = (imageUrl: string) => {
  if (!imageUrl) return ''
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) return imageUrl
  if (backendBaseUrl) return `${backendBaseUrl}${imageUrl}`
  return imageUrl
}

const openDetailUrl = (url: string) => {
  if (!url) return
  window.open(url, '_blank', 'noopener,noreferrer')
}

const openDeleteConfirm = (id: number) => {
  deleteConfirmId.value = id
}

const closeDeleteConfirm = () => {
  deleteConfirmId.value = null
}

const handleDelete = async (id: number) => {
  isDeleting.value = true

  try {
    await axios.delete(`/enterprise/advertisements/${id}`)
    toast.success('Advertisement deleted successfully!')
    closeDeleteConfirm()
    await loadAdvertisements()
  } catch (err) {
    const error_msg =
      (err as AxiosError<{ detail: string }>)?.response?.data?.detail ||
      (err as Error)?.message ||
      'Failed to delete advertisement'
    toast.error(error_msg)
  } finally {
    isDeleting.value = false
  }
}

onMounted(() => {
  loadAdvertisements()
})
</script>

<template>
  <div class="list-page">
    <div class="page-header">
      <div>
        <h2>Advertisements</h2>
        <p>Approved advertisements are shown here</p>
        <p v-if="pendingCount > 0" class="pending-note">
          You have {{ pendingCount }} advertisement request(s) waiting for admin approval.
        </p>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      {{ error }}
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading advertisements...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="advertisements.length === 0" class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
        />
      </svg>
      <p>No advertisements yet</p>
      <span class="empty-text">Start by uploading your first advertisement</span>
      <router-link to="/enterprise/advertisements/upload" class="btn btn-primary">
        Upload Advertisement
      </router-link>
    </div>

    <!-- Advertisements Table -->
    <div v-else class="table-wrap">
      <table class="ads-table">
        <thead>
          <tr>
            <th>Image</th>
            <th>Name</th>
            <th>Description</th>
            <th>Visits</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ad in advertisements" :key="ad.id">
            <td>
              <img :src="resolveImageUrl(ad.image_url)" :alt="ad.name" class="table-thumb" />
            </td>
            <td class="ad-name">{{ ad.name }}</td>
            <td class="ad-description">{{ ad.description }}</td>
            <td>
              <span class="clicks">{{ ad.click_count || 0 }}</span>
            </td>
            <td>{{ formatDate(ad.created_at) }}</td>
            <td>
              <div class="ad-actions">
                <button class="btn-details" @click="openDetailUrl(ad.detail_url)">Details</button>
                <button class="btn-delete" @click="openDeleteConfirm(ad.id)">
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
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Delete Confirmation Modal -->
      <teleport to="body">
        <div v-if="deleteConfirmId !== null" class="modal-overlay" @click="closeDeleteConfirm">
          <div class="modal-content" @click.stop>
            <h3>Delete Advertisement</h3>
            <p>This action cannot be undone.</p>
            <div class="modal-actions">
              <button class="btn btn-secondary" @click="closeDeleteConfirm" :disabled="isDeleting">
                Cancel
              </button>
              <button
                class="btn btn-danger"
                @click="deleteConfirmId !== null && handleDelete(deleteConfirmId)"
                :disabled="isDeleting"
              >
                <span v-if="isDeleting" class="spinner"></span>
                {{ isDeleting ? 'Deleting...' : 'Delete' }}
              </button>
            </div>
          </div>
        </div>
      </teleport>
    </div>
  </div>
</template>

<style scoped>
.list-page {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.page-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-header p {
  font-size: 16px;
  color: #64748b;
  margin: 0;
}

.pending-note {
  margin-top: 8px;
  font-size: 13px;
  color: #b45309;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 8px 12px;
  display: inline-block;
}

.error-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 14px;
}

.error-message svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-state svg,
.empty-state svg {
  width: 64px;
  height: 64px;
  color: #cbd5e1;
  margin-bottom: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(34, 197, 94, 0.1);
  border-radius: 50%;
  border-top-color: #22c55e;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p,
.empty-state p {
  font-size: 16px;
  color: #64748b;
  margin: 0 0 8px 0;
}

.empty-text {
  font-size: 14px;
  color: #94a3b8;
  margin-bottom: 24px;
}

.table-wrap {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  overflow: auto;
}

.ads-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 900px;
}

.ads-table thead th {
  text-align: left;
  padding: 14px;
  font-size: 12px;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.4px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.ads-table tbody td {
  padding: 14px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
  font-size: 14px;
  color: #1e293b;
}

.table-thumb {
  width: 84px;
  height: 56px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.ad-name {
  font-weight: 700;
}

.ad-description {
  color: #64748b;
  max-width: 360px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.clicks {
  font-size: 12px;
  color: #166534;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 999px;
  padding: 4px 12px;
  width: fit-content;
  margin: 0;
  font-weight: 600;
}

.ad-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-details {
  padding: 8px 14px;
  border-radius: 6px;
  border: 1px solid #86efac;
  background: #f0fdf4;
  color: #166534;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-details:hover {
  background: #dcfce7;
  border-color: #4ade80;
}

.btn-delete {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-delete:hover {
  background: #fecaca;
  transform: scale(1.05);
}

.btn-delete svg {
  width: 18px;
  height: 18px;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.btn-secondary {
  background: #f1f5f9;
  color: #1e293b;
  border: 1px solid #cbd5e1;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modal */
.modal-overlay {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 32px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15);
}

.modal-content h3 {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px 0;
}

.modal-content p {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 24px 0;
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

@media (max-width: 1024px) {
  .table-wrap {
    border-radius: 10px;
  }

  .ads-table {
    min-width: 760px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .ads-table {
    min-width: 640px;
  }

  .ads-table thead th,
  .ads-table tbody td {
    padding: 10px;
    font-size: 13px;
  }

  .ad-description {
    max-width: 220px;
  }

  .ad-actions {
    gap: 6px;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .modal-content {
    width: 95%;
  }
}

@media (max-width: 480px) {
  .ads-table {
    min-width: 560px;
  }

  .table-thumb {
    width: 64px;
    height: 44px;
  }
}
</style>
