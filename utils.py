import sys
import socket
import redis
import yaml
import logging

"""
Module containing all utility functions for roku remote control
"""

############# DB/Config Setup ################
with open('config/config.yaml', 'r+') as f:
    config = yaml.load(f)

redis_ctx = redis.StrictRedis(db=0)

############### logging #####################
def log_msg(msg, level='info'):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        filename='logs/roku.log')
    if level == 'info':
        logging.info(msg)
    elif level == 'warning':
        logging.warning(msg)
    elif level == 'error':
        logging.error(msg)

################# Helpers ####################
def update_config(updates):
    redis_ctx.hmset('roku_{}'.format(get_subnet()), updates)

def get_config():
     return redis_ctx.hgetall('roku_{}'.format(get_subnet()))

def get_subnet():
    """
    :return: int made up of first two octets of ip
    """
    return ''.join(socket.gethostbyname(socket.gethostname()).split('.')[:2])

# Socket requests helper
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