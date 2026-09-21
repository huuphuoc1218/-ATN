<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axiosInstance from '@/utils/axios'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import { useToast } from 'vue-toastification'

const authStore = useAuthStore()
const toast = useToast()
const backendOrigin = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(
  /\/api\/?$/,
  '',
)

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
  contact_phone: string
  contact_email?: string
  created_at: string
  updated_at?: string
}

const router = useRouter()
const courts = ref<Court[]>([])
const isLoading = ref(false)
const searchQuery = ref('')
const selectedWard = ref<string>('')
const selectedBookingDate = ref('')
const selectedStartTime = ref('')
const selectedEndTime = ref('')
const isAvailabilityFiltered = ref(false)
const today = new Date()
const todayDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

// Check if user is owner or enterprise for header props
const showManagement = computed(() => authStore.user?.role === 'owner')
const showAdvertisement = computed(() => authStore.user?.role === 'enterprise')

// Fetch courts from API
const fetchCourts = async () => {
  isLoading.value = true
  try {
    const params: Record<string, string> = {}

    if (isAvailabilityFiltered.value) {
      params.booking_date = selectedBookingDate.value
      params.start_time = selectedStartTime.value
      params.end_time = selectedEndTime.value
    }

    const response = await axiosInstance.get('/courts', { params })
    courts.value = response.data
  } catch (error) {
    console.error('Error fetching courts:', error)
    toast.error('Unable to load courts. Please try again.')
  } finally {
    isLoading.value = false
  }
}

const applyAvailabilitySearch = async () => {
  if (!selectedBookingDate.value || !selectedStartTime.value || !selectedEndTime.value) {
    toast.error('Please choose date, start time, and end time.')
    return
  }

  if (selectedStartTime.value >= selectedEndTime.value) {
    toast.error('Start time must be earlier than end time.')
    return
  }

  if (selectedBookingDate.value === todayDate) {
    const currentTime = getCurrentTime()
    if (selectedStartTime.value <= currentTime) {
      toast.error('For today, start time must be later than current time.')
      return
    }
  }

  isAvailabilityFiltered.value = true
  await fetchCourts()
}

// Filter courts based on search and ward
const filteredCourts = computed(() => {
  let filtered = courts.value

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (court) =>
        court.name.toLowerCase().includes(query) ||
        court.ward.toLowerCase().includes(query) ||
        court.city.toLowerCase().includes(query),
    )
  }

  // Filter by ward
  if (selectedWard.value) {
    filtered = filtered.filter((court) => court.ward === selectedWard.value)
  }

  return filtered
})

// Get unique wards for filter
const wards = computed(() => {
  const uniqueWards = [...new Set(courts.value.map((court) => court.ward))]
  return uniqueWards.sort()
})

// Get badge based on court quantity
const getBadgeClass = (quantity: number) => {
  if (quantity >= 10) return 'badge-gold'
  if (quantity >= 5) return 'badge-silver'
  return 'badge-bronze'
}

const getBadgeText = (quantity: number) => {
  if (quantity >= 10) return '10+'
  if (quantity >= 5) return '5+'
  return `${quantity}`
}

// Get first image or placeholder
const getCourtImage = (court: Court) => {
  if (court.images && court.images.length > 0) {
    const imagePath = court.images[0]
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
      return imagePath
    }
    if (imagePath.startsWith('/')) {
      return `${backendOrigin}${imagePath}`
    }
    return `${backendOrigin}/${imagePath}`
  }
  return 'https://i.pinimg.com/1200x/0e/c0/4d/0ec04dde4f138cac5ec5e928edef20e9.jpg'
}

// Get current time in HH:MM format
const getCurrentTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

// Check if court is currently open based on operating hours
const isCourtOpen = (court: Court) => {
  if (!court.is_active) return false

  const currentTime = getCurrentTime()
  const openingTime = court.opening_time
  const closingTime = court.closing_time

  return currentTime >= openingTime && currentTime < closingTime
}

// Get court status with appropriate text and class
const getCourtStatus = (court: Court) => {
  if (!court.is_active) {
    return { text: 'Inactive', class: 'inactive' }
  }

  if (isCourtOpen(court)) {
    return { text: 'Open Now', class: 'active' }
  }

  return { text: 'Closed', class: 'closed' }
}

