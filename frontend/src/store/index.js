import Vue from 'vue'
import Vuex from 'vuex'
import * as api from '@/api'
import start from '@/store/start'
import console from '@/store/console'
import { bus } from '@/eventbus'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    start,
    console
  },
  state: {
    devices: {},
    focusDeviceId: null,
    deviceInfo: {},
    isTakingScreen: false,
    screenShotUrl: null,
    packages: [],
    focusPackageName: null,
    packageInfo: {},
    installOptions: [],
    selectedInstallIndex: null,
    appList: [],
    isLoadingAppList: false,
    isDownloadingApp: false,
    isInstallingApp: false
  },
  mutations: {
    setDevices (state, devices) {
      state.devices = devices
    },
    setFocusDeviceId (state, deviceId) {
      state.focusDeviceId = deviceId
    },
    setDeviceInfo (state, deviceInfo) {
      state.deviceInfo = deviceInfo
    },
    setIsTakingScreen (state, isTakingScreen) {
      state.isTakingScreen = isTakingScreen
    },
    setScreenShotUrl (state, screenShotUrl) {
      state.screenShotUrl = screenShotUrl
    },
    setPackages (state, packages) {
      state.packages = packages
    },
    setFocusPackageName (state, focusPackageName) {
      state.focusPackageName = focusPackageName
    },
    setPackageInfo (state, packageInfo) {
      state.packageInfo = packageInfo
    },
    setInstallOptions (state, installOptions) {
      state.installOptions = installOptions
    },
    setSelectedInstallIndex (state, selectedInstallIndex) {
      state.selectedInstallIndex = selectedInstallIndex
    },
    setAppList (state, appList) {
      state.appList = appList
    },
    setIsLoadingAppList (state, isLoadingAppList) {
      state.isLoadingAppList = isLoadingAppList
    },
    setIsDownloadingApp (state, isDownloadingApp) {
      state.isDownloadingApp = isDownloadingApp
    },
    setIsInstallingApp (state, isInstallingApp) {
      state.isInstallingApp = isInstallingApp
    }
  },
  actions: {
    loadDevices ({ state, commit }) {
      api.getDevices().then(response => {
        commit('setDevices', response.data.device_list)
        if (!state.devices.hasOwnProperty(state.focusDeviceId)) {
          commit('setFocusDeviceId', null)
          commit('setScreenShotUrl', null)
        }
      })
    },
    takeScreenShot ({ state, commit }) {
      commit('setIsTakingScreen', true)
      api.getScreenShot(state.focusDeviceId).then(response => {
        commit('setScreenShotUrl', response.data.imgUrl)
        commit('setIsTakingScreen', false)
      })
    },
    loadPackages ({ state, commit, dispatch }) {
      api.getPackages(state.focusDeviceId).then(response => {
        commit('setPackages', response.data.packages)
        dispatch('loadDefaultPackageName')
      })
    },
    loadDefaultPackageName ({ state, commit, dispatch }) {
      api.getPackageName().then(response => {
        if (response.data.package_name && state.packages.includes(response.data.package_name)) {
          commit('setFocusPackageName', response.data.package_name)
          dispatch('loadPackageInfo')
        }
      })
    },
    loadPackageInfo ({ state, commit }) {
      api.getAppInfo(state.focusDeviceId, state.focusPackageName).then(response => {
        commit('setPackageInfo', response.data.app_info)
      })
    },
    executeCommand ({ state, commit, dispatch }, { command }) {
      api.executeCommand(state.focusDeviceId, command).then(response => {
        if (response.data.code === 1000) {
          commit('addTerminalLog', response.data.data)
        } else if (response.data.code === 3000) {
          commit('addTerminalLog', response.data.message)
        }
        dispatch('getHistoryCommand')
      })
    },
    getInstallOptions ({ commit, dispatch }) {
      api.getInstallOptions()
        .then(response => {
          commit('setInstallOptions', response.data.install_options)
          if (response.data.install_options.length) {
            commit('setSelectedInstallIndex', 0)
            dispatch('loadAppList', '')
          }
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load install remote list error: ' + error.data.message)
        })
    },
    loadAppList ({ state, commit }, searchStr) {
      commit('setIsLoadingAppList', true)
      api.getAppList(state.installOptions[state.selectedInstallIndex], searchStr)
        .then(response => {
          commit('setAppList', response.data.applist)
          commit('setIsLoadingAppList', false)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load App list ' + state.focusPackageName + ' error: ' + error.data.message)
        })
    },
    downloadAndInstallApp ({ commit, dispatch }, url) {
      commit('setIsDownloadingApp', true)
      api.downloadApk(url)
        .then(response => {
          commit('setIsDownloadingApp', false)
          dispatch('installApp', response.data.path)
        })
    },
    installApp ({ state, commit, dispatch }, path) {
      commit('setIsInstallingApp', true)
      api.installApp(state.focusDeviceId, path)
        .then(response => {
          commit('setIsInstallingApp', false)
          dispatch('loadPackages')
          bus.$emit('msg.success', 'Install App ' + state.focusPackageName + ' success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Install App ' + state.focusPackageName + ' error: ' + error.data.message)
        })
    },
    uninstallApp ({ state, commit, dispatch }) {
      api.uninstallApp(state.focusDeviceId, state.focusPackageName)
        .then(response => {
          dispatch('loadPackages')
          commit('setFocusPackageName', null)
          commit('setPackageInfo', {})
          bus.$emit('msg.success', 'Uninstall App ' + state.focusPackageName + ' success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Uninstall App ' + state.focusPackageName + ' error: ' + error.data.message)
        })
    },
    stopApp ({ state }) {
      api.stopApp(state.focusDeviceId, state.focusPackageName)
        .then(response => {
          bus.$emit('msg.success', 'Stop App ' + state.focusPackageName + ' success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Stop App ' + state.focusPackageName + ' error: ' + error.data.message)
        })
    },
    clearAppCache ({ state }) {
      api.clearAppCache(state.focusDeviceId, state.focusPackageName)
        .then(response => {
          bus.$emit('msg.success', 'Clear App cache ' + state.focusPackageName + ' success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Clear App cache ' + state.focusPackageName + ' error: ' + error.data.message)
        })
    }
  }
})
