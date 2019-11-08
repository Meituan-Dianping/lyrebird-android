import imp
import traceback
from pathlib import Path

from lyrebird import application
from lyrebird import get_logger


logger = get_logger()

def get_workspace():
    plugin_conf = application.config.get('plugin.android', {})
    android_workspace = plugin_conf.get('workspace', '')

    if android_workspace and Path(android_workspace).exists():
        return Path(android_workspace)

    ROOT = application._cm.ROOT
    metadata_dir = ROOT/'downloads'/'lyrebird_android'
    metadata_dir.mkdir(parents=True, exist_ok=True)
    logger.warning(f'Android workspace not exists! Create on {metadata_dir._str}')

    return metadata_dir

def install_options():
    workspace = get_workspace()
    install_workspace = workspace/'install'
    if not Path(install_workspace).exists():
        install_workspace.mkdir(parents=True, exist_ok=True)
    install_options = []
    for template_file in install_workspace.iterdir():
        if not template_file.name.endswith('.py'):
            continue
        try:
            template = imp.load_source(template_file.stem, str(template_file))
            install_options.append({'name': template.name, 'path': str(template_file), 'key': template.key})
            del template
        except Exception:
            logger.error(f'Load bug template failed:\nBad template: {template_file}\n{traceback.format_exc()}')
    return install_options

def get_template(file_path):
    if file_path:
        template = imp.load_source(Path(file_path).stem, str(file_path))
        return template
