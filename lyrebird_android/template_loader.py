import imp
import json
import codecs
import traceback
from pathlib import Path
from lyrebird import application
from lyrebird import get_logger
from lyrebird import get_plugin_storage


class AndroidTemplateIllegal(Exception):
    pass


class AndroidTemplateNotFound(Exception):
    pass


logger = get_logger()

def install_options():
    workspace_str = get_config('install.workspace')

    if not workspace_str:
        workspace = _init_install_workspace()
    elif not Path(workspace_str).exists():
        workspace = Path(workspace_str)
        workspace.mkdir(parents=True, exist_ok=True)
    else:
        workspace = Path(workspace_str)

    options = []
    workspace_files = _load_dir_file(workspace, '.py')
    for path in workspace_files:
        template = get_template(path)
        _check_install_template(template)
        options.append({'name': template.name, 'path': str(path)})
    return options

def start_options():
    start_files = get_remote_start_files()
    custom_start_files = get_custom_start_files()
    start_files.extend(custom_start_files)

    options = []
    for path in start_files:
        content = get_content(path)
        _check_launch_content(content)
        options.append({'name': content['name'], 'path': str(path), 'id': path.stem})
    return options

def get_remote_start_files():
    workspace_str = get_config('launch.workspace')

    if not workspace_str:
        workspace = _init_launch_workspace()
    elif not Path(workspace_str).exists():
        workspace = Path(workspace_str)
        workspace.mkdir(parents=True, exist_ok=True)
    else:
        workspace = Path(workspace_str)

    workspace_files = _load_dir_file(workspace, '.json')
    return workspace_files

def get_custom_start_files():
    storage = get_plugin_storage()
    workspace = Path(storage)/'launch_config'

    if not workspace.exists():
        workspace.mkdir(parents=True, exist_ok=True)

    workspace_files = _load_dir_file(workspace, '.json')
    return workspace_files

def get_config(config_name):
    plugin_conf = application.config.get('plugin.android', {})
    config = plugin_conf.get(config_name, '')
    return config

def _init_install_workspace():
    ROOT = application._cm.ROOT
    workspace = ROOT/'downloads'/'lyrebird_android'/'install'
    workspace.mkdir(parents=True, exist_ok=True)
    logger.warning(f'Android install workspace not exists! Create on {str(workspace)}')
    return workspace

def _init_launch_workspace():
    ROOT = application._cm.ROOT
    workspace = ROOT/'downloads'/'launch_app_config'
    workspace.mkdir(parents=True, exist_ok=True)
    logger.warning(f'Android launch workspace not exists! Create on {str(workspace)}')
    return workspace

def _load_dir_file(path, suffix):
    path_iterdir = [p for p in path.iterdir() if p.suffix == suffix]
    return path_iterdir

def _check_install_template(template):
    if not hasattr(template, 'name'):
        raise AndroidTemplateIllegal('Android install template should have `name attr` is requird')
    if not hasattr(template, 'get_apps'):
        raise AndroidTemplateIllegal('Android install template should have get_apps attr')
    if not callable(template.get_apps):
        raise AndroidTemplateIllegal('Android install template should have get_apps function')

def _check_launch_content(content):
    if 'name' not in content:
        raise AndroidTemplateIllegal('Android launch app config should have name')

def get_template(path):
    if not Path(path).exists():
        raise AndroidTemplateNotFound(f'Android template {str(path)} not found!')
    try:
        template = imp.load_source(Path(path).stem, str(path))
        return template
    except Exception:
        raise AndroidTemplateIllegal(f'Load template failed:\nBad content: {path}\n{traceback.format_exc()}')

def get_content(path):
    if not Path(path).exists():
        raise AndroidTemplateNotFound(f'Android content {str(path)} not found!')
    try:
        with codecs.open(str(path), 'r', 'utf-8') as f:
            content = json.load(f)
        return content
    except Exception:
        raise AndroidTemplateIllegal(f'Load content failed:\nBad content: {path}\n{traceback.format_exc()}')

def save_content(content, path):
    try:
        with codecs.open(str(path), 'w', 'utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
    except Exception:
        raise AndroidTemplateIllegal(f'Save content failed:\nBad content: {path}\n{traceback.format_exc()}')
