import os
import json
import uuid
import jinja2
import socket
import codecs
import requests
from pathlib import Path
from urllib.parse import urlparse
from flask import request, send_from_directory
from . import config
from . import template_loader
from .device_service import DeviceService
from lyrebird.mock.context import make_ok_response, make_fail_response
from lyrebird import application, get_plugin_storage, add_background_task, publish


device_service = DeviceService()
storage = get_plugin_storage()
tmp_dir = os.path.abspath(os.path.join(storage, 'tmp'))
anr_dir = os.path.abspath(os.path.join(storage, 'anr'))
screenshot_dir = os.path.abspath(os.path.join(storage, 'screenshot'))
launch_config_path = Path(storage)/'launch_config'
apk_dir = Path(storage)/'apk'

if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

def check_env():
    msg = device_service.check_env()
    if device_service.status == device_service.RUNNING:
        return make_ok_response()
    else:
        return make_fail_response(msg)

def device_list():
    device_list = device_service.devices_to_dict()
    return make_ok_response(device_list=device_list)

def last_package_name():
    conf = config.load()
    return make_ok_response(package_name=conf.package_name)

def app_info(device_id, package_name):

    def send_device_event():
        device_service.publish_devices_package_info(device_service.devices, package_name)
    add_background_task('SendAndroidDeviceInfo', send_device_event)

    device = device_service.devices.get(device_id)
    app = device.package_info(package_name)
    app_info = {
        'launchActivity': app.launch_activity,
        'version': app.version_name,
        'detail': app.raw
    }
    return make_ok_response(app_info=app_info)

def take_screen_shot(device_id):
    device = device_service.devices.get(device_id)
    img_info = device.take_screen_shot()
    timestamp = img_info.get('timestamp')
    if img_info.get('screen_shot_file'):
        return make_ok_response(imgUrl=f'/plugins/android/api/src/screenshot/{device_id}?time={timestamp}')

def get_all_package(device_id):
    device = device_service.devices.get(device_id)
    packages = device.get_all_packages()
    return make_ok_response(packages=packages)

def get_screenshot_image(device_id):
    if request.args.get('time'):
        timestamp = int(request.args.get('time'))
        return send_from_directory(screenshot_dir, f'android_screenshot_{device_id}_{timestamp}.png')
    else:
        return None

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
    publish('android.screenshot', screenshot_list)

def execute_command():
    if request.method == 'POST':
        _command = request.json.get('command')
        if not _command:
            return make_fail_response('Empty command!')

        _device_id = request.json.get('device_id', '')
        device = device_service.devices.get(_device_id)
        if not device:
            return make_fail_response('Device not found!')

        res = device.adb_command_executor(_command)
        output = res.stdout.decode()
        err_str = res.stderr.decode()

        publish_channel = 'android.command'
        publish_message = {
            'command': res.args,
            'returncode': res.returncode,
            'result': err_str if err_str else output
        }
        publish(publish_channel, publish_message)

        if err_str:
            return make_fail_response(err_str)
        else:
            return make_ok_response(data=output)

def template_options_controller(action):
    if request.method == 'GET':
        if action == 'install':
            install_options = template_loader.install_options()
            return make_ok_response(install_options=install_options)
        elif action == 'start':
            start_options = template_loader.start_options()
            return make_ok_response(start_options=start_options)
        else:
            return make_fail_response(f'Unknown template action: {action}')

def template_controller(action, template_id):
    if action == 'start':
        template = _find_template_by_id(template_loader.start_options(), template_id)
        if not template:
            return make_fail_response(f'Template {template_id} not found!')
        template_path = template.get('path')
        content = template_loader.get_content(template_path)

        if request.method == 'GET':
            actions = content['actions']
            return make_ok_response(launch_actions=actions)

        elif request.method == 'PUT':
            actions = request.json.get('actions')
            content['actions'] = actions
            template_loader.save_content(content, template_path)
            return make_ok_response()

        elif request.method == 'POST':
            actions = request.json.get('actions')
            new_template_name = request.json.get('name')

            content['actions'] = actions
            content['name'] = new_template_name
            config_file_name = str(uuid.uuid4()) + '.json'
            template_path = launch_config_path/config_file_name
            template_loader.save_content(content, template_path)

            start_options = template_loader.start_options()
            selected_option_index = None
            for i in start_options:
                if i['path'] == str(template_path):
                    selected_option_index = start_options.index(i)
                    break
            return make_ok_response(index=selected_option_index)

    else:
        return make_fail_response(f'Unknown template action: {action}')

def _find_template_by_id(options, template_id):
    for option in options:
        if option.get('id') == template_id:
            return option

