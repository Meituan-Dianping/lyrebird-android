import os
import json
import codecs
import lyrebird

"""
Android plugin config manager
"""

storage = lyrebird.get_plugin_storage()
CONFIG_FILE = os.path.abspath(os.path.join(storage, 'conf.json'))


class Config:

    def __init__(self):
        self.package_name = None

    def save(self):
        json_str = json.dumps(self.__dict__, indent=4, ensure_ascii=False)
        conf_file = codecs.open(CONFIG_FILE, 'w', 'utf-8')
        conf_file.write(json_str)
        conf_file.close()

def load():
    conf = Config()
    plugin_conf = lyrebird.context.application.conf.get('plugin.android', {})
    conf.package_name = plugin_conf.get('package', '')
    return conf

def get_config(config_name):
    plugin_conf = lyrebird.application.config.get('plugin.android', {})
    config = plugin_conf.get(config_name, '')
    return config
