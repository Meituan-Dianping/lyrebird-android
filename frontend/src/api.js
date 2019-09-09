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

export const stopApp = (deviceId, packageName) => {
  return axios({
    url: API_PREFIX + '/stop_app/' + deviceId + '/' + packageName
  })
}
