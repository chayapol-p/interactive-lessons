#!/usr/bin/env python3
"""Turn a lesson's theme (one accent colour, an optional font pair) into the page's colour tokens, and check them.

A theme has two layers:
- the brand layer, which the learner's theme may change: the accent, the accent's soft fill, the greys (tinted
  toward the accent), and the shade ramp that data pictures use;
- the meaning layer, which never changes: right (good), wrong (bad) and answer-shown (mark). Learners learn what
  these colours mean, so they look the same in every lesson.

The derivation works in OKLCH (lightness, chroma, hue), so lightness steps look even. Every colour pair the page
uses
is contrast-checked in light and dark. A theme that cannot pass is refused; nothing is ever lowered to fit.

Used by build_page.py (to write the tokens) and check_blueprint.py (to refuse a bad theme early).
"""

import math
import re

# ===== Colour maths: sRGB hex <-> OKLCH =====

def hex_to_rgb(hex_colour):
    value = hex_colour.lstrip("#")
    return [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def rgb_to_hex(rgb):
    return "#" + "".join(f"{round(min(max(channel, 0), 1) * 255):02x}" for channel in rgb)


def to_linear(channel):
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def from_linear(channel):
    return 12.92 * channel if channel <= 0.0031308 else 1.055 * channel ** (1 / 2.4) - 0.055


def rgb_to_oklch(rgb):
    red, green, blue = (to_linear(channel) for channel in rgb)
    long_cone = (0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue) ** (1 / 3)
    medium_cone = (0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue) ** (1 / 3)
    short_cone = (0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue) ** (1 / 3)
    lightness = 0.2104542553 * long_cone + 0.7936177850 * medium_cone - 0.0040720468 * short_cone
    a_axis = 1.9779984951 * long_cone - 2.4285922050 * medium_cone + 0.4505937099 * short_cone
    b_axis = 0.0259040371 * long_cone + 0.7827717662 * medium_cone - 0.8086757660 * short_cone
    return lightness, math.hypot(a_axis, b_axis), math.degrees(math.atan2(b_axis, a_axis)) % 360


def oklch_to_rgb(lightness, chroma, hue):
    a_axis, b_axis = chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))
    long_cone = (lightness + 0.3963377774 * a_axis + 0.2158037573 * b_axis) ** 3
    medium_cone = (lightness - 0.1055613458 * a_axis - 0.0638541728 * b_axis) ** 3
    short_cone = (lightness - 0.0894841775 * a_axis - 1.2914855480 * b_axis) ** 3
    linear = [4.0767416621 * long_cone - 3.3077115913 * medium_cone + 0.2309699292 * short_cone,
              -1.2684380046 * long_cone + 2.6097574011 * medium_cone - 0.3413193965 * short_cone,
              -0.0041960863 * long_cone - 0.7034186147 * medium_cone + 1.7076147010 * short_cone]
    return [from_linear(channel) for channel in linear]


def in_gamut(rgb):
    return all(-0.0005 <= channel <= 1.0005 for channel in rgb)


def oklch_hex(lightness, chroma, hue):
    """The colour, with chroma lowered until it fits the screen's range."""
    while chroma > 0 and not in_gamut(oklch_to_rgb(lightness, chroma, hue)):
        chroma -= 0.002
    return rgb_to_hex(oklch_to_rgb(lightness, max(chroma, 0), hue))


def contrast(first_hex, second_hex):
    """WCAG contrast ratio of two colours."""
    def luminance(hex_colour):
        red, green, blue = (to_linear(channel) for channel in hex_to_rgb(hex_colour))
        return 0.2126 * red + 0.7152 * green + 0.0722 * blue
    brighter, darker = sorted([luminance(first_hex), luminance(second_hex)], reverse=True)
    return (brighter + 0.05) / (darker + 0.05)


def hue_distance(first, second):
    gap = abs(first - second) % 360
    return min(gap, 360 - gap)


# ===== The fixed meaning layer: the same in every lesson =====

MEANING = {
    "light": {"good": "#1c7445", "good-soft": "#dcefe3", "bad": "#ad2a20", "bad-soft": "#f7e0dd",
              "mark": "#8a4a05", "mark-soft": "#f6e8d6"},
    "dark": {"good": "#66c690", "good-soft": "#173225", "bad": "#f08b80", "bad-soft": "#3d1e1b",
             "mark": "#e8a250", "mark-soft": "#3a2a17"},
}
MEANING_HUES = {"good": 150, "bad": 27, "answer shown (amber)": 65}
SMALLEST_HUE_GAP = 40          # an accent this close to a meaning colour would blur right, wrong or answer shown
SMALLEST_ACCENT_CHROMA = 0.03  # greyer than this cannot act as an accent
DEFAULT_THEME = {"name": "Ink blue", "accent": "#1d5ca8"}

