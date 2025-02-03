<template>
  <div class="stock-page">
    <h2 class="mb-4">Stock Management</h2>

    <div class="table-responsive">
      <table class="table table-hover">
        <thead>
          <tr>
            <th>Product Name</th>
            <th>Quantity</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in sortedStock" :key="item.id">
            <td>{{ item.name }}</td>
            <td>{{ item.quantity }}</td>
            <td>
              <div class="btn-group">
                <button class="btn btn-sm btn-success" @click="adjustStock(item, 1)">+</button>
                <button class="btn btn-sm btn-danger" @click="adjustStock(item, -1)">-</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StockPage',
  data() {
    return {
      stock: []
    }
  },
  computed: {
    sortedStock() {
      return [...this.stock].sort((a, b) => 
        b.name.localeCompare(a.name)
      )
    }
  },
  methods: {
    async fetchStock() {
      try {
        const response = await fetch('http://localhost:5000/current_stock')
        this.stock = await response.json()
      } catch (error) {
        console.error('Error fetching stock:', error)
      }
    },
    async adjustStock(item, amount) {
      try {
        const endpoint = amount > 0 ? '/add_stock' : '/remove_stock'
        await fetch(`http://localhost:5000${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            item_id: item.id,
            quantity: Math.abs(amount)
          })
        })
        await this.fetchStock()
      } catch (error) {
        console.error('Error adjusting stock:', error)
      }
    }
  },
  mounted() {
    this.fetchStock()
  }
}
</script>
