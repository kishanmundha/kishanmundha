#!/usr/bin/env python3
"""
ANSI terminal output -> animated terminal-window SVG.

Timing is inferred from the text itself:
  · a line starting with the prompt glyph is typed character by character
  · a line containing a check mark reveals its result tail a beat later
  · everything else fades in on a short beat
"""
import re, sys, html

THEMES = {
    "dark":  dict(bg="#0E1117", chrome="#171B24", dot="#2C3242", border="#1D2330",
                  default="#C3C8D6",
                  m={"97": "#E9EBF3", "38;5;245": "#8B91A4", "38;5;240": "#5A6072",
                     "38;5;179": "#E0A458", "38;5;79": "#4FC3B0"}),
    "light": dict(bg="#FFFFFF", chrome="#F1F3F7", dot="#D3D8E2", border="#DFE3EB",
                  default="#3B4256",
                  m={"97": "#14162B", "38;5;245": "#6E7490", "38;5;240": "#A2A8B8",
                     "38;5;179": "#9C6212", "38;5;79": "#0F7365"}),
}

FONT, CH, LH = 13.6, 8.16, 19.7
PADY, BAR = 16, 34
TYPE, BEAT, RESULT_LAG = 0.019, 0.115, 0.34
PROMPT, CHECK = "\u276f", "\u2713"
TOKEN = re.compile(r"\x1b\[([0-9;]*)m")


def parse(line, theme):
    """-> [(text, color, bold, start_col)]"""
    segs, col, color, bold, pos = [], 0, theme["default"], False, 0

    def push(text):
        # Split on runs of whitespace and pin each chunk to its own column, so
        # alignment never depends on the renderer preserving spaces.
        nonlocal col
        for chunk in re.split(r"(\s{2,})", text):
            if not chunk:
                continue
            if chunk.strip():
                lead = len(chunk) - len(chunk.lstrip(" "))
                stripped = chunk.strip(" ")
                segs.append((stripped, color, bold, col + lead))
            col += len(chunk)

    for m in TOKEN.finditer(line):
        push(line[pos:m.start()])
        code = m.group(1)
        if code in ("", "0"):
            color, bold = theme["default"], False
        elif code == "1":
            bold = True
        elif code in theme["m"]:
            color = theme["m"][code]
        pos = m.end()
    push(line[pos:])
    return segs


def build(lines, theme_name):
    t = THEMES[theme_name]
    cols = max((len(TOKEN.sub("", v))
                for l in lines for v in l.split("\r")), default=60) + 2
    PADX = 12 if cols <= 46 else 22
    width = int(PADX * 2 + CH * cols)
    height = int(BAR + PADY * 2 + LH * len(lines))

    body, clock = [], 0.25
    HOLD = 1.0
    for raw_line in lines:
        variants = raw_line.split("\r")
        for vi, raw in enumerate(variants[:-1]):
            for text, colr, bold, col in parse(raw, t):
                body.append(
                    f'<text x="{PADX + col * CH:.1f}" textLength="{len(text) * CH:.1f}" '
                    f'lengthAdjust="spacing" opacity="0" class="t tr{" b" if bold else ""}" '
                    f'fill="{colr}" xml:space="preserve" style="animation:'
                    f'in .18s ease-out {clock + vi * HOLD:.2f}s both,'
                    f'out .25s ease-in {clock + (vi + 1) * HOLD:.2f}s forwards">'
                    f'{html.escape(text)}</text>')
        clock += HOLD * (len(variants) - 1)
        raw = variants[-1]
        plain = TOKEN.sub("", raw)
        stripped = plain.lstrip()
        typed = stripped.startswith(PROMPT)
        check_col = plain.find(CHECK)

        for text, colr, bold, col in parse(raw, t):
            cls = "b" if bold else ""
            if typed:
                for i, chn in enumerate(text):
                    if chn == " ":
                        continue
                    body.append(
                        (f'<text x="{PADX + (col + i) * CH:.1f}" class="t ln {cls}" '
                         f'fill="{colr}" textLength="{CH:.1f}" lengthAdjust="spacing" '
                         f'xml:space="preserve" style="animation-delay:{clock + (col + i) * TYPE:.3f}s">'
                         f'{html.escape(chn)}</text>'))
            else:
                lag = RESULT_LAG if (check_col >= 0 and col >= check_col) else 0
                body.append(
                    (f'<text x="{PADX + col * CH:.1f}" textLength="{len(text) * CH:.1f}" '
                     f'lengthAdjust="spacing" class="t ln {cls}" fill="{colr}" '
                     f'xml:space="preserve" style="animation-delay:{clock + lag:.3f}s">'
                     f'{html.escape(text)}</text>'))
        # each fragment above needs its line's y; injected below
        body.append(("__NEWLINE__",))
        clock += (len(plain) * TYPE + 0.3) if typed else (0.05 if not plain.strip() else BEAT)

    # assign y per line
    rendered, y = [], BAR + PADY + 14
    for item in body:
        if item[0] == "__NEWLINE__":
            y += LH
            continue
        rendered.append(item.replace('class="t', f'y="{y:.0f}" class="t', 1))

    css = f"""
    .t{{font-family:ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,
        'Liberation Mono',monospace;font-size:{FONT}px;white-space:pre}}
    .b{{font-weight:700}}
    .ln{{animation:in .18s ease-out both}}
    @keyframes in{{from{{opacity:0}}to{{opacity:1}}}}
    @keyframes out{{to{{opacity:0}}}}
    @media (prefers-reduced-motion:reduce){{
      .ln{{animation:none;opacity:1}}
      .t{{animation:none!important;opacity:1}} .tr{{display:none}}
    }}
    """

    return "".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" '
        f'aria-label="Terminal session introducing Kishan Mundha">',
        f'<style>{css}</style>',
        f'<rect width="{width}" height="{height}" rx="10" fill="{t["bg"]}" '
        f'stroke="{t["border"]}"/>',
        f'<path d="M0 10a10 10 0 0 1 10-10h{width - 20}a10 10 0 0 1 10 10v{BAR - 10}H0Z" '
        f'fill="{t["chrome"]}"/>',
        "".join(f'<circle cx="{cx}" cy="17" r="5" fill="{t["dot"]}"/>'
                for cx in (20, 38, 56)),
        "".join(rendered),
        '</svg>',
    ])


if __name__ == "__main__":
    # newline="" keeps \r intact — universal-newline mode would eat it, and \r
    # is exactly how a terminal signals "overwrite this line".
    src = [l for l in open(sys.argv[1], newline="").read().split("\n")]
    while src and not src[-1].strip():
        src.pop()
    while src and not src[0].strip():
        src.pop(0)
    for theme in THEMES:
        open(sys.argv[2].replace("THEME", theme), "w").write(build(src, theme))
        print("wrote", sys.argv[2].replace("THEME", theme))
