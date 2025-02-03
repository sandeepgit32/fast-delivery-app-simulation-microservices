<template>
  <div class="graph-container">
    <div ref="graph"></div>
  </div>
</template>

<script>
import Plotly from 'plotly.js-dist'

export default {
  name: 'PlotlyGraph',
  data() {
    return {
      orderData: {
        completed: [],
        rejected: [],
        timestamps: []
      }
    }
  },
  methods: {
    async fetchStats() {
      try {
        const response = await fetch('http://localhost:5000/orders/stats')
        const data = await response.json()
        this.updateGraph(data)
      } catch (error) {
        console.error('Error fetching stats:', error)
      }
    },
    updateGraph(data) {
      const traces = [
        {
          x: this.orderData.timestamps,
          y: this.orderData.completed,
          name: 'Completed Orders',
          type: 'scatter'
        },
        {
          x: this.orderData.timestamps,
          y: this.orderData.rejected,
          name: 'Rejected Orders',
          type: 'scatter'
        }
      ]

      const layout = {
        title: 'Order Statistics',
        height: 400,
        xaxis: { title: 'Time' },
        yaxis: { title: 'Orders' }
      }

      Plotly.newPlot(this.$refs.graph, traces, layout)
    }
  },
  mounted() {
    this.fetchStats()
    setInterval(this.fetchStats, 5000)
  }
}
</script>

<style scoped>
.graph-container {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
