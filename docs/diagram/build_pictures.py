#!/usr/bin/env python3
"""
Build the README's pictures in the marked-worksheet style: ruled school paper, a margin line,
and red-pen notes. Paper by day, slate by night.

It draws each picture in a light and a dark variant:
  banner        the project name on a worksheet header
  tutorial-vs-lesson  a tutorial page against a lesson page
  how-it-works  the six steps the skill walks through
  strip         a thin ruled divider for above each README section

  Input:  nothing; every picture is drawn from the data in this file
  Output: <output folder>/<picture>.html and <picture>-dark.html, one <svg> per page
          (export each page to PNG with readme-kit's export_png.py)

Run: python3 docs/diagram/build_pictures.py docs/diagram
Fonts: the .woff2 files and their licences sit in docs/diagram/fonts/.
"""

import sys
from pathlib import Path

# Constants
## The project and the picture set
PROJECT_NAME = "Interactive Lessons"
CANVAS_WIDTH = 960                     # every picture shares this width; it exports to 1920 pixels
RULE_SPACING = 30                      # distance between the ruled lines of the paper
MARGIN_X = 44                          # where the paper's margin line runs

## Colours by role, light and dark. Drawing functions use these names, never colour codes.
LIGHT_PALETTE = {
    "ground": "#fbf8ef", "rule": "#c9d8ea", "margin": "#e6a5a0",
    "ink": "#22262b", "soft": "#6b6f74", "panel": "#ffffff",
    "accent": "#1d5ca8", "note": "#c0392b",
}
DARK_PALETTE = {
    "ground": "#1b2430", "rule": "#2c3a4a", "margin": "#7a3b3b",
    "ink": "#eef1ea", "soft": "#9fb0be", "panel": "#232e3b",
    "accent": "#8fb8ff", "note": "#ff8f7a",
}

## Fonts: a plain face for print, a hand face for red-pen notes
PRINT_FONT = "'Schibsted Grotesk', system-ui, sans-serif"
HAND_FONT = "'Caveat', cursive"
FONT_FILES = [
    ("Schibsted Grotesk", 400, "fonts/schibsted-grotesk-latin-400-normal.woff2"),
    ("Schibsted Grotesk", 700, "fonts/schibsted-grotesk-latin-700-normal.woff2"),
    ("Caveat", 700, "fonts/caveat-latin-700-normal.woff2"),
]


# ---- Text helpers ----

# Write printed words, such as a name or a label.
def print_text(colors, x, y, words, size=18, color_role="ink", weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" fill="{colors[color_role]}" font-size="{size}" font-weight="{weight}" '
            f'font-family="{PRINT_FONT}" text-anchor="{anchor}">{words}</text>')


# Write a red-pen note in the hand face.
def pen_text(colors, x, y, words, size=26, color_role="note", anchor="start"):
    return (f'<text x="{x}" y="{y}" fill="{colors[color_role]}" font-size="{size}" font-weight="700" '
            f'font-family="{HAND_FONT}" text-anchor="{anchor}">{words}</text>')


# ---- Line helpers ----

# Draw a right-angled connector through a list of (x, y) points, with a filled arrowhead pointing along the last piece.
def line_arrow(colors, points, color_role="ink", dashed=False):
    path = "M " + " L ".join(f"{x},{y}" for x, y in points)
    dash_pattern = ' stroke-dasharray="7,6"' if dashed else ""
    (from_x, from_y), (to_x, to_y) = points[-2], points[-1]
    if from_y == to_y:      # the last piece runs sideways
        direction = 1 if to_x > from_x else -1
        head = f"M{to_x},{to_y} l{-10 * direction},-6 v12 z"
    else:                   # the last piece runs up or down
        direction = 1 if to_y > from_y else -1
        head = f"M{to_x},{to_y} l-6,{-10 * direction} h12 z"
    return (f'<path d="{path}" fill="none" stroke="{colors[color_role]}" stroke-width="2"{dash_pattern}/>'
            f'<path d="{head}" fill="{colors[color_role]}"/>')


