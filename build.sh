#!/usr/bin/env bash
# Regenerate all four header variants. Never edit the SVGs by hand.
#
#   ./build.sh           frameless, transparent background (what's committed)
#   ./build.sh --frame   terminal window with background, border and title bar
set -euo pipefail
mkdir -p assets
FORCE_COLOR=1 node bin/about.js          > /tmp/about-wide.ansi
FORCE_COLOR=1 node bin/about.js --narrow > /tmp/about-narrow.ansi
python3 tools/ansi2term.py "$@" /tmp/about-wide.ansi   assets/about-wide-THEME.svg
python3 tools/ansi2term.py "$@" /tmp/about-narrow.ansi assets/about-narrow-THEME.svg

# npm's README page can't pick a theme-matched image (it wraps <img> in a link,
# which breaks <picture>), so npm gets one framed image that follows the system
# theme. Its own background keeps it readable when npm's theme toggle disagrees.
python3 tools/ansi2term.py --frame --theme auto /tmp/about-wide.ansi assets/about-wide-framed-THEME.svg
