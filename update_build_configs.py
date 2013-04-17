#!/usr/bin/env python2.7
"""
"""

import re
import xml.etree.ElementTree as ET

try:
    import requests
except ImportError:
    raise ImportError(
        "requests must be installed to use this script. "
        "Try `pip install requests`")

import jenkins_config as config


def fix_url(url):
    """
    Fix a ShiningPanda URL so the SSL certificates work.
    """
    # ShiningPanda's SSL certificates are for shiningpanda.com,
    # not shiningpanda-ci.com, so we change it to that so the
    # HTTPS support in requests is happy
    return url.replace('shiningpanda-ci.com', 'shiningpanda.com')


def get_build_list():
    """
    Gets the list of all builds in astropy's Jenkins instance.
    """
    r = requests.get(fix_url(config.root_url + "api/json"))
    build_list = r.json()
    return build_list


def make_axis(axis_type, name, values):
    """
    Makes the XML structure for a single build axis.

    Parameters
    ----------
    axis_type : str
        The type of axis.

    name : str
        The name of the variable used for the axis.

    values : list of str
        The values for the axis.
    """
    axis_elem = ET.Element('hudson.matrix.{0}'.format(axis_type))
    name_elem = ET.Element('name')
    name_elem.text = name
    axis_elem.append(name_elem)
    values_elem = ET.Element('values')
    axis_elem.append(values_elem)
    for val in values:
        val_elem = ET.Element('string')
        val_elem.text = str(val)
        values_elem.append(val_elem)
    return axis_elem


def remove_child(root, tag):
    """
    ElementTree helper function that removes the first child with the
    given name from an element.

    Parameters
    ----------
    root : ElementTree.Element

    tag : str
        The name of the child to remove from `root`.
    """
    for child in root:
        if child.tag == tag:
            root.remove(child)
            break


def update_build_config(xml):
    """
    Updates a multiconfig build config.xml file to include all of the
    Python and Numpy combinations in the configuration.

    Specifically, this updates the axes of the build matrix, and
    updates the "combination filter" which specifies which members of
    the axes are valid.

    The XML tree is updated in-place.

    Parameters
    ----------
    xml : ElementTree.Element
    """
    python_versions = sorted(config.versions.keys())
    numpy_versions = set()
    for numpys in config.versions.values():
        numpy_versions.update(numpys)
    numpy_versions.remove('dev')
    numpy_versions = sorted(list(numpy_versions))
    combos = []
    for python, numpys in config.versions.items():
        for numpy in numpys:
            if numpy == 'dev':
                continue
            combos.append('(PYTHON_VER == "{0}" && NUMPY_VER == "{1}")'.format(
                python, numpy))
    combos = "({0})".format(" || ".join(combos))

    root = xml.getroot()

    remove_child(root, 'axes')
    axes = ET.Element('axes')
    axes.extend([
        make_axis('TextAxis', 'PYTHON_VER', python_versions),
        make_axis('TextAxis', 'NUMPY_VER', numpy_versions),
        make_axis('LabelAxis', 'PLATFORM', ['debian6'])
        ])
    root.append(axes)

    remove_child(root, "combinationFilter")
    combinationFilter_elem = ET.Element("combinationFilter")
    combinationFilter_elem.text = combos
    root.append(combinationFilter_elem)


def update_build_configs(username, password, jobs):
    """
    Updates all build configs that should be updated.
    """
    for job in jobs:
        if re.match(config.multiconfig_build_regex, job['name']):
            print "Updating {0}".format(job['name'])

            url = fix_url(job['url'] + 'config.xml')

            r = requests.get(
                url, auth=(username, password), stream=True)
            xml = ET.parse(r.raw)

            update_build_config(xml)
            new_xml = ET.tostring(xml.getroot(), encoding='utf-8')

            r = requests.post(
                url, data=new_xml,
                auth=(username, password))


def get_name_and_password():
    """
    Gets a username and password from the console.
    """
    import getpass
    default_username = getpass.getuser()
    print "ShiningPanda username [{0}]:".format(default_username),
    username = raw_input()
    if username.strip() == '':
        username = default_username
    password = getpass.getpass()
    return username, password


def main(username, password):
    build_list = get_build_list()
    update_build_configs(username, password, build_list['jobs'])


if __name__ == '__main__':
    username, password = get_name_and_password()
    main(username, password)
