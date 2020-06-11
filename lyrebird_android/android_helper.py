import os
import sys
import time
import codecs
import lyrebird
import threading
import subprocess
from pathlib import Path
from . import config
from lyrebird.log import get_logger

"""
Android Debug Bridge command helper

Basic ADB command for device_service and API
"""

logger = get_logger()

here = os.path.dirname(__file__)
adb = None
static = os.path.abspath(os.path.join(here, 'static'))
storage = lyrebird.get_plugin_storage()

tmp_dir = os.path.abspath(os.path.join(storage, 'tmp'))
anr_dir = os.path.abspath(os.path.join(storage, 'anr'))
crash_dir = os.path.abspath(os.path.join(storage, 'crash'))
screenshot_dir = os.path.abspath(os.path.join(storage, 'screenshot'))
apk_dir = Path(storage)/'apk'

if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

if not os.path.exists(anr_dir):
    os.makedirs(anr_dir)

if not os.path.exists(crash_dir):
    os.makedirs(crash_dir)

class ADBError(Exception):
    pass


class AndroidHomeError(Exception):
    pass


def check_android_home():
    global adb
    android_home = os.environ.get('ANDROID_HOME')
    if not android_home:
        raise AndroidHomeError('Environment variable ANDROID_HOME not found!')
    if not os.path.exists(android_home):
        raise AndroidHomeError('ANDROID_HOME %s not exists' % android_home)
    if not os.path.isdir(android_home):
        raise AndroidHomeError('ANDROID_HOME %s is not a dir' % android_home)
    if sys.platform == 'win32':
        adb = os.path.abspath(os.path.join(android_home, 'platform-tools/adb.exe'))
    elif sys.platform == 'darwin' or sys.platform == 'linux':
        adb = os.path.abspath(os.path.join(android_home, 'platform-tools/adb'))
    else:
        raise ADBError('Unsupported platform')


class App:

    def __init__(self, package):
        self.package = package
        self.launch_activity = None
        self.version_name = None
        self.version_code = None
        self.raw = None

    @classmethod
    def from_raw(cls, package, raw_data):
        app = cls(package)
        app.raw = raw_data
        lines = raw_data.split('\n')

        actionMAIN_line_num = None

        for index, line in enumerate(lines):
            if 'versionCode' in line:
                app.version_code = line.strip().split(' ')[0]
            if 'versionName' in line:
                app.version_name = line.strip().split('=')[1]
            if 'android.intent.action.MAIN:' in line:
                actionMAIN_line_num = index + 1
            if app.version_name and app.version_code and actionMAIN_line_num:
                package_name_line = lines[actionMAIN_line_num]
                app.launch_activity = package_name_line.strip().split()[1]
                break

        return app


