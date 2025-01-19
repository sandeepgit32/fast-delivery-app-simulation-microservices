<template>
  <div id="app">
    <h1>Food Delivery Simulation App</h1>
    <div id="map"></div>
    <div id="graphs">
      <plotly-graph :data="orderData" :layout="orderLayout"></plotly-graph>
      <plotly-graph :data="stockData" :layout="stockLayout"></plotly-graph>
    </div>
  </div>
</template>

<script>
import PlotlyGraph from './components/PlotlyGraph.vue';

export default {
  name: 'App',
  components: {
    PlotlyGraph
  },
  data() {
    return {
      orderData: [],
      orderLayout: {},
      stockData: [],
      stockLayout: {}
    };
  },
  mounted() {
    this.loadMap();
    this.loadGraphs();
  },
  methods: {
    loadMap() {
      // Initialize Google Maps
      const map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: -34.397, lng: 150.644 },
        zoom: 8
      });
    },
    loadGraphs() {
      // Fetch order and stock data from the backend and update Plotly graphs
      fetch('/api/orders')
        .then(response => response.json())
        .then(data => {
          this.orderData = data;
          this.orderLayout = { title: 'Order Fulfillment' };
        });

      fetch('/api/stock')
        .then(response => response.json())
        .then(data => {
          this.stockData = data;
          this.stockLayout = { title: 'Stock Levels' };
        });
    }
  }
};
</script>

<style>
#map {
  height: 400px;
  width: 100%;
}
#graphs {
  display: flex;
  justify-content: space-around;
}
</style>