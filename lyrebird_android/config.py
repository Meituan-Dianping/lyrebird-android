import lyrebird
import os
import json
import codecs

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
    if os.path.exists(CONFIG_FILE):
        conf_data = json.loads(codecs.open(CONFIG_FILE, 'r', 'utf-8').read())
        conf = Config()
        conf.__dict__ = conf_data
        return conf
    else:
        return Config()
