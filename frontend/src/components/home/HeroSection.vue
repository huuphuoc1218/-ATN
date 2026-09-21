<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axios'

const router = useRouter()

// Advertisement carousel
const currentAdIndex = ref(0)
const isAutoPlaying = ref(true)
let autoPlayInterval: number | null = null

interface HomeAdvertisement {
  id: number
  title: string
  description: string
  company: string
  badge: string
  discount: string
  image: string
  link: string
  click_count?: number
}

// Mock data - sẽ được thay thế bằng API call trong tương lai
const advertisements = ref<HomeAdvertisement[]>([
  {
    id: 1,
    title: 'Premium Sports Equipment Sale',
    description: 'Professional paddles & gear with exclusive 30% discount for members',
    company: 'SportGear Pro',
    badge: 'HOT DEAL',
    discount: '30% OFF',
    image: 'https://i.pinimg.com/736x/79/aa/c4/79aac4a0826832e76dcb2aa01f4c6347.jpg',
    link: '#',
  },
  {
    id: 2,
    title: 'Elite Championship Training',
    description: 'Learn from pro coaches. Limited slots available this season',
    company: 'Elite Training Center',
    badge: 'NEW',
    discount: 'Free Trial',
    image: 'https://i.pinimg.com/736x/1c/b1/7d/1cb17db56b6e1f7ccc280c1db55a2c2b.jpg',
    link: '#',
  },
  {
    id: 3,
    title: 'VIP Court Membership 2025',
    description: 'Unlimited access to premium courts + exclusive benefits',
    company: 'VIP Court Access',
    badge: 'LIMITED',
    discount: 'Save 40%',
    image: 'https://i.pinimg.com/1200x/fd/b0/41/fdb04136073c37e5c0f2e5cb994ee5fb.jpg',
    link: '#',
  },
  {
    id: 4,
    title: 'Tournament Registration Open',
    description: 'Join the biggest pickleball tournament in Vietnam',
    company: 'NP Sports Events',
    badge: 'EVENT',
    discount: 'Register Now',
    image: 'https://i.pinimg.com/736x/d5/f7/0b/d5f70bfc59da6a1435df1d8fdbd59244.jpg',
    link: '#',
  },
])

const backendBaseUrl = String(axios.defaults.baseURL || '').replace(/\/api\/?$/, '')

const resolveImageUrl = (imageUrl: string) => {
  if (!imageUrl) return ''
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) return imageUrl
  return `${backendBaseUrl}${imageUrl}`
}

const fetchApprovedAdvertisements = async () => {
  try {
    const response = await axios.get('/advertisements/public')
    const items = response.data?.data || response.data || []
    if (!Array.isArray(items) || items.length === 0) return

    advertisements.value = items.map((item: any) => ({
      id: item.id,
      title: item.name,
      description: item.description,
      company: item.owner?.full_name || 'Verified Partner',
      badge: 'HOT DEAL',
      discount: 'Limited Time',
      image: resolveImageUrl(item.image_url),
      link: item.detail_url,
      click_count: item.click_count || 0,
    }))
    currentAdIndex.value = 0
  } catch (error) {
    console.error('Failed to load approved advertisements:', error)
  }
}

const handleAdClick = async (ad: HomeAdvertisement) => {
  if (!ad.link) return

  try {
    await axios.post(`/advertisements/${ad.id}/click`)
    const current = advertisements.value[currentAdIndex.value]
    if (current && current.id === ad.id) {
      current.click_count = (current.click_count || 0) + 1
    }
  } catch (error) {
    console.error('Failed to track ad click:', error)
  }

  window.open(ad.link, '_blank', 'noopener,noreferrer')
}

const nextAd = () => {
  if (!advertisements.value.length) return
  currentAdIndex.value = (currentAdIndex.value + 1) % advertisements.value.length
}

const prevAd = () => {
  if (!advertisements.value.length) return
  currentAdIndex.value =
    currentAdIndex.value === 0 ? advertisements.value.length - 1 : currentAdIndex.value - 1
}

const goToAd = (index: number) => {
  currentAdIndex.value = index
  resetAutoPlay()
}

const startAutoPlay = () => {
  if (autoPlayInterval) return
  autoPlayInterval = window.setInterval(() => {
    if (isAutoPlaying.value) {
      nextAd()
    }
  }, 5000) // Change ad every 5 seconds
}

