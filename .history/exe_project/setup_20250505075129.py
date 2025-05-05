#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
安装脚本
用于安装项目及其依赖
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ivas-ifm",
    version="1.1.0",
    description="Intelligent Video Acquisition System - Intelligent File Management",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="xiangye72",
    author_email='your.email@example.com',
    url='https://github.com/yourusername/ivas-ifm',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.1",
        "python-dotenv>=1.0.0",
        "pillow>=10.0.0",
        "pytube>=15.0.0",
        "fake-useragent>=1.1.1",
    ],
    entry_points={
        "console_scripts": [
            "ivas-ifm=src.main:main",
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Video',
        'Topic :: Internet :: WWW/HTTP',
    ],
    python_requires='>=3.8',
) 