from os.path import dirname, join

from setuptools import setup, find_packages

project_dir = dirname(__file__)

from setuptools import setup, find_packages

setup(
    name='Checkjiuyue',
    version='0.1',
    description='setup',
    long_description='no description',
    license='GPL',
    install_requires=['scrapy', 'xlwt', 'xlrd'],
    author='yqq',
    author_email='yangqiqi@xxxx.com',
    platforms='any',
    url='git@git.dk.com:yangqiqi/Checkjiuyue.git',
    include_package_data=True,
    packages= find_packages(exclude=()),
    # find_packages(exclude=()),

)
