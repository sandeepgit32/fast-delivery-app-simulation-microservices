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

      <!-- Stock Levels -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Stock Levels</h3>
          <router-link to="/stock" class="btn btn-sm btn-primary">Manage Stock</router-link>
        </div>
        <div class="stock-grid">
          <div 
            v-for="item in stockItems" 
            :key="item.item_id" 
            class="stock-item"
            :class="{ 'low-stock': item.quantity < 10 }"
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
      refreshInterval: null
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
        const [orders, activeOrders, idlePersons, enRoutePersons, stock] = await Promise.all([
          api.getAllOrders(),
          api.getActiveOrders(),
          api.getIdlePersons(),
          api.getEnRoutePersons(),
          api.getCurrentStock()
        ])

        this.stats.totalOrders = orders.data.length
        this.stats.activeOrders = activeOrders.data.length
        this.stats.idlePersonnel = idlePersons.data.length
        this.stats.enRoutePersonnel = enRoutePersons.data.length

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

.stock-item.low-stock {
  border-color: var(--danger-color);
  background: #fef2f2;
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
  background: linear-gradient(90deg, var(--success-color), var(--primary-color));
  transition: width 0.3s ease;
}

.stock-item.low-stock .stock-item-fill {
  background: var(--danger-color);
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
}
</style>
