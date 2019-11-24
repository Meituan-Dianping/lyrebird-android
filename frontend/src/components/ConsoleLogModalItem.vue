<template>
  <Input
    size="small"
    type="textarea"
    :autosize="{ minRows: 1 }"
    v-model="commandSplitItem"
  />
</template>

<script>
export default {
  props: ['index'],
  computed: {
    commandSplitItem: {
      get () {
        return this.$store.state.console.commandSplit[this.index]
      },
      set (val) {
        this.$store.state.console.commandSplit.splice(this.index, 1, val)
      }
    }
  }
}
</script>
