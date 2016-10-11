
from . import marshalling
from .report import Report


class YoutubeVideo(marshalling.Serializable):

    def __init__(self, data=None, media=None):
        self.data = data if data else YoutubeVideoData()
        self.media = media if media else YoutubeVideoMedia()

    @staticmethod
    def load(dump):
        return YoutubeVideo(
            data=marshalling.load(YoutubeVideoData, dump['data']),
            media=marshalling.load(YoutubeVideoMedia, dump['media']),
        )

    def dump(self):
        return {
            'data': marshalling.dump(self.data),
            'media': marshalling.dump(self.media),
        }


class YoutubeVideoData(marshalling.Serializable):

    def __init__(self, title=None, description=None, report=None):
        self.title = title
        self.description = description
        self.report = report if report else Report()

    def set_title(self, title):
        self.title = title

    def set_description(self, description):
        self.description = description

    @staticmethod
    def load(dump):
        return YoutubeVideoData(
            title=dump['title'],
            description=dump['description'],
            report=marshalling.load(Report, dump['report']),
        )

    def dump(self):
        return {
            'title': self.title,
            'description': self.description,
            'report': marshalling.dump(self.report),
        }


class YoutubeVideoMedia(marshalling.Serializable):

    def __init__(self, path=None, report=None):
        try:
            if path is not None:
                path = path.decode('utf-8')
        except (TypeError, AttributeError):
            pass
        self.path = None if path is None else path
        self.report = report if report else Report()

    def set_path(self, path):
        self.path = path

    @staticmethod
    def load(dump):
        return YoutubeVideoMedia(
            path=dump['path'],
            report=marshalling.load(Report, dump['report']),
        )

    def dump(self):
        return {
            'path': self.path,
            'report': marshalling.dump(self.report),
        }
