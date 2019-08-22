<template>
  <div>
    <Row class="info-header" type="flex" align="middle">
      <i-col span="24">
        <strong>Log</strong>
      </i-col>
    </Row>
    <div ref="logContainer" class="android-log">
      <p v-for="(log, index) in logs" :key="index">
        {{ log }}
      </p>
    </div>
  </div>
</template>

<script>
export default {
  created () {
    this.$io.on('log', this.pushLog)
  },
  computed: {
    logs () {
      return this.$store.state.deviceLog
    }
  },
  methods: {
    pushLog (logList) {
      this.$store.commit('addDeviceLog', logList)
      setTimeout(this.scrollDownLog, 500)
    },
    scrollDownLog () {
      const container = this.$refs.logContainer
      this.$refs.logContainer.scrollTop = container.scrollHeight
    }
  }
}
</script>
