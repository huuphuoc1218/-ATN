<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axiosInstance from '@/utils/axios'

const backendOrigin = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(
  /\/api\/?$/,
  '',
)

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
  contact_phone: string
  contact_email?: string
  time_slots?: TimeSlot[]
  created_at: string
  updated_at?: string
}

const router = useRouter()
const courts = ref<Court[]>([])
const isLoading = ref(false)

// Fetch courts from API
const fetchCourts = async () => {
  isLoading.value = true
  try {
    const response = await axiosInstance.get('/courts', {
      params: {
        limit: 3,
      },
    })
    courts.value = response.data
  } catch (error) {
    console.error('Error fetching courts:', error)
  } finally {
    isLoading.value = false
  }
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

// Get current time slot based on current time
const getCurrentTimeSlot = (court: Court) => {
  if (!court.time_slots || court.time_slots.length === 0) {
    return null
  }

  const currentTime = getCurrentTime()

  // Find the time slot that matches current time
  return court.time_slots.find((slot) => {
    return currentTime >= slot.start_time && currentTime < slot.end_time
  })
}

// Get current price or lowest price based on time
const getCurrentPrice = (court: Court) => {
  if (!court.time_slots || court.time_slots.length === 0) {
    return 150000 // Default price
  }

  // If there's a current time slot, use its price
  const currentSlot = getCurrentTimeSlot(court)
  if (currentSlot) {
    return currentSlot.price
  }

  // Otherwise, show the lowest price
  const prices = court.time_slots.map((slot) => slot.price)
  return Math.min(...prices)
}

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('vi-VN').format(price)
}

// Navigate to court details
const viewCourtDetails = (courtId: number) => {
  router.push(`/court/${courtId}`)
}

// Navigate to all courts page
const viewAllCourts = () => {
  router.push('/court')
}

onMounted(() => {
  fetchCourts()
})
</script>

<template>
  <section class="court-list-section">
    <div class="container">
      <div class="section-header">
        <div class="header-content">
          <span class="section-badge"><i class="fas fa-trophy"></i> Popular Courts</span>
          <h2 class="section-title">
            Discover nearby pickleball courts for<br />
            <span class="highlight">convenient and accessible gameplay</span>
          </h2>
          <p class="section-description">
            Find the perfect court near you with the best facilities and competitive prices
          </p>
        </div>
        <button class="view-all-btn" @click="viewAllCourts">View All Courts →</button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="loading-container">
        <div class="spinner"></div>
        <p>Loading courts...</p>
      </div>

      <!-- Courts Grid -->
      <div v-else-if="courts.length > 0" class="courts-grid">
        <div
          v-for="court in courts"
          :key="court.id"
          class="court-card"
          @click="viewCourtDetails(court.id)"
        >
          <div class="court-image">
            <img :src="getCourtImage(court)" :alt="court.name" loading="lazy" decoding="async" />
            <div class="image-overlay">
              <button class="favorite-btn" @click.stop><i class="fas fa-heart"></i></button>
            </div>
            <div class="court-badge" :class="getBadgeClass(court.court_quantity)">
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

            <p class="court-ward">
              <i class="fas fa-map-marker-alt"></i> Ward {{ court.ward }}, {{ court.city }}
            </p>

            <div class="court-footer">
              <div class="court-meta">
                <span class="price">{{ formatPrice(getCurrentPrice(court)) }} VND/h</span>
              </div>

              <button class="book-btn" @click.stop="viewCourtDetails(court.id)">Book Now</button>
            </div>
          </div>
        </div>
      </div>

      <!-- No Courts State -->
      <div v-else class="no-courts">
        <p>No courts available at the moment.</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.court-list-section {
  padding: 100px 40px;
  background: white;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 60px;
  gap: 40px;
}

.header-content {
  flex: 1;
}

.section-badge {
  display: inline-block;
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  color: #856404;
  padding: 10px 20px;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 16px;
}

.section-title {
  font-size: 2.8rem;
  color: #2d5016;
  font-weight: 800;
  line-height: 1.3;
  margin: 0 0 16px 0;
  letter-spacing: -1px;
}

.highlight {
  color: #4a7c2c;
  position: relative;
}

.section-description {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
  max-width: 600px;
}

.view-all-btn {
  padding: 16px 32px;
  background: transparent;
  border: 2px solid #4a7c2c;
  color: #4a7c2c;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.view-all-btn:hover {
  background: #4a7c2c;
  color: white;
  transform: translateX(5px);
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
  border-top-color: #4a7c2c;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-container p {
  color: #666;
  font-size: 1rem;
}

/* No Courts State */
.no-courts {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 1.1rem;
}

.courts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 40px;
}

.court-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #f0f0f0;
  cursor: pointer;
}

.court-card:hover {
  transform: translateY(-12px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}

.court-image {
  width: 100%;
  height: 260px;
  position: relative;
  overflow: hidden;
}

.court-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.court-card:hover .court-image img {
  transform: scale(1.15);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.3) 0%, transparent 50%);
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
  font-size: 1.3rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s;
  color: #ff4757;
}

.favorite-btn:hover {
  transform: scale(1.1);
  color: #ff6348;
}

.court-badge {
  position: absolute;
  bottom: 16px;
  left: 16px;
  padding: 10px 20px;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 700;
  backdrop-filter: blur(10px);
}

.badge-gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #000;
  box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
}

.badge-silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  color: #000;
  box-shadow: 0 4px 15px rgba(192, 192, 192, 0.4);
}

.badge-bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #e89f71 100%);
  color: #fff;
  box-shadow: 0 4px 15px rgba(205, 127, 50, 0.4);
}

.court-info {
  padding: 28px;
}

.court-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
}

.court-name {
  font-size: 1.6rem;
  font-weight: 800;
  color: #2d5016;
  margin: 0;
  letter-spacing: -0.5px;
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

.rating-value {
  font-weight: 700;
  color: #2d5016;
  font-size: 0.95rem;
}

.court-ward {
  color: #666;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
}

.court-ward i {
  color: #ff4757;
}

.court-footer {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.court-meta {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.distance,
.price {
  font-size: 0.95rem;
  font-weight: 600;
  color: #666;
}

.price {
  color: #4a7c2c;
  font-size: 1.1rem;
  font-weight: 800;
}

.book-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #4a7c2c 0%, #2d5016 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(74, 124, 44, 0.3);
}

.book-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 124, 44, 0.4);
}

@media (max-width: 1024px) {
  .section-title {
    font-size: 2.25rem;
  }

  .view-all-btn {
    padding: 10px 20px;
    font-size: 0.95rem;
  }

  .courts-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .court-list-section {
    padding: 60px 20px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .section-title {
    font-size: 2rem;
  }

  .courts-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .court-card {
    padding: 16px;
  }

  .court-image {
    height: 200px;
  }

  .court-name {
    font-size: 1.15rem;
  }

  .court-location,
  .court-price,
  .court-rating {
    font-size: 0.9rem;
  }

  .book-btn {
    padding: 14px;
    font-size: 0.95rem;
  }
}

@media (max-width: 480px) {
  .court-list-section {
    padding: 40px 16px;
  }

  .section-title {
    font-size: 1.75rem;
  }

  .view-all-btn {
    padding: 8px 16px;
    font-size: 0.85rem;
  }

  .court-card {
    padding: 12px;
  }

  .court-image {
    height: 180px;
  }

  .court-name {
    font-size: 1rem;
  }

  .court-info {
    gap: 8px;
  }

  .book-btn {
    padding: 12px;
    font-size: 0.9rem;
  }
}
</style>
