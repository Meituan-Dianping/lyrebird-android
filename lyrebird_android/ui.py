import os
import time
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


class MyUI(lyrebird.PluginView):

    def index(self):
        """
        插件首页        
        """
        return codecs.open(self.get_package_file_path('templates/index.html'), 'r', 'utf-8').read()

    def info(self):
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

    def device_list(self):
        return jsonify(device_service.devices_to_dict())

    def device_detail(self, device_id):
        return jsonify(device_service.devices.get(device_id).device_info)

    def last_package_name(self):
        conf = config.load()
        return jsonify({"packageName": conf.package_name})

    def app_info(self, device_id, package_name):

        conf = config.load()
        conf.package_name = package_name
        conf.save()

        device = device_service.devices.get(device_id)
        app = device.package_info(package_name)
        return jsonify({'launchActivity': app.launch_activity, 'version': app.version_name, 'detail': app.raw})

    def logcat_start(self, device_id):
        print('Logcat start', device_id)
        device_service.start_log_recorder(device_id)

    def take_screen_shot(self, device_id):
        device = device_service.devices.get(device_id)
        img_info = device.take_screen_shot()
        timestrap = img_info.get('timestrap')
        if img_info.get('screen_shot_file'):
            return jsonify({'imgUrl': f'/ui/plugin/android/api/src/screenshot/{device_id}?time={timestrap}'})

    def get_all_package(self, device_id):
        device = device_service.devices.get(device_id)
        packages = device.get_all_packages()
        res = []
        for package in packages:
            res.append({
                "value": package,
                "label": package
            })
        return jsonify(res)

    def get_screenshot_image(self, device_id):
        if request.args.get('time'):
            timestrap = int(request.args.get('time'))
            return send_from_directory(screenshot_dir, f'android_screenshot_{device_id}_{timestrap}.png')
        else: 
            return None

    def make_dump_data(self, path):
        device_data = {}
        device_data['name'] = os.path.basename(path)
        device_data['path'] = path
        return device_data

    def dump_data(self):
        """
        获取所有设备相关信息，包括设备日志，崩溃日志，ANR日志，快照图片，APP_INFO等
        :return: name, path
        e.g
        [
            {
                "name": "android_log_{imei}.log",
                "path": "/Users/someone/.lyrebird/plugins/lyrebird_android/tmp/android_log_{imei}.log"
            },
            {
                "name": "android_screenshot_{imei}.png",
                "path": "/Users/someone/.lyrebird/plugins/lyrebird_android/tmp/android_screenshot_{imei}.png"
            }
        ]
        """
        res = []
        devices = device_service.devices

        for udid in devices:
            device = devices[udid]
            if device.log_filtered_file and os.path.getsize(device.log_filtered_file):
                res.append(self.make_dump_data(device.log_filtered_file))
            if device.crash_filtered_file and os.path.getsize(device.crash_filtered_file):
                res.append(self.make_dump_data(device.crash_filtered_file))
            if device.anr_filtered_file and os.path.getsize(device.anr_filtered_file):
                res.append(self.make_dump_data(device.anr_filtered_file))
            if len(self.get_app_info_file_path(device)):
                res.append(self.make_dump_data(self.get_app_info_file_path(device)))
            if len(self.get_app_meminfo_file_path(device)):
                res.append(self.make_dump_data(self.get_app_meminfo_file_path(device)))
            if device.anr_file:
                res.append(self.make_dump_data(device.anr_file))
            if len(device.crash_file_list):
                for crash_path in device.crash_file_list:
                    res.append(self.make_dump_data(crash_path))
            res.append(self.make_dump_data(self.get_device_cpuinfo_file_path(device, udid)))
            res.append(self.make_dump_data(self.get_prop_file_path(device, udid)))
            res.append(self.make_dump_data(device.take_screen_shot()))

        return jsonify(res)

    def start_app(self, device_id, package_name):
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

    def stop_app(self, device_id, package_name):
        """

        :param device_id:
        :return:
        """
        device = device_service.devices.get(device_id)
        if not device:
            device = list(device_service.devices.values())[0]
        device.stop_app(package_name)
        return context.make_ok_response()

    def dump(self, device_id):
        """
        保存截图 设备信息 日志 app信息
        :param device_id:
        :return: 所有信息文件绝对路径 json list
        """
        device = device_service.devices.get(device_id)
        if device:
            device.take_screen_shot()
        dump_list = [device.screen_shot_file, self.get_prop_file_path(device, device_id)]
        if device.log_filtered_file and os.path.getsize(device.log_filtered_file):
            dump_list.append(device.log_filtered_file)
        if device.crash_filtered_file and os.path.getsize(device.crash_filtered_file):
            dump_list.append(device.crash_filtered_file)
        if device.anr_filtered_file and os.path.getsize(device.anr_filtered_file):
            dump_list.append(device.anr_filtered_file)
        if len(self.get_app_info_file_path(device)):
            dump_list.append(self.get_app_info_file_path(device))
        if len(self.get_app_meminfo_file_path(device)):
            dump_list.append(self.get_app_meminfo_file_path(device))
        if len(self.get_device_cpuinfo_file_path(device, device_id)):
            dump_list.append(self.get_device_cpuinfo_file_path(device, device_id))
        return jsonify(dump_list)

    def get_prop_file_path(self, device, device_id):
        device_prop_file_path = os.path.abspath(os.path.join(tmp_dir, f'android_info_{device_id}.txt'))
        device_prop = device.device_info
        device_prop_file = codecs.open(device_prop_file_path, 'w', 'utf-8')
        for prop_line in device_prop:
            device_prop_file.write(prop_line+'\n')
        device_prop_file.close()

        return device_prop_file_path

    def get_device_cpuinfo_file_path(self, device, device_id):
        device_cpuinfo_file_path = os.path.abspath(os.path.join(tmp_dir, f'android_cpuinfo_{device_id}.txt'))
        device_cpuinfo = device.device_cpuinfo()
        device_cpuinfo_file = codecs.open(device_cpuinfo_file_path, 'w', 'utf-8')
        for cpuinfo_line in device_cpuinfo:
            device_cpuinfo_file.write(cpuinfo_line+'\n')
        device_cpuinfo_file.close()

        return device_cpuinfo_file_path
        

    def get_app_meminfo_file_path(self, device):
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

    def get_app_info_file_path(self, device):
        conf = config.load()
        app_info_file_path = ''
        if conf.package_name:
            app_info_file_path = os.path.abspath(os.path.join(tmp_dir, f'android_info_{conf.package_name}.txt'))
            app_info = device.package_info(conf.package_name)
            app_info_file = codecs.open(app_info_file_path, 'w', 'utf-8')
            app_info_file.writelines(app_info.raw)
            app_info_file.close()

        return app_info_file_path

    def get_screenshots(self, message):
        if message.get('cmd') != 'screenshot':
            return
        screenshot_list = []
        device_list = message.get('id')
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

    def on_create(self):
        # for overbridge
        self.add_url_rule('/api/info', view_func=self.info)
        # Dump所有信息
        self.add_url_rule('/api/dump/<string:device_id>', view_func=self.dump)
        # 获取设备列表
        self.add_url_rule('/api/devices', view_func=self.device_list)
        # 设备详情
        self.add_url_rule('/api/device/<string:device_id>', view_func=self.device_detail)
        self.add_url_rule('/api/package_name', view_func=self.last_package_name)
        # 获取app详情
        self.add_url_rule('/api/app/<string:device_id>/<string:package_name>', view_func=self.app_info)
        # 进行截图
        self.add_url_rule('/api/screenshot/<string:device_id>', view_func=self.take_screen_shot)
        # 获取截图
        self.add_url_rule('/api/src/screenshot/<string:device_id>', view_func=self.get_screenshot_image)
        # 获取设备所有package
        self.add_url_rule('/api/packages/<string:device_id>', view_func=self.get_all_package)
        # 启动应用
        self.add_url_rule('/api/start_app/<string:device_id>/<string:package_name>', view_func=self.start_app)
        self.add_url_rule('/api/stop_app/<string:device_id>/<string:package_name>', view_func=self.stop_app)
        # 获取资源信息
        self.add_url_rule('/api/dump', view_func=self.dump_data)
        # 启动日志事件
        self.on_event('log-start', self.logcat_start, '/android-plugin')
        # 启动设备监听服务
        lyrebird.start_background_task(device_service.run)
        # 订阅频道 android.cmd
        lyrebird.subscribe('android.cmd', self.get_screenshots)

    def get_icon(self):
        return 'fa fa-fw fa-android'

def get_ip():
    """
    获取当前设备在网络中的ip地址

    :return: IP地址字符串
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 80))
    return s.getsockname()[0]
