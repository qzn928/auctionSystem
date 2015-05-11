# -*- coding: utf-8 -*-
"""
    由此文件获得包版本号.
"""
import sys
#sys.path.append('./lib')
VERSION = ('0', '1')
BUILD = "1"
RELEASE = False

def get_package_version():
    return ".".join(VERSION) + "-build-" + BUILD


def is_release():
    return RELEASE
