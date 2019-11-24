import Vue from 'vue'
import Vuex from 'vuex'
import * as api from '@/api'
import start from '@/store/start'
import console from '@/store/console'

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
    packageDetail: null,
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
        commit('setDevices', response.data)
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
    loadPackages ({ state, commit }) {
      api.getPackages(state.focusDeviceId).then(response => {
        commit('setPackages', response.data)
      })
    },
    loadDefaultPackageName ({ commit, dispatch }) {
      api.getPackageName().then(response => {
        if (response.data.packageName) {
          commit('setFocusPackageName', response.data.packageName)
          dispatch('loadPackageInfo')
        }
      })
    },
    loadPackageInfo ({ state, commit }) {
      api.getAppInfo(state.focusDeviceId, state.focusPackageName).then(response => {
        commit('setPackageInfo', response.data)
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
    getInstallOptions ({ commit }) {
      api.getInstallOptions()
        .then(response => {
          if (response.data.code === 1000) {
            commit('setInstallOptions', response.data.install_options)
            if (response.data.install_options.length) {
              commit('setSelectedInstallIndex', 0)
            }
          } else if (response.data.code === 3000) {
            console.log('get install source options error:', response)
          }
        })
    },
    loadAppList ({ state, commit }, searchStr) {
      commit('setIsLoadingAppList', true)
      api.getAppList(state.installOptions[state.selectedInstallIndex], searchStr)
        .then(response => {
          commit('setAppList', response.data.applist)
          commit('setIsLoadingAppList', false)
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
    installApp ({ state, commit }, path) {
      commit('setIsInstallingApp', true)
      api.installApp(state.focusDeviceId, path)
        .then(response => {
          commit('setIsInstallingApp', false)
        })
    }
  }
})
