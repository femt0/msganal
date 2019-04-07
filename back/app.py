#!/usr/bin/env python3

from flask import Flask, jsonify
from flask_cors import CORS
from celery import Celery
from celery.task.control import revoke
from flask_socketio import SocketIO
import logging
import config
import model
import time
import scanner
import eventlet

eventlet.monkey_patch(socket=True)

app = Flask(__name__)
CORS(app)
app.config.from_object(config)

#"""async_mode='eventlet',""" 
socketio = SocketIO()
socketio.init_app(app, message_queue=app.config['REDIS_EXCHANGE_URL'], async_mode='eventlet')
#app, message_queue=app.config['REDIS_EXCHANGE_URL'])  

celery = Celery(app.name, broker=app.config['REDIS_EXCHANGE_URL'])  
celery.conf.update(app.config) 

#scanner.init()
#model.init()

@app.route('/start')
def start():
    #async task
    celery.send_task('scanner.start')
    #start_task.delay()
    #asyncstart.delay()
    return 'start listening', 202

@app.route('/stop')
def stop():
    #client.stopListening()
    #async task
    celery.send_task('scanner.stop')
    #socketio.emit('stop_listening', 'stop_listening', namespace='/socket')
    return 'stop listening', 200

@app.route('/users')
def users():
    return jsonify(users=model.get_users()), 200

@app.route('/global')
def globaluser():
    return jsonify(user=model.get_user(config.GLOBAL)), 200

@app.route('/stickers')
def stickers():
    return jsonify(stickers=model.get_stickers()), 200

@app.route('/scan/<int:after>/<int:before>')
def scan(after, before):
    if after > before:
        return "'after' timestamp needs to be prior to 'before' timestamp", 400

    #async task
    celery.send_task('scanner.scan', kwargs={'before': before, 'after': after})
    #scanner.scan.delay(after=after, before=before)
    #scan_task.delay(after=after, before=before)
    return 'scan started from {} to {}'.format(after, before), 202

@app.route('/fullscan')
def fullscan():
    after = 0
    before = int(round(time.time() * 1000))
    #async task
    celery.send_task('scanner.scan', kwargs={'before': before, 'after': after, 'flush': True})
    #scan_task.delay(after=after, before=before, flush=True)
    return 'fullscan started', 202

@socketio.on('refresh_messages', namespace='/socket')
def log_messages(sid, data):
    print("HEEEEERRREEE")
    print(data)

@socketio.on('refresh_stickers', namespace='/socket')
def log_stickers(sid, data):
    print(data)

#@celery.task()
#def asyncstart():
#    scanner.listen()

#@celery.task()
#def asyncscan(after, before, flush=False):
#    scanner.scan(after, before, flush)


#with app.app_context():
    #model = get_model()
    #model.init_app()
    #scanner = get_scanner()
    #scanner.init_app()
    #scanner.listen()

# Register the api blueprint.
#from .api import api
#app.register_blueprint(api, url_prefix='/api')


#@app.errorhandler(500)
#def server_error(e):
#    return """
#    An internal error occurred: <pre>{}</pre>
#    See logs for full stacktrace.
#    """.format(e), 500
#
#    return app



#global thread_id, blobber #, celery
#celery = Celery(current_app.name, broker=current_app.config['CELERY_BROKER_URL'])  
#celery.conf.update(current_app.config) 

if __name__ == '__main__':
    socketio.run(app)
