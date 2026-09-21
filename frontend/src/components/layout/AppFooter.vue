<script setup lang="ts">
const currentYear = new Date().getFullYear()

const socialLinks = [
  { icon: 'fab fa-facebook-f', name: 'Facebook', url: 'https://facebook.com', color: '#1877F2' },
  { icon: 'fab fa-instagram', name: 'Instagram', url: 'https://instagram.com', color: '#E4405F' },
  { icon: 'fab fa-twitter', name: 'Twitter', url: 'https://twitter.com', color: '#1DA1F2' },
  { icon: 'fab fa-linkedin-in', name: 'LinkedIn', url: 'https://linkedin.com', color: '#0A66C2' },
]

const quickLinks = [
  { name: 'Home', url: '/' },
  { name: 'Court', url: '/court' },
  { name: 'About us', url: '/about' },
]
</script>

<template>
  <footer class="app-footer">
    <!-- Main Footer Content -->
    <div class="footer-main">
      <div class="footer-container">
        <!-- Company Info -->
        <div class="footer-section brand-section">
          <div class="footer-logo">
            <div class="logo-icon">
              <img src="/Logo.png" alt="Logo" />
            </div>
            <div class="logo-text">
              <span class="pickleball">Pickleball</span>
              <span class="brand">NP SPORTCLUB</span>
            </div>
          </div>
          <p class="brand-description">
            Your premier destination for Pickleball courts and facilities. Experience the best
            gameplay with top-quality courts and excellent service.
          </p>

          <!-- Social Links -->
          <div class="social-links">
            <a
              v-for="social in socialLinks"
              :key="social.name"
              :href="social.url"
              class="social-link"
              :title="social.name"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i :class="social.icon"></i>
            </a>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="footer-section">
          <h3 class="footer-title">Quick Links</h3>
          <ul class="footer-links">
            <li v-for="link in quickLinks" :key="link.name">
              <router-link :to="link.url" class="footer-link">
                {{ link.name }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Contact -->
        <div class="footer-section">
          <h3 class="footer-title">Contact Us</h3>
          <div class="contact-info">
            <div class="contact-item">
              <span class="contact-icon"><i class="fas fa-map-marker-alt"></i></span>
              <span>266 Ly Thuong Kiet, Dien Hong<br />Ward, HCMC</span>
            </div>
            <div class="contact-item">
              <span class="contact-icon"><i class="fas fa-envelope"></i></span>
              <a href="mailto:huuphuoc1218@gmail.com">huuphuoc1218@gmail.com</a>
            </div>
            <div class="contact-item">
              <span class="contact-icon"><i class="fas fa-phone"></i></span>
              <a href="tel:+84123948172">+84 123 948 172</a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Bottom -->
    <div class="footer-bottom">
      <div class="footer-container">
        <div class="footer-bottom-content">
          <p class="copyright">© {{ currentYear }} NP Sportclub. All rights reserved.</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: linear-gradient(135deg, #a8d5a8 0%, #8bc34a 100%);
  color: #1b5e20;
}

.footer-main {
  padding: 40px 40px 30px;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 40px;
}

.footer-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.brand-section {
  gap: 16px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 2px 6px rgba(45, 80, 22, 0.3));
  transition: transform 0.3s ease;
}

.logo-icon:hover {
  transform: scale(1.08);
}

.logo-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: brightness(1.05);
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.pickleball {
  font-size: 0.95rem;
  font-weight: 500;
  opacity: 0.9;
}

.brand {
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: 1.5px;
}

.brand-description {
  font-size: 1rem;
  line-height: 1.6;
  opacity: 0.9;
  margin: 0;
}

.social-links {
  display: flex;
  gap: 8px;
}

.social-link {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
  color: #1b5e20;
}

.social-link:hover {
  background: white;
  transform: translateY(-4px) scale(1.1);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  color: #2d5016;
}

.footer-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.4px;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-link {
  color: #1b5e20;
  text-decoration: none;
  font-size: 1rem;
  transition: all 0.3s;
  display: inline-block;
  font-weight: 500;
}

.footer-link:hover {
  color: #2d5016;
  transform: translateX(5px);
  font-weight: 600;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 1rem;
  line-height: 1.5;
}

.contact-icon {
  font-size: 1.15rem;
  flex-shrink: 0;
  color: #2d5016;
}

.contact-item a {
  color: #1b5e20;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.contact-item a:hover {
  color: #2d5016;
  text-decoration: underline;
}

.footer-bottom {
  background: rgba(0, 0, 0, 0.1);
  padding: 12px 24px;
  backdrop-filter: blur(10px);
}

.footer-bottom-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

.copyright {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
}

@media (max-width: 1024px) {
  .footer-container {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }
}

@media (max-width: 768px) {
  .footer-main {
    padding: 40px 20px 30px;
  }

  .footer-container {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .footer-bottom {
    padding: 16px 20px;
  }

  .footer-bottom-content {
    text-align: center;
  }
}

@media (max-width: 480px) {
  .footer-main {
    padding: 30px 14px 24px;
  }

  .footer-container {
    gap: 24px;
  }

  .logo-row {
    gap: 10px;
  }

  .logo-icon {
    width: 42px;
    height: 42px;
  }

  .company-name {
    font-size: 1.2rem;
  }

  .footer-description,
  .contact-item,
  .footer-link {
    font-size: 0.9rem;
  }

  .footer-bottom {
    padding: 12px 14px;
  }

  .copyright {
    font-size: 0.82rem;
    line-height: 1.4;
  }
}
</style>
