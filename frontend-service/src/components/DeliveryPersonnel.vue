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
              <th @click="sortTable('id')" class="sortable">
                <div class="th-content">
                  Person ID
                  <span class="sort-icon" v-if="sortBy === 'id'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('name')" class="sortable">
                <div class="th-content">
                  Name
                  <span class="sort-icon" v-if="sortBy === 'name'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('phone_number')" class="sortable">
                <div class="th-content">
                  Phone
                  <span class="sort-icon" v-if="sortBy === 'phone_number'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('person_status')" class="sortable">
                <div class="th-content">
                  Status
                  <span class="sort-icon" v-if="sortBy === 'person_status'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
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
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <div class="pagination-container" v-if="totalPages > 0">
        <div class="pagination-info">
          Showing {{ startItem }} to {{ endItem }} of {{ totalItems }} entries
        </div>
        <div class="pagination-controls">
          <button 
            @click="goToPage(1)" 
            :disabled="currentPage === 1"
            class="pagination-btn"
            title="First Page"
          >
            ««
          </button>
          <button 
            @click="prevPage" 
            :disabled="currentPage === 1"
            class="pagination-btn"
            title="Previous Page"
          >
            «
          </button>
          <template v-for="page in totalPages" :key="page">
            <button 
              v-if="page === 1 || page === totalPages || (page >= currentPage - 2 && page <= currentPage + 2)"
              @click="goToPage(page)"
              :class="['pagination-btn', { active: currentPage === page }]"
            >
              {{ page }}
            </button>
            <span 
              v-else-if="page === currentPage - 3 || page === currentPage + 3" 
              class="pagination-ellipsis"
            >
              ...
            </span>
          </template>
          <button 
            @click="nextPage" 
            :disabled="currentPage === totalPages"
            class="pagination-btn"
            title="Next Page"
          >
            »
          </button>
          <button 
            @click="goToPage(totalPages)" 
            :disabled="currentPage === totalPages"
            class="pagination-btn"
            title="Last Page"
          >
            »»
          </button>
        </div>
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
      selectedPerson: null,
      // Sorting state
      sortBy: null,
      sortOrder: 'asc',
      // Pagination state
      currentPage: 1,
      itemsPerPage: 10
    }
  },
  computed: {
    sortedPersonnel() {
      let result
      if (this.currentFilter === 'idle') result = this.idlePersonnel
      else if (this.currentFilter === 'en_route') result = this.enRoutePersonnel
      else result = this.allPersonnel

      if (!this.sortBy) return result

      const sorted = [...result]
      return sorted.sort((a, b) => {
        let aValue, bValue

        switch (this.sortBy) {
          case 'id':
            aValue = a.id
            bValue = b.id
            break
          case 'name':
            aValue = a.name.toLowerCase()
            bValue = b.name.toLowerCase()
            break
          case 'phone_number':
            aValue = a.phone_number
            bValue = b.phone_number
            break
          case 'person_status':
            aValue = a.person_status.toLowerCase()
            bValue = b.person_status.toLowerCase()
            break
          default:
            return 0
        }

        if (aValue < bValue) return this.sortOrder === 'asc' ? -1 : 1
        if (aValue > bValue) return this.sortOrder === 'asc' ? 1 : -1
        return 0
      })
    },
    filteredPersonnel() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.sortedPersonnel.slice(start, end)
    },
    totalPages() {
      return Math.ceil(this.sortedPersonnel.length / this.itemsPerPage)
    },
    totalItems() {
      return this.sortedPersonnel.length
    },
    startItem() {
      return this.totalItems === 0 ? 0 : (this.currentPage - 1) * this.itemsPerPage + 1
    },
    endItem() {
      return Math.min(this.currentPage * this.itemsPerPage, this.totalItems)
    }
  },
  watch: {
    currentFilter() {
      this.currentPage = 1
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
    },
    sortTable(column) {
      if (this.sortBy === column) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortBy = column
        this.sortOrder = 'asc'
      }
      this.currentPage = 1
    },
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
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

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  flex-wrap: wrap;
  gap: 16px;
}

.pagination-info {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-btn {
  min-width: 36px;
  height: 36px;
  padding: 0 8px;
  border: 1px solid var(--border-color);
  background: white;
  color: var(--text-primary);
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.pagination-ellipsis {
  padding: 0 8px;
  color: var(--text-secondary);
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
