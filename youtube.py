#!/usr/local/bin/python3

import argparse
import subprocess
import time

from youtube import clienterrors
from youtube import marshalling
from youtube import settings
from youtube import utils
from youtube.videodata import YoutubeVideo

import requests  # this must be below the settings import so we can add /lib


def parse_args():
    parser = argparse.ArgumentParser(description="Downloads the given YouTube URL")
    parser.add_argument("command", help="command or URL")

    return parser.parse_args()


def full_report():
    try:
        resp = requests.get(settings.FULL_ADDRESS + "/report")
    except Exception as err:
        raise clienterrors.ResponseParseError("Couldn't get report: {}".format(err))

    try:
        report = resp.json()
    except ValueError as err:
        raise clienterrors.ResponseParseError("Couldn't decode json from report response: {}".format(resp.text))

    return report


def format_entry(entry):
    (url, video) = entry
    video = marshalling.load(YoutubeVideo, video)
    return "{title} / [{status_d}] / [{status_m}] ({url})".format(
        title=video.data.title,
        status_d=video.data.report.status,
        status_m=video.media.report.status,
        url=url,
    )


@utils.fireandforget
def start_service():
    service_log = open("service.log", 'a')
    subprocess.Popen(
        [str(settings.ROOT / 'commands' / 'my-youtube-start')],
        stdout=service_log, stderr=service_log
    )


def heartbeat():
    return requests.get(settings.FULL_ADDRESS + "/heartbeat")


def is_good_heartbeat(resp):
    return (resp.status_code == 200) and (resp.text == settings.VERSION)


def guarantee_service():
    for attempts in range(settings.SERVICE_RETRIES):

        try:
            resp = heartbeat()

            if is_good_heartbeat(resp):
                if attempts > 0:
                    print("[+] Service started OK")
                return

            else:
                if resp.status_code == 200:
                    print("[ ] Version mismatch, restarting...")
                else:
                    print("[ ] Got abnormal code '{}', restarting...".format(resp.status_code))

                requests.post(settings.FULL_ADDRESS + "/shutdown")
                time.sleep(1)

                start_service()
                time.sleep(2)

                continue

        except requests.exceptions.ConnectionError:
            print("[ ] Service down, restarting...")
            start_service()
            time.sleep(2)

            continue

    raise clienterrors.CouldNotStartServiceError("Failed after {} retries!".format(settings.SERVICE_RETRIES))


def main():
    args = parse_args()
    command = args.command

    guarantee_service()

    if command == 'list':
        report = full_report()
        print('\n'.join(
            "{idx}) {rep}".format(idx=i, rep=format_entry(rep))
            for (i, rep) in enumerate(report, 1)
        ))
        return

    if command.isdigit():
        idx = int(command)
        report = full_report()
        try:
            if idx < 1 or idx > len(report):
                raise IndexError
            print(format_entry(report[idx - 1]))
        except IndexError:
            print("No download with id '{}'!".format(idx))
        return

    if command == 'shutdown':
        print("Attempting shutdown...")
        try:
            resp = requests.post(settings.FULL_ADDRESS + "/shutdown")
            print("Shutdown successful (?)")
            return
        except requests.exceptions.ConnectionError:
            raise clienterrors.ServiceAbnormalError("Service wasn't running or couldn't connect!")

    inp = input("Do you also want the [V]ideo or [A]udio (V/A/n)? ")

    try:
        resp = requests.post(
            settings.FULL_ADDRESS + "/download",
            json={
                "url": command,
                "audio_video": inp.upper(),
            }
        )
        if resp.status_code == 200:
            print("Request submitted.")
            return
        else:
            raise clienterrors.ServiceAbnormalError("Service gave abnormal status code '{}'!".format(resp.status_code))
    except requests.exceptions.ConnectionError:
        raise clienterrors.ServiceAbnormalError("Service wasn't running or couldn't connect!")


if __name__ == '__main__':
    try:
        main()
    except clienterrors.ResponseParseError as err:
        print(err)
