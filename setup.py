#!/usr/bin/env python3
from setuptools import setup


setup(
    name='carpeta',
    version='v0.1.0a1',
    description="A library to trace image changes in its processing",
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Debuggers',
        'Typing :: Typed'
    ],
    keywords='logging tracing image processing',
    author='Pablo Muñoz',
    author_email='pablerass@gmail.com',
    url='https://github.com/pablerass/carpeta',
    license='LGPLv3',
    packages=['carpeta'],
    install_requires=[line for line in open('requirements.txt')],
    python_requires='>=3.10'
)