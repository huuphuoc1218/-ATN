<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family:
    'Inter',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    'Helvetica Neue',
    Arial,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #ffffff;
  color: #333;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 12px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #4a7c2c 0%, #2d5016 100%);
  border-radius: 6px;
}

::-webkit-scrollbar-thumb:hover {
  background: #2d5016;
}

/* Selection */
::selection {
  background: #4a7c2c;
  color: white;
}

/* Smooth Scroll */
html {
  scroll-behavior: smooth;
}

/* Button Reset */
button {
  font-family: inherit;
}

/* Link Reset */
a {
  color: inherit;
  text-decoration: none;
}
</style>
