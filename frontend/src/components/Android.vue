<template>
  <Row>
    <i-col span="6" class="android-split">
      <device-list class="device-list"/>
      <screen-shot v-show="focusDeviceId"/>
    </i-col>

    <i-col span="18" class="android-split">
      <div v-if="focusDeviceId" style="height:100vh">
        <Split v-model="split" mode="vertical">
          <Row slot="top">
            <package-board/>
          </Row>
          <Row slot="top" style="height:calc(100% - 63px)">
            <i-col span="12" style="height:100%;border-right:1px solid #e8eaec;">
              <package-launch/>
            </i-col>
            <i-col span="12" style="height:100%">
              <package-install/>
            </i-col>
          </Row>
          <div slot="bottom" style="height:100%">
            <Tabs value="console" size="small" :animated="false" style="height:100%">
              <TabPane label="Console" name="console" style="height:100%">
                <ConsoleLog/>
              </TabPane>
              <TabPane label="DeviceLog" name="log" style="height:100%">
                <device-log/>
              </TabPane>
            </Tabs>
          </div>
        </Split>
      </div>
      <div v-else>
        <p class="cell-empty">Please select an Android device</p>
      </div>
    </i-col>
  </Row>
</template>

<script>
import ConsoleLog from '@/components/ConsoleLog.vue'
import DeviceLog from '@/components/DeviceLog.vue'
import DeviceList from '@/components/DeviceList.vue'
import ScreenShot from '@/components/ScreenShot.vue'
import PackageLaunch from '@/components/PackageLaunch.vue'
import PackageInstall from '@/components/PackageInstall.vue'
import PackageBoard from '@/components/PackageBoard.vue'

export default {
  components: {
    ConsoleLog,
    DeviceLog,
    DeviceList,
    ScreenShot,
    PackageBoard,
    PackageInstall,
    PackageLaunch
  },
  data () {
    return {
      split: 0.7
    }
  },
  created () {
    this.$store.dispatch('loadDevices')
    this.$io.on('device', this.getDevices)
  },
  computed: {
    focusDeviceId () {
      return this.$store.state.focusDeviceId
    }
  },
  methods: {
    getDevices () {
      this.$store.dispatch('loadDevices')
    }
  }
}
</script>

<style>
.android-split {
  height: 100vh;
  border-left:1px solid #e8eaec;
  border-right:1px solid #e8eaec;
  word-break: break-all;
}
.android-split-pane{
  overflow-y: auto;
  height: 100%;
}
.cell-empty{
  position: absolute;
  top:40%;
  left:50%;
  transform:translate(-50%,-50%);
  text-align: center;
}
.device-list {
  height: 30vh;
}
.android-img {
  height: calc(70vh - 10px);
}
.info-header {
  background-color: #f8f8f9;
  padding: 5px;
}
.ivu-tabs > .ivu-tabs-bar {
  border-bottom: 0px;
  background-color: #f8f8f9;
  margin-bottom: 0px;
  font-weight: bolder;
}
.ivu-tabs > .ivu-tabs-content {
  height: 100%;
}
</style>
