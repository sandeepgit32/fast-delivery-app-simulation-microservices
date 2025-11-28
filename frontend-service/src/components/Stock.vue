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
              <th>Item ID</th>
              <th>Item Name</th>
              <th>Quantity</th>
              <th>Max Quantity</th>
              <th>Stock Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="stockItems.length === 0">
              <td colspan="6" style="text-align: center; color: #94a3b8; padding: 40px;">
                No stock items found
              </td>
            </tr>
            <tr v-for="item in stockItems" :key="item.item_id">
              <td><strong>#{{ item.item_id }}</strong></td>
              <td>{{ item.item_name }}</td>
              <td>
                <strong :style="{ color: getQuantityColor(item.quantity) }">
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
                  :class="{
                    'badge-success': item.quantity >= 50,
                    'badge-warning': item.quantity >= 10 && item.quantity < 50,
                    'badge-danger': item.quantity < 10
                  }"
                >
                  {{ getStockStatus(item.quantity) }}
                </span>
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
                <input 
                  v-model.number="stockItem.item_id" 
                  type="number" 
                  placeholder="Item ID" 
                  class="item-input"
                />
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
      addStockItems: [{ item_id: 1, quantity: 10 }]
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
            items: [{ 
              item_id: this.selectedItem.item_id, 
              quantity: this.quantityToAdd 
            }]
          }
        } else {
          stockData = { items: this.addStockItems }
        }

        await api.addStock(stockData)
        this.successMessage = 'Stock added successfully!'
        this.closeAddStockModal()
        await this.fetchStock()
        setTimeout(() => this.successMessage = null, 3000)
      } catch (err) {
        this.error = 'Failed to add stock: ' + (err.response?.data?.error || err.message)
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
          items: [{ 
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
      this.addStockItems = [{ item_id: 1, quantity: 10 }]
    },
    closeRemoveStockModal() {
      this.showRemoveStockModal = false
      this.selectedItem = null
      this.quantityToRemove = 0
    },
    addAddStockItem() {
      this.addStockItems.push({ item_id: 1, quantity: 10 })
    },
    removeAddStockItem(index) {
      this.addStockItems.splice(index, 1)
    },
    refreshStock() {
      this.fetchStock()
    },
    getStockStatus(quantity) {
      if (quantity >= 50) return 'Good Stock'
      if (quantity >= 10) return 'Low Stock'
      return 'Critical'
    },
    getQuantityColor(quantity) {
      if (quantity >= 50) return 'var(--success-color)'
      if (quantity >= 10) return 'var(--warning-color)'
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
