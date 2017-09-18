"""Used to setup package file creation.
"""
from codecs import open as codec_open
from os import path
from setuptools import setup  # , find_packages

HERE = path.abspath(path.dirname(__file__))

with codec_open(path.join(HERE, "README.md"), encoding='utf-8') as f:
    LONG_DESC = f.read()

setup(
    name="wsdot.traffic",
    version="1.3.0",
    description="Retrieves data from WSDOT Traffic API",
    long_description=LONG_DESC,
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
    package_dir={
        'wsdot': 'src/wsdot'
    },
    packages=[
        'wsdot.traffic',
        'wsdot.traffic.gp'
    ],  # find_packages(),
    entry_points={
        'console_scripts': [
            'createwsdottrafficgdb = wsdot.traffic.gp.creategdb:main',
            'createwsdottraffictemplategdb = wsdot.traffic.gp.createtemplates:main',
            'dumpwsdottrafficjson = wsdot.traffic.dumpjson:main',
            'multipointtopoint = wsdot.traffic.gp.multipointtopoint:main',
            'zipgdb = wsdot.traffic.gp.zipgdb:main'
        ]
    },
    package_data={
        'wsdot.traffic.gp': ["*.json"]
    }
)
