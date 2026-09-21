<!-- filepath: c:\Users\PC\Desktop\DO_AN_TOT_NGHIEP\frontend\src\views\enterprise\EnterpriseHomePage.vue -->
<script setup lang="ts">
import AppHeader from '@/components/layout/AppHeader.vue'
import HeroSection from '@/components/home/HeroSection.vue'
import CourtList from '@/components/home/CourtList.vue'
import StatsSection from '@/components/home/StatsSection.vue'
import FAQSection from '@/components/home/FAQSection.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
</script>

<template>
  <div class="enterprise-home-page">
    <!-- Header cho Enterprise: Home, Court, Advertisement + Time + Enterprise Name -->
    <AppHeader :show-advertisement="true" />

    <HeroSection />
    <CourtList />
    <StatsSection />
    <FAQSection />
    <AppFooter />
  </div>
</template>

<style scoped>
.enterprise-home-page {
  min-height: 100vh;
}
</style>