class Device:

    def __init__(self, device_id):
        self.device_id = device_id
        self.state = None
        self.product = None
        self.model = None
        self._log_process = None
        self._log_cache = []
        self._log_crash_cache = []
        self._crashed_pid = None
        self._crashed_package = None
        self._log_file = None
        self._device_info = None
        self._app_info = None
        self.start_catch_log = False

    @property
    def log_file(self):
        return self._log_file

    @classmethod
    def from_adb_line(cls, line):
        device_info = [info for info in line.split(' ') if info]
        if len(device_info) < 2:
            raise ADBError(f'Read device info line error. {line}')
        _device = cls(device_info[0])
        _device.state = device_info[1]
        for info in device_info[2:]:
            info_kv = info.split(':')
            if len(info_kv) >= 2:
                setattr(_device, info_kv[0], info_kv[1])
            else:
                logger.error(f'Read device info error: unknown format {info_kv}')
        return _device

    def install(self, apk_file):
        subprocess.run(f'{adb} -s {self.device_id} install -r {apk_file}', shell=True)

    def push(self, src, dst):
        subprocess.run(f'{adb} -s {self.device_id} push {src} {dst}')

    def pull(self, src, dst):
        subprocess.run(f'{adb} -s {self.device_id} pull {src} {dst}')

    def start_log(self):
        self.stop_log()

        self._log_file = os.path.abspath(os.path.join(tmp_dir, f'android_log_{self.device_id}.log'))

        p = subprocess.Popen(f'{adb} -s {self.device_id} logcat', shell=True, stdout=subprocess.PIPE)
        
        def log_handler(logcat_process):
            log_file = codecs.open(self._log_file, 'w', 'utf-8')
            self._log_process = logcat_process

            while True:
                line = logcat_process.stdout.readline()
                line = line.decode(encoding='UTF-8', errors='ignore')

                if not line:
                    lyrebird.emit('android-log', self._log_cache)
                    log_file.close()
                    return

                self._log_cache.append(line)
                self.crash_checker(line)
                self.anr_checker(line)

                if len(self._log_cache) >= 10:
                    lyrebird.emit('android-log', self._log_cache)
                    log_file.writelines(self._log_cache)
                    log_file.flush()
                    self._log_cache = []
        threading.Thread(target=log_handler, args=(p,)).start()

    def get_package_from_pid(self, pid):
        p = subprocess.run(f'{adb} -s {self.device_id} shell ps | grep {pid}', shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not p.stdout.decode():
            return ''
        package = [line for line in p.stdout.decode().strip().split()][-1]
        package = package.replace(':', '')
        package = package.replace('/', '')
        return package

    def crash_checker(self, line):

        if line.find('FATAL EXCEPTION') > 0:
            self.start_catch_log = True
            _crashed_pid = [_ for _ in line.strip().split()][2]
            self._crashed_package = self.get_package_from_pid(_crashed_pid)
            self._log_crash_cache.append(line)

        elif line.find('AndroidRuntime') > 0 and self.start_catch_log:
            self._log_crash_cache.append(line)

        elif self.start_catch_log:
            _crash_file = os.path.abspath(os.path.join(
                crash_dir,
                f'android_crash_{self.device_id}_{self._crashed_package}.log'
            ))

            with codecs.open(_crash_file, 'w', 'utf-8') as f:
                f.write(''.join(self._log_crash_cache))

            target_package_name = config.load().package_name
            if self._crashed_package == target_package_name:
                crash_info = {
                    'device_id':self.device_id,
                    'log': self._log_crash_cache,
                    'log_file_path': _crash_file
                }
                lyrebird.publish('android.crash', crash_info)

                title = f'Android device {self.device_id} crashed!\n'
                desc = title + 'Crash log:\n\n' + ''.join(self._log_crash_cache)
                lyrebird.event.issue(title, desc)

            self.start_catch_log = False
            self._log_crash_cache = []
        
        else:
            return

    def anr_checker(self, line):
        if ('ANR' not in line) or ('ActivityManager' not in line):
            return

        anr_package = line.strip().split()[-2]
        anr_file_name = os.path.join(anr_dir, f'android_anr_{self.device_id}_{anr_package}.log')
        p = subprocess.run(f'{adb} -s {self.device_id} pull "/data/anr/traces.txt" {anr_file_name}',
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            logger.error('Catch ANR log error!\n' + p.stderr.decode())
            return

        # check whether pid of the anr_package exists or not
        with codecs.open(anr_file_name, 'r', 'utf-8') as f:
            anr_pid_line = f.readline()
            # expected anr_pid_line: ----- pid 21335 at 2019-06-24 16:21:15 -----
            while 'pid' not in anr_pid_line:
                anr_pid_line = f.readline()
        _anr_pid = anr_pid_line.strip().split()[2]
        anr_package = self.get_package_from_pid(_anr_pid)

        target_package_name = config.load().package_name
        if anr_package == target_package_name:
            with codecs.open(anr_file_name, 'r', 'utf-8') as f:
                log_anr_cache = f.readlines()
            anr_info = {
                'device_id':self.device_id,
                'log': log_anr_cache,
                'log_file_path': anr_file_name
            }
            lyrebird.publish('android.crash', anr_info)

            title = f'Application {anr_package} not responding on Android device {self.device_id}!\n'
            desc = title + 'ANR log:\n\n' + ''.join(log_anr_cache)

            lyrebird.event.issue(title, desc)

    @property
    def device_info(self):
        if not self._device_info:
            self._device_info = self.get_properties()
        return self._device_info

    def get_properties(self):
        p = subprocess.run(f'{adb} -s {self.device_id} shell getprop', shell=True, stdout=subprocess.PIPE)
        if p.returncode == 0:
            return p.stdout.decode().split('\n')

    def get_all_packages(self):
        p = subprocess.run(f'{adb} -s {self.device_id} shell pm list packages', shell=True, stdout=subprocess.PIPE)
        res = []
        if p.returncode == 0:
            output = p.stdout.decode()
            res = [item.split(':')[1].strip() for item in output.strip().split('\n') if item]
        return res

    def package_info(self, package_name):
        p = subprocess.run(f'{adb} -s {self.device_id} shell dumpsys package {package_name}', shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise ADBError(p.stderr.decode())
        app = App.from_raw(package_name, p.stdout.decode())
        if config.get_config('package.launch.activity'):
            app.launch_activity = config.get_config('package.launch.activity')
        return app

    def package_meminfo(self, package_name):
        p = subprocess.run(f'{adb} -s {self.device_id} shell dumpsys meminfo {package_name}', shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode == 0:
            return p.stdout.decode().split('\n')

    def device_cpuinfo(self):
        p = subprocess.run(f'{adb} -s {self.device_id} shell dumpsys cpuinfo', shell=True, stdout=subprocess.PIPE)
        if p.returncode == 0:
            return p.stdout.decode().split('\n')

    def stop_log(self):
        if self._log_process:
            self._log_process.kill()
            self._log_process = None

    def take_screen_shot(self):
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        timestamp = int(time.time())
        screen_shot_file = os.path.abspath(os.path.join(screenshot_dir, f'android_screenshot_{self.device_id}_{timestamp}.png'))
        p = subprocess.run(f'{adb} -s {self.device_id} exec-out screencap -p > {screen_shot_file}', shell=True)
        if p.returncode == 0:
            return dict({
                'screen_shot_file': screen_shot_file,
                'device_id': self.device_id,
                'timestamp': timestamp
            })
        return {}

    def get_device_ip(self):
        p = subprocess.run(f'{adb} -s {self.device_id} shell ip -o -4 address', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise ADBError(p.stderr.decode())
        output = [line.strip() for line in p.stdout.decode().strip().split('\n')]
        for net_line in output:
            if 'wlan0' in net_line:
                ipv4_list = net_line.split()
                break
        else:
            return ''
        for index, char in enumerate(ipv4_list):
            # ipv4_address, which we need, is behind of 'inet'
            if char == 'inet':
                # example of ipv4_address: 192.168.110.111/23
                return ipv4_list[index+1].split('/')[0]
        return ''

    def get_device_resolution(self):
        p = subprocess.run(f'{adb} -s {self.device_id} shell dumpsys window displays', shell=True, \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise ADBError(p.stderr.decode())
        output = [line.strip() for line in p.stdout.decode().strip().split('\n')]
        for index, char in enumerate(output):
            if char and char.startswith('Display'):
                # display_str, which we need, is in the next line of 'Display'
                display_str = output[index+1]
                break
        else:
            return ''
        # example of display: 'init=1080x1920 420dpi cur=1080x1920 app=1080x1794 rng=1080x1017-1794x1731',
        for resolution_str in display_str.split():
            if resolution_str.startswith('init'):
                return resolution_str[len('init='):]
        return ''

    def get_release_version(self):
        p = subprocess.run(f'{adb} -s {self.device_id} shell getprop ro.build.version.release', shell=True, \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise ADBError(p.stderr.decode())
        return p.stdout.decode().strip()

    def to_dict(self):
        device_info = {k: self.__dict__[k] for k in self.__dict__ if not k.startswith('_')}
        # get additional device info
        prop_lines = self.device_info
        if not prop_lines:
            return device_info

        for line in prop_lines:
            # 基带版本
            if 'ro.build.expect.baseband' in line:
                baseband = line[line.rfind('[')+1:line.rfind(']')].strip()
                device_info['baseBand'] = baseband
            # 版本号
            if 'ro.build.id' in line:
                build_id = line[line.rfind('[') + 1:line.rfind(']')].strip()
                device_info['buildId'] = build_id
            # Android 版本
            if 'ro.build.version.release' in line:
                build_version = line[line.rfind('[') + 1:line.rfind(']')].strip()
                device_info['releaseVersion'] = build_version
        return device_info

    def adb_command_executor(self, command):
        command = command.strip()

        isAdbCommand = command.startswith('adb ')
        if isAdbCommand:
            command_adb, command_options = command.split(' ', 1)
            command = f'{command_adb} -s {self.device_id} {command_options}'

        p = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p


def devices():
    res = subprocess.run(f'{adb} devices -l', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = res.stdout.decode()
    err_str = res.stderr.decode()
    online_devices = {}

    # ADB command error
    if res.returncode != 0:
        logger.error('Get devices list error' + err_str)
        return online_devices

    lines = [line for line in output.split('\n') if line]
    if len(lines) > 1:
        for line in lines[1:]:
            device = Device.from_adb_line(line)
            online_devices[device.device_id] = device

    return online_devices
