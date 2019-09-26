<template>
  <div id="scroller" class="android-log">
    <p v-for="(log, index) in logs" :key="index">
      {{ log }}
      <div id="anchor"></div>
    </p>
  </div>
</template>

<script>
export default {
  created () {
    this.$io.on('android-log', this.pushLog)
  },
  computed: {
    logs () {
      return this.$store.state.console.deviceLog
    }
  },
  methods: {
    pushLog (logList) {
      this.$store.commit('addDeviceLogs', logList)
    }
  }
}
</script>

<style>
#scroller * {
  overflow-anchor: none;
}
#anchor {
  overflow-anchor: auto;
  height: 1px;
}
.android-log {
  padding: 10px;
  height: calc(100% - 33px);
  /* tabs-bar: 33px */
  overflow-y: auto;
}
</style>
