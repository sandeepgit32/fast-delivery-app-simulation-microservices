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
              <th @click="sortTable('id')" class="sortable">
                <div class="th-content">
                  Order ID
                  <span class="sort-icon" v-if="sortBy === 'id'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('customer_name')" class="sortable">
                <div class="th-content">
                  Customer Name
                  <span class="sort-icon" v-if="sortBy === 'customer_name'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('customer_distance')" class="sortable">
                <div class="th-content">
                  Distance (km)
                  <span class="sort-icon" v-if="sortBy === 'customer_distance'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('order_status')" class="sortable">
                <div class="th-content">
                  Status
                  <span class="sort-icon" v-if="sortBy === 'order_status'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th>Message</th>
              <th @click="sortTable('order_time')" class="sortable">
                <div class="th-content">
                  Order Time
                  <span class="sort-icon" v-if="sortBy === 'order_time'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('delivered_at')" class="sortable">
                <div class="th-content">
                  Delivery Time
                  <span class="sort-icon" v-if="sortBy === 'delivered_at'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredOrders.length === 0">
              <td colspan="8" style="text-align: center; color: #94a3b8; padding: 40px;">
                No orders found
              </td>
            </tr>
            <tr v-for="order in filteredOrders" :key="order.id">
              <td><strong>#{{ order.id }}</strong></td>
              <td>{{ order.customer_name }}</td>
              <td>{{ order.customer_distance }}</td>
              <td>
                <span 
                  class="badge" 
                  :class="{
                    'badge-success': order.order_status === 'completed',
                    'badge-warning': order.order_status === 'confirmed',
                    'badge-info': order.order_status === 'pending',
                    'badge-danger': order.order_status === 'cancelled'
                  }"
                >
                  {{ order.order_status }}
                </span>
              </td>
              <td>{{ order.response_msg || '-' }}</td>
              <td>{{ formatDate(order.order_time) }}</td>
              <td>{{ formatDate(order.delivered_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button 
                    @click="viewOrderDetails(order.id)" 
                    class="btn btn-sm btn-primary"
                    title="View Order Details"
                  >
                    📦 Show Order
                  </button>
                  <button 
                    v-if="orderDeliveries[order.id]"
                    @click="viewDeliveryDetails(order.id)" 
                    class="btn btn-sm btn-info"
                    title="View Delivery Details"
                  >
                    🚚 Show Delivery
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
            <label>Customer Distance (km) *</label>
            <input v-model.number="newOrder.customer_distance" type="number" step="0.1" min="0" placeholder="Enter distance in kilometers" />
          </div>
          <div class="form-group">
            <label>Items *</label>
            <div v-for="(item, index) in newOrder.items" :key="index" class="item-row">
              <select 
                v-model.number="item.item_id" 
                class="item-input"
                required
              >
                <option value="" disabled>Select Item</option>
                <option 
                  v-for="stockItem in stockItems" 
                  :key="stockItem.item_id" 
                  :value="stockItem.item_id"
                >
                  {{ stockItem.item_name }} (Available: {{ stockItem.quantity }})
                </option>
              </select>
              <input 
                v-model.number="item.quantity" 
                type="number" 
                placeholder="Quantity" 
                class="item-input"
                min="1"
                required
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
          <h3>Order Details - #{{ selectedOrder?.id }}</h3>
          <button @click="showDetailsModal = false" class="close-btn">✕</button>
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
          <button @click="showDetailsModal = false" class="btn btn-primary">Close</button>
        </div>
      </div>
    </div>

    <!-- Delivery Details Modal -->
    <div v-if="showDeliveryModal" class="modal-overlay" @click.self="showDeliveryModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>🚚 Delivery Details - Order #{{ selectedDelivery?.order_id }}</h3>
          <button @click="showDeliveryModal = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body" v-if="selectedDelivery">
          <div class="detail-grid">
            <div class="detail-item">
              <strong>Delivery ID:</strong> {{ selectedDelivery.id }}
            </div>
            <div class="detail-item">
              <strong>Order ID:</strong> #{{ selectedDelivery.order_id }}
            </div>
            <div class="detail-item">
              <strong>Customer:</strong> {{ selectedDelivery.customer_name }}
            </div>
            <div class="detail-item">
              <strong>Distance:</strong> {{ selectedDelivery.customer_distance }} km
            </div>
            <div class="detail-item">
              <strong>Order Status:</strong> 
              <span 
                class="badge" 
                :class="{
                  'badge-success': selectedDelivery.order_status === 'completed',
                  'badge-warning': selectedDelivery.order_status === 'confirmed',
                  'badge-info': selectedDelivery.order_status === 'active',
                  'badge-danger': selectedDelivery.order_status === 'cancelled'
                }"
              >
                {{ selectedDelivery.order_status }}
              </span>
            </div>
            <div class="detail-item">
              <strong>Delivery Person:</strong> {{ selectedDelivery.delivery_person_name || 'N/A' }}
            </div>
            <div class="detail-item">
              <strong>Order Time:</strong> {{ formatDate(selectedDelivery.order_time) }}
            </div>
            <div class="detail-item">
              <strong>Delivered At:</strong> {{ formatDate(selectedDelivery.delivered_at) }}
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showDeliveryModal = false" class="btn btn-primary">Close</button>
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
      showDeliveryModal: false,
      selectedOrder: null,
      selectedDelivery: null,
      orderDeliveries: {},
      stockItems: [],
      newOrder: {
        customer_name: '',
        customer_distance: 0,
        items: [{ item_id: '', quantity: 1 }]
      },
      // Sorting state
      sortBy: null,
      sortOrder: 'asc'
    }
  },
  computed: {
    filteredOrders() {
      let orders
      if (this.currentFilter === 'active') orders = this.activeOrders
      else if (this.currentFilter === 'completed') orders = this.completedOrders
      else orders = this.allOrders

      if (!this.sortBy) return orders

      const sortedOrders = [...orders]
      return sortedOrders.sort((a, b) => {
        let aValue, bValue

        switch (this.sortBy) {
          case 'id':
            aValue = a.id
            bValue = b.id
            break
          case 'customer_name':
            aValue = a.customer_name.toLowerCase()
            bValue = b.customer_name.toLowerCase()
            break
          case 'customer_distance':
            aValue = a.customer_distance
            bValue = b.customer_distance
            break
          case 'order_status':
            aValue = a.order_status.toLowerCase()
            bValue = b.order_status.toLowerCase()
            break
          case 'order_time':
            aValue = new Date(a.order_time || 0)
            bValue = new Date(b.order_time || 0)
            break
          case 'delivered_at':
            aValue = new Date(a.delivered_at || 0)
            bValue = new Date(b.delivered_at || 0)
            break
          default:
            return 0
        }

        if (aValue < bValue) return this.sortOrder === 'asc' ? -1 : 1
        if (aValue > bValue) return this.sortOrder === 'asc' ? 1 : -1
        return 0
      })
    }
  },
  mounted() {
    this.fetchOrders()
    this.fetchStockItems()
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
        
        // Fetch delivery information for all orders
        await this.fetchOrderDeliveries()
      } catch (err) {
        this.error = 'Failed to load orders: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
      }
    },
    async fetchOrderDeliveries() {
      // Check each order for associated delivery
      const deliveryChecks = this.allOrders.map(async (order) => {
        try {
          const response = await api.getDeliveryByOrderId(order.id)
          if (response.data) {
            this.orderDeliveries[order.id] = response.data
          }
        } catch {
          // No delivery assigned for this order - this is expected for some orders
        }
      })
      await Promise.all(deliveryChecks)
    },
    async fetchStockItems() {
      try {
        const response = await api.getCurrentStock()
        this.stockItems = response.data
      } catch (err) {
        this.error = 'Failed to load stock items: ' + (err.response?.data?.error || err.message)
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
          customer_distance: 0,
          items: [{ item_id: '', quantity: 1 }]
        }
        await this.fetchOrders()
        setTimeout(() => this.successMessage = null, 3000)
      } catch (err) {
        this.error = 'Failed to create order: ' + (err.response?.data?.error || err.message)
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
    async viewDeliveryDetails(orderId) {
      try {
        // Use cached delivery info if available
        if (this.orderDeliveries[orderId]) {
          this.selectedDelivery = this.orderDeliveries[orderId]
          this.showDeliveryModal = true
        } else {
          const response = await api.getDeliveryByOrderId(orderId)
          this.selectedDelivery = response.data
          this.showDeliveryModal = true
        }
      } catch (err) {
        this.error = 'Failed to load delivery details: ' + (err.response?.data?.error || err.message)
      }
    },
    addItem() {
      this.newOrder.items.push({ item_id: '', quantity: 1 })
    },
    removeItem(index) {
      this.newOrder.items.splice(index, 1)
    },
    refreshOrders() {
      this.fetchOrders()
    },
    sortTable(column) {
      if (this.sortBy === column) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortBy = column
        this.sortOrder = 'asc'
      }
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

.btn-info {
  background-color: #0ea5e9;
  color: white;
}

.btn-info:hover {
  background-color: #0284c7;
}

.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
}

.sortable:hover {
  background-color: var(--bg-primary);
}

.th-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.sort-icon {
  font-size: 0.75rem;
  color: var(--primary-color);
  font-weight: bold;
}

.sort-icon.inactive {
  color: var(--text-secondary);
  opacity: 0.4;
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