# Font pairs from Google Fonts, each tested in the template: (interface face, reading face, the Google Fonts query)
FONT_PAIRS = {
    "schibsted-source": ("Schibsted Grotesk", "Source Serif 4",
                         "family=Schibsted+Grotesk:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600"),
    "plex": ("IBM Plex Sans", "IBM Plex Serif", "family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:wght@400;600"),
    "work-newsreader": ("Work Sans", "Newsreader", "family=Work+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,600"),
    "noto-thai": ("Noto Sans Thai", "Noto Serif Thai", "family=Noto+Sans+Thai:wght@400;500;600;700&family=Noto+Serif+Thai:wght@400;600"),
}
DEFAULT_FONTS = "schibsted-source"
THEME_KEYS = {"name", "accent", "fonts", "why"}
RAMP_STEPS = 6


# ===== Derivation: one accent -> every brand token, light and dark =====

def lightest_passing(hue, chroma, start, step, backgrounds, ratio, stop):
    """Walk lightness from `start` by `step` until the colour reaches `ratio` on every background."""
    lightness = start
    while (step < 0 and lightness >= stop) or (step > 0 and lightness <= stop):
        colour = oklch_hex(lightness, chroma, hue)
        if all(contrast(colour, background) >= ratio for background in backgrounds):
            return colour
        lightness += step
    return None


def derive_tokens(theme):
    """The brand tokens for light and dark, or raise ValueError saying why the theme cannot work."""
    accent = str(theme.get("accent", ""))
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
        raise ValueError(f"accent must be a colour like #1d5ca8, not '{accent}'")
    seed_lightness, seed_chroma, hue = rgb_to_oklch(hex_to_rgb(accent))
    if seed_chroma < SMALLEST_ACCENT_CHROMA:
        raise ValueError(f"accent {accent} is too grey to act as an accent; pick a stronger colour")
    for meaning, meaning_hue in MEANING_HUES.items():
        if hue_distance(hue, meaning_hue) < SMALLEST_HUE_GAP:
            raise ValueError(f"accent {accent} is too close in hue to the {meaning} colour, so right, wrong or "
                             "answer shown would blur; pick another colour, or use the default")
    chroma = min(seed_chroma, 0.16)

    tokens = {}
    for mode in ("light", "dark"):
        light = mode == "light"
        tint = 0.008
        neutral = (lambda lightness_value, chroma_value=tint: oklch_hex(lightness_value, chroma_value, hue))
        mode_tokens = {
            "bg": neutral(0.975 if light else 0.17), "surface": neutral(0.995 if light else 0.21, 0.004),
            "surface-2": neutral(0.945 if light else 0.25), "code-bg": neutral(0.955 if light else 0.145),
            "ink": neutral(0.22 if light else 0.93, 0.012), "muted": neutral(0.48 if light else 0.74, 0.015),
            "line": neutral(0.89 if light else 0.32), "line-strong": neutral(0.62 if light else 0.52, 0.012),
            "dim": neutral(0.70 if light else 0.46, 0.01),
        }
        mode_tokens["accent-soft"] = oklch_hex(0.935 if light else 0.30, 0.04 if light else 0.05, hue)
        backgrounds = [mode_tokens["bg"], mode_tokens["surface"], mode_tokens["surface-2"], mode_tokens["accent-soft"]]
        if light:
            accent_colour = lightest_passing(hue, chroma, min(seed_lightness, 0.58), -0.02, backgrounds, 4.5, 0.25)
        else:
            accent_colour = lightest_passing(hue, min(chroma, 0.13), 0.74, 0.02, backgrounds, 4.5, 0.92)
        if accent_colour is None:
            raise ValueError(f"no lightness of {accent} reads well on the {mode} background")
        mode_tokens["accent"] = accent_colour
        white, near_black = "#ffffff", mode_tokens["ink"] if not light else "#0d1117"
        mode_tokens["on-accent"] = max([white, near_black if light else oklch_hex(0.17, 0.02, hue)],
                                       key=lambda text: contrast(text, accent_colour))
        # The shade ramp for data pictures: steps from almost the page toward the accent. The lightness band in the
        # middle (about 0.56 to 0.68) is skipped, because there neither dark nor light text reaches 4.5:1 on the cell.
        accent_lightness = rgb_to_oklch(hex_to_rgb(accent_colour))[0]
        ramp_lightness = ([0.955, 0.89, 0.82, 0.74, 0.52, min(accent_lightness, 0.44)] if light
                          else [0.27, 0.33, 0.40, 0.47, 0.74, 0.84])
        for step, step_lightness in enumerate(ramp_lightness):
            share = step / (RAMP_STEPS - 1)
            cell = oklch_hex(step_lightness, chroma * (0.25 + 0.75 * share), hue)
            mode_tokens[f"ramp-{step}"] = cell
            mode_tokens[f"ramp-text-{step}"] = max([mode_tokens["ink"], mode_tokens["surface"]], key=lambda text: contrast(text, cell))
        mode_tokens.update(MEANING[mode])
        tokens[mode] = mode_tokens
    return tokens


