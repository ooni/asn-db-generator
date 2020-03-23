# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="ASNdbgenerator",
    packages=["mmdb",],
    entry_points={"console_scripts": ["asndbgenerator = asndbgenerator:main",]},
    description="Generate Maxmind DB compatible database",
    long_description="",
    license="",
    python_requires=">=3.7",
    install_requires=["setuptools",],
    tests_require=["pytest"],
    package_data={"asndbgenerator": ["tests/data/*"]},
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    version="0.0.1",
)