const stopAutoPlay = () => {
  if (autoPlayInterval) {
    clearInterval(autoPlayInterval)
    autoPlayInterval = null
  }
}

const resetAutoPlay = () => {
  stopAutoPlay()
  startAutoPlay()
}

const toggleAutoPlay = () => {
  isAutoPlaying.value = !isAutoPlaying.value
}

onMounted(() => {
  fetchApprovedAdvertisements()
  startAutoPlay()
})

onUnmounted(() => {
  stopAutoPlay()
})

// Navigate to signup with enterprise role
const goToEnterpriseSignup = () => {
  router.push({ path: '/signup', query: { role: 'enterprise' } })
}
</script>

<template>
  <section class="hero-section">
    <div class="hero-background">
      <div class="hero-overlay"></div>
    </div>

    <div class="hero-container">
      <!-- Left Content -->
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-icon"><i class="fas fa-trophy"></i></span>
          <span>#1 Pickleball Platform in Vietnam</span>
        </div>

        <h1 class="hero-title">
          <span class="title-line">Welcome to</span>
          <span class="title-brand">NP SPORTCLUB</span>
        </h1>

        <h2 class="hero-subtitle">
          Book Your Dream Court<br />
          <span class="highlight">Anytime, Anywhere</span>
        </h2>

        <p class="hero-description">
          🎯 Vietnam's <strong>#1 Pickleball Platform</strong> - Discover premium courts, connect
          with passionate players, and experience hassle-free booking in seconds. From beginner to
          pro, we've got the perfect court for you!
        </p>

        <!-- Features Grid -->
        <div class="hero-features">
          <div class="feature-item">
            <div class="feature-icon"><i class="fas fa-building"></i></div>
            <div class="feature-content">
              <span class="feature-number">100+</span>
              <span class="feature-label">Premium Courts</span>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon"><i class="fas fa-bolt"></i></div>
            <div class="feature-content">
              <span class="feature-number">24/7</span>
              <span class="feature-label">Instant Booking</span>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon"><i class="fas fa-users"></i></div>
            <div class="feature-content">
              <span class="feature-number">5K+</span>
              <span class="feature-label">Active Players</span>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon"><i class="fas fa-star"></i></div>
            <div class="feature-content">
              <span class="feature-number">4.9</span>
              <span class="feature-label">User Rating</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Advertisement Section -->
      <div class="hero-ad-section">
        <!-- Advertisement Carousel -->
        <div
          class="ad-carousel"
          @mouseenter="isAutoPlaying = false"
          @mouseleave="isAutoPlaying = true"
        >
          <transition name="slide" mode="out-in">
            <div class="ad-card" :key="currentAdIndex">
              <!-- Full Image Background -->
              <div class="ad-image-wrapper">
                <img
                  :src="advertisements[currentAdIndex].image"
                  :alt="advertisements[currentAdIndex].title"
                  class="ad-image"
                />
                <div class="ad-overlay"></div>

                <!-- Top Controls -->
                <div class="ad-top-bar">
                  <div class="ad-controls">
                    <span class="ad-counter"
                      >{{ currentAdIndex + 1 }}/{{ advertisements.length }}</span
                    >
                    <button
                      class="ad-autoplay-btn"
                      @click="toggleAutoPlay"
                      :title="isAutoPlaying ? 'Pause' : 'Play'"
                    >
                      <span v-if="isAutoPlaying">⏸</span>
                      <span v-else>▶</span>
                    </button>
                  </div>
                </div>

                <!-- Content Overlay at Bottom -->
                <div class="ad-content-overlay">
                  <div class="ad-header-mini">
                    <span class="ad-icon"><i class="fas fa-gift"></i></span>
                    <span class="ad-label">Hot Deals & Promotions</span>
                  </div>

                  <span class="company-badge">
                    <span class="badge-dot"></span>
                    {{ advertisements[currentAdIndex].company }}
                  </span>

                  <h4 class="ad-heading">{{ advertisements[currentAdIndex].title }}</h4>
                  <p class="ad-description">{{ advertisements[currentAdIndex].description }}</p>

                  <div class="ad-actions">
                    <a
                      :href="advertisements[currentAdIndex].link"
                      class="ad-cta-btn"
                      @click.prevent="handleAdClick(advertisements[currentAdIndex])"
                    >
                      <span>Get Detail</span>
                      <span class="btn-arrow">→</span>
                    </a>
                    <span class="ad-time"><i class="fas fa-clock"></i> Limited Time</span>
                  </div>
                </div>
              </div>
            </div>
          </transition>

          <!-- Navigation Arrows -->
          <button class="carousel-btn prev-btn" @click="prevAd" aria-label="Previous">
            <span>‹</span>
          </button>
          <button class="carousel-btn next-btn" @click="nextAd" aria-label="Next">
            <span>›</span>
          </button>
        </div>

        <!-- Carousel Indicators -->
        <div class="ad-indicators">
          <button
            v-for="(ad, index) in advertisements"
            :key="ad.id"
            class="indicator-dot"
            :class="{ active: currentAdIndex === index }"
            @click="goToAd(index)"
            :aria-label="`Go to ad ${index + 1}`"
          ></button>
        </div>

        <!-- Ad Info -->
        <div class="ad-footer">
          <p class="ad-info-text">
            <span class="info-icon"><i class="fas fa-briefcase"></i></span>
            Want to advertise here?
            <a @click.prevent="goToEnterpriseSignup" class="info-link" style="cursor: pointer"
              >Become a partner</a
            >
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ===== MAIN SECTION ===== */
.hero-section {
  position: relative;
  padding: 80px 40px 100px;
  overflow: hidden;
  min-height: 700px;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 50%, #a5d6a7 100%);
  z-index: -1;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(76, 175, 80, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(139, 195, 74, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 50% 20%, rgba(255, 255, 255, 0.5) 0%, transparent 40%);
}

.hero-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 60px;
  align-items: center;
}

