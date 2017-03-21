#!/usr/bin/python

'''clean.py -- Small script to clean up the directory.

Copyright (C) Abhijit J. Theophilus (abhitheo96@gmail.com)
For license see LICENSE.
'''

import os
import shutil
from sys import argv
from glob import glob

to_delete = {'pkg_retry', '__pycache__', 'logs', 'docs'}

error_msg = 'Invalid usage. Usage: ./clean.py [--force]'

if len(argv) > 2:
    print(error_msg)

elif len(argv) == 2:
    if argv[1] != '--force':
        print(error_msg)

else:
    for_delete = set(to_delete)
    print("Confirm deletes. Press 'n' to cancel.")
    for i in for_delete:
        print("%12s: " % (i), end='')
        if input() == 'n': to_delete.remove(i)

for i in to_delete:
    files = glob(i)
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        elif os.path.isdir(f):
            shutil.rmtree(f)
        else:
            print('Invalid file type %r' % (f))
