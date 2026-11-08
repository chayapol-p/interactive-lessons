#!/usr/bin/env python3
"""
Build the plugin icon in the README's marked-worksheet style: a filled-in blank on ruled paper,
marked right in red pen, with the tick breaking out of the box.

The icon follows icon rules, not README-picture rules: one idea, few shapes, bold strokes,
quiet paper, square corners (the marketplace rounds them), and it must still read at 16 px.

  Input:  nothing; the icon is drawn from the data in this file
  Output: <output folder>/icon.html, one 1024 x 1024 <svg>
          (export it to .claude-plugin/icon.png with readme-kit's export_png.py, or any
          headless browser screenshot of the <svg> at 1024 px)

Run: python3 docs/diagram/build_icon.py docs/diagram
"""

import sys
from pathlib import Path

# Constants
ICON_SIZE = 1024
RULE_SPACING = 205                     # four quiet rules: texture, never competing with the mark
MARGIN_X = 168                         # where the paper's margin line runs

## The same light colours as the README pictures, by role
PALETTE = {"ground": "#fbf8ef", "rule": "#c9d8ea", "margin": "#e6a5a0",
           "panel": "#ffffff", "accent": "#1d5ca8", "note": "#c0392b"}

## The answer box and the tick, placed so the pair sits centred on the canvas
BOX_LEFT, BOX_TOP, BOX_WIDTH, BOX_HEIGHT = 300, 400, 440, 260
TICK_START_X, TICK_START_Y, TICK_SCALE = 430, 560, 1.45


# Paint the paper: ground, ruled lines and the margin line.
def worksheet_paper():
    rules = "".join(f'<path d="M0 {y} H{ICON_SIZE}" stroke="{PALETTE["rule"]}" stroke-width="10"/>'
                    for y in range(RULE_SPACING, ICON_SIZE, RULE_SPACING))
    return (f'<rect width="{ICON_SIZE}" height="{ICON_SIZE}" fill="{PALETTE["ground"]}"/>{rules}'
            f'<path d="M{MARGIN_X} 0 V{ICON_SIZE}" stroke="{PALETTE["margin"]}" stroke-width="9"/>')


# Draw the blank the learner filled in: a blue-edged answer box.
def answer_box():
    return (f'<rect x="{BOX_LEFT}" y="{BOX_TOP}" width="{BOX_WIDTH}" height="{BOX_HEIGHT}" rx="34" '
            f'fill="{PALETTE["panel"]}" stroke="{PALETTE["accent"]}" stroke-width="40"/>')


# Draw the teacher's red-pen tick: a short stroke down, then a long stroke up and out of the box.
def pen_tick():
    return (f'<path d="M{TICK_START_X},{TICK_START_Y} l{70 * TICK_SCALE},{80 * TICK_SCALE} '
            f'l{150 * TICK_SCALE},{-210 * TICK_SCALE}" fill="none" stroke="{PALETTE["note"]}" '
            f'stroke-width="58" stroke-linecap="round" stroke-linejoin="round"/>')


# Wrap the icon in an accessible <svg> on its own page.
def icon_page():
    svg = (f'<svg width="{ICON_SIZE}" height="{ICON_SIZE}" viewBox="0 0 {ICON_SIZE} {ICON_SIZE}" '
           f'xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="icon-title">'
           f'<title id="icon-title">Interactive Lessons icon: a filled-in blank, marked right in red pen</title>'
           f'{worksheet_paper()}{answer_box()}{pen_tick()}</svg>')
    return f'<!DOCTYPE html>\n<html lang="en">\n<head><meta charset="UTF-8"><style>body {{ margin: 0; }}</style></head>\n<body>\n{svg}\n</body>\n</html>\n'


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("build_icon: usage: build_icon.py <output folder>")
    output_file = Path(sys.argv[1]) / "icon.html"
    output_file.write_text(icon_page(), encoding="utf-8")
    print(f"build_icon: wrote {output_file}")