// Navigate to court details
const viewCourtDetails = (courtId: number) => {
  router.push(`/court/${courtId}`)
}

onMounted(() => {
  fetchCourts()
})
</script>

<template>
  <div class="courts-page">
    <AppHeader :showManagement="showManagement" :showAdvertisement="showAdvertisement" />

    <section class="hero-section">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <div class="hero-badge">
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
              d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
            />
          </svg>
          <span>Premium Courts Platform</span>
        </div>
        <h1 class="hero-title">Discover Amazing Pickleball Courts</h1>
        <p class="hero-subtitle">
          Find and book the best courts near you with premium facilities and instant confirmation
        </p>

        <div class="search-hub">
          <div class="search-main-row">
            <div class="search-box">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                class="search-icon"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search by court name, ward, or city..."
                class="search-input"
              />
            </div>

            <div class="ward-filter-wrap">
              <select v-model="selectedWard" class="ward-filter">
                <option value="">All Wards</option>
                <option v-for="ward in wards" :key="ward" :value="ward">
                  {{ ward }}
                </option>
              </select>
            </div>
          </div>

          <div class="availability-row">
            <div class="availability-heading">
              <strong>Availability Search</strong>
              <span>Find courts that are free at your preferred date and time</span>
            </div>
            <div class="availability-fields">
              <input
                v-model="selectedBookingDate"
                type="date"
                class="availability-input"
                :min="todayDate"
                aria-label="Booking date"
              />
              <div class="time-range-combined" aria-label="Time range">
                <input
                  v-model="selectedStartTime"
                  type="time"
                  class="time-part-input"
                  aria-label="Start time"
                />
                <span class="time-range-divider">to</span>
                <input
                  v-model="selectedEndTime"
                  type="time"
                  class="time-part-input"
                  aria-label="End time"
                />
              </div>
              <button class="availability-btn" @click="applyAvailabilitySearch">
                Search Availability
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="courts-section">
      <div class="container">
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading courts...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredCourts.length === 0" class="empty-state">
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
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3>No courts found</h3>
          <p>Try adjusting your search or filters</p>
        </div>

        <!-- Courts Grid -->
        <div v-else class="courts-grid">
          <div
            v-for="court in filteredCourts"
            :key="court.id"
            class="court-card"
            @click="viewCourtDetails(court.id)"
          >
            <div class="court-image">
              <img :src="getCourtImage(court)" :alt="court.name" />
              <div class="image-overlay">
                <button class="favorite-btn" @click.stop>
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
                      d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                    />
                  </svg>
                </button>
              </div>
              <div class="court-badge" :class="getBadgeClass(court.court_quantity)">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M11.7 2.805a.75.75 0 01.6 0A60.65 60.65 0 0122.83 8.72a.75.75 0 01-.231 1.337 49.949 49.949 0 00-9.902 3.912l-.003.002-.34.18a.75.75 0 01-.707 0A50.009 50.009 0 007.5 12.174v-.224c0-.131.067-.248.172-.311a54.614 54.614 0 014.653-2.52.75.75 0 00-.65-1.352 56.129 56.129 0 00-4.78 2.589 1.858 1.858 0 00-.859 1.228 49.803 49.803 0 00-4.634-1.527.75.75 0 01-.231-1.337A60.653 60.653 0 0111.7 2.805z"
                  />
                  <path
                    d="M13.06 15.473a48.45 48.45 0 017.666-3.282c.134 1.414.22 2.843.255 4.285a.75.75 0 01-.46.71 47.878 47.878 0 00-8.105 4.342.75.75 0 01-.832 0 47.877 47.877 0 00-8.104-4.342.75.75 0 01-.461-.71c.035-1.442.121-2.87.255-4.286A48.4 48.4 0 016 13.18v1.27a1.5 1.5 0 00-.14 2.508c-.09.38-.222.753-.397 1.11.452.213.901.434 1.346.661a6.729 6.729 0 00.551-1.608 1.5 1.5 0 00.14-2.67v-.645a48.549 48.549 0 013.44 1.668 2.25 2.25 0 002.12 0z"
                  />
                  <path
                    d="M4.462 19.462c.42-.419.753-.89 1-1.394.453.213.902.434 1.347.661a6.743 6.743 0 01-1.286 1.794.75.75 0 11-1.06-1.06z"
                  />
                </svg>
                {{ getBadgeText(court.court_quantity) }} Courts
              </div>
            </div>

            <div class="court-info">
              <div class="court-header">
                <h3 class="court-name">{{ court.name }}</h3>
                <span :class="['status-badge', getCourtStatus(court).class]">
                  {{ getCourtStatus(court).text }}
                </span>
              </div>

              <p class="court-location">
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
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                Ward {{ court.ward }}, {{ court.city }}
              </p>

              <div class="court-details">
                <div class="detail-item">
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
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <span>{{ court.opening_time }} - {{ court.closing_time }}</span>
                </div>
                <div class="detail-item">
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
                      d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                    />
                  </svg>
                  <span>{{ court.court_quantity }} courts available</span>
                </div>
              </div>

              <button class="book-btn">View Details</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <AppFooter />
  </div>
