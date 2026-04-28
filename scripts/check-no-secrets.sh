#!/usr/bin/env sh
set -eu
if git ls-files | grep -E '(^|/)\.env$' >/dev/null; then
  echo "Do not track .env files"
  exit 1
fi
if git diff --cached --name-only | grep -E '(^|/)\.env$' >/dev/null; then
  echo "Do not commit .env files"
  exit 1
fi
if grep -R "BEGIN RSA PRIVATE KEY\|AWS_SECRET_ACCESS_KEY\|password *= *['\"][^'\"]" --exclude-dir=.git --exclude-dir=node_modules --exclude=.env --exclude=check-no-secrets.sh .; then
  echo "Potential secret found"
  exit 1
fi
echo "Secret check OK"
