import * as api from '@/api'
import { bus } from '@/eventbus'

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
    loadStartConfigOptions ({ state, commit, dispatch }) {
      api.getStartConfigOptions()
        .then(response => {
          commit('setStartConfigOptions', response.data.start_options)
          if (response.data.start_options.length && state.selectedStartConfigIndex === null) {
            commit('setSelectedStartConfigIndex', 0)
            dispatch('loadLaunchActions')
          }
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load start config list error: ' + error.data.message)
        })
    },
    loadLaunchActions ({ state, commit }) {
      api.getLaunchActions(state.startConfigOptions[state.selectedStartConfigIndex].id)
        .then(response => {
          commit('setLaunchActions', response.data.launch_actions)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load start config ' + state.startConfigOptions[state.selectedStartConfigIndex].name + ' error: ' + error.data.message)
        })
    },
    saveLaunchActions ({ state, dispatch }) {
      api.saveLaunchActions(
        state.startConfigOptions[state.selectedStartConfigIndex].id,
        state.launchActions
      )
        .then(response => {
          dispatch('loadLaunchActions')
          bus.$emit('msg.success', 'Save start config ' + state.startConfigOptions[state.selectedStartConfigIndex].name + ' success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Save start config ' + state.startConfigOptions[state.selectedStartConfigIndex].name + ' error: ' + error.data.message)
        })
    },
    createLaunchActions ({ state, commit, dispatch }, newConfigName) {
      api.createLaunchActions(
        state.startConfigOptions[state.selectedStartConfigIndex].id,
        state.launchActions,
        newConfigName
      )
        .then(response => {
          commit('setSelectedStartConfigIndex', response.data.index)
          dispatch('loadStartConfigOptions')
          bus.$emit('msg.success', 'Create start config ' + newConfigName + ' success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Create start config ' + newConfigName + ' error: ' + error.data.message)
        })
    },
    launchApp ({ state, commit }, { deviceId, packageName }) {
      commit('setIsStartingApp', true)
      api.launchApp(deviceId, packageName, state.launchActions)
        .then(response => {
          commit('setIsStartingApp', false)
          bus.$emit('msg.success', 'Start App ' + state.focusPackageName + ' success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Start App ' + state.focusPackageName + ' error: ' + error.data.message)
        })
    }
  }
}
