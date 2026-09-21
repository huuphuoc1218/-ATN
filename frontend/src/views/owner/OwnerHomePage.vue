<script setup lang="ts">
import AppHeader from '@/components/layout/AppHeader.vue'
import HeroSection from '@/components/home/HeroSection.vue'
import CourtList from '@/components/home/CourtList.vue'
import StatsSection from '@/components/home/StatsSection.vue'
import FAQSection from '@/components/home/FAQSection.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
</script>

<template>
  <div class="owner-home-page">
    <!-- Header cho Owner: Home, Court, Management + Time + Owner Name -->
    <AppHeader :show-management="true" />

    <HeroSection />

    <CourtList />
    <StatsSection />
    <FAQSection />
    <AppFooter />
  </div>
</template>

<style scoped>
.owner-home-page {
  min-height: 100vh;
}
</style>
