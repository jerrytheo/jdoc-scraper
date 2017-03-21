
'''
class_scrape.py -- A bunch of functions to scrape each class
information form the online Java documentation.

Copyright (C) Abhijit J. Theophilus (abhitheo96@gmail.com)
For license see LICENSE.
'''

import re
from bs4 import BeautifulSoup


def parse_parameters(row):
    
    '''Returns the parameters of the class as a dict of the form,
    parameter_type: parameter_label from its corresponding <tr> in the
    documentation <table>.
    '''

    td = row.find(class_='colLast')
    if not td:
        td = row.find(class_='colOne')

    # Matches the patterns specified as
    # (<group 1>)<some data>(<group 2>); thereby capturing the same
    # parameters from two different positions in the line.
    # group 1 -- captured from the link to method detail. Contains the
    #            class name in full.
    # group 2 -- captured from the text. Contains the parameter name.
    pregex = re.compile(r'\(([^)]+)\).*\(([^)]+)\)')
    td = ' '.join(str(i) for i in td.contents if str(i) != '\n')
    pmatch = re.search(pregex, td)
    if pmatch:
        # %20 is a space in HTTP requests.
        ptypes = pmatch.group(1).split('%20')       
        
        # Need to get every alternate element. e.g. 'a' from 'int a'.
        pnames = BeautifulSoup(pmatch.group(2), 'lxml').body.text.split()
        pnames = [ pnames[i] for i in range(1, len(pnames), 2) ]
        
        # After the regex capture, both may have ,'s if not the last
        # parameter in the prototype.
        pdict = { key.strip(','): value.strip(',')
                for key,value in zip(pnames, ptypes) }
        return pdict
    else:
        return


def parse_return_type(row):
    
    '''Get the return type of the class from its corresponding <tr> in
    the documentation <table>.
    '''

    # Methods declared private, protected or abstract are never
    # available to the user.
    _disallowed = ('private', 'protected' 'abstract')

    ret = row.find(class_ = 'colFirst').get_text()
    if [ i for i in ret.split() if i in _disallowed ]:
        return
    ret = ret.split()[-1]
    return None if ret == 'void' else ret


def scrape_class(soup, cls_name):

    '''Parse the Class description page. Saves info regarding
    constructors and class methods.'''
    
    methods = [] 
    
    span = soup.find('span', string='Methods')
    # Not all classes have methods.
    if span:
        tbl = span.parent.parent
        for row in tbl.find_all('tr')[1:]:
            # Check if method is not deprecated.
            inner = row.find('td', class_='colLast')
            if inner.div:
                descr = ' '.join(inner.div.get_text().split())
                if 'Deprecated' in descr: continue
            else:
                descr = None

            # Store metadata.
            name = inner.code.strong.a.text
            method_info = {
                'name': name,
                'description': descr,
                'parameters': parse_parameters(row),
                'return': parse_return_type(row),
                }
            methods.append(method_info)
    
    # Handling constructors as follows,
    #   Return type -- Class name.
    #   Parameters  -- As specified.
    #   Name        -- Class name.
    #   Description -- As specified.
    
    span = soup.find('span', string='Constructors')
    # Not all classes have constructors.
    if span:
        tbl = span.parent.parent
        for row in tbl.find_all('tr')[1:]:
            # Check if constructor deprecated.
            inner = row.find('td', class_='colOne')
            if not inner:
                inner = row.find('td', class_='colFirst')
                if 'protected' in inner.text or 'private' in inner.text:
                    continue
                inner = row.find('td', class_='colLast')

            if inner.div:
                descr = ' '.join(inner.div.get_text().split())
                if 'Deprecated' in descr: continue
            else:
                descr = None

            # Store metadata
            construct_info = {
                'name': cls_name,
                'description': descr,
                'parameters': parse_parameters(row),
                'return': cls_name,
                }
            methods.append(construct_info)
    
    # Save all inherited functions for a future implementation.
    inherited = {}
    name_re = re.compile('methods_inherited_from_class_(.*)')
    for a in soup.find_all('a'):
        if not a.has_attr('name'): continue
        name_mch = re.match(name_re, a['name'])
        if not name_mch: continue
        inherited[name_mch.group(1)] = a.parent.code.text.split(', ')
        
    return { 'methods': methods, 'inherited': inherited }


if __name__ == '__main__':
    import requests
    url = 'http://docs.oracle.com/javase/7/docs/api/java/awt/Dialog.html'
    r = requests.get(url)
    sp = BeautifulSoup(r.text, 'lxml')
    class_def = scrape_class(sp, 'java.awt.Dialog')
    
    for i in class_def['methods']:
        for key in i:
            print(key, ': ', i[key], sep='')
        print('')

    for key in class_def['inherited']:
        print(key, ': ', class_def['inherited'][key], sep='')
        print('')

