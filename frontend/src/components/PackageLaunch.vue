<template>
  <div style="height:100%">
    <Row class="info-header" type="flex" align="middle">
      <i-col span="24">
        <strong>Start App</strong>
      </i-col>
    </Row>
    <Row style="padding:5px;">
      <Select
        size="small"
        placeholder="Select a custom start config"
        v-model="selectedStartConfigIndex"
        clearable
        filterable
        allow-create
        @on-change="getLaunchActions"
        style="width:calc(100% - 180px);"
      >
        <Option v-for="(item, index) in startConfigOptions" :value="index" :label="item.name" :key="index">{{ item.name }}</Option>
      </Select>
      <Button
        type="primary"
        size="small"
        @click.native="saveLaunchActions"
        :disabled="selectedStartConfigIndex === null"
        style="margin-left:5px"
      >
        Save
      </Button>
      <Button
        type="primary"
        size="small"
        @click.native="shownCreateConfigModal=true"
        :disabled="selectedStartConfigIndex === null"
        style="margin-left:5px"
      >
        Save as
      </Button>
      <Button
        type="primary"
        size="small"
        @click.native="launchApp"
        :disabled="isStartingApp || !packageName"
        style="margin-left:5px"
      >
        Start App
      </Button>
    </Row>
    <Spin fix v-if="isStartingApp">
      <Icon type="ios-loading" size=18 class="spin-icon-load"></Icon>
      <div>Starting APP</div>
    </Spin>
    <div v-else style="height:calc(100% - 62px);overflow-y:auto;">
      <div v-for="(info, index) in launchActions" :key="index" style="padding:5px">
        <Divider v-show="isShownDivider(index)" dashed size="small" orientation="center">
          <span style="color:#515a6e">{{info.group?info.group:'None'}}</span>
        </Divider>
        <launch-action :index="index"/>
      </div>
      <Row type="flex" justify="end" style="padding:5px">
        <Tooltip content="Add" :delay="500" placement="bottom-end">
          <Icon type="md-add" size=14 @click.native="addLaunchActionsItem" />
        </Tooltip>
      </Row>
    </div>
    <Modal v-model="shownCreateConfigModal" title="Create launch config">
      <Row type="flex" align="middle">
        <b>Config name:</b>
        <Input
          v-model="newConfigName"
          placeholder="Input start config name"
          style="width:calc(100% - 88px);margin-left:10px;"
        />
      </Row>
      <div slot="footer">
        <Button size="large" type="primary" long @click="createLaunchActions">
          Save
        </Button>
      </div>
    </Modal>
  </div>
</template>

<script>
import LaunchAction from '@/components/PackageLaunchAction.vue'

export default {
  components: {
    LaunchAction
  },
  created () {
    this.$store.dispatch('loadStartConfigOptions')
  },
  data () {
    return {
      newConfigName: '',
      shownCreateConfigModal: false
    }
  },
  computed: {
    packageName () {
      return this.$store.state.focusPackageName
    },
    startConfigOptions () {
      return this.$store.state.start.startConfigOptions
    },
    selectedStartConfigIndex: {
      get () {
        return this.$store.state.start.selectedStartConfigIndex
      },
      set (val) {
        if (val === undefined) {
          this.$store.commit('setSelectedStartConfigIndex', null)
        } else {
          this.$store.commit('setSelectedStartConfigIndex', val)
        }
      }
    },
    launchActions () {
      return this.$store.state.start.launchActions
    },
    isStartingApp () {
      return this.$store.state.start.isStartingApp
    }
  },
  methods: {
    getLaunchActions (payload) {
      if (payload === undefined) {
        this.$store.commit('setLaunchActions', [])
      } else {
        this.$store.dispatch('loadLaunchActions')
      }
    },
    addLaunchActionsItem () {
      this.$store.commit('addLaunchActionsItem', {
        key: '',
        value: '',
        group: '',
        desc: ''
      })
    },
    saveLaunchActions () {
      this.$store.dispatch('saveLaunchActions')
    },
    createLaunchActions () {
      this.$store.dispatch('createLaunchActions', this.newConfigName)
      this.shownCreateConfigModal = false
      this.newConfigName = ''
    },
    launchApp () {
      this.$store.dispatch('launchApp', {
        deviceId: this.$store.state.focusDeviceId,
        packageName: this.$store.state.focusPackageName
      })
    },
    isShownDivider (index) {
      let currentAction = this.launchActions[index]
      let lastAction = this.launchActions[index - 1]
      if (!currentAction.group) {
        return false
      } else if (!lastAction || !lastAction.group) {
        return true
      } else {
        return currentAction.group.toLowerCase() !== lastAction.group.toLowerCase()
      }
    }
  }
}
</script>

<style>
  .spin-icon-load{
    animation: ani-demo-spin 1s linear infinite;
  }
</style>
