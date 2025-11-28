<template>
  <div class="container">
    <div class="page-header">
      <h2>🚚 Deliveries</h2>
      <div class="header-actions">
        <button @click="assignDelivery" class="btn btn-success">
          ➕ Assign Delivery
        </button>
        <button @click="refreshDeliveries" class="btn btn-primary">
          🔄 Refresh
        </button>
      </div>
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
                  Delivery ID
                  <span class="sort-icon" v-if="sortBy === 'id'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('order_id')" class="sortable">
                <div class="th-content">
                  Order ID
                  <span class="sort-icon" v-if="sortBy === 'order_id'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('order_status')" class="sortable">
                <div class="th-content">
                  Order Status
                  <span class="sort-icon" v-if="sortBy === 'order_status'">
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
              <th @click="sortTable('delivery_person_name')" class="sortable">
                <div class="th-content">
                  Delivery Person Name
                  <span class="sort-icon" v-if="sortBy === 'delivery_person_name'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="sortedDeliveries.length === 0">
              <td colspan="6" style="text-align: center; color: #94a3b8; padding: 40px;">
                No deliveries found
              </td>
            </tr>
            <tr v-for="delivery in sortedDeliveries" :key="delivery.id">
              <td><strong>#{{ delivery.id }}</strong></td>
              <td>#{{ delivery.order_id }}</td>
              <td>
                <span class="status-badge" :class="'status-' + delivery.order_status">
                  {{ delivery.order_status }}
                </span>
              </td>
              <td>{{ delivery.customer_name }}</td>
              <td>{{ delivery.delivery_person_name }}</td>
              <td>
                <button 
                  @click="viewDeliveryDetails(delivery.id)" 
                  class="btn btn-sm btn-primary"
                  title="View Details"
                >
                  👁️ View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Delivery Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click.self="showDetailsModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Delivery Details - #{{ selectedDelivery?.id }}</h3>
          <button @click="showDetailsModal = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body" v-if="selectedDelivery">
          <div class="detail-grid">
            <div class="detail-item">
              <strong>Delivery ID:</strong> #{{ selectedDelivery.id }}
            </div>
            <div class="detail-item">
              <strong>Order ID:</strong> #{{ selectedDelivery.order_id }}
            </div>
            <div class="detail-item">
              <strong>Order Status:</strong> 
              <span class="status-badge" :class="'status-' + selectedDelivery.order_status">
                {{ selectedDelivery.order_status }}
              </span>
            </div>
            <div class="detail-item">
              <strong>Customer Name:</strong> {{ selectedDelivery.customer_name }}
            </div>
            <div class="detail-item">
              <strong>Customer Distance:</strong> {{ selectedDelivery.customer_distance }} km
            </div>
            <div class="detail-item">
              <strong>Delivery Person ID:</strong> #{{ selectedDelivery.delivery_person_id }}
            </div>
            <div class="detail-item">
              <strong>Delivery Person Name:</strong> {{ selectedDelivery.delivery_person_name }}
            </div>
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

    <!-- Assign Delivery Modal -->
    <div v-if="showAssignModal" class="modal-overlay" @click.self="showAssignModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Assign Delivery</h3>
          <button @click="showAssignModal = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="order_id">Order ID:</label>
            <input 
              type="text" 
              id="order_id" 
              v-model="assignForm.order_id" 
              class="form-control"
              placeholder="Enter Order ID"
            >
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showAssignModal = false" class="btn btn-secondary">Cancel</button>
          <button @click="submitAssignDelivery" class="btn btn-success">Assign</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Deliveries',
  data() {
    return {
      loading: true,
      error: null,
      successMessage: null,
      deliveries: [],
      showDetailsModal: false,
      selectedDelivery: null,
      showAssignModal: false,
      assignForm: {
        order_id: ''
      },
      // Sorting state
      sortBy: null,
      sortOrder: 'asc'
    }
  },
  computed: {
    sortedDeliveries() {
      if (!this.sortBy) return this.deliveries

      const sorted = [...this.deliveries]
      return sorted.sort((a, b) => {
        let aValue, bValue

        switch (this.sortBy) {
          case 'id':
            aValue = a.id
            bValue = b.id
            break
          case 'order_id':
            aValue = a.order_id
            bValue = b.order_id
            break
          case 'order_status':
            aValue = a.order_status.toLowerCase()
            bValue = b.order_status.toLowerCase()
            break
          case 'customer_name':
            aValue = a.customer_name.toLowerCase()
            bValue = b.customer_name.toLowerCase()
            break
          case 'delivery_person_name':
            aValue = a.delivery_person_name.toLowerCase()
            bValue = b.delivery_person_name.toLowerCase()
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
    this.fetchDeliveries()
  },
  methods: {
    async fetchDeliveries() {
      this.loading = true
      this.error = null

      try {
        const response = await api.getAllDeliveries()
        this.deliveries = response.data
      } catch (err) {
        this.error = 'Failed to load deliveries: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
      }
    },
    assignDelivery() {
      this.error = null
      this.successMessage = null
      this.assignForm.order_id = ''
      this.showAssignModal = true
    },
    async submitAssignDelivery() {
      this.error = null
      this.successMessage = null

      if (!this.assignForm.order_id) {
        this.error = 'Please enter an Order ID'
        return
      }

      try {
        await api.assignDelivery(this.assignForm.order_id)
        this.successMessage = 'Delivery assignment queued successfully!'
        this.showAssignModal = false
        this.assignForm.order_id = ''
        await this.fetchDeliveries()
        setTimeout(() => this.successMessage = null, 3000)
      } catch (err) {
        this.error = 'Failed to assign delivery: ' + (err.response?.data?.detail || err.response?.data?.error || err.message)
      }
    },
    async viewDeliveryDetails(deliveryId) {
      try {
        const response = await api.getDelivery(deliveryId)
        this.selectedDelivery = response.data
        this.showDetailsModal = true
      } catch (err) {
        this.error = 'Failed to load delivery details: ' + (err.response?.data?.error || err.message)
      }
    },
    refreshDeliveries() {
      this.fetchDeliveries()
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

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
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

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-block;
}

.status-active {
  background: #dbeafe;
  color: #1e40af;
}

.status-completed {
  background: #dcfce7;
  color: #166534;
}

.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
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
}
</style>
