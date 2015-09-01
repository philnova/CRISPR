import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "CRISpy",
    version = "0.0.1",
    author = "Phil Nova",
    author_email = "pnova8@gmail.com",
    description = ("A pure Python module for designing guideRNA sequences for CRISPR gene editing"),
    license = "Open Source",
    keywords = "CRISPR gene RNA biology bioinformatics genetics",
    url = "",
    packages=['CRISpy', 'Tests'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
)