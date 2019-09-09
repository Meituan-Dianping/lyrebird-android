<template>
  <div>
    <Row class="info-header" type="flex" align="middle">
      <i-col span="6">
        <strong>Device information</strong>
      </i-col>
      <i-col span="18" align="right">
        <Button type="primary" size="small" style="margin:0px 5px" @click.native="takeScreenShot" :disabled="isTakingScreen">Take screen shot</Button>
        <Button type="primary" size="small" style="margin:0px 5px" @click.native="getDeviceDetail">more detail</Button>
      </i-col>
    </Row>
    <Row style="padding:10px">
      <i-col span="8">Device ID</i-col>
      <i-col span="16">{{deviceInfo.device_id}}</i-col>
    </Row>
    <Row style="padding:10px">
      <i-col span="8">Model</i-col>
      <i-col span="16">{{deviceInfo.model}}</i-col>
    </Row>
    <Row style="padding:10px">
      <i-col span="8">Android Version</i-col>
      <i-col span="16">{{deviceInfo.releaseVersion}}</i-col>
    </Row>

    <Modal v-model="showDeviceDetail" title="Detail" width="1000" :styles="{top: '5vh'}" :footer-hide=true>
      <pre style="height:70vh;overflow-x:auto;">{{deviceDetail}}</pre>
    </Modal>
  </div>
</template>

<script>
import * as api from '@/api'

export default {
  data () {
    return {
      showDeviceDetail: false,
      deviceDetail: null
    }
  },
  computed: {
    deviceInfo () {
      return this.$store.state.deviceInfo
    },
    isTakingScreen () {
      return this.$store.state.isTakingScreen
    }
  },
  methods: {
    getDeviceDetail () {
      this.showDeviceDetail = true
      api.getDeviceDetail(this.deviceInfo.device_id).then(response => {
        this.deviceDetail = response.data
      })
    },
    takeScreenShot () {
      this.$store.dispatch('takeScreenShot')
    }
  }
}
</script>
