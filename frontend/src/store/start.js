import * as api from '@/api'

export default {
  state: {
    isStartingApp: false,
    startConfigOptions: [],
    selectedStartConfigIndex: null,
    launchActions: []
  },
  mutations: {
    setIsStartingApp (state, isStartingApp) {
      state.isStartingApp = isStartingApp
    },
    setStartConfigOptions (state, startConfigOptions) {
      state.startConfigOptions = startConfigOptions
    },
    setSelectedStartConfigIndex (state, selectedStartConfigIndex) {
      state.selectedStartConfigIndex = selectedStartConfigIndex
    },
    setLaunchActions (state, launchActions) {
      state.launchActions = launchActions
    },
    addLaunchActionsItem (state, launchActionsItem) {
      state.launchActions.push(launchActionsItem)
    },
    deleteLaunchActionsItem (state, index) {
      state.launchActions.splice(index, 1)
    },
    setLaunchActionsItemKey (state, payload) {
      state.launchActions[payload.index].key = payload.info
    },
    setLaunchActionsItemValue (state, payload) {
      state.launchActions[payload.index].value = payload.info
    }
  },
  actions: {
    loadStartConfigOptions ({ commit }) {
      api.getStartConfigOptions()
        .then(response => {
          commit('setStartConfigOptions', response.data.start_options)
        })
    },
    loadLaunchActions ({ state, commit }) {
      api.getLaunchActions(state.startConfigOptions[state.selectedStartConfigIndex])
        .then(response => {
          commit('setLaunchActions', response.data.launch_actions)
        })
    },
    saveLaunchActions ({ state, dispatch }) {
      api.saveLaunchActions(
        state.startConfigOptions[state.selectedStartConfigIndex],
        state.launchActions
      )
        .then(response => {
          dispatch('loadLaunchActions')
        })
    },
    createLaunchActions ({ state, commit, dispatch }, newConfigName) {
      api.createLaunchActions(
        state.startConfigOptions[state.selectedStartConfigIndex],
        state.launchActions,
        newConfigName
      )
        .then(response => {
          dispatch('loadStartConfigOptions')
          commit('setSelectedStartConfigIndex', response.data.index)
        })
    },
    launchApp ({ state, commit }, { deviceId, packageName }) {
      commit('setIsStartingApp', true)
      api.launchApp(deviceId, packageName, state.launchActions)
        .then(response => {
          commit('setIsStartingApp', false)
        })
    }
  }
}