def application_controller(device_id, package_name, action):
    controller_actions = {
        'uninstall': _uninstall_package,
        'clear': _clear_package,
        'stop': _stop_package,
        'start': _start_package
    }

    if request.method == 'PUT':
        device = device_service.devices.get(device_id)
        if not device:
            return make_fail_response(f'Device {device_id} not found!')
        package = device.package_info(package_name)
        if not package:
            return make_fail_response(f'Application {package_name} not found!')
        if not controller_actions.get(action):
            return make_fail_response(f'Unknown application action: {action}')

        action_func = controller_actions.get(action)
        res = action_func(device, package, request)

        publish_channel = 'android.' + action
        publish_message = {
            'command': res.args,
            'returncode': res.returncode,
            'result': res.stderr.decode() if res.stderr.decode() else res.stdout.decode()
        }
        publish(publish_channel, publish_message)

        if res.returncode != 0:
            return make_fail_response(res.stderr.decode())
        # When adb uninstall <package> fail, the returncode is 0, while the output string contains `Failure`
        elif 'Failure' in res.stdout.decode():
            return make_fail_response(res.stdout.decode())
        else:
            return make_ok_response()

def _uninstall_package(device, package, _):
    package_name = package.package
    _command = f'adb uninstall {package_name}'
    res = device.adb_command_executor(_command)
    return res

def _clear_package(device, package, _):
    package_name = package.package
    _command = f'adb shell pm clear {package_name}'
    res = device.adb_command_executor(_command)
    return res

def _stop_package(device, package, _):
    package_name = package.package
    _command = f'adb shell am force-stop {package_name}'
    res = device.adb_command_executor(_command)
    return res

def _start_package(device, package, request):
    actions = request.json.get('actions')
    parameters_str = ''
    if actions:
        formated_actions = _format_config(actions)
        parameters_str = _get_parameters_str(formated_actions)
    _command = f'adb shell "am start --activity-clear-top -n {package.launch_activity} {parameters_str}"'
    res = device.adb_command_executor(_command)
    return res

def _format_config(config):
    """
    support format key:
    ip
    port
    """
    config_str = json.dumps(config, ensure_ascii=False)
    template = jinja2.Template(config_str)
    formated_config_str = template.render(
        ip=get_ip(),
        port=application.config.get('mock.port')
    )
    formated_config_str = formated_config_str.encode('utf-8')
    formated_config = json.loads(formated_config_str)
    return formated_config

def _get_parameters_str(actions):
    def escape_symbol(value):
        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value)
            escaped_value = value.replace('"', r'\"')
        else:
            escaped_value = str(value)
        escaped_value = "'" + escaped_value + "'"
        return escaped_value

    launch_actions = []
    command = '--es'
    for action in actions:
        launch_actions.extend([
            command,
            action['key'],
            escape_symbol(action['value'])
        ])
    actions_parameter = ' '.join(launch_actions)
    return actions_parameter

def device_controller(device_id, action):
    controller_actions = {
        'install': _install_package
    }

    if request.method == 'PUT':
        device = device_service.devices.get(device_id)
        if not device:
            return make_fail_response(f'Device {device_id} not found!')
        if not controller_actions.get(action):
            return make_fail_response(f'Unknown device action: {action}')

        action_func = controller_actions.get(action)
        res = action_func(device, request)

        publish_channel = 'android.' + action
        publish_message = {
            'command': res.args,
            'returncode': res.returncode,
            'result': res.stderr.decode() if res.stderr.decode() else res.stdout.decode()
        }
        publish(publish_channel, publish_message)

        if res.returncode != 0:
            return make_fail_response(res.stderr.decode())
        else:
            return make_ok_response()

def _install_package(device, request):
    apk_path = request.json.get('apkPath')
    _command = f'adb install -r {apk_path}'
    res = device.adb_command_executor(_command)
    return res

def download_application():
    app_url = request.json.get('appUrl')
    app_url_obj = urlparse(app_url)
    app_name = app_url_obj.path.split('/')[-1]

    apk_dir.mkdir(parents=True, exist_ok=True)
    app_file = apk_dir/app_name

    if not app_file.name.endswith('.apk'):
        return make_fail_response(f'Unexpected type: {app_file.stem}, url: {app_url}')
    _download_big_file(app_file, app_url)
    return make_ok_response(path=str(app_file))

def _download_big_file(path, url):
    response = requests.get(url, stream=True)
    with codecs.open(path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)

def search_app():
    if request.method == 'POST':
        search_str = request.json.get('searchStr')
        template = request.json.get('template')
        template_path = template.get('path')

        template = template_loader.get_template(template_path)
        origin_app_list = template.get_apps()

        if not search_str:
            return make_ok_response(applist=origin_app_list)

        matched_apps = [app for app in origin_app_list if search_str in app['name']]
        return make_ok_response(applist=matched_apps)

def get_ip():
    """
    获取当前设备在网络中的ip地址

    :return: IP地址字符串
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('bing.com', 80))
    return s.getsockname()[0]
