<template>
  <div class="stock-page">
    <div class="page-header">
      <div class="header-content">
        <h2><i class="bi bi-box"></i> Stock Management</h2>
        <p class="text-muted">Monitor and manage inventory levels</p>
      </div>
      <div class="stock-summary">
        <div class="summary-item">
          <div class="summary-label">Total Items</div>
          <div class="summary-value">{{ totalItems }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-label">Total Quantity</div>
          <div class="summary-value">{{ totalQuantity }}</div>
        </div>
      </div>
    </div>

    <div class="stock-grid">
      <div v-for="item in sortedStock" :key="item.id" class="stock-card">
        <div class="stock-card-header">
          <div class="product-icon">
            <i class="bi bi-box-seam"></i>
          </div>
          <h5 class="product-name">{{ item.name }}</h5>
        </div>
        <div class="stock-card-body">
          <div class="quantity-display">
            <div class="quantity-label">Current Stock</div>
            <div class="quantity-value" :class="getStockLevelClass(item.quantity)">
              {{ item.quantity }}
            </div>
          </div>
          <div class="stock-controls">
            <button class="btn btn-control btn-remove" @click="adjustStock(item, -1)" :disabled="item.quantity <= 0">
              <i class="bi bi-dash-circle"></i>
              Remove
            </button>
            <button class="btn btn-control btn-add" @click="adjustStock(item, 1)">
              <i class="bi bi-plus-circle"></i>
              Add
            </button>
          </div>
        </div>
        <div class="stock-card-footer" :class="getStockLevelClass(item.quantity)">
          <i :class="getStockIcon(item.quantity)"></i>
          {{ getStockLevelText(item.quantity) }}
        </div>
      </div>
      
      <div v-if="sortedStock.length === 0" class="empty-state">
        <i class="bi bi-inbox" style="font-size: 4rem;"></i>
        <p class="mt-3">No stock items found</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StockPage',
  data() {
    return {
      stock: []
    }
  },
  computed: {
    sortedStock() {
      return [...this.stock].sort((a, b) => 
        a.name.localeCompare(b.name)
      )
    },
    totalItems() {
      return this.stock.length
    },
    totalQuantity() {
      return this.stock.reduce((sum, item) => sum + item.quantity, 0)
    }
  },
  methods: {
    async fetchStock() {
      try {
        const response = await fetch('/api/current_stock')
        this.stock = await response.json()
      } catch (error) {
        console.error('Error fetching stock:', error)
      }
    },
    async adjustStock(item, amount) {
      try {
        const endpoint = amount > 0 ? '/add_stock' : '/remove_stock'
        await fetch(`/api${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            item_id: item.id,
            quantity: Math.abs(amount)
          })
        })
        await this.fetchStock()
      } catch (error) {
        console.error('Error adjusting stock:', error)
      }
    },
    getStockLevelClass(quantity) {
      if (quantity === 0) return 'stock-empty'
      if (quantity < 10) return 'stock-low'
      if (quantity < 30) return 'stock-medium'
      return 'stock-good'
    },
    getStockLevelText(quantity) {
      if (quantity === 0) return 'Out of Stock'
      if (quantity < 10) return 'Low Stock'
      if (quantity < 30) return 'Medium Stock'
      return 'In Stock'
    },
    getStockIcon(quantity) {
      if (quantity === 0) return 'bi bi-exclamation-circle'
      if (quantity < 10) return 'bi bi-exclamation-triangle'
      if (quantity < 30) return 'bi bi-info-circle'
      return 'bi bi-check-circle'
    }
  },
  mounted() {
    this.fetchStock()
    // Refresh data every 5 seconds
    this.interval = setInterval(this.fetchStock, 5000)
  },
  beforeUnmount() {
    if (this.interval) {
      clearInterval(this.interval)
    }
  }
}
</script>

<style scoped>
.stock-page {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  flex-wrap: wrap;
  gap: 1rem;
}

.header-content h2 {
  color: #2d3748;
  font-weight: 700;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-content p {
  margin: 0;
  font-size: 0.9rem;
}

.stock-summary {
  display: flex;
  gap: 2rem;
}

.summary-item {
  text-align: center;
}

.summary-label {
  font-size: 0.85rem;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.25rem;
}

.summary-value {
  font-size: 2rem;
  font-weight: 700;
  color: #667eea;
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.stock-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.stock-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stock-card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  text-align: center;
}

.product-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.product-name {
  margin: 0;
  font-weight: 700;
  font-size: 1.1rem;
}

.stock-card-body {
  padding: 1.5rem;
}

.quantity-display {
  text-align: center;
  margin-bottom: 1.5rem;
}

.quantity-label {
  font-size: 0.85rem;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.quantity-value {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
}

.quantity-value.stock-good {
  color: #48bb78;
}

.quantity-value.stock-medium {
  color: #ed8936;
}

.quantity-value.stock-low {
  color: #f56565;
}

.quantity-value.stock-empty {
  color: #e53e3e;
}

.stock-controls {
  display: flex;
  gap: 0.5rem;
}

.btn-control {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.btn-add {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
}

.btn-add:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(72, 187, 120, 0.4);
}

.btn-remove {
  background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
  color: white;
}

.btn-remove:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 101, 101, 0.4);
}

.btn-control:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stock-card-footer {
  padding: 1rem;
  text-align: center;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.stock-card-footer.stock-good {
  background-color: #c6f6d5;
  color: #22543d;
}

.stock-card-footer.stock-medium {
  background-color: #feebc8;
  color: #7c2d12;
}

.stock-card-footer.stock-low {
  background-color: #fed7d7;
  color: #742a2a;
}

.stock-card-footer.stock-empty {
  background-color: #feb2b2;
  color: #742a2a;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 4rem;
  color: #a0aec0;
}
</style>
