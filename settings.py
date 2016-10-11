
import pathlib
import sys

VERSION = "0.0.6"
SERVICE_RETRIES = 3

ROOT = pathlib.Path(__file__).resolve().parent
DOWNLOAD_PATH = ROOT / "downloads"
LIB_PATH = ROOT / "lib"
sys.path.append(str(LIB_PATH))

SERVICE_PORT = 14145
FULL_ADDRESS = "http://127.0.0.1:{port}".format(port=SERVICE_PORT)
