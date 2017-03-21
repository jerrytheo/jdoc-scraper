
'''
package_scrap.py -- Function to scrape information for a given package
from the online JAVA documentation.

Copyright (C) Abhijit J. Theophilus (abhitheo96@gmail.com)
For license see LICENSE.
'''

import os
import requests
from multiprocessing import Lock
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from misc import get_absolute_url, write_xml
from class_scraper import scrape_class


_STATUS_TEXT = '    {status}    {package:46}    {parsed:>5}    {total:>5}' \
             + '    {misc}'
_SUCCESS = '\033[92mSUCCESS\033[0m'
_PARTIAL = '\033[93mPARTIAL\033[0m'
_FAILURE = '\033[91mFAILURE\033[0m'


def scrape_package(package_name, package_url):

    '''Handles one package. It retrieves the web page, calculates the number of
    classes to parse, sequentially tries to retrieve each class' web page and
    parse it for its name, description, and methods.  This information is stored
    in an XML file named <package_name>.xml.
    '''

    log_path = os.path.join('logs', package_name + '.log')
    if os.path.isfile(log_path):
        os.remove(log_path)

    print_lock = Lock()

    try:
        # Get package page. Construct soup. Store package name and
        # description.

        package_page = requests.get(package_url)
        package_soup = BeautifulSoup(package_page.text, 'lxml')

        docSumm = package_soup.find(class_='docSummary')
        if docSumm:
            desc = docSumm.div.text
            desc = ' '.join(desc.split())
        else:
            desc = None
        package_info = {
            'name': package_name,
            'description': desc
            }

        # Classes are in a <table> captioned 'Class Summary'. Each
        # class is represented by a row in the table, where the
        # first column is its name and the last one is its
        # description.

        span = package_soup.find('span', string = 'Class Summary')
        if span:
            tbl = span.parent.parent
        else:
            return 'empty'
        cls_list = tbl.find_all('tr')[1:]           # First row is headers.

    except Exception as exc:
        statust = _STATUS_TEXT.format(status=_FAILURE,
                package=package_name, parsed='-', total='-', misc=exc)
        with print_lock:
            print(statust)
        raise

    else:
        successes = 0
        package_info['classes'] = []
        
        # Each class is parsed on one of 32 threads.
        nthreads = 32 if len(cls_list) >= 32 else len(cls_list)
        executor = ThreadPoolExecutor(nthreads)
        for cls_ in cls_list:
            cls_info = {}
            try:
                # Name.
                cls_info['name'] = package_name + '.' \
                                 + cls_.find('td', 'colFirst').a.text
                # Description.
                desc_tag = cls_.find('div', 'block')
                if desc_tag:
                    cls_info['description'] = ' '.join(desc_tag.text.split())
                else:
                    cls_info['description'] = None
                # Methods.
                cls_url = get_absolute_url(package_url,
                        cls_.find('td', 'colFirst').a['href'])
                cls_page = requests.get(cls_url)
                cls_soup = BeautifulSoup(cls_page.text, 'lxml')
                future = executor.submit(scrape_class, cls_soup, cls_name)
                cls_info['methods'] = future.result()
            except Exception as exc:
                with open(log_path, 'a') as log_file:
                    log_file.write('%s:%s\n' % (cls_name, str(exc)))
            else:
                successes +=  1
                package_info['classes'].append(cls_info)
        executor.shutdown()

        if successes == len(cls_list):
            status = _SUCCESS
        elif successes == 0:
            status = _FAILURE
        else:
            status = _PARTIAL
        statust = _STATUS_TEXT.format(status=status, package=package_name,
                parsed=successes, total=len(cls_list), misc='')

        write_xml(package_info)

        with print_lock:
            print(statust)

        if status == _SUCCESS:
            return 'success'
        else:
            return 'partial'


if __name__ == '__main__':
    url = 'http://docs.oracle.com/javase/7/docs/api/java/' \
        + 'awt/package-summary.html'
    name = 'java.awt'
    print('Starting dry run ... ')
    scrape_package(name, url)

