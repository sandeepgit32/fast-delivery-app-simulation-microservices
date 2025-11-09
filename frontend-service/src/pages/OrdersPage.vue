<template>
  <div class="orders-page">
    <div class="page-header">
      <div class="header-content">
        <h2><i class="bi bi-receipt"></i> Orders Management</h2>
        <p class="text-muted">Track and manage all delivery orders</p>
      </div>
      <button class="btn btn-primary btn-create" @click="showNewOrderModal = true">
        <i class="bi bi-plus-circle"></i>
        New Order
      </button>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th><i class="bi bi-hash"></i> Order ID</th>
                <th><i class="bi bi-person"></i> Customer ID</th>
                <th><i class="bi bi-clock"></i> Order Time</th>
                <th><i class="bi bi-truck"></i> Delivery Time</th>
                <th><i class="bi bi-info-circle"></i> Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in sortedOrders" :key="order.id" class="order-row">
                <td><strong>#{{ order.id }}</strong></td>
                <td>{{ order.customer_id }}</td>
                <td>{{ formatDate(order.order_time) }}</td>
                <td>{{ order.delivery_time ? formatDate(order.delivery_time) : '-' }}</td>
                <td><span :class="getStatusBadgeClass(order.status)">{{ order.status }}</span></td>
              </tr>
              <tr v-if="sortedOrders.length === 0">
                <td colspan="5" class="text-center text-muted py-4">
                  <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                  <p class="mt-2">No orders found</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- New Order Modal -->
    <div class="modal" v-if="showNewOrderModal" @click.self="showNewOrderModal = false">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create New Order</h5>
            <button type="button" class="btn-close" @click="showNewOrderModal = false"></button>
          </div>
          <div class="modal-body">
            <p>New order form coming soon...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrdersPage',
  data() {
    return {
      orders: [],
      showNewOrderModal: false
    }
  },
  computed: {
    sortedOrders() {
      return [...this.orders].sort((a, b) => 
        new Date(b.order_time) - new Date(a.order_time)
      )
    }
  },
  methods: {
    async fetchOrders() {
      try {
        const response = await fetch('/api/orders')
        this.orders = await response.json()
      } catch (error) {
        console.error('Error fetching orders:', error)
      }
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleString()
    },
    getStatusBadgeClass(status) {
      const classes = {
        'pending': 'badge bg-warning text-dark',
        'delivering': 'badge bg-info',
        'completed': 'badge bg-success',
        'cancelled': 'badge bg-danger'
      }
      return classes[status] || 'badge bg-secondary'
    }
  },
  mounted() {
    this.fetchOrders()
    // Refresh data every 5 seconds
    this.interval = setInterval(this.fetchOrders, 5000)
  },
  beforeUnmount() {
    if (this.interval) {
      clearInterval(this.interval)
    }
  }
}
</script>

<style scoped>
.orders-page {
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

.btn-create {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-create:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.card {
  border: none;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.95);
}

.table {
  margin-bottom: 0;
}

.table thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.table thead th {
  border: none;
  padding: 1rem;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.table tbody tr {
  transition: all 0.3s ease;
}

.table tbody tr:hover {
  background-color: rgba(102, 126, 234, 0.05);
  transform: scale(1.01);
}

.order-row td {
  padding: 1rem;
  vertical-align: middle;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.modal {
  display: flex;
  align-items: center;
  justify-content: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1050;
  animation: fadeIn 0.3s ease;
}

.modal-dialog {
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-content {
  border-radius: 12px;
  border: none;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: none;
  padding: 1.5rem;
  border-radius: 12px 12px 0 0;
}

.modal-title {
  font-weight: 700;
}

.btn-close {
  filter: brightness(0) invert(1);
}
</style>
