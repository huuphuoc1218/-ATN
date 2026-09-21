<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axiosInstance from '@/utils/axios'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const backendOrigin = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(
  /\/api\/?$/,
  '',
)

interface TimeSlot {
  start_time: string
  end_time: string
  price: number
}

interface IndividualCourt {
  id: number
  court_id: number
  name: string
  is_active: boolean
  is_available: boolean
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
  contact_phone: string
  contact_email?: string
  time_slots?: TimeSlot[]
  individual_courts?: IndividualCourt[]
  created_at: string
  updated_at?: string
}

const court = ref<Court | null>(null)
const isLoading = ref(false)
const currentImageIndex = ref(0)
const activeTab = ref('overview')

// Check if user is owner or enterprise for header props
const showManagement = computed(() => authStore.user?.role === 'owner')
const showAdvertisement = computed(() => authStore.user?.role === 'enterprise')

// Fetch court details
const fetchCourtDetails = async () => {
  isLoading.value = true
  try {
    const courtId = route.params.id
    const response = await axiosInstance.get(`/courts/${courtId}`)
    court.value = response.data
  } catch (error) {
    console.error('Error fetching court details:', error)
  } finally {
    isLoading.value = false
  }
}

// Get court images with full URL
const courtImages = computed(() => {
  if (!court.value || !court.value.images || court.value.images.length === 0) {
    return ['https://i.pinimg.com/1200x/0e/c0/4d/0ec04dde4f138cac5ec5e928edef20e9.jpg']
  }
  return court.value.images.map((img) => {
    if (img.startsWith('http://') || img.startsWith('https://')) {
      return img
    }
    if (img.startsWith('/')) {
      return `${backendOrigin}${img}`
    }
    return `${backendOrigin}/${img}`
  })
})

// Navigation for image carousel
const previousImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
  } else {
    currentImageIndex.value = courtImages.value.length - 1
  }
}

const nextImage = () => {
  if (currentImageIndex.value < courtImages.value.length - 1) {
    currentImageIndex.value++
  } else {
    currentImageIndex.value = 0
  }
}

const goToImage = (index: number) => {
  currentImageIndex.value = index
}

// Navigate to booking
const bookNow = () => {
  if (!authStore.user || !authStore.token) {
    router.push('/login')
    return
  }
  router.push(`/booking/${court.value?.id}`)
}

// Get current time in HH:MM format
const getCurrentTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

// Check if court is currently open
const isCourtOpen = computed(() => {
  if (!court.value) return false

  const currentTime = getCurrentTime()
  const openingTime = court.value.opening_time
  const closingTime = court.value.closing_time

  return currentTime >= openingTime && currentTime < closingTime
})

// Get current time slot based on current time
const currentTimeSlot = computed(() => {
  if (!court.value?.time_slots || court.value.time_slots.length === 0) {
    return null
  }

  const currentTime = getCurrentTime()

  // Find the time slot that matches current time
  return court.value.time_slots.find((slot) => {
    return currentTime >= slot.start_time && currentTime < slot.end_time
  })
})

// Get current price or lowest price
const displayPrice = computed(() => {
  if (!court.value?.time_slots || court.value.time_slots.length === 0) {
    return 150000 // Default price
  }

  // If there's a current time slot, use its price
  if (currentTimeSlot.value) {
    return currentTimeSlot.value.price
  }

  // Otherwise, show the lowest price
  const prices = court.value.time_slots.map((slot) => slot.price)
  return Math.min(...prices)
})

// Get price label text
const priceLabel = computed(() => {
  if (currentTimeSlot.value) {
    return 'Current price'
  }
  return 'Starting from'
})

// Get availability status text
const availabilityStatus = computed(() => {
  if (!court.value) return { text: 'Checking...', available: false }

  if (isCourtOpen.value) {
    return { text: 'Available now', available: true }
  }

  return { text: 'Closed now', available: false }
})

// Format price
const formatPrice = (price: number) => {
  return new Intl.NumberFormat('vi-VN').format(price)
}

// Mock booking count (you can fetch from API)
const bookingCount = ref(40)

onMounted(() => {
  fetchCourtDetails()
})
</script>

