<template>
  <div class="container">
    <div class="page-header">
      <h2>📊 Overview</h2>
      <button @click="refreshData" class="btn btn-primary">
        🔄 Refresh
      </button>
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
                  <th>Available</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in selectedOrder.items" :key="item.item_id">
                  <td>{{ item.item_id }}</td>
                  <td>{{ item.item_name || 'N/A' }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>
                    <span 
                      class="badge" 
                      :class="item.available ? 'badge-success' : 'badge-danger'"
                    >
                      {{ item.available ? 'Yes' : 'No' }}
                    </span>
                  </td>
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

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Dashboard',
  data() {
    return {
      loading: true,
      error: null,
      stats: {
        totalOrders: 0,
        activeOrders: 0,
        idlePersonnel: 0,
        enRoutePersonnel: 0
      },
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
      }
    }
  },
  computed: {
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
    }
  },
  mounted() {
    this.fetchDashboardData()
    // Auto-refresh every 5 seconds
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
      if (!silent) this.loading = true
      this.error = null

      try {
        const [orders, activeOrders, idlePersons, enRoutePersons, stock, deliveries] = await Promise.all([
          api.getAllOrders(),
          api.getActiveOrders(),
          api.getIdlePersons(),
          api.getEnRoutePersons(),
          api.getCurrentStock(),
          api.getAllDeliveries()
        ])

        this.stats.totalOrders = orders.data.length
        this.stats.activeOrders = activeOrders.data.length
        this.stats.idlePersonnel = idlePersons.data.length
        this.stats.enRoutePersonnel = enRoutePersons.data.length

        // Store active orders with delivery person info
        this.activeOrdersData = activeOrders.data.map(order => {
          const delivery = deliveries.data.find(d => d.order_id === order.id)
          return {
            ...order,
            delivery_person_name: delivery?.delivery_person_name || 'Not Assigned'
          }
        })

        this.stockItems = stock.data

      } catch (err) {
        this.error = 'Failed to load dashboard data: ' + (err.response?.data?.error || err.message)
        console.error('Dashboard error:', err)
      } finally {
        this.loading = false
      }
    },
    refreshData() {
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

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
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
}

@media (max-width: 480px) {
  .active-orders-grid {
    grid-template-columns: 1fr;
  }
}
</style>
