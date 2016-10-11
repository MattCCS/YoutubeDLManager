
import abc


def dump(maybe):
    if maybe is None:
        return None
    return maybe.dump()


def load(cls, maybe):
    if maybe is None:
        return None
    return cls.load(maybe)


class Serializable(object):
    __metaclass__ = abc.ABCMeta

    @staticmethod
    @abc.abstractmethod
    def load(dump):
        pass

    @abc.abstractmethod
    def dump(self):
        pass

    def __repr__(self):
        return repr(vars(self))
