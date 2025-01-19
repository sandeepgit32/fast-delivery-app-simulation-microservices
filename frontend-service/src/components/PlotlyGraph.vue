<template>
    <div ref="plotlyGraph"></div>
</template>

<script>
import Plotly from 'plotly.js-dist';

export default {
name: 'PlotlyGraph',
props: {
    data: Array,
    layout: Object
},
watch: {
    data: 'renderGraph',
    layout: 'renderGraph'
},
mounted() {
    this.renderGraph();
},
methods: {
    renderGraph() {
    Plotly.newPlot(this.$refs.plotlyGraph, this.data, this.layout);
    }
}
};
</script>

<style>
/* Add any necessary styles here */
</style>