#!/usr/bin/env sh
set -eu
for file in architecture roadmap installation deployment user-manual admin-manual developer-manual operations-manual security processing-pipeline api testing maintenance troubleshooting tfm-technical-summary; do
  test -s "docs/$file.md" || { echo "Missing docs/$file.md"; exit 1; }
done

if [ "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)" = "main" ]; then
  for path in .claude .opencode AGENTS.md CLAUDE.md opencode.json docs/ai-development-rules.md docs/agentic-workflow-audit.md; do
    test -z "$(git ls-files -- "$path")" || { echo "AI-only artifact must not be tracked on main: $path"; exit 1; }
  done

  if git grep -n -E '(AGENTS|CLAUDE|opencode|\.opencode|\.claude|ai-development-rules|agentic)' -- '*README.md'; then
    echo "README files on main must not mention AI-only artifacts"
    exit 1
  fi
fi

echo "Documentation OK"
