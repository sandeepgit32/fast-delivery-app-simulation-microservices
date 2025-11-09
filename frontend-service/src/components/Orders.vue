<template>
  <div class="container">
    <div class="page-header">
      <h2>📦 Orders Management</h2>
      <div class="header-actions">
        <button @click="showCreateModal = true" class="btn btn-primary">
          ➕ Create Order
        </button>
        <button @click="refreshOrders" class="btn btn-primary">
          🔄 Refresh
        </button>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <button 
        @click="currentFilter = 'all'" 
        :class="{ active: currentFilter === 'all' }"
        class="tab-btn"
      >
        All Orders ({{ allOrders.length }})
      </button>
      <button 
        @click="currentFilter = 'active'" 
        :class="{ active: currentFilter === 'active' }"
        class="tab-btn"
      >
        Active ({{ activeOrders.length }})
      </button>
      <button 
        @click="currentFilter = 'completed'" 
        :class="{ active: currentFilter === 'completed' }"
        class="tab-btn"
      >
        Completed ({{ completedOrders.length }})
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else class="card">
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer Name</th>
              <th>Phone</th>
              <th>Address</th>
              <th>Status</th>
              <th>Message</th>
              <th>Created At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredOrders.length === 0">
              <td colspan="8" style="text-align: center; color: #94a3b8; padding: 40px;">
                No orders found
              </td>
            </tr>
            <tr v-for="order in filteredOrders" :key="order.order_id">
              <td><strong>#{{ order.order_id }}</strong></td>
              <td>{{ order.customer_name }}</td>
              <td>{{ order.customer_phone }}</td>
              <td>{{ order.customer_address }}</td>
              <td>
                <span 
                  class="badge" 
                  :class="{
                    'badge-success': order.status === 'completed',
                    'badge-warning': order.status === 'confirmed',
                    'badge-info': order.status === 'pending',
                    'badge-danger': order.status === 'cancelled'
                  }"
                >
                  {{ order.status }}
                </span>
              </td>
              <td>{{ order.message || '-' }}</td>
              <td>{{ formatDate(order.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button 
                    @click="viewOrderDetails(order.order_id)" 
                    class="btn btn-sm btn-primary"
                    title="View Details"
                  >
                    👁️
                  </button>
                  <button 
                    v-if="order.status !== 'completed' && order.status !== 'cancelled'"
                    @click="closeOrder(order.order_id)" 
                    class="btn btn-sm btn-success"
                    title="Mark as Completed"
                  >
                    ✅
                  </button>
                  <button 
                    v-if="order.status !== 'completed' && order.status !== 'cancelled'"
                    @click="cancelOrder(order.order_id)" 
                    class="btn btn-sm btn-danger"
                    title="Cancel Order"
                  >
                    ❌
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Order Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Create New Order</h3>
          <button @click="showCreateModal = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Customer Name *</label>
            <input v-model="newOrder.customer_name" type="text" placeholder="Enter customer name" />
          </div>
          <div class="form-group">
            <label>Customer Phone *</label>
            <input v-model="newOrder.customer_phone" type="text" placeholder="Enter phone number" />
          </div>
          <div class="form-group">
            <label>Customer Address *</label>
            <textarea v-model="newOrder.customer_address" placeholder="Enter delivery address" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Items *</label>
            <div v-for="(item, index) in newOrder.items" :key="index" class="item-row">
              <input 
                v-model.number="item.item_id" 
                type="number" 
                placeholder="Item ID" 
                class="item-input"
              />
              <input 
                v-model.number="item.quantity" 
                type="number" 
                placeholder="Quantity" 
                class="item-input"
              />
              <button @click="removeItem(index)" class="btn btn-sm btn-danger">Remove</button>
            </div>
            <button @click="addItem" class="btn btn-sm btn-primary" style="margin-top: 8px;">
              ➕ Add Item
            </button>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showCreateModal = false" class="btn btn-secondary">Cancel</button>
          <button @click="createOrder" class="btn btn-primary">Create Order</button>
        </div>
      </div>
    </div>

    <!-- Order Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click.self="showDetailsModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Order Details - #{{ selectedOrder?.order_id }}</h3>
          <button @click="showDetailsModal = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body" v-if="selectedOrder">
          <div class="detail-grid">
            <div class="detail-item">
              <strong>Customer:</strong> {{ selectedOrder.customer_name }}
            </div>
            <div class="detail-item">
              <strong>Phone:</strong> {{ selectedOrder.customer_phone }}
            </div>
            <div class="detail-item">
              <strong>Address:</strong> {{ selectedOrder.customer_address }}
            </div>
            <div class="detail-item">
              <strong>Status:</strong> 
              <span 
                class="badge" 
                :class="{
                  'badge-success': selectedOrder.status === 'completed',
                  'badge-warning': selectedOrder.status === 'confirmed',
                  'badge-info': selectedOrder.status === 'pending',
                  'badge-danger': selectedOrder.status === 'cancelled'
                }"
              >
                {{ selectedOrder.status }}
              </span>
            </div>
            <div class="detail-item">
              <strong>Created:</strong> {{ formatDate(selectedOrder.created_at) }}
            </div>
            <div class="detail-item">
              <strong>Message:</strong> {{ selectedOrder.message || 'N/A' }}
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
          <button @click="showDetailsModal = false" class="btn btn-primary">Close</button>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Orders',
  data() {
    return {
      loading: true,
      error: null,
      successMessage: null,
      allOrders: [],
      activeOrders: [],
      completedOrders: [],
      currentFilter: 'all',
      showCreateModal: false,
      showDetailsModal: false,
      selectedOrder: null,
      newOrder: {
        customer_name: '',
        customer_phone: '',
        customer_address: '',
        items: [{ item_id: 1, quantity: 1 }]
      }
    }
  },
  computed: {
    filteredOrders() {
      if (this.currentFilter === 'active') return this.activeOrders
      if (this.currentFilter === 'completed') return this.completedOrders
      return this.allOrders
    }
  },
  mounted() {
    this.fetchOrders()
  },
  methods: {
    async fetchOrders() {
      this.loading = true
      this.error = null

      try {
        const [all, active, completed] = await Promise.all([
          api.getAllOrders(),
          api.getActiveOrders(),
          api.getCompletedOrders()
        ])

        this.allOrders = all.data
        this.activeOrders = active.data
        this.completedOrders = completed.data
      } catch (err) {
        this.error = 'Failed to load orders: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
      }
    },
    async createOrder() {
      this.error = null
      this.successMessage = null

      try {
        await api.createOrder(this.newOrder)
        this.successMessage = 'Order created successfully!'
        this.showCreateModal = false
        this.newOrder = {
          customer_name: '',
          customer_phone: '',
          customer_address: '',
          items: [{ item_id: 1, quantity: 1 }]
        }
        await this.fetchOrders()
        setTimeout(() => this.successMessage = null, 3000)
      } catch (err) {
        this.error = 'Failed to create order: ' + (err.response?.data?.error || err.message)
      }
    },
    async closeOrder(orderId) {
      if (!confirm('Mark this order as completed?')) return

      try {
        await api.closeOrder(orderId)
        this.successMessage = 'Order closed successfully!'
        await this.fetchOrders()
        setTimeout(() => this.successMessage = null, 3000)
      } catch (err) {
        this.error = 'Failed to close order: ' + (err.response?.data?.error || err.message)
      }
    },
    async cancelOrder(orderId) {
      const message = prompt('Enter cancellation reason:')
      if (!message) return

      try {
        await api.cancelOrder(orderId, message)
        this.successMessage = 'Order cancelled successfully!'
        await this.fetchOrders()
        setTimeout(() => this.successMessage = null, 3000)
      } catch (err) {
        this.error = 'Failed to cancel order: ' + (err.response?.data?.error || err.message)
      }
    },
    async viewOrderDetails(orderId) {
      try {
        const response = await api.getOrder(orderId)
        this.selectedOrder = response.data
        this.showDetailsModal = true
      } catch (err) {
        this.error = 'Failed to load order details: ' + (err.response?.data?.error || err.message)
      }
    },
    addItem() {
      this.newOrder.items.push({ item_id: 1, quantity: 1 })
    },
    removeItem(index) {
      this.newOrder.items.splice(index, 1)
    },
    refreshOrders() {
      this.fetchOrders()
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
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid var(--border-color);
}

.tab-btn {
  padding: 12px 24px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
}

.tab-btn:hover {
  color: var(--primary-color);
}

.tab-btn.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.action-buttons {
  display: flex;
  gap: 8px;
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
  max-width: 600px;
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

.item-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.item-input {
  flex: 1;
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

.btn-secondary {
  background-color: var(--secondary-color);
  color: white;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
  }

  .filter-tabs {
    overflow-x: auto;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
