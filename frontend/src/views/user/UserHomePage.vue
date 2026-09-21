<script setup lang="ts">
import AppHeader from '@/components/layout/AppHeader.vue'
import HeroSection from '@/components/home/HeroSection.vue'
import CourtList from '@/components/home/CourtList.vue'
import StatsSection from '@/components/home/StatsSection.vue'
import FAQSection from '@/components/home/FAQSection.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
</script>

<template>
  <div class="user-home-page">
    <!-- Header cho User: Home, Court + Time + Username -->
    <AppHeader />

    <HeroSection />
    <CourtList />
    <StatsSection />
    <FAQSection />
    <AppFooter />
  </div>
</template>

<style scoped>
.user-home-page {
  min-height: 100vh;
}
</style>
