
'''
misc.py -- Miscellaneous functions for the scraper.

Copyright (C) Abhijit J. Theophilus, abhitheo96@gmail.com
For license see LICENSE.
'''


import os
import xml.etree.ElementTree as ET
from xml.dom import minidom


def get_absolute_url(current_url, relative_url):

    '''Returns the absolute url given the current url and the url
    relative to the current url.
    '''

    current_url = current_url.split('/')
    relative_url = relative_url.split('/')

    # Number of levels to go up.
    levels = relative_url.count('..')

    abs_url = '/'.join(current_url[: -(levels+1)]) + '/' \
            + '/'.join(relative_url[levels:])
    return abs_url


def write_xml(package_info):

    '''Write the package info to an xml file.
    The xml is structured as follows,

    package
      ├── name
      ├── description
      ├── class (id)
      │     ├── name
      │     └── description
      └── method (id)
            ├── name
            ├── description
            ├── parameter
            │     ├── name
            │     └── type
            ├── return
            └── class

    The bracketed terms indicate attributes.
    '''
    root = ET.Element('package')

    # Name.
    name = ET.SubElement(root, 'name')
    name.text = package_info['name']

    # Description.
    desc = ET.SubElement(root, 'desc')
    desc.text = package_info['description']

    # Classes.
    cls_id = 0
    mtd_id = 0
    for class_ in package_info['classes']:
        cls = ET.SubElement(root, 'class')

        # Class ID.
        cls.set('id', str(cls_id))
        cls_id = cls_id + 1

        # Class name.
        cls_name = ET.SubElement(cls, 'name')
        cls_name.text = class_['name']

        # Class description.
        cls_desc = ET.SubElement(cls, 'description')
        cls_desc.text = class_['description']

    for class_ in package_info['classes']:
        for method in class_['methods']['methods']:
            mtd = ET.SubElement(root, 'method')

            # Method ID.
            mtd.set('id', str(mtd_id))
            mtd_id = mtd_id + 1

            # Method name.
            mtd_name = ET.SubElement(mtd, 'name')
            mtd_name.text = method['name']

            # Method description.
            mtd_desc = ET.SubElement(mtd, 'description')
            mtd_desc.text = method['description']

            # Method parameters.
            prm_id = 0
            if method['parameters']:
                for param in method['parameters']:
                    prm = ET.SubElement(mtd, 'parameter')
                    prm.set('id', str(prm_id))
                    prm_id = prm_id + 1

                    prm_name = ET.SubElement(prm, 'name')
                    prm_name.text = param

                    prm_type = ET.SubElement(prm, 'type')
                    prm_type.text = method['parameters'][param]

            # Method return type.
            if method['return']:
                mtd_retn = ET.SubElement(mtd, 'return')
                mtd_retn.text = method['return']

            # Method class.
            mtd_clsn = ET.SubElement(mtd, 'class')
            mtd_clsn.text = class_['name']

    # Prettify the xml to double space indentation.
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)

    xml_path = os.path.join('docs', package_info['name'] + '.xml')
    with open(xml_path, 'w') as xml_file:
        xml_file.write(reparsed.toprettyxml(indent='  '))
