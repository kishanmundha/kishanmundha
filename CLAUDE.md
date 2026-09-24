# CLAUDE.md

@AGENTS.md

## Claude-specific notes

- After any edit to `bin/about.js` or `tools/ansi2term.py`, run `./build.sh`, then
  check `git status` and confirm that only the SVGs you expected changed.
- `build.sh` writes intermediate files to `/tmp/about-*.ansi`. They are safe to ignore.
- Don't hand-edit anything in `assets/`. Change the generator and rebuild instead.
