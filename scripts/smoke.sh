#!/usr/bin/env sh
set -eu
curl -fsS http://localhost/api/health
printf '\nSmoke OK\n'
