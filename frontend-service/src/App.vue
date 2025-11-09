<template>
  <div class="app-container">
    <nav class="navbar navbar-expand-lg navbar-dark">
      <div class="container-fluid px-4">
        <span class="navbar-brand">
          <i class="bi bi-box-seam"></i>
          Food Delivery System
        </span>
        <div class="navbar-nav">
          <router-link class="nav-link" to="/orders">
            <i class="bi bi-receipt"></i>
            Orders
          </router-link>
          <router-link class="nav-link" to="/delivery-persons">
            <i class="bi bi-person-badge"></i>
            Delivery Persons
          </router-link>
          <router-link class="nav-link" to="/stock">
            <i class="bi bi-box"></i>
            Stock
          </router-link>
        </div>
      </div>
    </nav>
    
    <div class="container-fluid px-4 py-4">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import PlotlyGraph from './components/PlotlyGraph.vue'
import SimulationControls from './components/SimulationControls.vue'

export default {
  name: 'App',
  components: {
    PlotlyGraph,
    SimulationControls
  }
}
</script>

<style>
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-attachment: fixed;
}

.navbar {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
}

.navbar-brand {
  color: #667eea !important;
  font-weight: 700;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.navbar-brand i {
  font-size: 1.8rem;
}

.nav-link {
  color: #4a5568 !important;
  font-weight: 500;
  margin: 0 0.5rem;
  padding: 0.5rem 1rem !important;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-link:hover {
  background-color: rgba(102, 126, 234, 0.1);
  color: #667eea !important;
  transform: translateY(-2px);
}

.nav-link.router-link-active {
  background-color: #667eea;
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.nav-link i {
  font-size: 1.2rem;
}
</style>
