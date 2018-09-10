# -*- Coding:utf-8 -*-
"""

"""
import os
import re
import codecs
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()


def find_version():
    here = os.path.abspath(os.path.dirname(__file__))
    there = os.path.join(here, 'shell_op', '__init__.py')

    version_file = codecs.open(there, 'r').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)

    else:
        raise RuntimeError("Unable to find version string.")


__version__ = find_version()

setup(
    name='shell-op',
    version=__version__,
    install_requires=REQUIRED,
    packages=find_packages(),
    py_modules=['op'],
    include_package_data=True,
    license='BSD License',
    description='A pure python shell operation utils support undo and redo',
    long_description=README,
    url='https://github.com/minghu6/shell-op',
    author='minghu6',
    author_email='a19678zy@163.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
