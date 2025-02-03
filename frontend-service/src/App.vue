<template>
  <div class="app-container">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <span class="navbar-brand">Food Delivery System</span>
        <div class="navbar-nav">
          <router-link class="nav-link" to="/orders">Orders</router-link>
          <router-link class="nav-link" to="/delivery-persons">Delivery Persons</router-link>
          <router-link class="nav-link" to="/stock">Stock</router-link>
        </div>
      </div>
    </nav>
    
    <div class="container mt-4">
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
.app-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}
.nav-link {
  color: #fff !important;
  margin-right: 1rem;
}
.nav-link.active {
  font-weight: bold;
}
</style>
