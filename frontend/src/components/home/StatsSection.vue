<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Stat {
  image: string
  title: string
  value: string
  description: string
}

const stats = ref<Stat[]>([
  {
    image: 'https://i.pinimg.com/1200x/97/ec/0a/97ec0a1b0daedcb7439d18da17ced144.jpg',
    title: 'COURTS',
    value: '100+',
    description: 'Top-quality courts for your Pickleball game.',
  },
  {
    image: 'https://i.pinimg.com/1200x/6c/7d/60/6c7d60f66a26b050bb7aae75b2b47539.jpg',
    title: 'CUSTOMERS',
    value: '4500+',
    description: 'Your game starts here',
  },
])

const additionalStats = ref([
  { number: '98%', label: 'Customer Satisfaction', icon: 'fas fa-smile' },
  { number: '24/7', label: 'Customer Support', icon: 'fas fa-headset' },
  { number: '50+', label: 'Locations', icon: 'fas fa-map-marker-alt' },
  { number: '15k+', label: 'Monthly Bookings', icon: 'fas fa-calendar-check' },
])

const isVisible = ref(false)

onMounted(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          isVisible.value = true
        }
      })
    },
    { threshold: 0.2 },
  )

  const section = document.querySelector('.stats-section')
  if (section) observer.observe(section)
})
</script>

<template>
  <section class="stats-section">
    <!-- Main Stats Cards -->
    <div class="stats-container">
      <div
        v-for="(stat, index) in stats"
        :key="index"
        class="stat-card"
        :class="{ animate: isVisible }"
        :style="{ animationDelay: `${index * 0.2}s` }"
      >
        <div class="stat-image">
          <img :src="stat.image" :alt="stat.title" />
          <div class="stat-overlay">
            <div class="stat-content">
              <h3 class="stat-title">{{ stat.title }}</h3>
              <div class="stat-value">{{ stat.value }}</div>
              <p class="stat-description">{{ stat.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Additional Stats Grid -->
    <div class="additional-stats">
      <div class="stats-grid">
        <div
          v-for="(stat, index) in additionalStats"
          :key="index"
          class="mini-stat"
          :class="{ animate: isVisible }"
          :style="{ animationDelay: `${0.4 + index * 0.1}s` }"
        >
          <div class="mini-stat-icon"><i :class="stat.icon"></i></div>
          <div class="mini-stat-number">{{ stat.number }}</div>
          <div class="mini-stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- CTA Section -->
    <div class="cta-section">
      <div class="cta-content">
        <h2 class="cta-title">Ready to Start Playing?</h2>
        <p class="cta-description">
          Join thousands of players who trust us for their Pickleball experience
        </p>
        <div class="cta-buttons">
          <button class="cta-btn primary">
            <span class="btn-icon">🎾</span>
            <span>Book a Court Now</span>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.stats-section {
  padding: 100px 40px;
  background: linear-gradient(180deg, #f5f5f5 0%, #e8f5e9 100%);
  position: relative;
  overflow: hidden;
}

.stats-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(to bottom, white, transparent);
  pointer-events: none;
}

.stats-container {
  max-width: 1400px;
  margin: 0 auto 60px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 40px;
}

.stat-card {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  height: 450px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0;
  transform: translateY(50px);
}

.stat-card.animate {
  opacity: 1;
  transform: translateY(0);
}

.stat-card:hover {
  transform: translateY(-12px) scale(1.02);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
}

.stat-image {
  width: 100%;
  height: 100%;
  position: relative;
}

.stat-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.7s;
}

.stat-card:hover .stat-image img {
  transform: scale(1.1);
}

.stat-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.2) 0%,
    rgba(45, 80, 22, 0.8) 70%,
    rgba(45, 80, 22, 0.95) 100%
  );
  display: flex;
  align-items: flex-end;
  padding: 50px;
  transition: background 0.3s;
}

.stat-card:hover .stat-overlay {
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.3) 0%,
    rgba(45, 80, 22, 0.9) 60%,
    rgba(45, 80, 22, 1) 100%
  );
}

.stat-content {
  color: white;
  width: 100%;
}

.stat-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  display: inline-block;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.stat-title {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0 0 12px 0;
  letter-spacing: 3px;
  opacity: 0.9;
}

