"""Used to setup package file creation.
"""
from codecs import open as codec_open
from os import path
from setuptools import setup #, find_packages

HERE = path.abspath(path.dirname(__file__))

with codec_open(path.join(HERE, "README.md"), encoding='utf-8') as f:
    LONG_DESC = f.read()

setup(
    name="wsdottraffic",
    version="4.0.0",
    description="Retrieves data from WSDOT Traffic API",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    url="https://github.com/WSDOT-GIS/wsdot-traffic-gp",
    author="Washington State Department of Transportation",
    author_email="WSDOTGISDevelopers@WSDOT.WA.GOV",
    license="Unlicense",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: Public Domain",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: GIS"
    ],
    # packages=find_packages(),
    packages=[
        "wsdottraffic",
        "wsdottraffic.classes",
        "wsdottraffic.scanweb"
    ],
    entry_points={
        'console_scripts': [
            'wsdottraffic = wsdottraffic.__main__:main'
        ]
    }
    # ,package_data={
    #     'wsdottraffic.gp': ["*.json"]
    # }
)