</template>

<style scoped>
.courts-page {
  min-height: 100vh;
  background: #f8f9fa;
}

/* Hero Section */
.hero-section {
  background:
    linear-gradient(
      135deg,
      rgba(45, 80, 22, 0.95) 0%,
      rgba(61, 102, 32, 0.9) 50%,
      rgba(74, 124, 44, 0.85) 100%
    ),
    url('https://i.pinimg.com/1200x/0e/c0/4d/0ec04dde4f138cac5ec5e928edef20e9.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  padding: 100px 40px;
  text-align: center;
  position: relative;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
}

.hero-content {
  max-width: 900px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 24px;
  animation: fadeInDown 0.8s ease;
}

.hero-badge svg {
  width: 20px;
  height: 20px;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 900;
  color: white;
  margin: 0 0 20px 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  animation: fadeInUp 0.8s ease 0.2s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 50px 0;
  line-height: 1.6;
  animation: fadeInUp 0.8s ease 0.4s both;
}

.search-hub {
  max-width: 1080px;
  margin: 0 auto;
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.32);
  backdrop-filter: blur(12px);
  box-shadow: 0 16px 38px rgba(0, 0, 0, 0.22);
}

.search-main-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.ward-filter-wrap {
  min-width: 360px;
}

.availability-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.availability-heading {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: center;
}

.availability-heading strong {
  color: #ffffff;
  font-size: 0.95rem;
}

.availability-heading span {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.82rem;
}

.availability-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  align-items: center;
}

.availability-input {
  padding: 12px 14px;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  outline: none;
  color: #1e293b;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.16);
}

.time-range-combined {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #ffffff;
  border-radius: 10px;
  padding: 8px 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.16);
}

.time-part-input {
  border: none;
  background: transparent;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
  outline: none;
  min-width: 120px;
}

.time-range-divider {
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
}

.availability-btn,
.clear-availability-btn {
  padding: 12px 16px;
  border: none;
  border-radius: 10px;
  font-size: 0.86rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.availability-btn {
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  color: #1e3a8a;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.22);
}

.availability-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.26);
}

.clear-availability-btn {
  background: rgba(255, 255, 255, 0.18);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.38);
}

.clear-availability-btn:hover {
  background: rgba(255, 255, 255, 0.28);
}

.clear-all-btn {
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.38);
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.clear-all-btn:hover {
  background: rgba(255, 255, 255, 0.27);
  transform: translateY(-1px);
}

.search-box {
  flex: 1;
  min-width: 280px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  color: #6b7280;
}

.search-input {
  width: 100%;
  padding: 14px 18px 14px 54px;
  border: none;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  outline: none;
  color: #0f172a;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
  transition: all 0.3s;
}

.search-input:focus {
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.28);
}

.ward-filter {
  padding: 14px 16px;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  background: white;
  color: #0f172a;
  cursor: pointer;
  outline: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
  transition: all 0.3s;
  min-width: 360px;
}

.ward-filter:hover {
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.25);
}

/* Courts Section */
.courts-section {
  padding: 80px 40px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top-color: #2d5016;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
}

.empty-state svg {
  width: 100px;
  height: 100px;
  color: #d1d5db;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #6b7280;
  margin: 0;
}

