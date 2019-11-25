<template>
  <div style="height:100%">
    <div id="scroller" v-if="terminalLogs.length" class="android-console">
      <pre v-for="(log, index) in terminalLogs" :key="index" style="margin:0px">{{log}}</pre>
      <div id="anchor"></div>
    </div>
    <div v-else class="android-console">
      <p style="text-align: center;">No console log</p>
    </div>
    <Poptip v-model="isShownPoptip" placement="top-start" disabled>
      <div slot="content">{{PoptipContent}}</div>
      <Input
        prefix="ios-arrow-forward"
        size="small"
        class="android-console-input"
        v-model="commandLine"
        placeholder="Use ↑ to view history command"
        @on-enter="onInputEnter"
        @on-keydown="onKeyPress"
        style="width:calc(75vw - 68px);"
      />
      <Button type="primary" size="small" @click="showModal">Format it</Button>
    </Poptip>
    <Modal v-model="isShownModal" title="Command editor" width="60%" :styles="{top: '80px'}" :footer-hide=true>
      <div class="command-format">
        <div v-for="(value, index) in commandSplit" :key="index" style="padding-bottom:10px;">
          <InputItem :index="index" />
        </div>
        <Button type="primary" long size="small" icon="md-add" @click.native="addCommandSplit"></Button>
      </div>
      <Divider dashed size="small" orientation="left">
        <span style="color:#515a6e">Preview</span>
      </Divider>
      <div class="command-after-format">
        <code style="word-break:break-all">
          {{commandLine}}
        </code>
      </div>
    </Modal>
  </div>
</template>

<script>
import InputItem from '@/components/ConsoleLogModalItem.vue'

export default {
  components: {
    InputItem
  },
  data () {
    return {
      isShownModal: false,
      isShownPoptip: false,
      PoptipContent: ''
    }
  },
  created () {
    this.$store.dispatch('getHistoryCommand')
  },
  computed: {
    commandLine: {
      get () {
        return this.$store.state.console.commandLine
      },
      set (val) {
        this.$store.commit('setCommandLine', val)
      }
    },
    commandSplit () {
      return this.$store.state.console.commandSplit
    },
    historyCommand () {
      return this.$store.state.console.historyCommand
    },
    terminalLogs () {
      return this.$store.state.console.terminalLog
    }
  },
  watch: {
    commandSplit (val) {
      this.$store.commit('setCommandLine', val.join(' '))
    }
  },
  methods: {
    showModal () {
      this.$store.commit('setCommandSplit', this.getCommandSplit())
      this.isShownModal = true
    },
    getCommandSplit () {
      const splitChar = ' -'
      const commandChar = '-'
      let commandSplit = this.commandLine.trim().split(splitChar)
      for (let i = 1; i < commandSplit.length; i++) {
        commandSplit[i] = commandChar + commandSplit[i]
      }
      return commandSplit
    },
    onInputEnter () {
      if (this.commandLine) {
        this.$store.commit('addTerminalLog', '> ' + this.commandLine)
        this.$store.dispatch('executeCommand', { command: this.commandLine })
        this.$store.commit('setHistoryCommandIndex', -1)
        this.$store.commit('setCommandLine', '')
      }
    },
    onKeyPress (payload) {
      let pointer
      if (payload.key === 'ArrowUp') {
        pointer = this.$store.state.console.historyCommandIndex + 1
      } else if (payload.key === 'ArrowDown') {
        pointer = this.$store.state.console.historyCommandIndex - 1
      } else {
        return
      }

      if (pointer <= -1) {
        this.$store.commit('setHistoryCommandIndex', -1)
        this.$store.commit('setCommandLine', '')
        this.isShownPoptip = false
      } else if (pointer > this.historyCommand.length) {
        this.PoptipContent = 'Nothing forward, display ' + this.historyCommand.length + ' history commands at most'
        this.isShownPoptip = true
      } else {
        this.$store.commit('setHistoryCommandIndex', pointer)
        this.$store.commit('setCommandLine', JSON.parse(this.historyCommand[pointer].content))
        this.isShownPoptip = false
      }
    },
    addCommandSplit () {
      this.$store.commit('addCommandSplit', '')
    }
  }
}
</script>

<style>
#scroller * {
  overflow-anchor: none;
}
#anchor {
  overflow-anchor: auto;
  height: 1px;
}
.android-console {
  padding: 10px;
  height: calc(100% - 33px - 24px);
  /* tabs-bar: 33px
    input: 24px */
  overflow-y: auto;
}
.android-console-input .ivu-input {
  background: #e8eaec;
  border-radius: 0px;
}
.command-format {
  margin-bottom: 25px;
  max-height: 40vh;
  overflow-y: auto;
}
.command-after-format {
  max-height: 20vh;
  overflow-y: auto;
}
</style>