.stat-value {
  font-size: 5rem;
  font-weight: 900;
  margin: 0 0 16px 0;
  line-height: 1;
  background: linear-gradient(135deg, #ffffff 0%, #c8e6c9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-description {
  font-size: 1.15rem;
  margin: 0;
  opacity: 0.9;
  line-height: 1.6;
  font-weight: 500;
}

.additional-stats {
  max-width: 1400px;
  margin: 0 auto 80px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 32px;
}

.mini-stat {
  background: white;
  padding: 40px 32px;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.4s;
  border: 2px solid transparent;
  opacity: 0;
  transform: translateY(30px);
}

.mini-stat.animate {
  opacity: 1;
  transform: translateY(0);
}

.mini-stat:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 45px rgba(0, 0, 0, 0.15);
  border-color: #4a7c2c;
}

.mini-stat-icon {
  font-size: 3rem;
  margin-bottom: 20px;
  color: #4a7c2c;
}

.mini-stat-number {
  font-size: 3.5rem;
  font-weight: 900;
  color: #2d5016;
  margin-bottom: 12px;
  line-height: 1;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.mini-stat-label {
  font-size: 1.05rem;
  color: #666;
  font-weight: 600;
  line-height: 1.4;
}

.cta-section {
  max-width: 1200px;
  margin: 0 auto;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  border-radius: 32px;
  padding: 80px 60px;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(45, 80, 22, 0.3);
}

.cta-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
}

.cta-section::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 70%);
  border-radius: 50%;
}

.cta-content {
  position: relative;
  z-index: 1;
}

.cta-title {
  font-size: 3.5rem;
  color: white;
  font-weight: 900;
  margin: 0 0 20px 0;
  letter-spacing: -1px;
}

.cta-description {
  font-size: 1.3rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 40px 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.cta-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-btn {
  padding: 20px 40px;
  border: none;
  border-radius: 14px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.cta-btn.primary {
  background: white;
  color: #2d5016;
}

.cta-btn.primary:hover {
  background: #f0f0f0;
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
}

.cta-btn.secondary {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 2px solid white;
  backdrop-filter: blur(10px);
}

.cta-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
}

.btn-icon {
  font-size: 1.4rem;
}

@media (max-width: 1024px) {
  .stats-container {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .stat-card {
    height: 450px;
  }

  .cta-title {
    font-size: 2.5rem;
  }

  .cta-description {
    font-size: 1.15rem;
  }
}

@media (max-width: 768px) {
  .stats-section {
    padding: 60px 20px;
  }

  .stats-container {
    gap: 20px;
  }

  .stat-card {
    height: 380px;
  }

  .stat-overlay {
    padding: 28px;
  }

  .stat-value {
    font-size: 3.5rem;
  }

  .stat-label {
    font-size: 1.15rem;
  }

  .stat-description {
    font-size: 0.95rem;
  }

  .mini-stats-grid {
    gap: 20px;
  }

  .mini-stat-number {
    font-size: 2.25rem;
  }

  .mini-stat-label {
    font-size: 0.9rem;
  }

  .cta-section {
    padding: 50px 28px;
    border-radius: 20px;
  }

  .cta-title {
    font-size: 2rem;
  }

  .cta-description {
    font-size: 1.05rem;
  }

  .cta-buttons {
    gap: 12px;
  }

  .cta-btn {
    padding: 14px 28px;
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .stats-section {
    padding: 40px 16px;
  }

  .stat-card {
    height: 320px;
  }

  .stat-overlay {
    padding: 24px;
  }

  .stat-value {
    font-size: 3rem;
  }

  .stat-label {
    font-size: 1rem;
  }

  .stat-description {
    font-size: 0.9rem;
  }

  .mini-stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .mini-stat-card {
    padding: 16px;
  }

  .mini-stat-number {
    font-size: 2rem;
  }

  .mini-stat-label {
    font-size: 0.85rem;
  }

  .cta-section {
    padding: 40px 20px;
    border-radius: 16px;
  }

  .cta-title {
    font-size: 1.75rem;
  }

  .cta-description {
    font-size: 1rem;
  }

  .cta-buttons {
    flex-direction: column;
    width: 100%;
  }

  .cta-btn {
    width: 100%;
    padding: 12px 24px;
    font-size: 0.95rem;
  }

  .btn-icon {
    font-size: 1.2rem;
  }
}
</style>
