import axios from 'axios'
const API_PREFIX = '/plugins/android/api'

const successHandler = (response) => {
  if (!response.data.hasOwnProperty('code')) {
    return Promise.reject(response)
  } else if (response.data.code !== 1000) {
    return Promise.reject(response)
  } else {
    return response
  }
}

const errorHandler = (error) => {
  return Promise.reject(error)
}

axios.interceptors.response.use(successHandler, errorHandler)

export const checkEnv = () => {
  return axios({
    url: API_PREFIX + '/check_env'
  })
}

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

export const launchApp = (deviceId, packageName, actions) => {
  return axios({
    url: API_PREFIX + '/device/' + deviceId + '/app/' + packageName + '/start',
    method: 'PUT',
    data: { actions }
  })
}

export const installApp = (deviceId, apkPath) => {
  return axios({
    url: API_PREFIX + '/device/' + deviceId + '/install',
    method: 'PUT',
    data: { apkPath }
  })
}

export const getInstallOptions = () => {
  return axios({
    url: API_PREFIX + '/template/install'
  })
}

export const downloadApk = (appUrl) => {
  return axios({
    url: API_PREFIX + '/src/apk',
    method: 'PUT',
    data: { appUrl }
  })
}

export const getAppList = (template, searchStr) => {
  return axios({
    url: API_PREFIX + '/search/app',
    method: 'POST',
    data: { template, searchStr }
  })
}

export const getStartConfigOptions = () => {
  return axios({
    url: API_PREFIX + '/template/start'
  })
}

export const getLaunchActions = (templateId) => {
  return axios({
    url: API_PREFIX + '/template/start/' + templateId
  })
}

export const saveLaunchActions = (templateId, actions) => {
  return axios({
    url: API_PREFIX + '/template/start/' + templateId,
    method: 'PUT',
    data: { actions }
  })
}

export const createLaunchActions = (templateId, actions, name) => {
  return axios({
    url: API_PREFIX + '/template/start/' + templateId,
    method: 'POST',
    data: { actions, name }
  })
}
