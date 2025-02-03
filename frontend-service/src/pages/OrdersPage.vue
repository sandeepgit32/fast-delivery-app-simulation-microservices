<template>
  <div class="orders-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Orders</h2>
      <button class="btn btn-primary" @click="showNewOrderModal = true">
        New Order
      </button>
    </div>

    <div class="table-responsive">
      <table class="table table-hover">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Customer ID</th>
            <th>Order Time</th>
            <th>Delivery Time</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in sortedOrders" :key="order.id">
            <td>{{ order.id }}</td>
            <td>{{ order.customer_id }}</td>
            <td>{{ formatDate(order.order_time) }}</td>
            <td>{{ order.delivery_time ? formatDate(order.delivery_time) : '-' }}</td>
            <td><span :class="getStatusBadgeClass(order.status)">{{ order.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- New Order Modal -->
    <div class="modal" v-if="showNewOrderModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <!-- Modal implementation -->
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
        const response = await fetch('http://localhost:5000/orders')
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
        'pending': 'badge bg-warning',
        'delivering': 'badge bg-info',
        'completed': 'badge bg-success',
        'cancelled': 'badge bg-danger'
      }
      return classes[status] || 'badge bg-secondary'
    }
  },
  mounted() {
    this.fetchOrders()
  }
}
</script>
