#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

mkdir -p /var/run/celeryd
mkdir -p /var/log/celeryd

uv run celery -A app.celery.celery worker -E --loglevel=debug

tail -F /var/log/celeryd/*.log
