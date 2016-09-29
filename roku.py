#!/usr/bin/python
import re
from utils import get_config, socket_request

################# roku api calls ###################

def home():
    host, port = get_config()
    method = 'post'
    path = '/keypress/home'

    return socket_request(method, host, port, path)

def query_apps():
    host, port = get_config()
    method = 'get'
    path = '/query/apps'

    return socket_request(method, host, port, path)

def active_app():
    host, port = get_config()
    method = 'get'
    path = '/query/active-app'

    return socket_request(method, host, port, path)

def find_app(app_name):
    success = False
    id = None
    resp = query_apps()['data']
    app_name = app_name[0].upper() + app_name[1:]
    regex = r"<app id=\"(\d*)\".*{}</app>".format(re.escape(app_name))
    id_match = re.search(regex, resp)

    if id_match:
        success = True
        id = id_match.group(1)

    # create api response
    msg = {
        "success": success,
        "data": {'resp': resp, 'id': id}
    }

    return msg

def lauch_app(id):
    host, port = get_config()
    method = 'post'
    path = '/launch/{}'.format(id)

    return socket_request(method, host, port, path)
    # todo: need to do something after this i.e. paly most recety played

# if in app, pauses/un-pauses ap
def play_pause():
    host, port = get_config()
    method = 'post'
    path = '/keypress/Select'

    return socket_request(method, host, port, path)



############## entry - test only ##############
if __name__ == '__main__':
    pass
    # home()
    # locate_device()
    # netflix_id = find_app('Netflix')['data']['id']
    # print lauch_app(netflix_id)
    # print play_pause()
    #
    # pandora_id = find_app('pandora')['data']['id']
    # print lauch_app(pandora_id)

    # print play_pause()