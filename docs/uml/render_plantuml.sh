#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
JAR="$ROOT/.tools/plantuml.jar"
if [[ ! -f "$JAR" ]]; then
  echo "plantuml.jar not present at $JAR — Mermaid Markdown remains the GitHub-visible source"
  echo "To enable SVG: mkdir -p docs/uml/.tools && download plantuml.jar there"
  exit 0
fi
mkdir -p "$ROOT/rendered"
java -jar "$JAR" -tsvg -o rendered "$ROOT"/*.puml 2>/dev/null || true
echo "rendered SVGs under docs/uml/rendered/ (if any .puml sources exist)"
