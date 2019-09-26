import os
import socket
import codecs
import lyrebird
from . import config
from lyrebird import context
from .device_service import DeviceService
from flask import request, jsonify, send_from_directory


device_service = DeviceService()
storage = lyrebird.get_plugin_storage()
tmp_dir = os.path.abspath(os.path.join(storage, 'tmp'))
anr_dir = os.path.abspath(os.path.join(storage, 'anr'))
screenshot_dir = os.path.abspath(os.path.join(storage, 'screenshot'))

if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

def info():
    device_info = {'device': None, 'app': None}
    if len(device_service.devices) == 0:
        return jsonify(device_info)
    device = list(device_service.devices.values())[0]
    device_prop = device.to_dict()
    device_info['device'] = {'UDID': device_prop['device_id'], 'Model': device_prop['model'], 'Version': device_prop['releaseVersion']}

    conf = config.load()
    if hasattr(conf, 'package_name'):
        package_name = conf.package_name
    else:
        package_name = 'com.sankuai.meituan'

    app = device.package_info(package_name)
    device_info['app'] = {'PackageName': package_name, 'LaunchActivity': app.launch_activity,
                            'Version': app.version_name}
    return jsonify(device_info)

def device_list():
    return jsonify(device_service.devices_to_dict())

def device_detail(device_id):
    return jsonify(device_service.devices.get(device_id).device_info)

def last_package_name():
    conf = config.load()
    return jsonify({"packageName": conf.package_name})

def app_info(device_id, package_name):

    def send_device_event():
        device_service.publish_devices_package_info(device_service.devices, package_name)
    lyrebird.add_background_task('SendAndroidDeviceInfo', send_device_event)

    device = device_service.devices.get(device_id)
    app = device.package_info(package_name)
    return jsonify({'launchActivity': app.launch_activity, 'version': app.version_name, 'detail': app.raw})

def take_screen_shot(device_id):
    device = device_service.devices.get(device_id)
    img_info = device.take_screen_shot()
    timestamp = img_info.get('timestamp')
    if img_info.get('screen_shot_file'):
        return jsonify({'imgUrl': f'/plugins/android/api/src/screenshot/{device_id}?time={timestamp}'})

def get_all_package(device_id):
    device = device_service.devices.get(device_id)
    packages = device.get_all_packages()
    res = []
    for package in packages:
        res.append({
            "value": package,
            "label": package
        })
    return jsonify(res)

def get_screenshot_image(device_id):
    if request.args.get('time'):
        timestamp = int(request.args.get('time'))
        return send_from_directory(screenshot_dir, f'android_screenshot_{device_id}_{timestamp}.png')
    else:
        return None

def start_app(device_id, package_name):
    """

    :param device_id:
    :return:
    """
    device = device_service.devices.get(device_id)
    if not device:
        device = list(device_service.devices.values())[0]
    app = device.package_info(package_name)
    device.stop_app(package_name)
    port = lyrebird.context.application.conf.get('mock.port')
    device.start_app(app.launch_activity, get_ip(), port)
    return context.make_ok_response()

def stop_app(device_id, package_name):
    """

    :param device_id:
    :return:
    """
    device = device_service.devices.get(device_id)
    if not device:
        device = list(device_service.devices.values())[0]
    device.stop_app(package_name)
    return context.make_ok_response()

def get_prop_file_path(device, device_id):
    device_prop_file_path = os.path.abspath(os.path.join(tmp_dir, f'android_info_{device_id}.txt'))
    device_prop = device.device_info
    device_prop_file = codecs.open(device_prop_file_path, 'w', 'utf-8')
    for prop_line in device_prop:
        device_prop_file.write(prop_line+'\n')
    device_prop_file.close()

    return device_prop_file_path

def get_device_cpuinfo_file_path(device, device_id):
    device_cpuinfo_file_path = os.path.abspath(os.path.join(tmp_dir, f'android_cpuinfo_{device_id}.txt'))
    device_cpuinfo = device.device_cpuinfo()
    device_cpuinfo_file = codecs.open(device_cpuinfo_file_path, 'w', 'utf-8')
    for cpuinfo_line in device_cpuinfo:
        device_cpuinfo_file.write(cpuinfo_line+'\n')
    device_cpuinfo_file.close()

    return device_cpuinfo_file_path

def get_app_meminfo_file_path(device):
    conf = config.load()
    app_meminfo_file_path = ''
    if conf.package_name:
        app_meminfo_file_path = os.path.abspath(os.path.join(tmp_dir, f'android_meminfo_{conf.package_name}.txt'))
        app_meminfo = device.package_meminfo(conf.package_name)
        app_meminfo_file = codecs.open(app_meminfo_file_path, 'w', 'utf-8')
        for meminfo_line in app_meminfo:
            app_meminfo_file.write(meminfo_line+'\n')
        app_meminfo_file.close()

    return app_meminfo_file_path

def get_app_info_file_path(device):
    conf = config.load()
    app_info_file_path = ''
    if conf.package_name:
        app_info_file_path = os.path.abspath(os.path.join(tmp_dir, f'android_info_{conf.package_name}.txt'))
        app_info = device.package_info(conf.package_name)
        app_info_file = codecs.open(app_info_file_path, 'w', 'utf-8')
        app_info_file.writelines(app_info.raw)
        app_info_file.close()

    return app_info_file_path

def get_screenshots(message):
    if message.get('cmd') != 'screenshot':
        return
    screenshot_list = []
    device_list = message.get('device_id')
    for device_id in device_list:
        device_detail = device_service.devices.get(device_id)
        if not device_detail:
            continue
        screenshot_detail = device_detail.take_screen_shot()
        screenshot_list.append(
            {
                'id': device_id,
                'screenshot': {
                    'name': os.path.basename(screenshot_detail.get('screen_shot_file')),
                    'path': screenshot_detail.get('screen_shot_file')
                }
            }
        )
    lyrebird.publish('android.screenshot', screenshot_list)

def execute_command():
    if request.method == 'POST':
        _command = request.json.get('command')
        if not _command:
            return context.make_fail_response('Empty command!')

        _device_id = request.json.get('device_id', '')
        device = device_service.devices.get(_device_id)
        if not device:
            return context.make_fail_response('Device not found!')

        res = device.adb_command_executor(_command)
        output = res.stdout.decode()
        err_str = res.stderr.decode()
        if err_str:
            return context.make_fail_response(err_str)
        else:
            return context.make_ok_response(data=output)

def get_ip():
    """
    获取当前设备在网络中的ip地址

    :return: IP地址字符串
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('bing.com', 80))
    return s.getsockname()[0]
