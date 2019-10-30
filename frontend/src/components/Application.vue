<template>
  <div style="height:100%">
    <Row class="info-header" type="flex" align="middle">
      <strong>APP Shortcuts</strong>
    </Row>
    <Row type="flex" align="middle" style="padding: 5px;">
      <i-select size="small" v-model="packageName" placeholder="package name" filterable style="width:calc(100% - 400px);">
        <i-option v-for="item in packages" :value="item.value" :key="item.value">{{ item.label }}</i-option>
      </i-select>
      <Button type="primary" size="small" style="margin:0px 5px" @click.native="startApp" :disabled="isStartingApp || !packageName">Start app</Button>
      <Button type="primary" size="small" style="margin:0px 5px" @click.native="stopApp" :disabled="!packageName">Stop app</Button>
      <Button type="primary" size="small" style="margin:0px 5px" @click.native="shownUninstallModal=true" :disabled="!packageName">Uninstall</Button>
      <Button type="primary" size="small" style="margin:0px 5px" @click.native="clearCache" :disabled="!packageName">Clear Cache</Button>
      <Button type="primary" size="small" style="margin-left:5px" @click.native="showAppDetail = true" :disabled="!packageName">more detail</Button>
    </Row>
    <Modal v-model="shownUninstallModal">
      <p slot="header" style="color:#f60;text-align:center">
        <Icon type="ios-information-circle"></Icon>
        <span>Uninstall confirmation</span>
      </p>
      <div style="text-align:center">
        <span style="font-size:14px">
          Are you sure you want to uninstall <b>{{packageName}}</b> ?
        </span>
      </div>
      <div slot="footer">
        <Button type="error" size="large" long @click="uninstall">Uninstall</Button>
      </div>
    </Modal>
    <Modal v-model="showAppDetail" title="Detail" width="1000" :styles="{top: '5vh'}" :footer-hide=true>
      <pre style="height:70vh;overflow-x:auto;">{{packageInfo.detail}}</pre>
    </Modal>
  </div>
</template>

<script>
import * as api from '@/api'

export default {
  data () {
    return {
      shownUninstallModal: false,
      showAppDetail: false
    }
  },
  computed: {
    packageName: {
      get () {
        return this.$store.state.focusPackageName
      },
      set (val) {
        this.$store.commit('setFocusPackageName', val)
        this.$store.dispatch('loadPackageInfo')
      }
    },
    packages () {
      return this.$store.state.packages
    },
    packageInfo () {
      return this.$store.state.packageInfo
    },
    focusDeviceId () {
      return this.$store.state.focusDeviceId
    },
    isStartingApp () {
      return this.$store.state.isStartingApp
    }
  },
  methods: {
    startApp () {
      this.$store.dispatch('startApp')
    },
    stopApp () {
      api.stopApp(this.focusDeviceId, this.packageName)
      .then(response => {
        console.log('Stop APP ' + this.packageName + ' result: ' + response.data.message)
      })
    },
    uninstall () {
      api.uninstallApp(this.focusDeviceId, this.packageName)
      .then(response => {
        console.log('Uninstall APP ' + this.packageName + ' result: ' + response.data.message)
      })
      this.shownUninstallModal = false
    },
    clearCache () {
      api.clearAppCache(this.focusDeviceId, this.packageName)
      .then(response => {
        console.log('Clear APP ' + this.packageName + ' cache result: ' + response.data.message)
      })
    }
  }
}
</script>
