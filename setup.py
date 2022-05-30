#!/usr/bin/env python
from pathlib import Path

from setuptools import find_packages, setup

from devcontainer_manager import __version__ as version

requirements = [req for req in Path("requirements.txt").read_text().splitlines() if req]
dev_requirements = [
    req
    for req in Path("requirements-dev.txt").read_text().splitlines()
    if req and not req.startswith("-")
]

setup(
    name="devcontainer_manager",
    version=version,
    author="gnox",
    url="https://github.com/gnox/devcontainer-manager",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=requirements,
    python_requires=">=3.6",
    extras_require={"dev": dev_requirements},
    license="MIT",
    entry_points={
        "console_scripts": ["devcontainer_manager = devcontainer_manager.__main__:main"]
    },
    packages=find_packages(),
    package_dir={"devcontainer_manager": "devcontainer_manager"},
    include_package_data=True,
)
