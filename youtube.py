#!/usr/local/bin/python3

import argparse
import subprocess


def get_title_and_description(url):
    proc = subprocess.Popen(
        ['youtube-dl', '--get-title', '--get-description', url],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")

    args = parser.parse_args()
    return vars(args)


def main():
    args = parse_args()
    url = args['url']

    inp = input("Do you also want the [V]ideo or [A]udio (V/A/n)? ")



if __name__ == '__main__':
    main()
