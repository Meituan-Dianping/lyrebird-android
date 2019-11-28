<template>
  <div style="height:100%">
    <Row class="info-header" type="flex" align="middle">
      <i-col span="24">
        <strong>Install App</strong>
      </i-col>
    </Row>
    <Row style="padding:5px;">
      <i-input
        size="small"
        v-model="inputStr"
        :search="installMode === 'remote' ? true : false"
        :placeholder="installMode === 'remote' ? 'Input search string' : 'Input link'"
        @on-enter="installMode === 'remote' ? searchApp() : installApp(inputStr)"
      >
        <Select
          v-model="selectedInstallIndex"
          size="small"
          slot="prepend"
          style="width:80px;"
          placeholder="Source"
          not-found-text="No data"
          :label-in-value=true
        >
          <Option v-for="(item, index) in installOptions" :value="index" :key="index">{{ item.name }}</Option>
          <Divider v-show="installOptions.length" size="small" dashed style="margin:0px 0px"/>
          <Option value="link" key="link">Link</Option>
        </Select>
        <span slot="append">
          <Icon
            :type="installMode === 'remote' ? 'md-search' : 'md-archive'"
            @click="installMode === 'remote' ? searchApp() : installApp(inputStr)"
          />
        </span>
      </i-input>
    </Row>
    <Spin fix v-if="isLoadingAppList||isInstallingApp||isDownloadingApp">
      <Icon type="ios-loading" size=18 class="spin-icon-load"></Icon>
      <div>{{spinLoadingText}}</div>
    </Spin>
    <div v-else-if="appList.length" style="height:calc(100% - 62px);overflow-y:auto;">
      <Row type="flex" align="middle" v-for="item in appList" :key="item.id" style="border-bottom: 1px dashed #ccc;padding:5px;">
        <Tooltip content="Install" placement="bottom-start" :delay="500">
          <Icon
            type="md-archive"
            color="#5cadff"
            size="16"
            style="cursor: pointer;padding-right:5px;"
            @click.stop="installApp(item.url)"
          />
        </Tooltip>
        <span>{{item.time.substring(5)}}</span>
        <span style="padding:0px 5px;word-break:break-all;font-weight:bold;">{{item.name}}</span>
      </Row>
    </div>
    <div v-else class="cell-empty">
      <p style="text-align:center;">No data</p>
    </div>
  </div>
</template>

<script>
export default {
  data () {
    return {
      inputStr: '',
      installMode: ''
    }
  },
  created () {
    this.$store.dispatch('getInstallOptions')
  },
  computed: {
    installOptions () {
      return this.$store.state.installOptions
    },
    selectedInstallIndex: {
      get () {
        return this.$store.state.selectedInstallIndex
      },
      set (val) {
        this.$store.commit('setSelectedInstallIndex', val)
      }
    },
    appList () {
      return this.$store.state.appList
    },
    isLoadingAppList () {
      return this.$store.state.isLoadingAppList
    },
    isInstallingApp () {
      return this.$store.state.isInstallingApp
    },
    isDownloadingApp () {
      return this.$store.state.isDownloadingApp
    },
    spinLoadingText () {
      if (this.isLoadingAppList) {
        return 'Loading APP list...'
      } else if (this.isDownloadingApp) {
        return 'Downloading APP...'
      } else if (this.isInstallingApp) {
        return 'Installing App...'
      } else {
        return ''
      }
    }
  },
  watch: {
    selectedInstallIndex () {
      if (this.selectedInstallIndex < this.$store.state.installOptions.length) {
        this.installMode = 'remote'
      } else {
        this.installMode = 'link'
      }
    }
  },
  methods: {
    searchApp () {
      this.$store.dispatch('loadAppList', this.inputStr)
    },
    installApp (url) {
      this.$store.dispatch('downloadAndInstallApp', url)
    }
  }
}
</script>

<style>
  .spin-icon-load{
    animation: ani-demo-spin 1s linear infinite;
  }
</style>
