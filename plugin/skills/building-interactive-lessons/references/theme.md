# Theme: one accent colour, checked

A lesson's look comes from one accent colour and an optional font pair. The page works out every other colour from the accent when it loads, checks that each pair is readable, and keeps the default theme if the accent fails. Never write a colour by hand: not in the blueprint, not in a scene.

## The blueprint field

```yaml
theme:
  name: Deep teal          # what you call it when you show it to the author
  accent: "#0f766e"         # one hex colour, quoted
  fonts: schibsted-source   # optional: schibsted-source (default), plex, work-newsreader, noto-thai
  why: the author's team colour
```

No theme means **Ink blue** (`#1d5ca8`) with Schibsted Grotesk and Source Serif 4. Use `noto-thai` for a lesson in Thai.

## Two layers

- **The brand layer** follows the accent: the page background, surfaces and greys (each tinted slightly toward the accent), the accent itself, its soft fill, the text on it, and a 6-step shade ramp for data pictures (grid cells, bars).
- **The meaning layer** never changes: green for right, red for wrong, amber for "answer shown". Learners learn what these mean, so they look the same in every lesson.

## When an accent fails

The page refuses an accent that would blur meaning or hurt reading:

| Rule | Why |
|---|---|
| A 6-digit hex colour | the page reads only that form |
| Not too grey (OKLCH chroma at least 0.03) | a grey cannot act as an accent |
| At least 40° of hue from green (150°), red (27°) and amber (65°) | otherwise right, wrong or answer shown would blur with the brand |
| Some lightness of it reaches 4.5:1 on every background, light and dark | text in the accent must stay readable |

Most reds, oranges, browns, yellows and greens fail the hue rule. Blues, teals, purples and pinks pass.

## How the colours are worked out

All of this happens in the page; it is here so you can explain it.

1. Read the accent's lightness, chroma and hue in OKLCH (a colour space where equal lightness steps look equal). Chroma is capped at 0.16.
2. Make the greys from the accent's hue with very low chroma: background, surface, a second surface, code background, ink, muted text, lines.
3. Find the accent: in light mode, start at the accent's own lightness (at most 0.58) and darken in small steps until it reaches 4.5:1 on every background; in dark mode, start light (0.74) and lighten until it does.
4. Text on the accent is white or near-black, whichever contrasts more.
5. Build the shade ramp from almost the page colour toward the accent. It skips a middle band of lightness where neither dark nor light text reaches 4.5:1 on the cell, and each cell's number uses whichever text colour reads better.
6. Check every pair the page draws (body text on every surface, the accent, right and wrong on their soft fills, lines at 3:1, every ramp cell with its text), in light and dark.

## Showing it to the author (step 1, Discover)

- Draft one accent and its name: a colour they named, their organisation's colour (ask them to confirm it), the topic's world, or the default Ink blue.
- Check it against the four rules above. You can work out the hue and chroma with your own code tool; the full check happens when the page loads.
- If it fails, say which rule, and offer the nearest passing colour (move the hue past 40° from the meaning colour, or pick a stronger chroma).
- No organisation name or logo goes on the page without a yes.

## Checking it on the built page

Open the page. If the theme failed, the page shows the default Ink blue, writes the reasons to the console (`[lesson] theme not used…`), and puts them on `document.documentElement.dataset.themeProblem`. The layout reviewer reports either.