<template>
  <div class="court-detail-page">
    <AppHeader :showManagement="showManagement" :showAdvertisement="showAdvertisement" />

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading court details...</p>
    </div>

    <!-- Court Details -->
    <div v-else-if="court" class="detail-container">
      <!-- Image Carousel -->
      <section class="carousel-section">
        <div class="carousel-container">
          <button class="carousel-btn prev" @click="previousImage">
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
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>

          <div class="carousel-images">
            <img
              v-for="(img, index) in courtImages"
              :key="index"
              :src="img"
              :alt="`${court.name} - Image ${index + 1}`"
              :class="{ active: index === currentImageIndex }"
              class="carousel-image"
            />
          </div>

          <button class="carousel-btn next" @click="nextImage">
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
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>

          <!-- Carousel Indicators -->
          <div class="carousel-indicators">
            <button
              v-for="(_img, index) in courtImages"
              :key="index"
              :class="{ active: index === currentImageIndex }"
              class="indicator"
              @click="goToImage(index)"
            ></button>
          </div>
        </div>
      </section>

      <!-- Main Content -->
      <section class="main-content">
        <div class="content-wrapper">
          <!-- Left Column - Court Information -->
          <div class="info-column">
            <!-- Court Header -->
            <div class="court-header">
              <h1 class="court-title">{{ court.name }}</h1>
              <div class="court-badges">
                <span class="badge booking-badge">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
                    <path
                      fill-rule="evenodd"
                      d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM17.25 12a5.25 5.25 0 11-10.5 0 5.25 5.25 0 0110.5 0z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  {{ bookingCount }}+ Bookings
                </span>
                <span class="badge indoor-badge">Indoor</span>
              </div>
            </div>

            <!-- Court Contact Info -->
            <div class="contact-info">
              <div class="contact-item">
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
                <span>{{ court.address }}, Ward {{ court.ward }}, {{ court.city }}</span>
              </div>
              <div class="contact-item" v-if="court.contact_email">
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
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
                <span>{{ court.contact_email }}</span>
              </div>
              <div class="contact-item">
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
                    d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                  />
                </svg>
                <span>{{ court.contact_phone }}</span>
              </div>
            </div>

            <!-- Tabs -->
            <div class="tabs">
              <button
                :class="{ active: activeTab === 'overview' }"
                class="tab-btn"
                @click="activeTab = 'overview'"
              >
                Overview
              </button>
              <button
                :class="{ active: activeTab === 'pricing' }"
                class="tab-btn"
                @click="activeTab = 'pricing'"
              >
                Pricing
              </button>
              <button
                :class="{ active: activeTab === 'facilities' }"
                class="tab-btn"
                @click="activeTab = 'facilities'"
              >
                Facilities
              </button>
              <button
                :class="{ active: activeTab === 'reviews' }"
                class="tab-btn"
                @click="activeTab = 'reviews'"
              >
                Reviews
              </button>
            </div>

            <!-- Tab Content -->
            <div class="tab-content">
              <!-- Overview Tab -->
              <div v-if="activeTab === 'overview'" class="overview-content">
                <h3>Overview</h3>
                <p v-if="court.description" class="description">{{ court.description }}</p>
                <p v-else class="no-description">No description available for this court.</p>

                <div class="court-features">
                  <div class="feature-item">
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
                    <div>
                      <strong>Opening Hours</strong>
                      <p>{{ court.opening_time }} - {{ court.closing_time }}</p>
                    </div>
                  </div>
                  <div class="feature-item">
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
                    <div>
                      <strong>Available Courts</strong>
                      <p>{{ court.court_quantity }} courts available</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Pricing Tab -->
              <div v-if="activeTab === 'pricing'" class="pricing-content">
                <h3>Pricing Details</h3>
                <p class="pricing-description">
                  Our flexible pricing structure to suit your schedule
                </p>

                <div v-if="court.time_slots && court.time_slots.length > 0" class="pricing-grid">
                  <div v-for="(slot, index) in court.time_slots" :key="index" class="pricing-card">
                    <div class="pricing-time">
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
                      <span>{{ slot.start_time }} - {{ slot.end_time }}</span>
                    </div>
                    <div class="pricing-amount">
                      <span class="price-value">{{ formatPrice(slot.price) }}</span>
                      <span class="price-unit">VND/hour</span>
                    </div>
                  </div>
                </div>
                <div v-else class="no-pricing">
                  <p>Pricing information will be updated soon. Please contact us for details.</p>
                </div>
              </div>

              <!-- Facilities Tab -->
              <div v-if="activeTab === 'facilities'" class="facilities-content">
                <h3>Facilities</h3>
                <div class="facilities-grid">
                  <div class="facility-item">
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
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span>Free Parking</span>
                  </div>
                  <div class="facility-item">
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
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span>Free Drinks</span>
                  </div>
                  <div class="facility-item">
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
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span>Locker Rooms</span>
                  </div>
                  <div class="facility-item">
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
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span>Shower Facilities</span>
                  </div>
                  <div class="facility-item">
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
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span>Equipment Rental</span>
                  </div>
                  <div class="facility-item">
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
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span>WiFi Available</span>
                  </div>
                </div>
              </div>

              <!-- Reviews Tab -->
              <div v-if="activeTab === 'reviews'" class="reviews-content">
                <h3>Reviews</h3>
                <div class="reviews-summary">
                  <div class="rating-box">
                    <div class="rating-score">5.0</div>
                    <div class="stars">
                      <svg
                        v-for="i in 5"
                        :key="i"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                      >
                        <path
                          d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z"
                        />
                      </svg>
                    </div>
                  </div>

                  <div class="rating-details">
                    <div class="rating-item">
                      <span class="rating-label">Service</span>
                      <div class="rating-bar">
                        <div class="rating-fill" style="width: 100%"></div>
                      </div>
                      <span class="rating-value">5.0</span>
                    </div>
                    <div class="rating-item">
                      <span class="rating-label">Parking</span>
                      <div class="rating-bar">
                        <div class="rating-fill" style="width: 100%"></div>
                      </div>
                      <span class="rating-value">5.0</span>
                    </div>
                    <div class="rating-item">
                      <span class="rating-label">Facility</span>
                      <div class="rating-bar">
                        <div class="rating-fill" style="width: 100%"></div>
                      </div>
                      <span class="rating-value">5.0</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column - Booking Card -->
          <div class="booking-column">
            <div class="booking-card">
              <div class="availability">
                <div class="availability-badge" :class="{ closed: !availabilityStatus.available }">
                  <div class="pulse-dot" v-if="availabilityStatus.available"></div>
                  <div class="closed-dot" v-else></div>
                  <span>{{ availabilityStatus.text }}</span>
                </div>
              </div>

              <div class="pricing">
                <div class="price-main">
                  <span class="price">{{ formatPrice(displayPrice) }} VND/h</span>
                  <span class="guests">{{ priceLabel }}</span>
                </div>
                <div v-if="currentTimeSlot" class="price-range current-slot">
                  {{ currentTimeSlot.start_time }} - {{ currentTimeSlot.end_time }}
                </div>
                <div
                  v-else-if="court.time_slots && court.time_slots.length > 1"
                  class="price-range"
                >
                  Multiple pricing options available
                </div>
              </div>

              <div class="inclusions">
                <div class="inclusion-badge">
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
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  <span>FREE</span>
                </div>
                <div class="inclusion-items">
                  <span>drinks, parking</span>
                </div>
              </div>

              <button class="book-now-btn" @click="bookNow">BOOK NOW</button>

              <div class="booking-note">
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
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <span>Instant confirmation upon booking</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Error State -->
    <div v-else class="error-state">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <h3>Court not found</h3>
      <p>The court you're looking for doesn't exist or has been removed.</p>
      <button @click="router.push('/courts')" class="back-btn">Back to Courts</button>
    </div>

    <AppFooter />
  </div>
