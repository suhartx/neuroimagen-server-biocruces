#!/usr/bin/env sh
set -eu
if find . -name .env -not -path './.git/*' | grep -q .; then
  echo "Do not commit .env files"
  exit 1
fi
if grep -R "BEGIN RSA PRIVATE KEY\|AWS_SECRET_ACCESS_KEY\|password *= *['\"][^'\"]" --exclude-dir=.git --exclude=check-no-secrets.sh .; then
  echo "Potential secret found"
  exit 1
fi
echo "Secret check OK"