/* ===== LEFT CONTENT ===== */
.hero-content {
  display: flex;
  flex-direction: column;
  gap: 28px;
  animation: fadeInLeft 0.8s ease;
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  color: white;
  padding: 14px 28px;
  border-radius: 50px;
  font-size: 0.95rem;
  font-weight: 700;
  width: fit-content;
  box-shadow: 0 6px 20px rgba(45, 80, 22, 0.3);
  animation: pulse 3s ease-in-out infinite;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.badge-icon {
  font-size: 1.2rem;
  animation: rotate 4s linear infinite;
  color: #ffd700;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    box-shadow: 0 6px 20px rgba(45, 80, 22, 0.3);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 8px 30px rgba(45, 80, 22, 0.5);
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.hero-title {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title-line {
  font-size: 1.3rem;
  color: #666;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.title-brand {
  font-size: 2.8rem;
  font-weight: 900;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 50%, #66bb6a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1px;
  text-shadow: 0 4px 20px rgba(74, 124, 44, 0.2);
}

.hero-subtitle {
  font-size: 3.8rem;
  color: #1a1a1a;
  font-weight: 900;
  line-height: 1.1;
  margin: 0;
  letter-spacing: -2px;
}

.highlight {
  background: linear-gradient(135deg, #4a7c2c 0%, #66bb6a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  display: inline-block;
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0%,
  100% {
    filter: brightness(1);
  }
  50% {
    filter: brightness(1.2);
  }
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: 12px;
  left: 0;
  right: 0;
  height: 18px;
  background: linear-gradient(90deg, rgba(102, 187, 106, 0.3) 0%, rgba(139, 195, 74, 0.2) 100%);
  z-index: -1;
  border-radius: 4px;
  animation: slideWidth 2s ease-in-out infinite;
}

@keyframes slideWidth {
  0%,
  100% {
    left: 0;
    right: 0;
  }
  50% {
    left: -5px;
    right: -5px;
  }
}

.hero-description {
  font-size: 1.2rem;
  color: #444;
  line-height: 1.85;
  margin: 0;
  font-weight: 500;
  max-width: 650px;
}

.hero-description strong {
  color: #2d5016;
  font-weight: 800;
}

/* ===== CTA BUTTONS ===== */
.cta-buttons {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

.btn-primary {
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  color: white;
  border: 2px solid transparent;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(45, 80, 22, 0.4);
}

.btn-secondary {
  background: white;
  color: #2d5016;
  border: 2px solid #2d5016;
}

.btn-secondary:hover {
  background: #2d5016;
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(45, 80, 22, 0.3);
}

.btn-icon {
  font-size: 1.2rem;
}

/* ===== FEATURES GRID ===== */
.hero-features {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 14px;
  background: white;
  padding: 18px 22px;
  border-radius: 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.feature-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  border-color: #4a7c2c;
}

.feature-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #4a7c2c 0%, #2d5016 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(74, 124, 44, 0.3);
  color: white;
}

.feature-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.feature-number {
  font-size: 1.4rem;
  font-weight: 800;
  color: #2d5016;
  line-height: 1;
}

.feature-label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 600;
}

/* ===== RIGHT ADVERTISEMENT SECTION ===== */
.hero-ad-section {
  animation: fadeInRight 0.8s ease;
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.ad-container {
  background: white;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 3px solid rgba(74, 124, 44, 0.2);
}

.ad-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 3px solid transparent;
  background:
    linear-gradient(white, white) padding-box,
    linear-gradient(90deg, #4a7c2c 0%, #66bb6a 100%) border-box;
  border-image: linear-gradient(90deg, #4a7c2c 0%, #66bb6a 100%) 1;
  border-bottom-style: solid;
}

.ad-header-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ad-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.4rem;
  font-weight: 900;
  color: #1a3a0f;
  margin: 0;
}

.ad-icon {
  font-size: 1.6rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.ad-counter {
  font-size: 0.85rem;
  color: #666;
  font-weight: 700;
  background: #f0f0f0;
  padding: 4px 12px;
  border-radius: 12px;
  width: fit-content;
}

.ad-autoplay-btn {
  width: 44px;
  height: 44px;
  border: 3px solid #4a7c2c;
  background: white;
  border-radius: 12px;
  color: #4a7c2c;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(74, 124, 44, 0.2);
}

.ad-autoplay-btn:hover {
  background: linear-gradient(135deg, #4a7c2c 0%, #66bb6a 100%);
  color: white;
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 6px 20px rgba(74, 124, 44, 0.4);
}

/* ===== ADVERTISEMENT CAROUSEL ===== */
.ad-carousel {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  min-height: 750px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
}

.ad-card {
  position: relative;
  height: 100%;
  min-height: 750px;
}

.ad-image-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 750px;
  overflow: hidden;
}

.ad-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.8s ease;
}

.ad-card:hover .ad-image {
  transform: scale(1.08);
}

.ad-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.3) 0%,
    rgba(0, 0, 0, 0.5) 50%,
    rgba(0, 0, 0, 0.85) 100%
  );
}

/* Top Bar Controls */
.ad-top-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 24px;
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  z-index: 10;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.4) 0%, transparent 100%);
}

