#!/usr/local/bin/python3

import os

from youtube import settings


def main():
    os.system("open {}/report".format(settings.FULL_ADDRESS))


if __name__ == '__main__':
    main()
