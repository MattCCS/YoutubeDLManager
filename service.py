#!/usr/local/bin/python3

import argparse
import json
import sys

from youtube import manager
from youtube import settings

from flask import Flask, request, Response
app = Flask(__name__)
if not app.debug:
    import logging
    file_handler = logging.FileHandler('service.log')
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)


MANAGER = manager.DownloadManager()


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return (settings.VERSION, 200)  # everything will be ok


@app.route('/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    MANAGER.download(data['url'], data['audio_video'])
    return ('', 200)


@app.route('/report', methods=['GET'])
def report():
    return Response(json.dumps(MANAGER.dump()), mimetype='text/plain; charset=utf-8')


if __name__ == '__main__':
    try:
        app.run(port=settings.SERVICE_PORT, threaded=True)
    except OSError as exc:
        if exc.errno == 48:
            print("Service is already running.")
        else:
            raise exc
