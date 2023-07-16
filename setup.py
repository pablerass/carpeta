#!/usr/bin/env python3
from setuptools import setup


setup(
    name='carpeta',
    version='0.0.0a0',
    description="A tool to create print and play card games",
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Games/Entertainment :: Board Games',
        'Typing :: Typed'
    ],
    keywords='PnP card board game print',
    author='Pablo Muñoz',
    author_email='pablerass@gmail.com',
    url='https://github.com/pablerass/carpeta',
    license='LGPLv3',
    entry_points={
        'console_scripts': [
            'carturli=carpeta.__main__:main',
        ],
    },
    packages=['carpeta'],
    install_requires=[line for line in open('requirements.txt')],
    python_requires='>=3.10'
)