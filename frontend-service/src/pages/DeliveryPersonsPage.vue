<template>
  <div class="delivery-persons-page">
    <div class="page-header">
      <div class="header-content">
        <h2><i class="bi bi-person-badge"></i> Delivery Personnel</h2>
        <p class="text-muted">Monitor delivery staff and their assignments</p>
      </div>
      <div class="status-summary">
        <div class="status-card">
          <div class="status-icon idle">
            <i class="bi bi-person"></i>
          </div>
          <div>
            <div class="status-count">{{ idleCount }}</div>
            <div class="status-label">Idle</div>
          </div>
        </div>
        <div class="status-card">
          <div class="status-icon active">
            <i class="bi bi-truck"></i>
          </div>
          <div>
            <div class="status-count">{{ activeCount }}</div>
            <div class="status-label">Active</div>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th><i class="bi bi-person-circle"></i> Name</th>
                <th><i class="bi bi-receipt"></i> Order ID</th>
                <th><i class="bi bi-info-circle"></i> Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="person in sortedPersonnel" :key="person.id" class="person-row">
                <td>
                  <div class="person-info">
                    <div class="person-avatar">
                      {{ person.name.charAt(0).toUpperCase() }}
                    </div>
                    <strong>{{ person.name }}</strong>
                  </div>
                </td>
                <td>{{ person.order_id ? `#${person.order_id}` : '-' }}</td>
                <td><span :class="getStatusBadgeClass(person.status)">{{ formatStatus(person.status) }}</span></td>
              </tr>
              <tr v-if="sortedPersonnel.length === 0">
                <td colspan="3" class="text-center text-muted py-4">
                  <i class="bi bi-people" style="font-size: 3rem;"></i>
                  <p class="mt-2">No delivery personnel found</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
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
    },
    idleCount() {
      return this.personnel.filter(p => p.status === 'idle').length
    },
    activeCount() {
      return this.personnel.filter(p => p.status !== 'idle').length
    }
  },
  methods: {
    async fetchPersonnel() {
      try {
        const response = await fetch('/api/delivery_persons')
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
    },
    formatStatus(status) {
      const statusMap = {
        'idle': 'Idle',
        'en_route': 'En Route',
        'delivering': 'Delivering'
      }
      return statusMap[status] || status
    }
  },
  mounted() {
    this.fetchPersonnel()
    // Refresh data every 3 seconds
    this.interval = setInterval(this.fetchPersonnel, 3000)
  },
  beforeUnmount() {
    if (this.interval) {
      clearInterval(this.interval)
    }
  }
}
</script>

<style scoped>
.delivery-persons-page {
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

.status-summary {
  display: flex;
  gap: 1rem;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.status-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.status-icon.idle {
  background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
}

.status-icon.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.status-count {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  line-height: 1;
}

.status-label {
  font-size: 0.85rem;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
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

.person-row td {
  padding: 1rem;
  vertical-align: middle;
}

.person-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.person-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
</style>
