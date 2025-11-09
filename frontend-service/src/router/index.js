import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../components/Dashboard.vue'
import Orders from '../components/Orders.vue'
import Deliveries from '../components/Deliveries.vue'
import DeliveryPersonnel from '../components/DeliveryPersonnel.vue'
import Stock from '../components/Stock.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/orders',
    name: 'Orders',
    component: Orders
  },
  {
    path: '/deliveries',
    name: 'Deliveries',
    component: Deliveries
  },
  {
    path: '/personnel',
    name: 'DeliveryPersonnel',
    component: DeliveryPersonnel
  },
  {
    path: '/stock',
    name: 'Stock',
    component: Stock
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
