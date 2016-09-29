from flask import Flask, render_template
import thread
from locate import locate_device
import subprocess
from utils import log_msg

"""
Main application entry. Starts webserver, redis-server, and roku device location thread
"""

app = Flask(__name__)

################# resources ######################
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


#################### entry #######################
if __name__ == '__main__':
    try:
        # thread for roku location script
        log_msg('Starting roku device location thread...')
        t = thread.start_new_thread(locate_device, ())

        # start redis-server
        log_msg('Starting redis-server...')
        p = subprocess.Popen(['redis-server'], stdout=subprocess.PIPE, shell=True)

        # start views
        log_msg('Starting views...')
        app.run(debug=False, port=5000)

    except (Exception, KeyboardInterrupt):
        p.kill()
        t.kill()
