#!/usr/bin/env bash

CWD=$(readlink -e "$(dirname "$0")")
cd $CWD/.. || exit $?

DOCKER_BUILDKIT=1 docker build -f .devcontainer/devcontainer.Dockerfile \
    --ssh default \
    -t {{ cookiecutter.devcontainer.image }} . || exit $?
