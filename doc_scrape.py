
'''
doc_scrape.py -- Scrape the documentation of the public methods and
constructors specified in the pkg_list.json file from the online Java
documentation.

Copyright (C) Abhijit J. Theophilus (abhitheo96@gmail.com)
For license see LICENSE.
'''

import os
import json
from multiprocessing import Process

from package_scrape import PackageThread

_BASE_URL = 'https://docs.oracle.com/javase/7/docs/api/'

class PackageGroupProcess(Process):
    def __init__(self, pkgs):
        self.pkgs = pkgs
        if not os.path.isdir('docs'):
            os.mkdir('docs')
        if not os.path.isdir('logs'):
            os.mkdir('logs')


    def run(self):
        pkg_threads = []
        for package in self.pkgs:
            url = _BASE_URL + self.pkgs[package]
            name = package
            pkg_threads.append(PackageThread(name, url))

        for pkg_thread in pkg_threads:
            pkg_thread.start()

        for pkg_thread in pkg_threads:
            pkg_thread.join()


def main():
    with open('pkg_list.json') as jfile:
        pkg_list = json.load(jfile)
    print(pkg_list)

if __name__ == '__main__':
    main()

