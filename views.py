from flask import Flask, render_template
import thread
from locate import locate_device
import subprocess

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
        t = thread.start_new_thread(locate_device, ())

        # start redis-server
        p = subprocess.Popen(['redis-server'], stdout=subprocess.PIPE, shell=True)

        app.run(debug=False, port=5000)

    except (Exception, KeyboardInterrupt):
        p.kill()
        t.kill()