# Every pair the page draws, with the ratio it needs. (text colour, background, ratio)
CONTRAST_PAIRS = (
    [("ink", background, 4.5) for background in ("bg", "surface", "surface-2", "code-bg", "accent-soft", "mark-soft", "good-soft", "bad-soft")]
    + [("muted", background, 4.5) for background in ("bg", "surface", "surface-2")]
    + [(colour, background, 4.5) for colour in ("accent", "good", "bad") for background in ("bg", "surface")]
    + [("mark", "mark-soft", 4.5), ("mark", "surface", 4.5), ("good", "good-soft", 4.5), ("bad", "bad-soft", 4.5),
       ("on-accent", "accent", 4.5), ("accent", "accent-soft", 4.5)]
    + [("line-strong", background, 3.0) for background in ("bg", "surface", "code-bg")]
    + [("accent", "code-bg", 3.0)]
    + [(f"ramp-text-{step}", f"ramp-{step}", 4.5) for step in range(RAMP_STEPS)]
)


def check_tokens(tokens):
    """Every failing pair, as readable lines. Empty means the theme passes."""
    failures = []
    for mode, mode_tokens in tokens.items():
        for text, background, ratio in CONTRAST_PAIRS:
            measured = contrast(mode_tokens[text], mode_tokens[background])
            if measured < ratio:
                failures.append(f"{mode}: {text} on {background} is {measured:.2f}:1, needs {ratio}:1")
        ramp = [rgb_to_oklch(hex_to_rgb(mode_tokens[f"ramp-{step}"]))[0] for step in range(RAMP_STEPS)]
        steps_in_order = all(a > b for a, b in zip(ramp, ramp[1:])) if mode == "light" else all(a < b for a, b in zip(ramp, ramp[1:]))
        if not steps_in_order:
            failures.append(f"{mode}: the shade ramp does not get stronger step by step")
    return failures


def theme_problems(theme):
    """Why a blueprint's theme field cannot be used, as readable lines. Empty means it is fine."""
    if theme is None:
        return []
    if not isinstance(theme, dict):
        return ["theme must be a mapping with accent (and optional name, fonts, why)"]
    problems = [f"theme has an unknown field '{key}' (allowed: {', '.join(sorted(THEME_KEYS))})" for key in theme if key not in THEME_KEYS]
    if "accent" not in theme:
        problems.append("theme needs accent: one colour like #1d5ca8")
    if theme.get("fonts", DEFAULT_FONTS) not in FONT_PAIRS:
        problems.append(f"theme fonts must be one of: {', '.join(FONT_PAIRS)}")
    if problems:
        return problems
    try:
        tokens = derive_tokens(theme)
    except ValueError as reason:
        return [str(reason)]
    return check_tokens(tokens)


def css_for(theme):
    """The token CSS for the page: light on :root, dark for the system setting and for an explicit dark choice."""
    tokens = derive_tokens(theme or DEFAULT_THEME)
    fonts = FONT_PAIRS[(theme or {}).get("fonts", DEFAULT_FONTS)]
    fixed = (f'  --font-ui: "{fonts[0]}", "Helvetica Neue", Arial, sans-serif;\n'
             f'  --font-read: "{fonts[1]}", Georgia, "Times New Roman", serif;\n')

    def block(mode):
        return "".join(f"  --{name}: {value};\n" for name, value in tokens[mode].items())
    dark = block("dark") + "  color-scheme: dark;\n"
    return (f":root {{\n{block('light')}{fixed}}}\n"
            f"@media (prefers-color-scheme: dark) {{\n  :root:not([data-theme=\"light\"]) {{\n{dark}  }}\n}}\n"
            f":root[data-theme=\"dark\"] {{\n{dark}}}\n"), fonts[2]


def adjustment_note(theme):
    """What the build changed from the seed, so the learner sees the colour actually used."""
    tokens = derive_tokens(theme)
    seed = theme["accent"].lower()
    light, dark = tokens["light"]["accent"], tokens["dark"]["accent"]
    if seed == light:
        return f"accent {seed} is used as given in light mode; dark mode uses {dark}"
    return f"accent {seed} became {light} in light mode and {dark} in dark mode, so text stays readable"


if __name__ == "__main__":
    import sys
    for seed in sys.argv[1:] or [DEFAULT_THEME["accent"]]:
        problems = theme_problems({"accent": seed})
        print(seed, "->", "passes" if not problems else problems)
        if not problems:
            print("  ", adjustment_note({"accent": seed}))
