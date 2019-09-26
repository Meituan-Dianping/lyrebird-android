<template>
  <div>
    <Row class="info-header" type="flex" align="middle">
      <i-col span="6">
        <strong>APP information</strong>
      </i-col>
      <i-col span="18" align="right">
        <Button type="primary" size="small" style="margin:0px 5px" @click.native="startApp" :disabled="isStartingApp || !packageName">Start app</Button>
        <Button type="primary" size="small" style="margin:0px 5px" @click.native="stopApp" :disabled="!packageName">Stop app</button>
        <Button type="primary" size="small" style="margin:0px 5px" @click.native="showAppDetail = true" :disabled="!packageName">more detail</Button>
      </i-col>
    </Row>

    <Row style="padding:10px;">
      <i-col span="6"><b>PackageName</b></i-col>
      <i-col span="18">
        <i-select size="small" v-model="packageName" placeholder="package name" filterable>
          <i-option v-for="item in packages" :value="item.value" :key="item.value">{{ item.label }}</i-option>
        </i-select>
      </i-col>
    </Row>
    <Row style="padding:10px">
      <i-col span="6"><b>StartActivity</b></i-col>
      <i-col span="18">
        <span>{{packageInfo.launchActivity}}</span>
      </i-col>
    </Row>
    <Row style="padding:10px">
      <i-col span="6"><b>AppVersion</b></i-col>
      <i-col span="18">
        <span>{{packageInfo.version}}</span>
      </i-col>
    </Row>

    <Modal v-model="showAppDetail" title="Detail" width="1000" :styles="{top: '5vh'}" :footer-hide=true>
      <pre style="height:70vh;overflow-x:auto;">{{packageInfo.detail}}</pre>
    </Modal>

  </div>
</template>

<script>
export default {
  data () {
    return {
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
    isStartingApp () {
      return this.$store.state.isStartingApp
    }
  },
  methods: {
    startApp () {
      this.$store.dispatch('startApp')
    },
    stopApp () {
      this.$store.dispatch('stopApp')
    }
  }
}
</script>