</template>

<style scoped>
.court-detail-page {
  min-height: 100vh;
  background: #f8f9fa;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
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

/* Error State */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 20px;
  padding: 40px;
}

.error-state svg {
  width: 80px;
  height: 80px;
  color: #ef4444;
}

.error-state h3 {
  font-size: 1.8rem;
  color: #1f2937;
  margin: 0;
}

.error-state p {
  color: #6b7280;
  margin: 0;
}

.back-btn {
  padding: 12px 32px;
  background: linear-gradient(135deg, #2d5016 0%, #3d6620 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(45, 80, 22, 0.3);
}

/* Carousel Section */
.carousel-section {
  background: white;
  padding: 10px 0;
}

.carousel-container {
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  height: 300px;
  overflow: hidden;
  border-radius: 12px;
}

.carousel-images {
  width: 100%;
  height: 100%;
  position: relative;
}

.carousel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
  opacity: 0;
  transition: opacity 0.5s ease-in-out;
}

.carousel-image.active {
  opacity: 1;
}

.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  z-index: 10;
}

.carousel-btn:hover {
  background: white;
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.carousel-btn svg {
  width: 24px;
  height: 24px;
  color: #2d5016;
}

.carousel-btn.prev {
  left: 20px;
}

.carousel-btn.next {
  right: 20px;
}

.carousel-indicators {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 10;
}

.indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s;
}

