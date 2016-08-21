#!/usr/bin/python
import sys
import socket
import re
import json

############ Locate Roku Devices #################
def locate_device():
    ssdpRequest = "M-SEARCH * HTTP/1.1\r\n" + \
            "HOST: 239.255.255.250:1900\r\n" + \
            "Man: \"ssdp:discover\"\r\n" + \
            "MX: 5\r\n" + \
            "ST: roku:ecp\r\n\r\n"

    socket.setdefaulttimeout(10)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.sendto(ssdpRequest, ("239.255.255.250", 1900))

    while True:
        try:
            resp = sock.recv(1024)
            match = re.match(r'.*USN: uuid:roku:ecp:([\w\d]{12}).*LOCATION: http://([\d\.]*):(\d*)', resp, re.S)
            host = match.group(2)
            port = match.group(3)

            # update config
            update_config({'host': host, 'port': int(port)})
            success = True
            break

        except:  # socket.timeout:
            success = False


    # create api response
    msg = {
        'success': success,
        'data': resp
    }

    return msg

############ Socket requests helper ##########
def socket_request(method, host, port, path):
    # establish connection and send request
    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect((host, port))
      sock.send("{0} {1} HTTP/1.0\r\nHost: {2}\r\n\r\n".format(method.upper(), path, host))
    except socket.error, msg:
      sys.stderr.write("[ERROR] %s\n" % msg[1])
      sys.exit(1)

    # receive resp
    data = sock.recv(1024)
    resp = ""
    while len(data):
      resp += data
      data = sock.recv(1024)
    sock.close()

    # create api response
    msg = {
        "success": False,
        "data": resp
    }

    if 'HTTP/1.1 200 OK' in resp:
        msg['success'] = True

    return msg

################# Helpers ####################
def update_config(updates):
    with open('config.json', 'r+') as f:
        try:
            config = json.load(f)
        except ValueError:
            config = {}

        config.update(updates)
        f.seek(0)
        f.write(json.dumps(config))
        f.truncate()

def get_config():
     with open('config.json', 'r') as f:
        config = json.load(f)
        return config['host'], config['port']

################# resources ###################

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

def find_netflix():
    success = False
    netflix_id = None
    resp = query_apps()['data']
    netflix_id_match = re.search('<app id="(\d*)".*Netflix</app>', resp)

    if netflix_id_match:
        success = True
        netflix_id = netflix_id_match.group(1)

    # create api response
    msg = {
        "success": success,
        "data": {'resp': resp, 'id': netflix_id}
    }

    return msg


############## entry -- test only ##############
if __name__ == '__main__':

    locate_device()
    print find_netflix()['data']['id']