.empty-state p {
  color: #9ca3af;
  margin: 0;
}

/* Courts Grid */
.courts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 32px;
  animation: fadeIn 0.8s ease;
}

.court-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
  border: 2px solid transparent;
  animation: fadeInUp 0.6s ease backwards;
}

.court-card:nth-child(1) {
  animation-delay: 0.1s;
}

.court-card:nth-child(2) {
  animation-delay: 0.2s;
}

.court-card:nth-child(3) {
  animation-delay: 0.3s;
}

.court-card:nth-child(n + 4) {
  animation-delay: 0.4s;
}

.court-card:hover {
  transform: translateY(-12px);
  box-shadow: 0 20px 40px rgba(45, 80, 22, 0.2);
  border-color: rgba(45, 80, 22, 0.3);
}

.court-image {
  position: relative;
  height: 260px;
  overflow: hidden;
}

.court-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.court-card:hover .court-image img {
  transform: scale(1.1);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.2) 0%, transparent 50%);
  opacity: 0;
  transition: opacity 0.3s;
}

.court-card:hover .image-overlay {
  opacity: 1;
}

.favorite-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 44px;
  height: 44px;
  background: white;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s;
}

.favorite-btn svg {
  width: 22px;
  height: 22px;
  color: #ef4444;
  transition: fill 0.3s;
}

.favorite-btn:hover {
  background: #ef4444;
  transform: scale(1.1);
}

.favorite-btn:hover svg {
  fill: white;
  stroke: white;
}

.court-badge {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 8px 16px;
  border-radius: 50px;
  font-weight: 700;
  font-size: 0.85rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  gap: 6px;
  animation: slideInLeft 0.5s ease;
}

.court-badge svg {
  width: 16px;
  height: 16px;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.badge-gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #92400e;
}

.badge-silver {
  background: linear-gradient(135deg, #e5e7eb 0%, #f3f4f6 100%);
  color: #374151;
}

.badge-bronze {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  color: #78350f;
}

.court-info {
  padding: 24px;
}

.court-header {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.court-name {
  font-size: 1.5rem;
  font-weight: 800;
  color: #2d5016;
  margin: 0;
  line-height: 1.3;
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
  animation: fadeIn 0.5s ease;
}

.status-badge.active {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.status-badge.closed {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.status-badge.inactive {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.court-location {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 0.95rem;
  margin: 0 0 16px 0;
}

.court-location svg {
  width: 18px;
  height: 18px;
  color: #ef4444;
}

.court-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #6b7280;
}

.detail-item svg {
  width: 18px;
  height: 18px;
  color: #2d5016;
}

.book-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #2d5016 0%, #3d6620 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.book-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.book-btn:hover::before {
  left: 100%;
}

.book-btn:hover {
  background: linear-gradient(135deg, #3d6620 0%, #4a7c2c 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(45, 80, 22, 0.4);
}

.book-btn:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(45, 80, 22, 0.3);
}

/* Responsive */
@media (max-width: 1024px) {
  .courts-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 24px;
  }

  .hero-title {
    font-size: 2.8rem;
  }

  .search-hub {
    max-width: 940px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 80px 24px;
  }

  .hero-title {
    font-size: 2.2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
    margin-bottom: 40px;
  }

  .search-main-row,
  .availability-fields {
    flex-direction: column;
    align-items: stretch;
  }

  .availability-input,
  .time-range-combined,
  .availability-btn,
  .clear-availability-btn {
    width: 100%;
  }

  .time-part-input {
    min-width: 0;
    width: 100%;
  }

  .ward-filter {
    width: 100%;
    min-width: 0;
  }

  .ward-filter-wrap {
    width: 100%;
    min-width: 0;
  }

  .search-box {
    min-width: 0;
  }

  .courts-section {
    padding: 60px 24px;
  }

  .courts-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .court-name {
    font-size: 1.25rem;
  }

  .court-header {
    flex-wrap: wrap;
  }

  .status-badge {
    font-size: 0.7rem;
    padding: 3px 10px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 1.8rem;
  }

  .court-badge {
    font-size: 0.75rem;
    padding: 6px 12px;
  }

  .court-badge svg {
    width: 14px;
    height: 14px;
  }
}
</style>
