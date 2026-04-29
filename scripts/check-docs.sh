#!/usr/bin/env sh
set -eu
for file in architecture roadmap installation deployment user-manual admin-manual developer-manual operations-manual security processing-pipeline api testing ai-development-rules maintenance troubleshooting tfm-technical-summary agentic-workflow-audit; do
  test -s "docs/$file.md" || { echo "Missing docs/$file.md"; exit 1; }
done
echo "Documentation OK"
