#!/usr/bin/python

'''
doc_scrape.py -- Scrape the documentation of the public methods and
constructors for each class in every package specified in the
pkg_list.json file from the online Java documentation.

Copyright (C) Abhijit J. Theophilus (abhitheo96@gmail.com)
For license see LICENSE.
'''

import os
import json
from concurrent.futures import ProcessPoolExecutor

from package_scraper import scrape_package

_BASE_URL = 'https://docs.oracle.com/javase/7/docs/api/'

with open('pkg_list.json') as jsonfile:
    packages = json.load(jsonfile)
    header = '    {:>7}    {:^46}    {:>5}    {:>5}    {}'
    print(header.format('status', 'package', 'done', 'total', 'errors'))

    with ProcessPoolExecutor(4) as executor:
        for key in packages:
            name = key
            url = _BASE_URL + packages[key]
            executor.submit(scrape_package, name, url)
