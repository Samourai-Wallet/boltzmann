#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext as _build_ext

class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())

setup(
    name='boltzmann',
    packages=find_packages(),
    version='0.0.1',
    description='A python script computing the entropy of Bitcoin transactions and the linkability of their inputs and outputs',
    author='laurentmt',
    author_email='llll@lll.com',
    maintainer='laurentmt',
    url='https://www.github.com/LaurentMT/boltzmann',
    download_url='https://www.github.com/LaurentMT/boltzmann/tarball/0.0.1',
    keywords=['bitcoin', 'privacy'],
    classifiers=['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English', 'Programming Language :: Python :: 3.3',
                 'Topic :: Security'],
    cmdclass={'build_ext': build_ext},
    install_requires=[
        'numpy >= 1.8.0',
        'sortedcontainers',
        'python-bitcoinrpc'
    ]
)
