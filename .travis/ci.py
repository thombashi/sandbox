#!/usr/bin/env python3

import os


def _is_ci() -> bool:
    CI = os.environ.get("CI")

    return CI and CI.lower() == "true"


def _is_travis_ci() -> bool:
    return os.environ.get("TRAVIS") == "true"


def main():
    print("CI: {}".format(_is_ci()))
    print("TRAVIS: {}".format(_is_travis_ci()))


if __name__ == '__main__':
    main()