# A short curved pen stroke, the way a teacher points from a note to what it is about.
def pen_stroke(colors, x, y, width):
    return f'<path d="M{x},{y} q{width / 2},-16 {width},-4" fill="none" stroke="{colors["note"]}" stroke-width="2.5" stroke-linecap="round"/>'


# ---- Shape helpers ----

# Draw a box on the paper colour, so ruled lines and connectors behind it stay hidden.
def paper_box(colors, x, y, width, height, stroke_role="soft", dashed=False, corner=6):
    dash_pattern = ' stroke-dasharray="6,6"' if dashed else ""
    return (f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{corner}" fill="{colors["panel"]}" '
            f'stroke="{colors[stroke_role]}" stroke-width="{2 if stroke_role == "accent" else 1.4}"{dash_pattern}/>')


# Draw a step box: a number in the hand face, the step's name, and a short line under it.
def step_box(colors, x, y, number, name, label, focal=False):
    width, height = 236, 92
    return (paper_box(colors, x, y, width, height, "accent" if focal else "soft")
            + pen_text(colors, x + 18, y + 40, number, size=30, color_role="accent" if focal else "soft")
            + print_text(colors, x + 50, y + 38, name, size=21, weight=700, color_role="accent" if focal else "ink")
            + print_text(colors, x + 50, y + 66, label, size=15, color_role="soft"))


# ---- Sheet helpers: paper and the repeating mark ----

# Paint the paper: ground, ruled lines and the margin line.
def worksheet_paper(colors, height, slug):
    return (f'<defs><pattern id="{slug}-rules" width="{CANVAS_WIDTH}" height="{RULE_SPACING}" patternUnits="userSpaceOnUse">'
            f'<path d="M0 {RULE_SPACING - 0.5} H{CANVAS_WIDTH}" stroke="{colors["rule"]}" stroke-width="1"/></pattern></defs>'
            f'<rect width="{CANVAS_WIDTH}" height="{height}" fill="{colors["ground"]}"/>'
            f'<rect width="{CANVAS_WIDTH}" height="{height}" fill="url(#{slug}-rules)"/>'
            f'<path d="M{MARGIN_X} 0 V{height}" stroke="{colors["margin"]}" stroke-width="2"/>')


# Draw the repeating mark: a red-pen circle with the picture's lesson number, top right.
def lesson_mark(colors, number):
    center_x, center_y = CANVAS_WIDTH - 70, 62
    return (f'<circle cx="{center_x}" cy="{center_y}" r="36" fill="none" stroke="{colors["note"]}" stroke-width="2.5"/>'
            + pen_text(colors, center_x, center_y - 4, "Lesson", size=20, anchor="middle")
            + pen_text(colors, center_x, center_y + 20, str(number), size=24, anchor="middle"))


# ---- Picture: the banner ----

BANNER_HEIGHT = 180


# Draw the project name on a worksheet header, with the promise as a pen note.
def banner_svg(colors, slug):
    parts = [worksheet_paper(colors, BANNER_HEIGHT, slug),
             print_text(colors, 80, 92, PROJECT_NAME, size=52, weight=700),
             pen_text(colors, 82, 140, "any subject · every result is real", size=30),
             lesson_mark(colors, "✓")]
    return wrap_svg(slug, BANNER_HEIGHT, PROJECT_NAME,
                    "The project name written on a ruled worksheet, with a red-pen note: any subject, every result is real.",
                    "".join(parts))


# ---- Picture: a tutorial against a lesson ----

CONTRAST_HEIGHT = 470


