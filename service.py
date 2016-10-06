#!/usr/local/bin/python3

import subprocess
import sys
import threading
import time
sys.path.append("dir")

from flask import Flask, request, Response
app = Flask(__name__)
if not app.debug:
    import logging
    file_handler = logging.FileHandler('service.log')
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

import settings


DOWNLOADS = {}


class Status(object):

    NEW = (0, "New")
    WORKING = (1, "Working...")
    FAILED = (2, "Failed!")
    SUCCESS = (3, "Success")

    def __init__(self):
        self.status = Status.NEW

    def working(self):
        self.status = Status.WORKING

    def failed(self):
        self.status = Status.FAILED

    def success(self):
        self.status = Status.SUCCESS

    def __repr__(self):
        return "<Status: {}>".format(self.status[1])


class Report(Status):

    def __init__(self):
        super().__init__()
        self.stdout = b''
        self.stderr = b''

    def on(self, process):
        self.add_stdout(process)
        self.add_stderr(process)

    def add_stdout(self, process):
        self.stdout += process.stdout.read()

    def add_stderr(self, process):
        self.stderr += process.stderr.read()

    def __repr__(self):
        return "<Report: {}, {}, {}>".format(super().__repr__(), len(self.stdout), len(self.stderr))


def get_title_and_description(url, report):
    proc = subprocess.Popen(
        ['youtube-dl', '--get-title', '--get-description', url],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    report.working()
    rc = proc.wait()

    report.on(proc)
    if rc:
        report.failed()
        return (None, None)
    report.success()

    text = report.stdout.decode('utf-8')
    (title, description) = text.split('\n', 1)
    print("Title: {}\nDescription: {}".format(title, description))
    return (title, description)


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return ('', 200)


@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data['url']

    if url in DOWNLOADS:
        return ('', 202)

    report = Report()
    DOWNLOADS[url] = report

    args = (url, report)
    t = threading.Thread(target=get_title_and_description, args=args)
    t.start()

    return ('', 200)


@app.route('/report', methods=['GET'])
def report():
    return Response(str(DOWNLOADS), mimetype='text/plain; charset=utf-8')


if __name__ == '__main__':
    app.run(port=settings.SERVICE_PORT, threaded=True)
