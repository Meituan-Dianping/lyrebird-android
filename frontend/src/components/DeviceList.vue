<template>
  <div v-if="Object.keys(devices).length === 0" class="cell-empty">
    <p style="text-align:center;">No devices</p>
  </div>
  <div v-else>
    <CellGroup @on-click="onCellClick">
      <Cell
        class="device-list-cell"
        v-for="(device, id) in devices"
        :key="id"
        :name="id"
        :selected="focusDeviceId === id"
      >
        <span>{{device.model ? device.model : 'Unknown'}}</span>
        <span style="padding-left:20px;font-size:12px;color:#bbbbbb">{{id}}</span>
        <Icon type="md-camera" slot="extra" size="18" @click.native="takeScreenShot"/>
      </Cell>
    </CellGroup>
  </div>
</template>

<script>
export default {
  computed: {
    devices () {
      return this.$store.state.devices
    },
    focusDeviceId () {
      return this.$store.state.focusDeviceId
    }
  },
  methods: {
    onCellClick (deviceId) {
      this.$store.commit('setFocusDeviceId', deviceId)
      this.$store.commit('setDeviceInfo', this.devices[deviceId])
      this.$store.dispatch('loadPackages')
      this.$store.dispatch('takeScreenShot')
    },
    takeScreenShot () {
      if (this.focusDeviceId) {
        this.$store.dispatch('takeScreenShot')
      }
    }
  }
}
</script>

<style>
.device-list-cell {
  padding: 5px 5px 5px 15px;
  border-bottom: 1px solid #dcdee2;
}
</style>