.indicator.active {
  background: white;
  width: 32px;
  border-radius: 6px;
}

/* Main Content */
.main-content {
  padding: 30px 40px;
  background: #f8f9fa;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 40px;
}

/* Info Column */
.info-column {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.court-header {
  margin-bottom: 24px;
}

.court-title {
  font-size: 1.8rem;
  font-weight: 900;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.court-badges {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.booking-badge {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #78350f;
}

.booking-badge svg {
  width: 16px;
  height: 16px;
}

.indoor-badge {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

/* Contact Info */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 2px solid #e5e7eb;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #4b5563;
  font-size: 1rem;
}

.contact-item svg {
  width: 20px;
  height: 20px;
  color: #2d5016;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid #e5e7eb;
  margin-bottom: 32px;
}

.tab-btn {
  padding: 16px 24px;
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}

.tab-btn.active {
  color: #2d5016;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(135deg, #2d5016 0%, #3d6620 100%);
  border-radius: 2px 2px 0 0;
}

.tab-btn:hover {
  color: #2d5016;
}

/* Tab Content */
.tab-content {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tab-content h3 {
  font-size: 1.5rem;
  font-weight: 800;
  color: #2d5016;
  margin: 0 0 12px 0;
}

.description {
  color: #4b5563;
  line-height: 1.8;
  margin-bottom: 24px;
  white-space: pre-wrap;
}

.no-description {
  color: #9ca3af;
  line-height: 1.8;
  margin-bottom: 24px;
  font-style: italic;
  text-align: center;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
}

.pricing-description,
.courts-description {
  color: #6b7280;
  margin-bottom: 24px;
  font-size: 1rem;
}

/* Pricing Tab */
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.pricing-card {
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
  border: 2px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s;
  cursor: pointer;
}

.pricing-card:hover {
  border-color: #2d5016;
  box-shadow: 0 8px 24px rgba(45, 80, 22, 0.15);
  transform: translateY(-4px);
}

.pricing-time {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  color: #4b5563;
  font-weight: 600;
  font-size: 1.05rem;
}

.pricing-time svg {
  width: 24px;
  height: 24px;
  color: #2d5016;
}

.pricing-amount {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.price-value {
  font-size: 2rem;
  font-weight: 900;
  color: #2d5016;
  line-height: 1;
}

.price-unit {
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 500;
}

.no-pricing {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
  background: #f9fafb;
  border-radius: 12px;
}

.court-features {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-top: 32px;
}

.feature-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.feature-item svg {
  width: 28px;
  height: 28px;
  color: #2d5016;
  flex-shrink: 0;
}

.feature-item strong {
  display: block;
  color: #1f2937;
  font-size: 1rem;
  margin-bottom: 4px;
}

.feature-item p {
  color: #6b7280;
  margin: 0;
  font-size: 0.9rem;
}

/* Facilities */
.facilities-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.facility-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
}

.facility-item svg {
  width: 24px;
  height: 24px;
  color: #10b981;
  flex-shrink: 0;
}

.facility-item span {
  color: #4b5563;
  font-weight: 500;
}

/* Reviews */
.reviews-summary {
  display: flex;
  gap: 40px;
}

.rating-box {
  flex-shrink: 0;
  text-align: center;
}

.rating-score {
  font-size: 4rem;
  font-weight: 900;
  color: #fbbf24;
  line-height: 1;
  margin-bottom: 12px;
}

.stars {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.stars svg {
  width: 24px;
  height: 24px;
  color: #fbbf24;
}

.rating-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.rating-item {
  display: grid;
  grid-template-columns: 80px 1fr 50px;
  align-items: center;
  gap: 16px;
}

.rating-label {
  font-weight: 600;
  color: #4b5563;
}

.rating-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.rating-fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%);
  border-radius: 4px;
}

.rating-value {
  font-weight: 700;
  color: #1f2937;
  text-align: right;
}

/* Booking Column */
.booking-column {
  position: sticky;
  top: 100px;
  height: fit-content;
}

.booking-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border: 2px solid #e5e7eb;
}

.availability {
  margin-bottom: 24px;
}

.availability-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #ecfdf5;
  border: 1px solid #10b981;
  border-radius: 20px;
  color: #065f46;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.availability-badge.closed {
  background: #fef2f2;
  border: 1px solid #ef4444;
  color: #991b1b;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.closed-dot {
  width: 10px;
  height: 10px;
  background: #ef4444;
  border-radius: 50%;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.pricing {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 2px solid #e5e7eb;
}

.price-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.price {
  font-size: 2.2rem;
  font-weight: 900;
  color: #2d5016;
  line-height: 1;
}

.guests {
  color: #6b7280;
  font-size: 0.9rem;
}

.price-range {
  color: #059669;
  font-size: 0.85rem;
  font-weight: 600;
  margin-top: 8px;
}

.price-range.current-slot {
  color: #2d5016;
  font-weight: 700;
  font-size: 0.9rem;
}

.inclusions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f0fdf4;
  border-radius: 12px;
}

.inclusion-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #10b981;
  color: white;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.85rem;
}

