import Vue from 'vue'
import App from './App.vue'
import store from './store/index'
import iView from 'iview'
import 'iview/dist/styles/iview.css'
import locale from 'iview/dist/locale/en-US'
import io from 'socket.io-client'

Vue.config.productionTip = false
Vue.use(iView, { locale })
Vue.use(iView)
Vue.prototype['$io'] = io()

new Vue({
  store,
  render: h => h(App)
}).$mount('#app')
