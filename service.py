#!/usr/local/bin/python3

import subprocess
import sys
sys.path.append("lib")
import threading

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

    def save_data(self, process):
        self.add_stdout(process)
        self.add_stderr(process)

    def add_stdout(self, process):
        self.stdout += process.stdout.read()

    def add_stderr(self, process):
        self.stderr += process.stderr.read()

    def __repr__(self):
        return "<Report: {}, {}, {}>".format(super().__repr__(), len(self.stdout), len(self.stderr))


def get_title_and_description(url):
    if url in DOWNLOADS:
        return
    report = Report()
    DOWNLOADS[url] = report

    proc = subprocess.Popen(
        ['youtube-dl', '--get-title', '--get-description', url],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    report.working()
    rc = proc.wait()

    report.save_data(proc)
    if rc:
        report.failed()
        return (None, None)
    report.success()

    text = report.stdout.decode('utf-8')
    (title, description) = text.split('\n', 1)
    print("Title: {}\nDescription: {}".format(title, description))
    return (title, description)


def download_video_or_audio(url, audio_video):
    if audio_video not in ('A', 'V'):
        return

    if url in DOWNLOADS:
        return
    report = Report()
    DOWNLOADS[url] = report

    audio_video_spec = "{}bestaudio[ext=m4a]".format('bestvideo[mp4]+' if audio_video == 'V' else '')

    proc = subprocess.Popen(
        ['youtube-dl', '-f', audio_video_spec, url],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    report.working()
    rc = proc.wait()

    report.save_data(proc)
    if rc:
        report.failed()
    report.success()
    return


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return ('', 200)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data['url']
    audio_video = data['audio_video']

    args = (url, audio_video)
    t = threading.Thread(target=get_title_and_description, args=args)
    t.start()

    return ('', 200)


@app.route('/report', methods=['GET'])
def report():
    return Response(str(DOWNLOADS), mimetype='text/plain; charset=utf-8')


if __name__ == '__main__':
    app.run(port=settings.SERVICE_PORT, threaded=True)
