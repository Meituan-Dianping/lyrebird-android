from lyrebird.plugins import manifest
from . import apis

manifest(
    id='android',
    name='Android',
    api=[
        # check env
        ('/api/check_env', apis.check_env, ['GET']),
        # 获取设备列表
        ('/api/devices', apis.device_list, ['GET']),
        # 应用详情
        ('/api/package_name', apis.last_package_name, ['GET']),
        # 获取app详情
        ('/api/app/<string:device_id>/<string:package_name>', apis.app_info, ['GET']),
        # 进行截图
        ('/api/screenshot/<string:device_id>', apis.take_screen_shot, ['GET']),
        # 获取截图
        ('/api/src/screenshot/<string:device_id>', apis.get_screenshot_image, ['GET']),
        # 获取设备所有package
        ('/api/packages/<string:device_id>', apis.get_all_package, ['GET']),
        # execute command
        ('/api/command', apis.execute_command, ['POST']),
        # actions of application
        ('/api/device/<string:device_id>/app/<string:package_name>/<string:action>', apis.application_controller, ['PUT']),
        # actions of device
        ('/api/device/<string:device_id>/<string:action>', apis.device_controller, ['PUT']),
        # actions of templates
        ('/api/template/<string:action>', apis.template_options_controller, ['GET']),
        # actions of template
        ('/api/template/<string:action>/<string:template_id>', apis.template_controller, ['GET', 'PUT', 'POST']),
        # download apk
        ('/api/src/apk', apis.download_application, ['PUT']),
        # search app
        ('/api/search/app', apis.search_app, ['POST'])
    ],
    background=[
        ('android_device_service', apis.device_service.run)
    ],
    event=[
        ('android.cmd', apis.get_screenshots)
    ]
)
