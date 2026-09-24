#!/usr/bin/env bash
# Regenerate all four header variants. Never edit the SVGs by hand.
set -euo pipefail
mkdir -p assets
FORCE_COLOR=1 node bin/about.js          > /tmp/about-wide.ansi
FORCE_COLOR=1 node bin/about.js --narrow > /tmp/about-narrow.ansi
python3 tools/ansi2term.py /tmp/about-wide.ansi   assets/about-wide-THEME.svg
python3 tools/ansi2term.py /tmp/about-narrow.ansi assets/about-narrow-THEME.svg
