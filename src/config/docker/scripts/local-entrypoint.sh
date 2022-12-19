#!/bin/bash
set -eu

cd /app;
poetry install

exec "$@"
