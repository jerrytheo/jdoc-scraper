#!/usr/bin/python

'''
doc_scrape.py -- Scrape the documentation of the public methods and
constructors for each class in every package specified in the
pkg_list.json file from the online Java documentation.

Copyright (C) Abhijit J. Theophilus (abhitheo96@gmail.com)
For license see LICENSE.
'''

import os
import sys
import json
from concurrent.futures import ProcessPoolExecutor

from package_scraper import scrape_package

_BASE_URL = 'https://docs.oracle.com/javase/7/docs/api/'

_STATUS_TEXT = '    {status}    {package:46}    {parsed:>5}    {total:>5}' \
             + '    {misc}'
_SUCCESS = '\033[92mSUCCESS\033[0m'
_PARTIAL = '\033[93mPARTIAL\033[0m'
_FAILURE = '\033[91mFAILURE\033[0m'


# Read the list of packages.
with open('pkg_list.json') as jsonfile:
    packages = json.load(jsonfile)

# If retry is specified, run only for failed/partially parsed packages.
if len(sys.argv) == 2 and sys.argv[1] == '--retry':
    if os.path.isfile('pkg_retry'):
        with open('pkg_retry') as retryfile:
            retry_for = retryfile.read()
        retry_for = retry_for.split()
        packages = { k: packages[k] for k in packages if k in retry_for }
    else:
        print('No pkg_retry file found.')

# Print the header.
header = '    {:>7}    {:^46}    {:>5}    {:>5}    {}'
print(header.format('status', 'package', 'done', 'total', 'errors'))

# Create required folders.
for dir_ in ['logs', 'docs']:
    if not os.path.isdir(dir_): os.mkdir(dir_)

futures = {}
# Each package is parsed on one of 8 processes.
with ProcessPoolExecutor(8) as executor:
    for key in packages:
        name = key
        url = _BASE_URL + packages[key]
        futures[name] = executor.submit(scrape_package, name, url)

success = 0
partial = 0
failure = 0
empties = 0
with open('pkg_retry', 'w') as rf:
    for name in futures:
        try:
            result = futures[name].result()
            if result == 'success':
                success += 1
            elif result == 'partial':
                rf.write(name + '\n')
                partial += 1
            elif result == 'empty':
                empties += 1
        except Exception as exc:
            rf.write(name + '\n')
            failure += 1

print('\nTotal packages:', success+partial+failure+empties, 'packages')
print('Complete:', success, 'packages')
print('Incomplete:', partial, 'packages')
print('Failed:', failure, 'packages')
print('Empty:', empties, 'packages')
