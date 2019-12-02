<template>
  <div style="height:100%">
    <Row class="info-header" type="flex" align="middle">
      <strong>App Shortcuts</strong>
    </Row>
    <Row type="flex" align="middle" style="padding: 5px;">
      <i-select size="small" v-model="packageName" placeholder="package name" filterable style="width:calc(100% - 310px);">
        <i-option v-for="item in packages" :value="item" :key="item">{{ item }}</i-option>
      </i-select>
      <Button type="primary" size="small" style="margin-left:5px" @click.native="stopApp" :disabled="!packageName">Stop App</Button>
      <Button type="primary" size="small" style="margin-left:5px" @click.native="shownUninstallModal=true" :disabled="!packageName">Uninstall</Button>
      <Button type="primary" size="small" style="margin-left:5px" @click.native="clearCache" :disabled="!packageName">Clear Cache</Button>
      <Button type="primary" size="small" style="margin-left:5px" @click.native="showAppDetail = true" :disabled="!packageName">More Detail</Button>
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
    }
  },
  methods: {
    stopApp () {
      this.$store.dispatch('stopApp')
    },
    uninstall () {
      this.$store.dispatch('uninstallApp')
      this.shownUninstallModal = false
    },
    clearCache () {
      this.$store.dispatch('clearAppCache')
    }
  }
}
</script>