# Draw the contrast: a page of tutorial text you only read, against a lesson moment where a wrong pick shows its result.
def tutorial_vs_lesson_svg(colors, slug):
    parts = [worksheet_paper(colors, CONTRAST_HEIGHT, slug)]

    # The tutorial: grey lines of text, read and forgotten
    parts.append(print_text(colors, 80, 96, "A tutorial", size=22, color_role="soft", weight=700))
    for row, width in enumerate([300, 330, 280, 320, 260, 310, 290, 200]):
        parts.append(f'<rect x="80" y="{128 + row * 30}" width="{width}" height="9" rx="4.5" fill="{colors["soft"]}" opacity="0.32"/>')
    parts.append(pen_text(colors, 230, 420, "read · nod · forget", size=28, color_role="soft", anchor="middle"))

    # The arrow between them
    parts.append(line_arrow(colors, [(436, 240), (520, 240)]))

    # The lesson: a wrong pick, where it really leads, and the teacher's note (the same words as the real lesson)
    parts.append(print_text(colors, 560, 96, "A lesson", size=22, color_role="accent", weight=700))
    parts.append(print_text(colors, 560, 136, "After the host opens door 3,", size=19))
    parts.append(print_text(colors, 560, 162, "door 2's chance of hiding the car is", size=19))
    parts.append(f'<rect x="560" y="176" width="112" height="40" rx="4" fill="{colors["panel"]}" stroke="{colors["note"]}" stroke-width="2.5"/>')
    parts.append(print_text(colors, 576, 203, "1 in 2  ✗", size=19, color_role="note", weight=700))
    parts.append(pen_stroke(colors, 684, 200, 34))
    parts.append(pen_text(colors, 726, 200, "see why ↓", size=27))
    parts.append(paper_box(colors, 560, 234, 340, 112, corner=8))
    parts.append(print_text(colors, 580, 264, "What this choice leads to", size=16, color_role="soft", weight=700))
    for row, line in enumerate(["1 in 2 would mean your door's chance", "grew from 1 in 3, but the host never", "touches your door. Door 2 holds 2 in 3."]):
        parts.append(print_text(colors, 580, 292 + row * 22, line, size=17))
    parts.append(pen_text(colors, 730, 420, "guess · pick · see why", size=28, color_role="accent", anchor="middle"))

    parts.append(lesson_mark(colors, 1))
    return wrap_svg(slug, CONTRAST_HEIGHT, "A tutorial against a lesson",
                    "Left, a tutorial: lines of text you read, nod at and forget. Right, a lesson: in the Monty Hall game the "
                    "learner says door 2's chance is 1 in 2, and sees why it is really 2 in 3.",
                    "".join(parts))


# ---- Picture: how it works ----

HOW_IT_WORKS_HEIGHT = 480
STEPS = [  # number, name, short line; the first row runs left to right, the second right to left
    ("1", "Discover", "who learns, and what"),
    ("2", "Verify", "real facts and results"),
    ("3", "Plan", "chapters, as data"),
    ("4", "Build", "fill the page template"),
    ("5", "Check", "scripts, then screenshots"),
    ("6", "Publish", "then revise from use"),
]
FOCAL_STEPS = {"Discover", "Check"}    # at most two accents per picture


# Draw the six steps in two rows, joined by right-angled arrows, with two red-pen notes.
def how_it_works_svg(colors, slug):
    parts = [worksheet_paper(colors, HOW_IT_WORKS_HEIGHT, slug)]
    box_width, box_height, gap = 236, 92, 48
    row_tops = [126, 306]
    first_left = 80
    lefts = [first_left + i * (box_width + gap) for i in range(3)]

    # Where each step sits: row 1 left to right, row 2 right to left, so the path turns down at the end of row 1
    places = [(lefts[0], row_tops[0]), (lefts[1], row_tops[0]), (lefts[2], row_tops[0]),
              (lefts[2], row_tops[1]), (lefts[1], row_tops[1]), (lefts[0], row_tops[1])]

    # Connectors first, so the boxes sit on top of them
    for i in range(2):
        start_x = places[i][0] + box_width
        middle_y = row_tops[0] + box_height // 2
        parts.append(line_arrow(colors, [(start_x, middle_y), (start_x + gap, middle_y)]))
    down_x = lefts[2] + box_width // 2
    parts.append(line_arrow(colors, [(down_x, row_tops[0] + box_height), (down_x, row_tops[1])]))
    for i in range(3, 5):
        start_x = places[i][0]
        middle_y = row_tops[1] + box_height // 2
        parts.append(line_arrow(colors, [(start_x, middle_y), (start_x - gap, middle_y)]))

    # The boxes
    for (number, name, label), (left, top) in zip(STEPS, places):
        parts.append(step_box(colors, left, top, number, name, label, focal=name in FOCAL_STEPS))

    # Red-pen notes, each right under the step it is about
    parts.append(pen_text(colors, lefts[0] + 8, row_tops[0] + box_height + 42, "you confirm what it assumed", size=25))
    parts.append(pen_text(colors, lefts[1] + 8, row_tops[1] + box_height + 42, "every result really ran", size=25))

    parts.append(lesson_mark(colors, 2))
    return wrap_svg(slug, HOW_IT_WORKS_HEIGHT, "How it works",
                    "Six steps: discover the learner, verify facts and results, plan chapters as data, build the page from a "
                    "template, check it with scripts and screenshots, publish and revise.",
                    "".join(parts))


