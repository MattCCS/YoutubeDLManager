
try:
    from . import marshalling
except SystemError:
    import marshalling


class Status(object):

    NEW = "New"
    WORKING = "Working..."
    FAILED = "Failed!"
    SUCCESS = "Success"

    def __init__(self, status=None):
        self.status = Status.NEW if status is None else status

    def working(self):
        self.status = Status.WORKING

    def failed(self):
        self.status = Status.FAILED

    def success(self):
        self.status = Status.SUCCESS


class Report(Status, marshalling.Serializable):

    def __init__(self, status=None, stdout=None, stderr=None):
        super().__init__(status=status)
        self.stdout = stdout if stdout else ''
        self.stderr = stderr if stderr else ''

    def save_output(self, process):
        self.add_stdout(process)
        self.add_stderr(process)

    def add_stdout(self, process):
        try:
            text = process.stdout.read()
            text = text.decode('utf-8')
        except TypeError:
            pass
        self.stdout += text

    def add_stderr(self, process):
        try:
            text = process.stderr.read()
            text = text.decode('utf-8')
        except TypeError:
            pass
        self.stderr += text

    @staticmethod
    def load(dump):
        return Report(
            status=dump['status'],
            stdout=dump['stdout'],
            stderr=dump['stderr'],
        )

    def dump(self):
        return {
            'status': self.status,
            'stdout': self.stdout,
            'stderr': self.stderr,
        }
