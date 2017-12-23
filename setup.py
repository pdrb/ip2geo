from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


version = '0.1'


setup(
    name='ip2geo',
    version=version,
    description='Get geolocation from IP address or hostname',
    long_description=long_description,
    author='Pedro Buteri Gonring',
    author_email='pedro@bigode.net',
    url='https://github.com/pdrb/ip2geo',
    license='MIT',
    classifiers=[],
    keywords='ip geo geolocation ip-api.com freegeoip.net ipinfo.io',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    entry_points={
        'console_scripts': ['ip2geo=ip2geo.ip2geo:cli'],
    },
)
