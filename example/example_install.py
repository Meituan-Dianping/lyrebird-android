import requests

"""
Template name
"""
name = "NAME"

def get_apps():
    """
    :param:
    :return list:

    Android plugin callback function
    This function will be called when appliction list is required from frontend

    Given a list of dict as application list, each dict required following key:
        id      string      id
        name    string      App name
        time    string      App release time
        url     string      Downloads link

    """
    app_list = []
    origin_app_list = requests.get('URL_OF_APPLICATION_LIST').json()
    for app in origin_app_list:
        app_list.append({
            'id': app.get('id'),
            'name': app.get('name'),
            'time': app.get('time'),
            'url': app.get('url')
        })
    return app_list
