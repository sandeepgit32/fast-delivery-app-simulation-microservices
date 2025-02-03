<template>
  <div class="controls-container">
    <h4>Simulation Controls</h4>
    <div class="form-group">
      <label>Order Rate (orders/hour)</label>
      <input 
        type="number" 
        class="form-control" 
        v-model="orderRate"
        @change="updateSettings"
      >
    </div>
    <div class="form-group mt-3">
      <label>Number of Delivery Personnel</label>
      <input 
        type="number" 
        class="form-control" 
        v-model="deliveryPersonnel"
        @change="updateSettings"
      >
    </div>
    <div class="form-group mt-3">
      <label>Stock Limit</label>
      <input 
        type="number" 
        class="form-control" 
        v-model="stockLimit"
        @change="updateSettings"
      >
    </div>
    <button 
      class="btn btn-primary mt-3"
      @click="restartSimulation"
    >
      Restart Simulation
    </button>
  </div>
</template>

<script>
export default {
  name: 'SimulationControls',
  data() {
    return {
      orderRate: 10,
      deliveryPersonnel: 5,
      stockLimit: 100
    }
  },
  methods: {
    async updateSettings() {
      try {
        await fetch('http://localhost:5000/simulation/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            orderRate: this.orderRate,
            deliveryPersonnel: this.deliveryPersonnel,
            stockLimit: this.stockLimit
          })
        })
      } catch (error) {
        console.error('Error updating settings:', error)
      }
    },
    async restartSimulation() {
      try {
        await fetch('http://localhost:5000/simulation/restart', {
          method: 'POST'
        })
      } catch (error) {
        console.error('Error restarting simulation:', error)
      }
    }
  }
}
</script>

<style scoped>
.controls-container {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
