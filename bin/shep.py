#!/usr/bin/env python

from os.path import abspath, dirname
import sys

sys.path.insert(0, abspath(dirname(__file__) + '/..'))
import stampede.run as entry_point


def run():
    """Pass control to the application."""
    entry_point.run()


if __name__ == '__main__':
    run()
