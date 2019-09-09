<template>
  <div v-if="screenShotUrl" style="text-align:center;">
    <span>
      <img :src="screenShotUrl" class="android-img">
    </span>
  </div>
</template>

<script>
export default {
  computed: {
    screenShotUrl () {
      return this.$store.state.screenShotUrl
    }
  }
}
</script>
