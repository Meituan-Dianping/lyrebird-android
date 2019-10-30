import axios from 'axios'
const API_PREFIX = '/plugins/android/api'

export const getDevices = () => {
  return axios({
    url: API_PREFIX + '/devices'
  })
}

export const getAppInfo = (deviceId, packageName) => {
  return axios({
    url: API_PREFIX + '/app/' + deviceId + '/' + packageName
  })
}

export const getPackageName = () => {
  return axios({
    url: API_PREFIX + '/package_name'
  })
}

export const getDeviceDetail = (deviceId) => {
  return axios({
    url: API_PREFIX + '/device/' + deviceId
  })
}

export const getPackages = (deviceId) => {
  return axios({
    url: API_PREFIX + '/packages/' + deviceId
  })
}

export const getScreenShot = (deviceId) => {
  return axios({
    url: API_PREFIX + '/screenshot/' + deviceId
  })
}

export const startApp = (deviceId, packageName) => {
  return axios({
    url: API_PREFIX + '/start_app/' + deviceId + '/' + packageName
  })
}

export const getHistoryCommand = () => {
  let channel = 'android.command'
  return axios({
    url: '/api/event/' + channel,
    method: 'GET'
  })
}

export const executeCommand = (deviceId, command) => {
  return axios({
    url: API_PREFIX + '/command',
    method: 'POST',
    data: { command, 'device_id': deviceId }
  })
}

export const uninstallApp = (deviceId, packageName) => {
  return axios({
    url: API_PREFIX + '/device/' + deviceId + '/app/' + packageName + '/uninstall',
    method: 'PUT'
  })
}

export const clearAppCache = (deviceId, packageName) => {
  return axios({
    url: API_PREFIX + '/device/' + deviceId + '/app/' + packageName + '/clear',
    method: 'PUT'
  })
}

export const stopApp = (deviceId, packageName) => {
  return axios({
    url: API_PREFIX + '/device/' + deviceId + '/app/' + packageName + '/stop',
    method: 'PUT'
  })
}
