# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name = "CRISpy",
    version = "0.0.1",
    author = "Phil Nova",
    author_email = "pnova8@gmail.com",
    description = ("A pure Python module for designing guideRNA sequences for CRISPR gene editing"),
    license = "CreativeCommons",
    keywords = "CRISPR gene RNA biology bioinformatics genetics",
    url = "https://github.com/philnova/CRISPR",
    packages=find_packages(),
    install_requires=['multiprocessing'],
    extras_require={
        'tests': ['coverage'],
    },
    classifiers=["Development Status :: 3 - Alpha",
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7'
    'Intended Audience :: Biologists',]
)