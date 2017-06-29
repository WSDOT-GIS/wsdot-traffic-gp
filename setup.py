"""Used to setup package file creation.
"""
from setuptools import setup, find_packages
from codecs import open as codec_open
from os import path

HERE = path.abspath(path.dirname(__file__))

with codec_open(path.join(HERE, "README.md"), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="wsdottraffic",
    version="1.0.0",
    description="Retrieves data from WSDOT Traffic API",
    long_description=long_description,
    url="https://github.com/WSDOT-GIS/wsdot-traffic-gp",
    author="Washington State Department of Transportation",
    license="Unlicense",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: Public Domain",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: GIS"
    ],

    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'createwsdottrafficgdb = creategdb:main',
            'dumpwsdottrafficjson = dumpjson:main'
        ]
    },
    package_data={
        'wsdottraffic.gp': ["*.json"]
    }
)
