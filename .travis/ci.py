#!/usr/bin/env python3

import os


def main():
    CI = os.environ.get("CI")
    print(CI)
    if CI:
        print(CI == "true", CI.strip() == "true")

    TRAVIS = os.environ.get("TRAVIS")
    print(TRAVIS)
    if TRAVIS:
        print(TRAVIS == "true", TRAVIS.strip() == "true")


if __name__ == '__main__':
    main()