.inclusion-badge svg {
  width: 16px;
  height: 16px;
}

.inclusion-items {
  color: #065f46;
  font-weight: 600;
  font-size: 0.95rem;
}

.book-now-btn {
  width: 100%;
  padding: 18px;
  background: linear-gradient(135deg, #0a2463 0%, #0d3380 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 900;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(10, 36, 99, 0.3);
}

.book-now-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(10, 36, 99, 0.4);
  background: linear-gradient(135deg, #0d3380 0%, #1047a8 100%);
}

.book-now-btn:active {
  transform: translateY(-1px);
}

.booking-note {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  color: #6b7280;
  font-size: 0.85rem;
}

.booking-note svg {
  width: 18px;
  height: 18px;
  color: #10b981;
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .content-wrapper {
    grid-template-columns: 1fr 350px;
    gap: 30px;
  }
}

@media (max-width: 992px) {
  .content-wrapper {
    grid-template-columns: 1fr;
    gap: 40px;
  }

  .booking-column {
    position: static;
  }

  .court-features {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .carousel-container {
    height: 250px;
  }

  .main-content {
    padding: 20px;
  }

  .info-column,
  .booking-card {
    padding: 16px;
  }

  .court-title {
    font-size: 1.5rem;
  }

  .court-badges {
    gap: 8px;
  }

  .badge {
    font-size: 0.8rem;
    padding: 6px 12px;
  }

  .tabs {
    overflow-x: auto;
    scrollbar-width: thin;
  }

  .tab-btn {
    padding: 12px 16px;
    font-size: 0.9rem;
    white-space: nowrap;
  }

  .facilities-grid {
    grid-template-columns: 1fr;
  }

  .reviews-summary {
    flex-direction: column;
    align-items: center;
  }

  .rating-details {
    width: 100%;
  }

  .price {
    font-size: 2rem;
  }
}

@media (max-width: 640px) {
  .main-content {
    padding: 16px 12px;
  }

  .content-wrapper {
    gap: 16px;
  }

  .contact-item {
    align-items: flex-start;
    font-size: 0.92rem;
    word-break: break-word;
  }

  .tabs {
    margin-bottom: 20px;
  }

  .tab-btn {
    padding: 10px 12px;
    font-size: 0.85rem;
  }

  .pricing-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .rating-item {
    grid-template-columns: 64px 1fr 36px;
    gap: 10px;
  }

  .rating-label,
  .rating-value {
    font-size: 0.82rem;
  }

  .booking-note {
    align-items: flex-start;
    line-height: 1.45;
  }
}

@media (max-width: 480px) {
  .carousel-container {
    height: 200px;
  }

  .carousel-btn {
    width: 40px;
    height: 40px;
  }

  .carousel-btn svg {
    width: 20px;
    height: 20px;
  }

  .court-title {
    font-size: 1.3rem;
  }

  .rating-score {
    font-size: 2.5rem;
  }

  .badge {
    font-size: 0.74rem;
    padding: 5px 10px;
  }

  .info-column,
  .booking-card {
    padding: 14px;
  }

  .book-now-btn {
    padding: 14px;
    font-size: 0.95rem;
  }
}
</style>
