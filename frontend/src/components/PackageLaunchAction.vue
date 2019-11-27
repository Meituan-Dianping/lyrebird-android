<template>
  <p style="word-break:break-all;">
    <span class="start-item-info-btn">
      <Tooltip
        :content="infoDesc?infoDesc:'No description'"
        :delay="500"
        placement="bottom-start"
        theme="light"
        max-width="500"
      >
        <Icon type="ios-help-circle-outline" size="14"/>
      </Tooltip>
    </span>
    <span class="start-item-key">
      <Input size="small" v-model="infoKey" placeholder="Input key" />
    </span>
    <span class="start-item-type">
      <Select v-model="infoValueType" size="small">
        <Option v-for="item in valueTypeList" :value="item.value" :key="item.value">{{ item.label }}</Option>
      </Select>
    </span>
    <span class="start-item-value">
      <i-switch
        v-if="infoValueType==='boolean'"
        size="large"
        v-model="infoValue"
      >
        <span slot="open">true</span>
        <span slot="close">false</span>
      </i-switch>
      <Input
        v-else
        size="small"
        type="textarea"
        v-model="infoValue"
        :autosize="{minRows: 1,maxRows: 20}"
      />
    </span>
    <span class="start-item-delete-btn">
      <Tooltip content="Delete" :delay="500" placement="bottom-end">
        <Icon type="md-trash" size=14 @click.native="deleteInfoKey"/>
      </Tooltip>
    </span>
  </p>
</template>

<script>
export default {
  props: ['index'],
  data () {
    return {
      infoValueType: '',
      valueTypeList: [
        {
          value: 'text',
          label: 'Text'
        },
        {
          value: 'boolean',
          label: 'Boolean'
        },
        {
          value: 'object',
          label: 'JSON'
        }
      ]
    }
  },
  created () {
    this.initValueType()
  },
  computed: {
    infoDesc () {
      return this.$store.state.start.launchActions[this.index].desc
    },
    infoKey: {
      get () {
        return this.$store.state.start.launchActions[this.index].key
      },
      set (val) {
        this.$store.commit('setLaunchActionsItemKey', { index: this.index, info: val })
      }
    },
    infoValue: {
      get () {
        if (this.infoValueType === 'object') {
          return JSON.stringify(this.$store.state.start.launchActions[this.index].value, null, 4)
        } else if (this.infoValueType === 'boolean') {
          return Boolean(this.$store.state.start.launchActions[this.index].value)
        } else {
          if (typeof this.$store.state.start.launchActions[this.index].value === 'object') {
            return JSON.stringify(this.$store.state.start.launchActions[this.index].value)
          } else {
            return String(this.$store.state.start.launchActions[this.index].value)
          }
        }
      },
      set (val) {
        if (this.infoValueType === 'object') {
          let valObj = JSON.parse(val)
          this.$store.commit('setLaunchActionsItemValue', { index: this.index, info: valObj })
        } else {
          this.$store.commit('setLaunchActionsItemValue', { index: this.index, info: val })
        }
      }
    }
  },
  methods: {
    deleteInfoKey () {
      this.$store.commit('deleteLaunchActionsItem', this.index)
    },
    initValueType () {
      if (typeof this.$store.state.start.launchActions[this.index].value === 'boolean') {
        this.infoValueType = 'boolean'
      } else if (typeof this.$store.state.start.launchActions[this.index].value === 'object') {
        this.infoValueType = 'object'
      } else {
        this.infoValueType = 'text'
      }
    }
  }
}
</script>

<style>
.start-item-info-btn {
  line-height: 24px;
  vertical-align: top;
}
.start-item-key {
  width: 100px;
  display: inline-block;
  vertical-align: top;
  margin-left: 5px;
}
.start-item-type {
  width: 80px;
  display: inline-block;
  vertical-align: top;
  margin-left: 5px;
}
.start-item-value {
  width: calc(100% - 238px);
  display: inline-block;
  vertical-align: middle;
  margin-left: 5px
}
.start-item-delete-btn {
  line-height: 24px;
  vertical-align: top;
  margin-left: 5px;
}
.enable-button {
  cursor: pointer;
}
.disable-button {
  color: #c5c8ce;
}
</style>
