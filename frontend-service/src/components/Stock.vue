<template>
  <div class="container">
    <div class="page-header">
      <h2>📦 Stock Management</h2>
      <div class="header-actions">
        <button @click="showAddStockModal = true" class="btn btn-success">
          ➕ Add Stock
        </button>
        <button @click="refreshStock" class="btn btn-primary">
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
              <th @click="sortTable('item_id')" class="sortable">
                <div class="th-content">
                  Item ID
                  <span class="sort-icon" v-if="sortBy === 'item_id'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('item_name')" class="sortable">
                <div class="th-content">
                  Item Name
                  <span class="sort-icon" v-if="sortBy === 'item_name'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('quantity')" class="sortable">
                <div class="th-content">
                  Quantity
                  <span class="sort-icon" v-if="sortBy === 'quantity'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('max_quantity')" class="sortable">
                <div class="th-content">
                  Max Quantity
                  <span class="sort-icon" v-if="sortBy === 'max_quantity'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('status')" class="sortable">
                <div class="th-content">
                  Stock Status
                  <span class="sort-icon" v-if="sortBy === 'status'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th @click="sortTable('progress')" class="sortable">
                <div class="th-content">
                  Progress
                  <span class="sort-icon" v-if="sortBy === 'progress'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                  </span>
                  <span class="sort-icon inactive" v-else>⇅</span>
                </div>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="sortedStockItems.length === 0">
              <td colspan="7" style="text-align: center; color: #94a3b8; padding: 40px;">
                No stock items found
              </td>
            </tr>
            <tr v-for="item in sortedStockItems" :key="item.item_id">
              <td><strong>#{{ item.item_id }}</strong></td>
              <td>{{ item.item_name }}</td>
              <td>
                <strong :style="{ color: getQuantityColor(getStockPercentage(item.quantity, item.max_quantity)) }">
                  {{ item.quantity }}
                </strong>
              </td>
              <td>
                <strong style="color: var(--text-secondary);">
                  {{ item.max_quantity }}
                </strong>
              </td>
              <td>
                <span 
                  class="badge" 
                  :class="getStockStatusClass(getStockPercentage(item.quantity, item.max_quantity))"
                >
                  {{ getStockStatus(getStockPercentage(item.quantity, item.max_quantity)) }}
                </span>
              </td>
              <td>
                <div class="progress-cell">
                  <div class="progress-bar-container">
                    <div 
                      class="progress-bar-fill"
                      :class="getStockLevelClass(getStockPercentage(item.quantity, item.max_quantity))"
                      :style="{ width: getStockPercentage(item.quantity, item.max_quantity) + '%' }"
                    ></div>
                  </div>
                  <span class="progress-label">{{ getStockPercentage(item.quantity, item.max_quantity) }}%</span>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    @click="openAddItemStock(item)" 
                    class="btn btn-sm btn-success"
                    title="Add Stock"
                  >
                    ➕ Add
                  </button>
                  <button 
                    @click="openRemoveItemStock(item)" 
                    class="btn btn-sm btn-danger"
                    title="Remove Stock"
                  >
                    ➖ Remove
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

    <!-- Add Stock Modal -->
    <div v-if="showAddStockModal" class="modal-overlay" @click.self="showAddStockModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ selectedItem ? 'Add Stock to ' + selectedItem.item_name : 'Add Stock' }}</h3>
          <button @click="closeAddStockModal" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="!selectedItem">
            <div class="form-group">
              <label>Stock Items</label>
              <div v-for="(stockItem, index) in addStockItems" :key="index" class="item-row">
                <select 
                  v-model.number="stockItem.item_id" 
                  class="item-input"
                >
                  <option value="" disabled>Select Product</option>
                  <option 
                    v-for="item in stockItems" 
                    :key="item.item_id" 
                    :value="item.item_id"
                  >
                    {{ item.item_name }}
                  </option>
                </select>
                <input 
                  v-model.number="stockItem.quantity" 
                  type="number" 
                  placeholder="Quantity to add" 
                  class="item-input"
                />
                <button @click="removeAddStockItem(index)" class="btn btn-sm btn-danger">Remove</button>
              </div>
              <button @click="addAddStockItem" class="btn btn-sm btn-primary" style="margin-top: 8px;">
                ➕ Add Item
              </button>
            </div>
          </div>
          <div v-else>
            <div class="form-group">
              <label>Item ID</label>
              <input v-model.number="selectedItem.item_id" type="number" disabled />
            </div>
            <div class="form-group">
              <label>Item Name</label>
              <input v-model="selectedItem.item_name" type="text" disabled />
            </div>
            <div class="form-group">
              <label>Current Quantity</label>
              <input v-model.number="selectedItem.quantity" type="number" disabled />
            </div>
            <div class="form-group">
              <label>Max Quantity</label>
              <input v-model.number="selectedItem.max_quantity" type="number" disabled />
            </div>
            <div class="form-group">
              <label>Quantity to Add *</label>
              <input v-model.number="quantityToAdd" type="number" placeholder="Enter quantity" min="1" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeAddStockModal" class="btn btn-secondary">Cancel</button>
          <button @click="addStock" class="btn btn-success">Add Stock</button>
        </div>
      </div>
    </div>

    <!-- Remove Stock Modal -->
    <div v-if="showRemoveStockModal" class="modal-overlay" @click.self="showRemoveStockModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Remove Stock from {{ selectedItem?.item_name }}</h3>
          <button @click="closeRemoveStockModal" class="close-btn">✕</button>
        </div>
        <div class="modal-body" v-if="selectedItem">
          <div class="form-group">
            <label>Item ID</label>
            <input v-model.number="selectedItem.item_id" type="number" disabled />
          </div>
          <div class="form-group">
            <label>Item Name</label>
            <input v-model="selectedItem.item_name" type="text" disabled />
          </div>
          <div class="form-group">
            <label>Current Quantity</label>
            <input v-model.number="selectedItem.quantity" type="number" disabled />
          </div>
          <div class="form-group">
            <label>Max Quantity</label>
            <input v-model.number="selectedItem.max_quantity" type="number" disabled />
          </div>
          <div class="form-group">
            <label>Quantity to Remove *</label>
            <input 
              v-model.number="quantityToRemove" 
              type="number" 
              placeholder="Enter quantity" 
              min="1" 
              :max="selectedItem.quantity"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeRemoveStockModal" class="btn btn-secondary">Cancel</button>
          <button @click="removeStock" class="btn btn-danger">Remove Stock</button>
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
  name: 'Stock',
  data() {
    return {
      loading: true,
      error: null,
      successMessage: null,
      stockItems: [],
      showAddStockModal: false,
      showRemoveStockModal: false,
      selectedItem: null,
      quantityToAdd: 0,
      quantityToRemove: 0,
      addStockItems: [{ item_id: null, quantity: 10 }],
      // Configurable stock level thresholds
      stockThresholds: {
        high: 50,    // >= 50% - Green
        medium: 25,  // >= 25% and < 50% - Yellow
        // < 25% - Red
      },
      // Sorting state
      sortBy: null,
      sortOrder: 'asc', // 'asc' or 'desc'
      // Pagination state
      currentPage: 1,
      itemsPerPage: 10
    }
  },
  computed: {
    allSortedStockItems() {
      if (!this.sortBy) {
        return this.stockItems
      }

      const items = [...this.stockItems]
      
      return items.sort((a, b) => {
        let aValue, bValue

        switch (this.sortBy) {
          case 'item_id':
            aValue = a.item_id
            bValue = b.item_id
            break
          case 'item_name':
            aValue = a.item_name.toLowerCase()
            bValue = b.item_name.toLowerCase()
            break
          case 'quantity':
            aValue = a.quantity
            bValue = b.quantity
            break
          case 'max_quantity':
            aValue = a.max_quantity
            bValue = b.max_quantity
            break
          case 'status':
            aValue = this.getStockPercentage(a.quantity, a.max_quantity)
            bValue = this.getStockPercentage(b.quantity, b.max_quantity)
            break
          case 'progress':
            aValue = this.getStockPercentage(a.quantity, a.max_quantity)
            bValue = this.getStockPercentage(b.quantity, b.max_quantity)
            break
          default:
            return 0
        }

        if (aValue < bValue) {
          return this.sortOrder === 'asc' ? -1 : 1
        }
        if (aValue > bValue) {
          return this.sortOrder === 'asc' ? 1 : -1
        }
        return 0
      })
    },
    sortedStockItems() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.allSortedStockItems.slice(start, end)
    },
    totalPages() {
      return Math.ceil(this.allSortedStockItems.length / this.itemsPerPage)
    },
    totalItems() {
      return this.allSortedStockItems.length
    },
    startItem() {
      return this.totalItems === 0 ? 0 : (this.currentPage - 1) * this.itemsPerPage + 1
    },
    endItem() {
      return Math.min(this.currentPage * this.itemsPerPage, this.totalItems)
    }
  },
  mounted() {
    this.fetchStock()
  },
  methods: {
    async fetchStock() {
      this.loading = true
      this.error = null

      try {
        const response = await api.getCurrentStock()
        this.stockItems = response.data
      } catch (err) {
        this.error = 'Failed to load stock: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
      }
    },
    async addStock() {
      this.error = null
      this.successMessage = null

      try {
        let stockData
        if (this.selectedItem) {
          stockData = {
            order_items: [{ 
              item_id: this.selectedItem.item_id, 
              quantity: this.quantityToAdd 
            }]
          }
        } else {
          stockData = { order_items: this.addStockItems }
        }

        await api.addStock(stockData)
        this.successMessage = 'Stock added successfully!'
        this.closeAddStockModal()
        await this.fetchStock()
        setTimeout(() => this.successMessage = null, 3000)
      } catch (err) {
        const errorDetail = err.response?.data?.detail || err.response?.data?.error || err.message
        
        // Check if it's a capacity exceeded error and format a user-friendly message
        if (err.response?.status === 400 && errorDetail.includes('exceed maximum capacity')) {
          // Parse the error to extract useful info
          const match = errorDetail.match(/Adding (\d+) units to (.+) would exceed maximum capacity \((\d+)\)\. Current: (\d+)/)
          if (match) {
            const [, requested, itemName, maxQty, currentQty] = match
            const available = parseInt(maxQty) - parseInt(currentQty)
            this.error = `Cannot add ${requested} units to ${itemName}. Maximum capacity is ${maxQty} and current stock is ${currentQty}. You can add up to ${available} more units.`
          } else {
            this.error = errorDetail
          }
        } else {
          this.error = 'Failed to add stock: ' + errorDetail
        }
      }
    },
    async removeStock() {
      this.error = null
      this.successMessage = null

      if (this.quantityToRemove > this.selectedItem.quantity) {
        this.error = 'Cannot remove more than available quantity'
        return
      }

      try {
        const stockData = {
          order_items: [{ 
            item_id: this.selectedItem.item_id, 
            quantity: this.quantityToRemove 
          }]
        }

        await api.removeStock(stockData)
        this.successMessage = 'Stock removed successfully!'
        this.closeRemoveStockModal()
        await this.fetchStock()
        setTimeout(() => this.successMessage = null, 3000)
      } catch (err) {
        this.error = 'Failed to remove stock: ' + (err.response?.data?.error || err.message)
      }
    },
    openAddItemStock(item) {
      this.selectedItem = { ...item }
      this.quantityToAdd = 10
      this.showAddStockModal = true
    },
    openRemoveItemStock(item) {
      this.selectedItem = { ...item }
      this.quantityToRemove = 1
      this.showRemoveStockModal = true
    },
    closeAddStockModal() {
      this.showAddStockModal = false
      this.selectedItem = null
      this.quantityToAdd = 0
      this.addStockItems = [{ item_id: null, quantity: 10 }]
    },
    closeRemoveStockModal() {
      this.showRemoveStockModal = false
      this.selectedItem = null
      this.quantityToRemove = 0
    },
    addAddStockItem() {
      this.addStockItems.push({ item_id: null, quantity: 10 })
    },
    removeAddStockItem(index) {
      this.addStockItems.splice(index, 1)
    },
    refreshStock() {
      this.fetchStock()
    },
    sortTable(column) {
      if (this.sortBy === column) {
        // Toggle sort order if clicking the same column
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        // Set new column and default to ascending
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
    },
    getStockPercentage(quantity, maxQuantity) {
      if (!maxQuantity || maxQuantity === 0) return 0
      return Math.round((quantity / maxQuantity) * 100)
    },
    getStockLevelClass(percentage) {
      if (percentage >= this.stockThresholds.high) {
        return 'progress-high'
      } else if (percentage >= this.stockThresholds.medium) {
        return 'progress-medium'
      } else {
        return 'progress-low'
      }
    },
    getStockStatus(percentage) {
      if (percentage >= this.stockThresholds.high) return 'High Stock'
      if (percentage >= this.stockThresholds.medium) return 'Medium Stock'
      return 'Low Stock'
    },
    getStockStatusClass(percentage) {
      if (percentage >= this.stockThresholds.high) return 'badge-success'
      if (percentage >= this.stockThresholds.medium) return 'badge-warning'
      return 'badge-danger'
    },
    getQuantityColor(percentage) {
      if (percentage >= this.stockThresholds.high) return 'var(--success-color)'
      if (percentage >= this.stockThresholds.medium) return 'var(--warning-color)'
      return 'var(--danger-color)'
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

.btn-secondary {
  background-color: var(--secondary-color);
  color: white;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
}

.progress-bar-container {
  flex: 1;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.progress-high {
  background: var(--success-color);
}

.progress-medium {
  background: var(--warning-color);
}

.progress-low {
  background: var(--danger-color);
}

.progress-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  min-width: 45px;
  text-align: right;
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

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
