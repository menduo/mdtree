#!/usr/bin/env python
# encoding: utf-8
from setuptools import setup
import mdtree

repo_url = "https://github.com/menduo/mdtree"
packages = ["mdtree"]

setup(
    name="mdtree",
    version=mdtree.__version__,
    keywords=("markdown", "toc", "tree", "html"),
    description="Convert markdown to html with TOC(table of contents)",
    long_description="see more at:\n%s\n" % repo_url,
    license="MIT",
    url=repo_url,
    author="menduo",
    author_email="shimenduo@gmail.com",
    packages=packages,
    package_data={
        "mdtree": [
            "static/css/*.css",
            "static/js/*.js",
            "static/html/*.html",
        ]
    },
    scripts=["bin/mdtree"],
    platforms="any",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Filters",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    install_requires=["markdown", "pygments"],
)
