import Vue from 'vue'
import Vuex from 'vuex'
import * as api from '@/api'

Vue.use(Vuex)

export default new Vuex.Store({
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
    isStartingApp: false,
    deviceLog: []
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
    setIsStartingApp (state, isStartingApp) {
      state.isStartingApp = isStartingApp
    },
    addDeviceLog (state, logList) {
      const displayLogLength = 200
      if (state.deviceLog.length > displayLogLength) {
        state.deviceLog.splice(0, state.deviceLog.length - displayLogLength)
      }
      for (const log of logList) {
        state.deviceLog.push(log)
      }
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
    startApp ({ state, commit }) {
      commit('setIsStartingApp', true)
      api.startApp(state.focusDeviceId, state.focusPackageName)
        .then(response => {
          commit('setIsStartingApp', false)
        })
    },
    stopApp ({ state }) {
      api.stopApp(state.focusDeviceId, state.focusPackageName)
    }
  }
})
