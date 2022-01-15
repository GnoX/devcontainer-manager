#!/usr/bin/env python
from pathlib import Path

from setuptools import setup

from devcontainer_manager import version

default_config = Path("devcontainer_manager/default_config.yaml").read_text()
readme = (
    Path("README.md.template")
    .read_text()
    .format(devcontainer_config=default_config)
)
Path("README.md").write_text(readme)

requirements = [
    req for req in Path("requirements.txt").read_text().splitlines() if req
]


setup(
    name="devcontainer_manager",
    version=version,
    author="gnox",
    url="https://github.com/gnox/devcontainer-manager",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    python_requires=">=3.6",
    license="MIT",
    entry_points={
        "console_scripts": [
            "devcontainer_manager = devcontainer_manager.__main__:main"
        ]
    },
    packages=["devcontainer_manager"],
    package_dir={"devcontainer_manager": "devcontainer_manager"},
    include_package_data=True,
)
