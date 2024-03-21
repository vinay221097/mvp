#!/usr/bin/env sh

set -o errexit
set -o nounset

# We are using `gunicorn` for production, see:
# http://docs.gunicorn.org/en/stable/configure.html


gunicorn app:app \
    --workers=4 `# Sync worker settings` \
    --max-requests=2000 \
    --max-requests-jitter=400 \
    --timeout=180 \
    --bind='0.0.0.0:8000' `# Run Flask on 8000 port` \
    --chdir='/code'       `# Locations` \
    --log-file=- \
    --worker-tmp-dir='/dev/shm'
