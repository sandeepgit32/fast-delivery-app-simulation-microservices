<template>
  <div class="container">
    <div class="page-header">
      <h2>👥 Delivery Personnel</h2>
      <button @click="refreshPersonnel" class="btn btn-primary">
        🔄 Refresh
      </button>
    </div>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <button 
        @click="currentFilter = 'all'" 
        :class="{ active: currentFilter === 'all' }"
        class="tab-btn"
      >
        All Personnel ({{ allPersonnel.length }})
      </button>
      <button 
        @click="currentFilter = 'idle'" 
        :class="{ active: currentFilter === 'idle' }"
        class="tab-btn"
      >
        Idle ({{ idlePersonnel.length }})
      </button>
      <button 
        @click="currentFilter = 'en_route'" 
        :class="{ active: currentFilter === 'en_route' }"
        class="tab-btn"
      >
        En Route ({{ enRoutePersonnel.length }})
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
              <th>Person ID</th>
              <th>Name</th>
              <th>Phone</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredPersonnel.length === 0">
              <td colspan="5" style="text-align: center; color: #94a3b8; padding: 40px;">
                No personnel found
              </td>
            </tr>
            <tr v-for="person in filteredPersonnel" :key="person.id">
              <td><strong>#{{ person.id }}</strong></td>
              <td>{{ person.name }}</td>
              <td>{{ person.phone_number }}</td>
              <td>
                <span 
                  class="badge" 
                  :class="{
                    'badge-success': person.person_status === 'idle',
                    'badge-warning': person.person_status === 'en_route'
                  }"
                >
                  {{ person.person_status }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    @click="viewPersonDetails(person.id)" 
                    class="btn btn-sm btn-primary"
                    title="View Details"
                  >
                    👁️ View
                  </button>
                  <button 
                    v-if="person.person_status === 'en_route'"
                    @click="updateStatus(person.id, 'idle')" 
                    class="btn btn-sm btn-success"
                    title="Mark as Idle"
                  >
                    ✅ Mark Idle
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Person Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click.self="showDetailsModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Personnel Details - {{ selectedPerson?.name }}</h3>
          <button @click="showDetailsModal = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body" v-if="selectedPerson">
          <div class="detail-grid">
            <div class="detail-item">
              <strong>Person ID:</strong> #{{ selectedPerson.id }}
            </div>
            <div class="detail-item">
              <strong>Name:</strong> {{ selectedPerson.name }}
            </div>
            <div class="detail-item">
              <strong>Phone:</strong> {{ selectedPerson.phone_number }}
            </div>
            <div class="detail-item">
              <strong>Status:</strong>
              <span 
                class="badge" 
                :class="{
                  'badge-success': selectedPerson.person_status === 'idle',
                  'badge-warning': selectedPerson.person_status === 'en_route'
                }"
              >
                {{ selectedPerson.person_status }}
              </span>
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
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'DeliveryPersonnel',
  data() {
    return {
      loading: true,
      error: null,
      successMessage: null,
      allPersonnel: [],
      idlePersonnel: [],
      enRoutePersonnel: [],
      currentFilter: 'all',
      showDetailsModal: false,
      selectedPerson: null
    }
  },
  computed: {
    filteredPersonnel() {
      let result
      if (this.currentFilter === 'idle') result = this.idlePersonnel
      else if (this.currentFilter === 'en_route') result = this.enRoutePersonnel
      else result = this.allPersonnel
      
      console.log('Filtered Personnel:', result)
      console.log('Current Filter:', this.currentFilter)
      return result
    }
  },
  mounted() {
    this.fetchPersonnel()
  },
  methods: {
    async fetchPersonnel() {
      this.loading = true
      this.error = null

      try {
        const [all, idle, enRoute] = await Promise.all([
          api.getAllDeliveryPersons(),
          api.getIdlePersons(),
          api.getEnRoutePersons()
        ])

        console.log('API Response - All:', all)
        console.log('API Response - All Data:', all.data)
        console.log('API Response - Idle:', idle.data)
        console.log('API Response - En Route:', enRoute.data)

        this.allPersonnel = all.data
        this.idlePersonnel = idle.data
        this.enRoutePersonnel = enRoute.data

        console.log('Component State - All Personnel:', this.allPersonnel)
        console.log('Component State - Idle Personnel:', this.idlePersonnel)
        console.log('Component State - En Route Personnel:', this.enRoutePersonnel)
      } catch (err) {
        this.error = 'Failed to load personnel: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
      }
    },
    async updateStatus(personId, status) {
      this.error = null
      this.successMessage = null

      try {
        await api.updateDeliveryPersonStatus(personId, status)
        this.successMessage = 'Status updated successfully!'
        await this.fetchPersonnel()
        setTimeout(() => this.successMessage = null, 3000)
      } catch (err) {
        this.error = 'Failed to update status: ' + (err.response?.data?.error || err.message)
      }
    },
    async viewPersonDetails(personId) {
      try {
        const response = await api.getDeliveryPerson(personId)
        this.selectedPerson = response.data
        this.showDetailsModal = true
      } catch (err) {
        this.error = 'Failed to load person details: ' + (err.response?.data?.error || err.message)
      }
    },
    refreshPersonnel() {
      this.fetchPersonnel()
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

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .filter-tabs {
    overflow-x: auto;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
