<template>
  <div class="delivery-persons-page">
    <h2 class="mb-4">Delivery Personnel</h2>

    <div class="table-responsive">
      <table class="table table-hover">
        <thead>
          <tr>
            <th>Name</th>
            <th>Order ID</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="person in sortedPersonnel" :key="person.id">
            <td>{{ person.name }}</td>
            <td>{{ person.order_id || '-' }}</td>
            <td><span :class="getStatusBadgeClass(person.status)">{{ person.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DeliveryPersonsPage',
  data() {
    return {
      personnel: []
    }
  },
  computed: {
    sortedPersonnel() {
      return [...this.personnel].sort((a, b) => {
        if (a.status === 'en_route' && b.status !== 'en_route') return -1
        if (b.status === 'en_route' && a.status !== 'en_route') return 1
        return a.name.localeCompare(b.name)
      })
    }
  },
  methods: {
    async fetchPersonnel() {
      try {
        const response = await fetch('http://localhost:5000/delivery_persons')
        this.personnel = await response.json()
      } catch (error) {
        console.error('Error fetching personnel:', error)
      }
    },
    getStatusBadgeClass(status) {
      const classes = {
        'idle': 'badge bg-secondary',
        'en_route': 'badge bg-primary',
        'delivering': 'badge bg-info'
      }
      return classes[status] || 'badge bg-secondary'
    }
  },
  mounted() {
    this.fetchPersonnel()
  }
}
</script>