# ---- Picture: the section strip ----

STRIP_HEIGHT = 36


# Draw a thin strip of ruled paper with the margin line, reused above every README section.
def strip_svg(colors, slug):
    parts = [f'<rect width="{CANVAS_WIDTH}" height="{STRIP_HEIGHT}" fill="{colors["ground"]}"/>',
             f'<path d="M0 {STRIP_HEIGHT // 2} H{CANVAS_WIDTH}" stroke="{colors["rule"]}" stroke-width="1.5"/>',
             f'<path d="M{MARGIN_X} 0 V{STRIP_HEIGHT}" stroke="{colors["margin"]}" stroke-width="2"/>']
    return wrap_svg(slug, STRIP_HEIGHT, "Section divider", "A thin strip of ruled paper between README sections.", "".join(parts))


# ---- Page wrapper ----

# Wrap drawn parts in an accessible <svg> with a title and a description.
def wrap_svg(slug, height, title, description, body):
    return (f'<svg viewBox="0 0 {CANVAS_WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-labelledby="{slug}-title {slug}-desc">'
            f'<title id="{slug}-title">{title}</title><desc id="{slug}-desc">{description}</desc>{body}</svg>')


# Put one picture on its own page, loading the bundled fonts by relative path.
def picture_page(colors, heading, svg):
    font_faces = "".join(f"@font-face {{ font-family: '{family}'; font-weight: {weight}; src: url('{path}') format('woff2'); }}\n    "
                         for family, weight, path in FONT_FILES)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{heading} · {PROJECT_NAME}</title>
  <style>
    {font_faces}body {{ margin: 0; padding: 2rem; background: {colors["ground"]}; }}
    svg {{ width: 100%; display: block; }}
  </style>
</head>
<body>
{svg}
</body>
</html>
"""


# ---- Write every picture, light and dark ----

PICTURES = [  # file name, page heading, drawing function
    ("banner", PROJECT_NAME, banner_svg),
    ("tutorial-vs-lesson", "A tutorial against a lesson", tutorial_vs_lesson_svg),
    ("how-it-works", "How it works", how_it_works_svg),
    ("strip", "Section divider", strip_svg),
]


# Write a light and a dark page for every picture into the output folder.
def write_all_pictures(output_folder: Path) -> None:
    output_folder.mkdir(parents=True, exist_ok=True)
    for suffix, colors in (("", LIGHT_PALETTE), ("-dark", DARK_PALETTE)):
        for file_name, heading, draw_picture in PICTURES:
            slug = f"{file_name}{suffix}"
            page_file = output_folder / f"{slug}.html"
            page_file.write_text(picture_page(colors, heading, draw_picture(colors, slug)), encoding="utf-8")
            print(f"build_pictures: wrote {page_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("build_pictures: usage: build_pictures.py <output folder>")
    write_all_pictures(Path(sys.argv[1]))
