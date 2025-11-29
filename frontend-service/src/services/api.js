import axios from 'axios'

// Use /api prefix for proxying in production
const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  // Orders
  getAllOrders() {
    return api.get('/orders')
  },
  getActiveOrders() {
    return api.get('/orders/active')
  },
  getCompletedOrders() {
    return api.get('/orders/completed')
  },
  getOrder(orderId) {
    return api.get(`/order/${orderId}`)
  },
  createOrder(orderData) {
    return api.post('/create_order', orderData)
  },
  closeOrder(orderId) {
    return api.post(`/close_order/${orderId}`)
  },
  cancelOrder(orderId, message) {
    return api.post(`/cancel_order/${orderId}`, { message })
  },
  updateOrderMessage(orderId, message) {
    return api.post(`/update_msg/${orderId}`, { message })
  },

  // Delivery Persons
  getAllDeliveryPersons() {
    return api.get('/delivery_persons')
  },
  getEnRoutePersons() {
    return api.get('/delivery_persons/en_route')
  },
  getIdlePersons() {
    return api.get('/delivery_persons/idle')
  },
  getDeliveryPerson(personId) {
    return api.get(`/delivery_persons/${personId}`)
  },
  updateDeliveryPersonStatus(personId, status) {
    return api.post(`/update_delivery_person_status/${personId}`, { person_status: status })
  },

  // Deliveries
  getAllDeliveries() {
    return api.get('/deliveries')
  },
  getDelivery(deliveryId) {
    return api.get(`/deliveries/${deliveryId}`)
  },
  getDeliveryByOrderId(orderId) {
    return api.get(`/deliveries/by_order/${orderId}`)
  },
  assignDelivery(orderId) {
    return api.post('/assign_delivery', { order_id: orderId })
  },

  // Stock
  getCurrentStock() {
    return api.get('/current_stock')
  },
  getStockItem(itemId) {
    return api.get(`/current_stock/${itemId}`)
  },
  addStock(stockData) {
    return api.post('/add_stock', stockData)
  },
  removeStock(stockData) {
    return api.post('/remove_stock', stockData)
  },
  validateStock(stockData) {
    return api.post('/validate_stock', stockData)
  }
}
