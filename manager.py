
import collections
import subprocess


try:
    from . import marshalling
    from . import settings
    from . import utils
    from .videodata import YoutubeVideo
except SystemError:
    import marshalling
    import settings
    import utils
    from videodata import YoutubeVideo


def get_path_of_download(stdout):
    MERGING = "Merging formats into \""
    ALREADY = " has already been downloaded"
    if ALREADY in stdout:
        return stdout.split(ALREADY, 1)[0].split('\n[download] ')[-1]
    else:
        return stdout.split(MERGING)[1].split("\"\n", 1)[0]


class DownloadManager(marshalling.Serializable):

    def __init__(self, downloads=None):
        self.downloads = collections.OrderedDict() if downloads is None else downloads

    @staticmethod
    def load(dump):
        return DownloadManager(
            downloads={
                url: marshalling.load(YoutubeVideo, video)
                for (url, video) in dump
            }
        )

    def dump(self):
        return [
            (url, video.dump())
            for (url, video) in self.downloads.items()
        ]

    def has(self, url):
        return url in self.downloads

    def get(self, url):
        return self.downloads[url]

    def make(self, url):
        video = YoutubeVideo()
        self.downloads[url] = video
        return video

    def download(self, url, audio_video):
        self.get_title_and_description(url)
        self.download_video_or_audio(url, audio_video)

    @utils.fireandforget
    def get_title_and_description(self, url):
        if self.has(url):
            video = self.get(url)
        else:
            video = self.make(url)

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
        print("Title: {}\nDescription: {}".format(title, description))

    @utils.fireandforget
    def download_video_or_audio(self, url, audio_video):
        print("Got: {}".format(audio_video))
        if audio_video not in ('A', 'V'):
            return

        if self.has(url):
            video = self.get(url)
        else:
            video = self.make(url)
        video_media = video.media
        report = video_media.report

        destination = str(settings.DOWNLOAD_PATH / "%(title)s.%(ext)s")

        audio_video_spec = "bestaudio[ext=m4a]"
        if audio_video == 'V':
            audio_video_spec = 'bestvideo[ext=mp4]+' + audio_video_spec

        proc = subprocess.Popen(
            ['youtube-dl',
             '-f', audio_video_spec,
             '-o', destination,
             url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        report.working()
        rc = proc.wait()

        report.save_output(proc)
        if rc:
            report.failed()
        report.success()

        path = get_path_of_download(report.stdout)
        video_media.set_path(path)
        print("Download of '{}': {} ({})".format(audio_video, report.status, path))
