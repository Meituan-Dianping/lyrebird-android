import * as api from '@/api'

export default {
  state: {
    deviceLog: [],
    terminalLog: [],
    commandLine: '',
    commandSplit: [],
    historyCommand: [],
    historyCommandIndex: -1
  },
  mutations: {
    addDeviceLogs (state, logList) {
      const displayLogLength = 200
      if (state.deviceLog.length > displayLogLength) {
        state.deviceLog.splice(0, state.deviceLog.length - displayLogLength)
      }
      for (const log of logList) {
        state.deviceLog.push(log)
      }
    },
    addTerminalLog (state, log) {
      state.terminalLog.push(log)
    },
    setCommandLine (state, commandLine) {
      state.commandLine = commandLine
    },
    setCommandSplit (state, commandSplit) {
      state.commandSplit = commandSplit
    },
    addCommandSplit (state, item) {
      state.commandSplit.push(item)
    },
    setHistoryCommand (state, historyCommand) {
      state.historyCommand = historyCommand
    },
    setHistoryCommandIndex (state, historyCommandIndex) {
      state.historyCommandIndex = historyCommandIndex
    }
  },
  actions: {
    getHistoryCommand ({ commit }) {
      api.getHistoryCommand().then(response => {
        commit('setHistoryCommand', response.data.events)
      })
    }
  }
}
