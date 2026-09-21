<script setup lang="ts">
import { ref } from 'vue'

interface FAQ {
  question: string
  answer: string
  isOpen: boolean
  icon: string
}

const faqs = ref<FAQ[]>([
  {
    question: 'How can I book a court?',
    answer:
      'You can book a court through our website or mobile app. Simply select your preferred date, time, and location. Our system provides real-time availability and instant confirmation.',
    isOpen: false,
    icon: '📅',
  },
  {
    question: 'What about locker room?',
    answer:
      'All our facilities include clean and secure locker rooms with showers and changing areas. We maintain high hygiene standards and provide complimentary toiletries.',
    isOpen: false,
    icon: '🚿',
  },
  {
    question: 'Can I rent equipment?',
    answer:
      'Yes, we offer equipment rental including paddles, balls, and other accessories at affordable rates. Professional-grade equipment is available for both beginners and advanced players.',
    isOpen: false,
    icon: '🎾',
  },
  {
    question: 'What are the payment options?',
    answer:
      'We accept various payment methods including credit/debit cards, e-wallets (Momo, ZaloPay), and bank transfers. Online payment is secure and encrypted.',
    isOpen: false,
    icon: '💳',
  },
  {
    question: 'Do you offer coaching services?',
    answer:
      'Yes, we have professional coaches available for private and group lessons. You can book coaching sessions along with your court booking.',
    isOpen: false,
    icon: '👨‍🏫',
  },
  {
    question: 'What is your cancellation policy?',
    answer:
      'You can cancel your booking up to 24 hours before the scheduled time for a full refund. Cancellations within 24 hours are subject to a 50% cancellation fee.',
    isOpen: false,
    icon: '🔄',
  },
])

const toggleFAQ = (index: number) => {
  faqs.value[index].isOpen = !faqs.value[index].isOpen
}
</script>

<template>
  <section class="faq-section">
    <div class="faq-container">
      <!-- Section Header -->
      <div class="section-header">
        <span class="section-badge">❓ FAQ</span>
        <h2 class="section-title">Frequently Asked <span class="highlight">Questions</span></h2>
        <p class="section-description">
          Find answers to common questions about our services and facilities
        </p>
      </div>

      <!-- FAQ Grid -->
      <div class="faq-grid">
        <div
          v-for="(faq, index) in faqs"
          :key="index"
          class="faq-item"
          :class="{ active: faq.isOpen }"
          @click="toggleFAQ(index)"
        >
          <div class="faq-question">
            <div class="question-left">
              <span class="faq-emoji">{{ faq.icon }}</span>
              <h3>{{ faq.question }}</h3>
            </div>
            <div class="faq-toggle">
              <span class="toggle-icon">{{ faq.isOpen ? '−' : '+' }}</span>
            </div>
          </div>

          <transition name="slide">
            <div v-if="faq.isOpen" class="faq-answer">
              <p>{{ faq.answer }}</p>
            </div>
          </transition>
        </div>
      </div>

      <!-- Contact CTA -->
      <div class="faq-cta">
        <div class="cta-card">
          <div class="cta-icon">💬</div>
          <h3>Still have questions?</h3>
          <p>Our customer support team is here to help you 24/7</p>
          <button class="contact-btn">Contact Support</button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.faq-section {
  padding: 100px 40px;
  background: white;
  position: relative;
}

.faq-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-badge {
  display: inline-block;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1565c0;
  padding: 10px 24px;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 20px;
}

.section-title {
  font-size: 3rem;
  color: #2d5016;
  font-weight: 900;
  margin: 0 0 16px 0;
  letter-spacing: -1px;
}

.highlight {
  color: #4a7c2c;
  position: relative;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: 4px;
  left: 0;
  right: 0;
  height: 12px;
  background: rgba(139, 195, 74, 0.3);
  z-index: -1;
}

.section-description {
  font-size: 1.2rem;
  color: #666;
  max-width: 600px;
  margin: 0 auto;
}

.faq-grid {
  display: grid;
  gap: 20px;
  margin-bottom: 60px;
}

.faq-item {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 16px;
  padding: 28px 32px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.faq-item:hover {
  border-color: #4a7c2c;
  box-shadow: 0 8px 30px rgba(74, 124, 44, 0.1);
  transform: translateY(-2px);
}

.faq-item.active {
  border-color: #4a7c2c;
  background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%);
  box-shadow: 0 8px 30px rgba(74, 124, 44, 0.15);
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.question-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.faq-emoji {
  font-size: 2rem;
  flex-shrink: 0;
}

.faq-question h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #2d5016;
  font-weight: 700;
  line-height: 1.4;
}

.faq-toggle {
  flex-shrink: 0;
}

.toggle-icon {
  width: 40px;
  height: 40px;
  border: 2px solid #4a7c2c;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: #4a7c2c;
  font-weight: 300;
  transition: all 0.3s;
  background: white;
}

.faq-item.active .toggle-icon {
  transform: rotate(180deg);
  background: #4a7c2c;
  color: white;
}

.faq-answer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #e8f5e9;
  overflow: hidden;
}

.faq-answer p {
  margin: 0;
  color: #555;
  line-height: 1.8;
  font-size: 1.05rem;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.faq-cta {
  margin-top: 60px;
}

.cta-card {
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  padding: 60px 40px;
  border-radius: 24px;
  text-align: center;
  color: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 15px 50px rgba(45, 80, 22, 0.3);
}

.cta-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
}

.cta-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

.cta-card h3 {
  font-size: 2.2rem;
  margin: 0 0 16px 0;
  font-weight: 800;
}

.cta-card p {
  font-size: 1.2rem;
  margin: 0 0 32px 0;
  opacity: 0.9;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.contact-btn {
  padding: 18px 48px;
  background: white;
  color: #2d5016;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
}

.contact-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
  background: #f0f0f0;
}

@media (max-width: 1024px) {
  .section-title {
    font-size: 2.25rem;
  }

  .faq-grid {
    gap: 16px;
  }

  .cta-card {
    padding: 50px 40px;
  }

  .cta-title {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .faq-section {
    padding: 60px 20px;
  }

  .section-title {
    font-size: 2rem;
  }

  .faq-grid {
    gap: 12px;
  }

  .faq-item {
    padding: 20px;
  }

  .faq-question h3 {
    font-size: 1.1rem;
  }

  .faq-emoji {
    font-size: 1.5rem;
    width: 40px;
    height: 40px;
  }

  .faq-answer {
    font-size: 0.95rem;
  }

  .cta-card {
    padding: 40px 24px;
  }

  .cta-title {
    font-size: 1.75rem;
  }

  .cta-description {
    font-size: 1rem;
  }

  .contact-btn {
    padding: 14px 28px;
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .faq-section {
    padding: 40px 16px;
  }

  .section-title {
    font-size: 1.75rem;
  }

  .faq-item {
    padding: 16px;
  }

  .faq-question h3 {
    font-size: 1rem;
  }

  .faq-emoji {
    font-size: 1.25rem;
    width: 36px;
    height: 36px;
  }

  .faq-answer {
    font-size: 0.9rem;
  }

  .cta-card {
    padding: 32px 20px;
  }

  .cta-title {
    font-size: 1.5rem;
  }

  .cta-description {
    font-size: 0.95rem;
  }

  .contact-btn {
    padding: 12px 24px;
    font-size: 0.95rem;
  }
}
</style>
