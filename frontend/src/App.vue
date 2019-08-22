<template>
  <div id="app">
    <Android/>
  </div>
</template>

<script>
import Android from './components/Android.vue'

export default {
  name: 'app',
  components: {
    Android
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