.ad-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ad-counter {
  font-size: 0.9rem;
  color: white;
  font-weight: 800;
  background: rgba(255, 255, 255, 0.25);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.4);
}

.ad-autoplay-btn {
  width: 44px;
  height: 44px;
  border: 3px solid rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.ad-autoplay-btn:hover {
  background: rgba(255, 255, 255, 0.35);
  border-color: white;
  transform: scale(1.1);
}

/* Content Overlay */
.ad-content-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 32px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ad-header-mini {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.ad-icon {
  font-size: 1.4rem;
  animation: bounce 2s infinite;
  color: #ffd700;
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.ad-label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.company-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(74, 124, 44, 0.95);
  color: white;
  padding: 8px 18px;
  border-radius: 25px;
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  box-shadow: 0 4px 16px rgba(74, 124, 44, 0.5);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  width: fit-content;
}

.badge-dot {
  width: 8px;
  height: 8px;
  background: #66bb6a;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
  box-shadow: 0 0 8px #66bb6a;
}

.ad-heading {
  font-size: 2rem;
  font-weight: 900;
  color: white;
  margin: 0;
  line-height: 1.2;
  letter-spacing: -0.5px;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.ad-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.6;
  margin: 0;
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

.ad-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.ad-time {
  font-size: 0.9rem;
  color: #ffed4e;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 6px;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
}

.ad-cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: white;
  color: #2d5016;
  padding: 16px 36px;
  border-radius: 50px;
  font-weight: 900;
  font-size: 1.05rem;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 8px 24px rgba(255, 255, 255, 0.3);
  border: 3px solid white;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.ad-cta-btn:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 12px 32px rgba(255, 255, 255, 0.5);
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  gap: 16px;
}

.btn-arrow {
  font-size: 1.4rem;
  transition: transform 0.3s ease;
  font-weight: 900;
}

.ad-cta-btn:hover .btn-arrow {
  transform: translateX(6px);
}

/* ===== CAROUSEL NAVIGATION ===== */
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.3);
  border: 3px solid rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  color: white;
  font-size: 2rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 15;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.carousel-btn:hover {
  background: rgba(255, 255, 255, 0.9);
  color: #2d5016;
  border-color: white;
  transform: translateY(-50%) scale(1.15);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.4);
}

