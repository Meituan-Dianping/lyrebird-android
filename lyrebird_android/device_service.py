import shutil
import lyrebird
from pathlib import Path
from lyrebird import context, get_logger
from . import android_helper
from . import config
import traceback


logger = get_logger()


class DeviceService:
    """
    Background service : Android devices monitor

    Poll devices status per 1 sec with adb command
    """

    READY = 0
    RUNNING = 1
    STOP = 2

    def __init__(self):
        self.status = self.READY
        self.handle_interval = 1
        self.devices = {}
        self.reset_resources_dir()
        logger.debug('DeviceService OnCreate')

    def check_env(self):
        try:
            android_helper.check_android_home()
            self.status = self.RUNNING
            logger.debug('Android device listener start')
        except Exception as e:
            self.status = self.STOP
            msg = e.args[0]
            logger.error(msg)
            return msg

    def devices_to_dict(self):
        json_obj = {}
        for device_id in self.devices:
            json_obj[device_id] = self.devices[device_id].to_dict()
        return json_obj

    def run(self):
        self.check_env()
        while self.status == self.RUNNING:
            try:
                self.handle()
                context.application.socket_io.sleep(self.handle_interval)
            except Exception:
                logger.error("DeviceService Crash:\n"+traceback.format_exc())
        self.status = self.STOP
        logger.debug('Android device listener stop')

    def handle(self):
        devices = android_helper.devices()
        if len(devices) == len(self.devices):
            if len([k for k in devices if k not in self.devices]) == 0:
                return

        for _device_id in [k for k in devices if k not in self.devices]:
            self.devices = devices
            self.devices[_device_id].start_log()
        for _device_id in [k for k in self.devices if k not in devices]:
            self.devices[_device_id].stop_log()
            self.devices = devices

        lyrebird.emit('android-device')
        self.publish_devices_package_info(self.devices, config.load().package_name)

    @staticmethod
    def publish_devices_package_info(online_devices, package_name):
        devices_info_list = []
        for device_id, device_info in online_devices.items():
            device_detail = online_devices[device_id]
            if device_detail.device_info is None:
                continue
            item = {
                'id': device_id,
                'info': {
                    'product': device_detail.product,
                    'model': device_detail.model,
                    'os': device_detail.get_release_version(),
                    'ip': device_detail.get_device_ip(),
                    'resolution': device_detail.get_device_resolution()
                }
            }
            app = device_info.package_info(package_name)
            if app.version_name:
                item['app'] = {
                    'packageName': package_name,
                    'startActivity': app.launch_activity,
                    'version': app.version_name
                }
            devices_info_list.append(item)

        lyrebird.publish('android.device', devices_info_list, state=True)

    @staticmethod
    def reset_resources_dir():
        reset_dir = [
            Path(android_helper.screenshot_dir),
            Path(android_helper.apk_dir)
        ]

        for path in reset_dir:
            if path.exists():
                shutil.rmtree(path)

        logger.debug('Android device log file reset')
