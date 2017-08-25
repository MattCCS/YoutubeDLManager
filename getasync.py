
import argparse
import subprocess

from youtube import settings
from youtube import utils
from youtube.videodata import YoutubeVideo


DEBUG = False


def get_path_of_download(stdout):
    MERGING = "Merging formats into \""
    ALREADY = " has already been downloaded"
    try:
        if ALREADY in stdout:
            return stdout.split(ALREADY, 1)[0].split('\n[download] ')[-1]
        else:
            return stdout.split(MERGING)[1].split("\"\n", 1)[0]
    except IndexError as exc:
        raise RuntimeError(stdout)


def download_video_async(audio_video_spec, destination, url):
    stdoutpath = str(settings.DOWNLOAD_PATH / "stdout.txt")
    stderrpath = str(settings.DOWNLOAD_PATH / "stderr.txt")
    stdout = open(stdoutpath, 'wb', buffering=0) if DEBUG else subprocess.DEVNULL
    stderr = open(stderrpath, 'wb', buffering=0) if DEBUG else subprocess.DEVNULL

    subprocess.Popen(
        ['youtube-dl',
         '-f', audio_video_spec,
         '-o', destination,
         url],
        stdout=stdout, stderr=stderr)


@utils.fireandforget
def get_async(url, audio_video):
    print("Got: {}".format(audio_video))
    if audio_video not in ('A', 'V'):
        return

    # Part 1
    video = YoutubeVideo()

    video_data = video.data
    report = video_data.report

    proc = subprocess.Popen(
        ['youtube-dl', '--get-title', '--get-description', url],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    report.working()
    rc = proc.wait()

    report.save_output(proc)
    if rc:
        report.failed()
        return
    report.success()

    text = report.stdout
    (title, description) = text.split('\n', 1)
    video_data.set_title(title)
    video_data.set_description(description)
    print("Title:  {}\nDescription:  {}...".format(title, description[:40]))

    # Part 2
    video_media = video.media
    report = video_media.report

    destination = str(settings.DOWNLOAD_PATH / "%(title)s.%(ext)s")

    audio_video_spec = "bestaudio[ext=m4a]"
    if audio_video == 'V':
        audio_video_spec = 'bestvideo[ext=mp4]+' + audio_video_spec

    download_video_async(audio_video_spec, destination, url)
    # report.working()
    # rc = proc.wait()

    # report.save_output(proc)
    # if rc:
    #     report.failed()
    #     return
    # report.success()

    # path = get_path_of_download(report.stdout)
    # video_media.set_path(path)
    # print("Download of '{}': {} ({})".format(audio_video, report.status, path))


def get(url, audio_video):
    get_async(url, audio_video)


def parse_args():
    parser = argparse.ArgumentParser(description="Downloads the given YouTube URL")
    parser.add_argument("url", help="The URL to download")
    parser.add_argument("-d", "--debug", action="store_true", help="Write to stdout/stderr files")

    return parser.parse_args()


def main():
    global DEBUG

    try:
        args = parse_args()
        DEBUG = args.debug
        if args.debug:
            print("(DEBUG MODE)")

        audio_video = input("Do you also want the [V]ideo or [A]udio (V/A/n)? ")
        get(args.url, audio_video.upper())
    except KeyboardInterrupt:
        print("\n[+] Cancelled.")


if __name__ == '__main__':
    main()
