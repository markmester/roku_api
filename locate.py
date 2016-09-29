import socket
import re
from utils import update_config
from functools import wraps
import signal

"""
Module for locating roku device and saving device stats to redis store
"""

# raises TimeoutError after user specified timeout
class TimeoutError(Exception): pass
def timeout(seconds, error_message = 'Function call timed out'):
    def decorated(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorated

############ Locate Roku Devices #################

# @timeout(10)
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

    msg = {
        'success': False,
        'data': None
    }

    while True:
        try:
            resp = sock.recv(1024)
            match = re.match(r'.*USN: uuid:roku:ecp:([\w\d]{12}).*LOCATION: http://([\d\.]*):(\d*)', resp, re.S)
            host = match.group(2)
            port = match.group(3)

            # update config
            update_config({'host': host, 'port': int(port), 'connected': 1})

            # update resp
            msg.update({'success': True, 'data': resp})

            break

        except socket.timeout:
            update_config({'connected': 0})
            continue

        except KeyboardInterrupt:
            print 'Exiting...'
            break

    return msg

if __name__ == '__main__':
    locate_device()
