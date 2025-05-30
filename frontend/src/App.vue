<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <RouterView />
    </div>
</template>

<style>
/* Global Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f8f9fa;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
}

/* Bootstrap classes for grid system */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -0.5rem;
}

.col-md-3 {
  flex: 0 0 25%;
  padding: 0 0.5rem;
}

.col-md-8 {
  flex: 0 0 66.666667%;
  padding: 0 0.5rem;
}

.col-sm-6 {
  flex: 0 0 50%;
  padding: 0 0.5rem;
  }

.mb-4 {
  margin-bottom: 1.5rem;
  }

.text-center {
  text-align: center;
}

.justify-content-center {
  justify-content: center;
  }

/* Responsive adjustments */
@media (max-width: 768px) {
  .col-md-3,
  .col-md-8,
  .col-sm-6 {
    flex: 0 0 100%;
  }
  
  .container {
    padding: 0 0.5rem;
  }
}

@media (max-width: 576px) {
  .col-sm-6 {
    flex: 0 0 100%;
  }
}
</style>
