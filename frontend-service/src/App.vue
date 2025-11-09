<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <h1>🚀 Food Delivery Dashboard</h1>
        </div>
        <ul class="nav-menu">
          <li>
            <router-link to="/" :class="{ active: $route.path === '/' }">
              📊 Dashboard
            </router-link>
          </li>
          <li>
            <router-link to="/orders" :class="{ active: $route.path === '/orders' }">
              📦 Orders
            </router-link>
          </li>
          <li>
            <router-link to="/deliveries" :class="{ active: $route.path === '/deliveries' }">
              🚚 Deliveries
            </router-link>
          </li>
          <li>
            <router-link to="/personnel" :class="{ active: $route.path === '/personnel' }">
              👥 Personnel
            </router-link>
          </li>
          <li>
            <router-link to="/stock" :class="{ active: $route.path === '/stock' }">
              📦 Stock
            </router-link>
          </li>
        </ul>
      </div>
    </nav>
    
    <main class="main-content">
      <router-view/>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand h1 {
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  padding: 20px 0;
}

.nav-menu {
  display: flex;
  list-style: none;
  gap: 8px;
  margin: 0;
  padding: 0;
}

.nav-menu li a {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  display: block;
  font-size: 14px;
}

.nav-menu li a:hover {
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
}

.nav-menu li a.active {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.main-content {
  padding: 32px 0;
  min-height: calc(100vh - 80px);
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 16px;
  }

  .nav-brand h1 {
    padding: 16px 0 8px;
    font-size: 1.25rem;
  }

  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
    padding-bottom: 12px;
  }

  .nav-menu li a {
    padding: 8px 12px;
    font-size: 13px;
  }
}
</style>
