import { createRouter, createWebHistory } from 'vue-router'
import OrdersPage from '../pages/OrdersPage.vue'
import DeliveryPersonsPage from '../pages/DeliveryPersonsPage.vue'
import StockPage from '../pages/StockPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/orders'
  },
  {
    path: '/orders',
    component: OrdersPage
  },
  {
    path: '/delivery-persons',
    component: DeliveryPersonsPage
  },
  {
    path: '/stock',
    component: StockPage
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
