<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3 class="chart-title">📈 Active Orders Over Time</h3>
      <div class="chart-controls">
        <select v-model="selectedTimeRange" @change="onTimeRangeChange" class="time-range-select">
          <option value="15m">Last 15 mins</option>
          <option value="30m">Last 30 mins</option>
          <option value="1h">Last 1 hr</option>
          <option value="2h">Last 2 hrs</option>
          <option value="3h">Last 3 hrs</option>
          <option value="6h">Last 6 hrs</option>
          <option value="12h">Last 12 hrs</option>
          <option value="24h">Last 24 hrs</option>
        </select>
      </div>
    </div>
    <div class="chart-wrapper">
      <div v-if="loading" class="chart-loading">
        <div class="spinner"></div>
        <span>Loading metrics...</span>
      </div>
      <Line v-else :data="chartData" :options="chartOptions" />
    </div>
    <div class="chart-footer">
      <span class="auto-refresh-indicator">
        <span class="pulse-dot"></span>
        Auto-refreshing every 5 seconds
      </span>
      <span class="last-updated">
        Last updated: {{ lastUpdatedFormatted }}
      </span>
    </div>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import api from '../services/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

export default {
  name: 'ActiveOrdersChart',
  components: {
    Line
  },
  data() {
    return {
      selectedTimeRange: '15m', // Default 15 minutes
      dataPoints: [], // Array of { timestamp: Date, count: number }
      lastUpdated: null,
      isRefreshing: false,
      loading: true,
      refreshInterval: null
    }
  },
  computed: {
    // Check if time range is >= 30 minutes
    isLargeTimeWindow() {
      const largeTimeRanges = ['30m', '1h', '2h', '3h', '6h', '12h', '24h']
      return largeTimeRanges.includes(this.selectedTimeRange)
    },
    chartData() {
      return {
        labels: this.dataPoints.map(point => this.formatTime(point.timestamp)),
        datasets: [
          {
            label: 'Active Orders',
            data: this.dataPoints.map(point => point.count),
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            fill: true,
            stepped: 'before', // Staircase effect
            tension: 0,
            // Hide markers for time windows >= 30 min, show only on hover
            pointRadius: this.isLargeTimeWindow ? 0 : 4,
            pointHoverRadius: 6,
            pointBackgroundColor: '#6366f1',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            borderWidth: 2
          }
        ]
      }
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index'
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            padding: 12,
            cornerRadius: 8,
            displayColors: false,
            callbacks: {
              title: (context) => {
                const dataIndex = context[0].dataIndex
                if (this.dataPoints[dataIndex]) {
                  return this.formatFullTime(this.dataPoints[dataIndex].timestamp)
                }
                return ''
              },
              label: (context) => {
                return `Active Orders: ${context.parsed.y}`
              }
            }
          }
        },
        scales: {
          x: {
            display: true,
            grid: {
              display: false
            },
            ticks: {
              maxRotation: 45,
              minRotation: 0,
              autoSkip: true,
              maxTicksLimit: 12,
              color: '#6b7280',
              font: {
                size: 11
              }
            }
          },
          y: {
            display: true,
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
              stepSize: 1,
              color: '#6b7280',
              font: {
                size: 11
              }
            },
            title: {
              display: true,
              text: 'Number of Orders',
              color: '#374151',
              font: {
                size: 12,
                weight: 'bold'
              }
            }
          }
        }
      }
    },
    lastUpdatedFormatted() {
      if (!this.lastUpdated) return 'Never'
      return this.formatFullTime(this.lastUpdated)
    }
  },
  mounted() {
    this.fetchMetricsFromAPI()
    // Auto-refresh every 5 seconds
    this.refreshInterval = setInterval(() => {
      this.fetchMetricsFromAPI(true)
    }, 5000)
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  methods: {
    async fetchMetricsFromAPI(silent = false) {
      try {
        if (!silent) this.loading = true
        
        const response = await api.getActiveOrdersMetrics(this.selectedTimeRange)
        
        if (response.data && response.data.data) {
          this.dataPoints = response.data.data.map(point => ({
            timestamp: new Date(point.timestamp),
            count: point.count
          }))
        }
        
        this.lastUpdated = new Date()
      } catch (err) {
        console.error('Failed to fetch metrics from API:', err)
        // If API fails, data will be empty but chart will still render
      } finally {
        this.loading = false
      }
    },
    async manualRefresh() {
      this.isRefreshing = true
      await this.fetchMetricsFromAPI(true)
      setTimeout(() => {
        this.isRefreshing = false
      }, 500)
    },
    onTimeRangeChange() {
      // Fetch new data for the selected time range
      this.fetchMetricsFromAPI()
    },
    formatTime(date) {
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
    },
    formatFullTime(date) {
      return date.toLocaleString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      })
    }
  }
}
</script>

<style scoped>
.chart-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-md);
  margin-bottom: 50px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.chart-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-range-select {
  padding: 8px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 140px;
}

.time-range-select:hover {
  border-color: var(--primary-color);
}

.time-range-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.chart-wrapper {
  height: 300px;
  position: relative;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: var(--text-secondary);
}

.chart-loading .spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.chart-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.auto-refresh-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: var(--success-color);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.last-updated {
  font-weight: 500;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .chart-controls {
    width: 100%;
    justify-content: space-between;
  }

  .time-range-select {
    flex: 1;
  }

  .chart-wrapper {
    height: 250px;
  }

  .chart-footer {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
}
</style>