.prev-btn {
  left: 20px;
}

.next-btn {
  right: 20px;
}

/* ===== CAROUSEL INDICATORS ===== */
.ad-indicators {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
  padding: 0;
}

.indicator-dot {
  width: 12px;
  height: 12px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.indicator-dot:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: scale(1.3);
}

.indicator-dot.active {
  background: white;
  width: 36px;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.5);
}

/* ===== AD FOOTER ===== */
.ad-footer {
  margin-top: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.ad-info-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #666;
  margin: 0;
  text-align: center;
}

.info-icon {
  font-size: 1.1rem;
}

.info-link {
  color: #4a7c2c;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.3s ease;
}

.info-link:hover {
  color: #2d5016;
  text-decoration: underline;
}

/* ===== SLIDE TRANSITION ===== */
.slide-enter-active {
  transition: all 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.slide-leave-active {
  transition: all 0.4s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(50px) scale(0.95);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-50px) scale(0.95);
}

/* ===== RESPONSIVE DESIGN ===== */
@media (max-width: 1200px) {
  .hero-container {
    grid-template-columns: 1fr;
    gap: 50px;
  }

  .hero-subtitle {
    font-size: 3rem;
  }

  .ad-carousel {
    min-height: 450px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 60px 20px 80px;
  }

  .hero-subtitle {
    font-size: 2.5rem;
  }

  .title-brand {
    font-size: 2.2rem;
  }

  .title-line {
    font-size: 1.1rem;
  }

  .hero-description {
    font-size: 1.05rem;
  }

  .cta-buttons {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
    justify-content: center;
  }

  .hero-features {
    grid-template-columns: 1fr;
  }

  .ad-image-wrapper {
    height: 250px;
  }

  .ad-carousel {
    min-height: 420px;
  }

  .carousel-btn {
    width: 40px;
    height: 40px;
    font-size: 1.4rem;
  }

  .prev-btn {
    left: 10px;
  }

  .next-btn {
    right: 10px;
  }

  .ad-badges {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .ad-badge-discount {
    font-size: 0.85rem;
    padding: 8px 14px;
  }
}

@media (max-width: 480px) {
  .hero-badge {
    font-size: 0.8rem;
    padding: 10px 18px;
  }

  .hero-subtitle {
    font-size: 2rem;
  }

  .title-brand {
    font-size: 1.8rem;
  }

  .ad-heading {
    font-size: 1.3rem;
  }

  .ad-description {
    font-size: 0.95rem;
  }

  .feature-icon {
    width: 45px;
    height: 45px;
    font-size: 1.3rem;
  }

  .feature-number {
    font-size: 1.2rem;
  }

  .ad-image-wrapper,
  .ad-carousel,
  .ad-card {
    min-height: 550px;
  }

  .ad-top-bar {
    padding: 12px;
  }

  .ad-controls {
    justify-content: space-between;
  }

  .ad-content-overlay {
    padding: 20px;
  }

  .ad-heading {
    font-size: 1.3rem;
  }

  .ad-description {
    font-size: 0.95rem;
  }

  .ad-cta-btn {
    width: 100%;
    justify-content: center;
    padding: 14px 24px;
    font-size: 0.9rem;
  }

  .ad-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .carousel-btn {
    width: 40px;
    height: 40px;
    font-size: 1.3rem;
  }

  .prev-btn {
    left: 8px;
  }

  .next-btn {
    right: 8px;
  }
}
</style>
