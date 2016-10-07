#!/usr/local/bin/python3

import argparse
import sys
sys.path.append("lib")

import requests

import settings


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="command or URL")

    return parser.parse_args()


def main():
    args = parse_args()
    command = args.command

    if not command:
        return  # list

    if command.isdigit():
        return  # list

    if command == 'shutdown':
        print("Attempting shutdown...")
        try:
            resp = requests.post("http://127.0.0.1:{port}/shutdown".format(port=settings.SERVICE_PORT))
            print("?")
        except requests.exceptions.ConnectionError as err:
            print("Service wasn't running or couldn't connect!")
        return

    inp = input("Do you also want the [V]ideo or [A]udio (V/A/n)? ")



if __name__ == '__main__':
    main()
