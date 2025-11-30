<template>
  <div class="container">
    <div class="page-header">
      <h2>📊 Overview</h2>
      <div class="header-buttons">
        <button @click="openSimulationModal" class="btn btn-success" :disabled="simulationRunning">
          ▶️ Start Simulation
        </button>
        <button @click="stopSimulation" class="btn btn-danger" :disabled="!simulationRunning">
          ⏹️ Stop Simulation
        </button>
        <button @click="refreshData" class="btn btn-primary">
          🔄 Refresh
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else>
      <!-- Statistics Cards -->
      <div class="grid grid-4" style="margin-bottom: 50px;">
        <div class="stat-card stat-primary">
          <div class="stat-icon">📦</div>
          <div class="stat-details">
            <div class="stat-label">Total Orders</div>
            <div class="stat-value">{{ stats.totalOrders }}</div>
          </div>
        </div>

        <div class="stat-card stat-success">
          <div class="stat-icon">✅</div>
          <div class="stat-details">
            <div class="stat-label">Active Orders</div>
            <div class="stat-value">{{ stats.activeOrders }}</div>
          </div>
        </div>

        <div class="stat-card stat-info">
          <div class="stat-icon">👥</div>
          <div class="stat-details">
            <div class="stat-label">Idle Personnel</div>
            <div class="stat-value">{{ stats.idlePersonnel }}</div>
          </div>
        </div>

        <div class="stat-card stat-warning">
          <div class="stat-icon">🚚</div>
          <div class="stat-details">
            <div class="stat-label">En Route</div>
            <div class="stat-value">{{ stats.enRoutePersonnel }}</div>
          </div>
        </div>
      </div>

      <!-- Active Orders Chart (Integrated) -->
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
          <div v-if="chartLoading" class="chart-loading">
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

      <!-- Active Orders -->
      <div class="card" style="margin-bottom: 50px;">
        <div class="card-header">
          <h3 class="card-title">Active Orders</h3>
          <router-link to="/orders" class="btn btn-sm btn-primary">View All Orders</router-link>
        </div>
        <div v-if="activeOrdersData.length === 0" class="empty-state">
          <div class="empty-icon">📦</div>
          <div class="empty-text">No active orders</div>
        </div>
        <div v-else class="active-orders-grid">
          <div 
            v-for="order in activeOrdersData" 
            :key="order.id" 
            class="order-card"
            @click="openOrderDetails(order.id)"
          >
            <div class="order-card-header">
              <span class="order-id">#{{ order.id }}</span>
            </div>
            <div class="order-card-time">
              {{ formatDate(order.order_time) }}
            </div>
            <div class="order-card-body">
              <div class="order-info-row">
                <div class="info-icon">👤</div>
                <div class="info-content">
                  <div class="info-label">Customer</div>
                  <div class="info-value">{{ order.customer_name }}</div>
                </div>
              </div>
              <div class="order-info-row">
                <div class="info-icon">📍</div>
                <div class="info-content">
                  <div class="info-label">Distance</div>
                  <div class="info-value">{{ order.customer_distance }} km</div>
                </div>
              </div>
              <div class="order-info-row">
                <div class="info-icon">🚚</div>
                <div class="info-content">
                  <div class="info-label">Delivery</div>
                  <div class="info-value">{{ order.delivery_person_name }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Stock Levels -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Stock Levels</h3>
          <router-link to="/stock" class="btn btn-sm btn-primary">Manage Stock</router-link>
        </div>
        <div class="stock-categories-grid">
          <!-- Red Category (Low Stock) -->
          <div class="stock-category">
            <div class="category-header category-red">
              <h4>Low Stock (&lt;{{ stockThresholds.medium }}%)</h4>
            </div>
            <div class="stock-column">
              <div 
                v-for="item in categorizedStock.low" 
                :key="item.item_id" 
                class="stock-item stock-low"
              >
                <div class="stock-item-name">{{ item.item_name }}</div>
                <div class="stock-item-quantity">
                  <span class="quantity-value">{{ item.quantity }}/{{ item.max_quantity }}</span>
                  <span class="quantity-label">({{ getStockPercentage(item.quantity, item.max_quantity) }}%)</span>
                </div>
                <div class="stock-item-bar">
                  <div 
                    class="stock-item-fill" 
                    :style="{ width: getStockPercentage(item.quantity, item.max_quantity) + '%' }"
                  ></div>
                </div>
              </div>
              <div v-if="categorizedStock.low.length === 0" class="empty-category">
                No items in this category
              </div>
            </div>
          </div>

          <!-- Yellow Category (Medium Stock) -->
          <div class="stock-category">
            <div class="category-header category-yellow">
              <h4>Medium Stock ({{ stockThresholds.medium }}%-{{ stockThresholds.high - 0.1 }}%)</h4>
            </div>
            <div class="stock-column">
              <div 
                v-for="item in categorizedStock.medium" 
                :key="item.item_id" 
                class="stock-item stock-medium"
              >
                <div class="stock-item-name">{{ item.item_name }}</div>
                <div class="stock-item-quantity">
                  <span class="quantity-value">{{ item.quantity }}/{{ item.max_quantity }}</span>
                  <span class="quantity-label">({{ getStockPercentage(item.quantity, item.max_quantity) }}%)</span>
                </div>
                <div class="stock-item-bar">
                  <div 
                    class="stock-item-fill" 
                    :style="{ width: getStockPercentage(item.quantity, item.max_quantity) + '%' }"
                  ></div>
                </div>
              </div>
              <div v-if="categorizedStock.medium.length === 0" class="empty-category">
                No items in this category
              </div>
            </div>
          </div>

          <!-- Green Category (High Stock) -->
          <div class="stock-category">
            <div class="category-header category-green">
              <h4>High Stock (≥{{ stockThresholds.high }}%)</h4>
            </div>
            <div class="stock-column">
              <div 
                v-for="item in categorizedStock.high" 
                :key="item.item_id" 
                class="stock-item stock-high"
              >
                <div class="stock-item-name">{{ item.item_name }}</div>
                <div class="stock-item-quantity">
                  <span class="quantity-value">{{ item.quantity }}/{{ item.max_quantity }}</span>
                  <span class="quantity-label">({{ getStockPercentage(item.quantity, item.max_quantity) }}%)</span>
                </div>
                <div class="stock-item-bar">
                  <div 
                    class="stock-item-fill" 
                    :style="{ width: getStockPercentage(item.quantity, item.max_quantity) + '%' }"
                  ></div>
                </div>
              </div>
              <div v-if="categorizedStock.high.length === 0" class="empty-category">
                No items in this category
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Order Details Modal -->
    <div v-if="showOrderDetailsModal" class="modal-overlay" @click.self="closeOrderDetailsModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Order Details - #{{ selectedOrder?.id }}</h3>
          <button @click="closeOrderDetailsModal" class="close-btn">✕</button>
        </div>
        <div class="modal-body" v-if="selectedOrder">
          <div class="detail-grid">
            <div class="detail-item">
              <strong>Customer:</strong> {{ selectedOrder.customer_name }}
            </div>
            <div class="detail-item">
              <strong>Distance:</strong> {{ selectedOrder.customer_distance }} km
            </div>
            <div class="detail-item">
              <strong>Status:</strong> 
              <span 
                class="badge" 
                :class="{
                  'badge-success': selectedOrder.order_status === 'completed',
                  'badge-warning': selectedOrder.order_status === 'confirmed',
                  'badge-info': selectedOrder.order_status === 'pending',
                  'badge-danger': selectedOrder.order_status === 'cancelled'
                }"
              >
                {{ selectedOrder.order_status }}
              </span>
            </div>
            <div class="detail-item">
              <strong>Order Time:</strong> {{ formatDate(selectedOrder.order_time) }}
            </div>
            <div class="detail-item">
              <strong>Delivery Time:</strong> {{ formatDate(selectedOrder.delivered_at) }}
            </div>
            <div class="detail-item">
              <strong>Message:</strong> {{ selectedOrder.response_msg || 'N/A' }}
            </div>
          </div>
          <div v-if="selectedOrder.items && selectedOrder.items.length > 0">
            <h4 style="margin-top: 20px; margin-bottom: 12px;">Order Items</h4>
            <table>
              <thead>
                <tr>
                  <th>Item ID</th>
                  <th>Item Name</th>
                  <th>Quantity</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in selectedOrder.items" :key="item.item_id">
                  <td>{{ item.item_id }}</td>
                  <td>{{ item.item_name || 'N/A' }}</td>
                  <td>{{ item.quantity }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeOrderDetailsModal" class="btn btn-primary">Close</button>
        </div>
      </div>
    </div>

    <!-- Simulation Settings Modal -->
    <div v-if="showSimulationModal" class="modal-overlay" @click.self="closeSimulationModal">
      <div class="modal simulation-modal">
        <div class="modal-header">
          <h3>⚙️ Simulation Settings</h3>
          <button @click="closeSimulationModal" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <p class="modal-description">Configure the order generation interval for the simulation.</p>
          <div class="form-group">
            <label for="orderIntervalMin">Minimum Interval (seconds)</label>
            <input 
              type="number" 
              id="orderIntervalMin" 
              v-model.number="orderIntervalMin" 
              min="1" 
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label for="orderIntervalMax">Maximum Interval (seconds)</label>
            <input 
              type="number" 
              id="orderIntervalMax" 
              v-model.number="orderIntervalMax" 
              min="1" 
              class="form-input"
            />
          </div>
          <div v-if="intervalError" class="alert alert-error" style="margin-top: 12px;">
            {{ intervalError }}
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeSimulationModal" class="btn btn-secondary">Cancel</button>
          <button @click="startSimulation" class="btn btn-success" :disabled="startingSimulation">
            {{ startingSimulation ? 'Starting...' : '▶️ Start Simulation' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>
  </div>
</template>

<script>
import api from '../services/api'
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
  name: 'Dashboard',
  components: {
    Line
  },
  data() {
    return {
      loading: true,
      chartLoading: true,
      error: null,
      stats: {
        totalOrders: 0,
        activeOrders: 0,
        idlePersonnel: 0,
        enRoutePersonnel: 0
      },
      isFetching: false,
      pendingRefresh: false,
      stockItems: [],
      activeOrdersData: [],
      showOrderDetailsModal: false,
      selectedOrder: null,
      refreshInterval: null,
      // Configurable stock level thresholds
      stockThresholds: {
        high: 50,    // >= 50% - Green
        medium: 25,  // >= 25% and < 50% - Yellow
        // < 25% - Red
      },
      // Simulation state
      showSimulationModal: false,
      simulationRunning: false,
      orderIntervalMin: 5,
      orderIntervalMax: 15,
      startingSimulation: false,
      intervalError: null,
      // Chart data
      selectedTimeRange: '15m',
      chartDataPoints: [],
      liveChartPoint: null,
      lastUpdated: null
    }
  },
  computed: {
    combinedChartPoints() {
      const historicalPoints = this.chartDataPoints || []
      const points = historicalPoints.map(point => ({ ...point }))

      if (this.liveChartPoint) {
        const lastPoint = points[points.length - 1]
        if (!lastPoint) {
          points.push({ ...this.liveChartPoint })
        } else {
          const lastTime = lastPoint.timestamp?.getTime?.() || new Date(lastPoint.timestamp).getTime()
          const liveTime = this.liveChartPoint.timestamp.getTime()
          if (lastTime === liveTime) {
            // Replace the last point if timestamps match to keep only the freshest value
            points[points.length - 1] = { ...this.liveChartPoint }
          } else if (liveTime > lastTime) {
            points.push({ ...this.liveChartPoint })
          }
        }
      }

      return points
    },
    categorizedStock() {
      const low = []
      const medium = []
      const high = []

      this.stockItems.forEach(item => {
        const percentage = this.getStockPercentage(item.quantity, item.max_quantity)
        if (percentage >= this.stockThresholds.high) {
          high.push(item)
        } else if (percentage >= this.stockThresholds.medium) {
          medium.push(item)
        } else {
          low.push(item)
        }
      })

      // Sort each category in ascending order by quantity
      const sortByQuantity = (a, b) => a.quantity - b.quantity

      return {
        low: low.sort(sortByQuantity),
        medium: medium.sort(sortByQuantity),
        high: high.sort(sortByQuantity)
      }
    },
    // Chart computed properties
    isLargeTimeWindow() {
      const largeTimeRanges = ['30m', '1h', '2h', '3h', '6h', '12h', '24h']
      return largeTimeRanges.includes(this.selectedTimeRange)
    },
    chartData() {
      const combinedPoints = this.combinedChartPoints
      const labels = combinedPoints.map(point => this.formatChartTime(point.timestamp))
      const historicalData = combinedPoints.map(point => point.count)
      const liveHighlightData = combinedPoints.map((point, index) => {
        if (!this.liveChartPoint) return null
        return index === combinedPoints.length - 1 ? point.count : null
      })

      const datasets = [
        {
          label: 'Active Orders',
          data: historicalData,
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99, 102, 241, 0.1)',
          fill: true,
          stepped: 'before',
          tension: 0,
          pointRadius: this.isLargeTimeWindow ? 0 : 4,
          pointHoverRadius: 6,
          pointBackgroundColor: '#6366f1',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          borderWidth: 2
        }
      ]

      if (this.liveChartPoint) {
        datasets.push({
          label: 'Current Snapshot',
          data: liveHighlightData,
          borderColor: '#10b981',
          borderWidth: 0,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: '#10b981',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          showLine: false,
          fill: false
        })
      }

      return {
        labels,
        datasets
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
                if (this.chartDataPoints[dataIndex]) {
                  return this.formatFullTime(this.chartDataPoints[dataIndex].timestamp)
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
    this.fetchDashboardData()
    this.checkSimulationStatus()
    // Auto-refresh every 5 seconds - all data fetched together synchronously
    this.refreshInterval = setInterval(() => {
      this.fetchDashboardData(true)
    }, 5000)
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  methods: {
    async fetchDashboardData(silent = false) {
      if (this.isFetching) {
        // Defer another refresh until the current one completes
        this.pendingRefresh = true
        return
      }
      this.isFetching = true
      if (!silent) {
        this.loading = true
        this.chartLoading = true
      }
      this.error = null

      try {
        // Fetch ALL data in a single Promise.all for true synchronization
        const [orders, activeOrders, idlePersons, enRoutePersons, stock, deliveries, metricsResponse] = await Promise.all([
          api.getAllOrders(),
          api.getActiveOrders(),
          api.getIdlePersons(),
          api.getEnRoutePersons(),
          api.getCurrentStock(),
          api.getAllDeliveries(),
          api.getActiveOrdersMetrics(this.selectedTimeRange)
        ])

        // Prepare all data before updating state
        const newActiveOrdersData = activeOrders.data.map(order => {
          const delivery = deliveries.data.find(d => d.order_id === order.id)
          return {
            ...order,
            delivery_person_name: delivery?.delivery_person_name || 'Not Assigned'
          }
        })

        let newChartDataPoints = []
        if (metricsResponse.data && metricsResponse.data.data) {
          newChartDataPoints = metricsResponse.data.data.map(point => ({
            timestamp: new Date(point.timestamp),
            count: point.count
          }))
        }

        const now = new Date()

        // Batch all state updates together
        // Replace entire stats object to trigger single reactive update
        this.stats = {
          totalOrders: orders.data.length,
          activeOrders: activeOrders.data.length,
          idlePersonnel: idlePersons.data.length,
          enRoutePersonnel: enRoutePersons.data.length
        }
        this.activeOrdersData = newActiveOrdersData
        this.stockItems = stock.data
        this.chartDataPoints = newChartDataPoints
        this.liveChartPoint = {
          timestamp: now,
          count: this.stats.activeOrders
        }
        this.lastUpdated = now

      } catch (err) {
        this.error = 'Failed to load dashboard data: ' + (err.response?.data?.error || err.message)
        console.error('Dashboard error:', err)
          this.liveChartPoint = null
      } finally {
        this.loading = false
        this.chartLoading = false
        this.isFetching = false
        if (this.pendingRefresh) {
          this.pendingRefresh = false
          // Fire-and-forget silent refresh with the latest data request queued
          this.fetchDashboardData(true)
        }
      }
    },
    refreshData() {
      this.fetchDashboardData()
    },
    onTimeRangeChange() {
      // Fetch new data when time range changes
      this.fetchDashboardData()
    },
    getStockPercentage(quantity, maxQuantity) {
      if (!maxQuantity || maxQuantity === 0) return 0
      return Math.round((quantity / maxQuantity) * 100)
    },
    getStockLevelClass(percentage) {
      if (percentage >= this.stockThresholds.high) {
        return 'stock-high'
      } else if (percentage >= this.stockThresholds.medium) {
        return 'stock-medium'
      } else {
        return 'stock-low'
      }
    },
    async openOrderDetails(orderId) {
      try {
        const response = await api.getOrder(orderId)
        this.selectedOrder = response.data
        this.showOrderDetailsModal = true
      } catch (err) {
        this.error = 'Failed to load order details: ' + (err.response?.data?.error || err.message)
      }
    },
    closeOrderDetailsModal() {
      this.showOrderDetailsModal = false
      this.selectedOrder = null
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    formatChartTime(date) {
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
    },
    async checkSimulationStatus() {
      try {
        const response = await api.getOrderInterval()
        this.simulationRunning = response.data.status === 'running'
        if (response.data.order_interval_min) {
          this.orderIntervalMin = response.data.order_interval_min
        }
        if (response.data.order_interval_max) {
          this.orderIntervalMax = response.data.order_interval_max
        }
      } catch (err) {
        console.error('Failed to check simulation status:', err)
      }
    },
    openSimulationModal() {
      this.showSimulationModal = true
      this.intervalError = null
    },
    closeSimulationModal() {
      this.showSimulationModal = false
      this.intervalError = null
    },
    async startSimulation() {
      // Validate intervals
      if (this.orderIntervalMin < 1 || this.orderIntervalMax < 1) {
        this.intervalError = 'Intervals must be at least 1 second'
        return
      }
      if (this.orderIntervalMin > this.orderIntervalMax) {
        this.intervalError = 'Minimum interval cannot be greater than maximum interval'
        return
      }

      this.startingSimulation = true
      this.intervalError = null

      try {
        // Set the order interval first
        await api.setOrderInterval(this.orderIntervalMin, this.orderIntervalMax)
        // Then start the simulation
        await api.startSimulation()
        this.simulationRunning = true
        this.closeSimulationModal()
      } catch (err) {
        this.intervalError = 'Failed to start simulation: ' + (err.response?.data?.error || err.message)
      } finally {
        this.startingSimulation = false
      }
    },
    async stopSimulation() {
      try {
        await api.stopSimulation()
        this.simulationRunning = false
      } catch (err) {
        this.error = 'Failed to stop simulation: ' + (err.response?.data?.error || err.message)
      }
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-header h2 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

/* Chart styles */
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

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: var(--shadow-md);
  border-left: 4px solid;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-primary {
  border-color: var(--primary-color);
}

.stat-success {
  border-color: var(--success-color);
}

.stat-info {
  border-color: var(--info-color);
}

.stat-warning {
  border-color: var(--warning-color);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-details {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stock-categories-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.stock-category {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-header {
  padding: 12px 16px;
  border-radius: 8px;
  text-align: center;
  font-weight: 600;
}

.category-header h4 {
  margin: 0;
  font-size: 0.95rem;
  color: white;
}

.category-red {
  background: var(--danger-color);
}

.category-yellow {
  background: var(--warning-color);
}

.category-green {
  background: var(--success-color);
}

.stock-column {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.empty-category {
  padding: 24px;
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  background: var(--bg-primary);
  border-radius: 8px;
  border: 2px dashed var(--border-color);
  grid-column: 1 / -1;
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.stock-item {
  background: var(--bg-primary);
  padding: 16px;
  border-radius: 8px;
  border: 2px solid var(--border-color);
  transition: all 0.3s ease;
}

.stock-item:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.stock-item.stock-high {
  border-color: var(--success-color);
}

.stock-item.stock-high .stock-item-fill {
  background: var(--success-color);
}

.stock-item.stock-medium {
  border-color: var(--warning-color);
  background: #fffbeb;
}

.stock-item.stock-medium .stock-item-fill {
  background: var(--warning-color);
}

.stock-item.stock-low {
  border-color: var(--danger-color);
  background: #fef2f2;
}

.stock-item.stock-low .stock-item-fill {
  background: var(--danger-color);
}

.stock-item-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  font-size: 14px;
}

.stock-item-quantity {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.quantity-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.quantity-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.stock-item-bar {
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
}

.stock-item-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 1.125rem;
  font-weight: 500;
}

.active-orders-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  padding: 20px;
}

.order-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.order-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color);
}

.order-card-header {
  background: linear-gradient(135deg, var(--primary-color), #4f46e5);
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-id {
  font-size: 1rem;
  font-weight: 700;
  color: white;
  letter-spacing: 0.5px;
}

.order-card-time {
  padding: 8px 16px;
  background: var(--bg-primary);
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
  text-align: center;
  border-bottom: 1px solid var(--border-color);
}

.order-card-body {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 16px;
}

.order-info-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
}

.order-info-row:not(:last-child) {
  border-bottom: 1px solid var(--border-color);
}

.info-icon {
  font-size: 1.25rem;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 2px;
}

.info-content {
  flex: 1;
  min-width: 0;
}

.info-label {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.info-value {
  font-size: 0.875rem;
  color: var(--text-primary);
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: white;
  border-radius: 12px;
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  padding: 24px;
  border-bottom: 2px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  padding: 24px;
  border-top: 2px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.detail-item {
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.detail-item strong {
  display: block;
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 4px;
}

@media (max-width: 1400px) {
  .active-orders-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1024px) {
  .active-orders-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.header-buttons {
  display: flex;
  gap: 12px;
}

.btn-success {
  background: var(--success-color);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.btn-danger {
  background: var(--danger-color);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-secondary {
  background: var(--text-secondary);
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.simulation-modal {
  max-width: 450px;
}

.modal-description {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-buttons {
    flex-wrap: wrap;
  }

  .page-header h2 {
    font-size: 1.5rem;
  }

  .stat-card {
    padding: 16px;
    gap: 12px;
  }

  .stat-icon {
    font-size: 2rem;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .stock-categories-grid {
    grid-template-columns: 1fr;
  }

  .stock-column {
    grid-template-columns: 1fr;
  }

  .active-orders-grid {
    grid-template-columns: repeat(2, 1fr);
  }

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

@media (max-width: 480px) {
  .active-orders-grid {
    grid-template-columns: 1fr;
  }
}
</style>
