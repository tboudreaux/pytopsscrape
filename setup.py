import setuptools
from setuptools import Extension as pyExt
from numpy.distutils.core import Extension as npyExt
from numpy.distutils.core import setup
from distutils.command.install import install as DistutilsInstall
import os
import numpy
from sysconfig import get_paths


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# setuptools.setup(
setup(
        name="pyTOPSScrape",
        version="1.0",
        author="Thomas M. Boudreaux",
        author_email="thomas@boudreauxmail.com",
        description="Python bindings around TOPS webform for OPLIB opacities",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/tboudreaux/pytopsscrape",
        classifiers=[
            "Programming Language :: Python",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX :: Linux",
            "Topic :: Scientific/Engineering :: Astronomy",
        ],
        package_dir={"": "src"},
        packages=setuptools.find_packages(where="src"),
        include_package_data=True,
        package_data={
            'pyTOPSScrape.misc.dataFiles': ['*.npy'],
        },
        python_requires=">=3.8",
        install_requires=[
            'mechanize>=0.4.5',
            'numpy>=1.19.2',
            'scipy>=1.5.2',
            'importlib_resources>=5.2.0',
            'tqdm>=4.50.2',
            'beautifulsoup4>=4.9.3'
        ],
        scripts=[
            'src/pyTOPSScrape/scripts/generateTOPStables',
        ],
        # cmdclass={'install': extInstall},
        zip_safe=False
)
