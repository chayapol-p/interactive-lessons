"""Record the README's feature pictures from a real build of the no-code Monty Hall example.

What it saves, in light and dark:
  ten-doors(-dark).gif     chapter 2's ten doors: you pick, the host opens 8 goat doors one at a time, one door is left
  field-guide(-dark).png   the field guide at the end: the big idea and one line per chapter (the score line hidden)

Usage (from the repo root):
    pip install pyyaml playwright pillow
    python3 docs/diagram/capture_feature_shots.py

Outside requests (web fonts) are refused, so the shots use the system fonts and repeat exactly.
"""

import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

# Constants
## Where things are
REPO = Path(__file__).resolve().parents[2]
SKILL = Path(os.environ.get("SKILL_FOLDER", REPO / "skills" / "building-interactive-lessons"))
IMAGES = REPO / "docs" / "images"

## The phone the shots are taken on
PHONE_VIEWPORT = {"width": 390, "height": 844}
SHOT_SCALE = 2

## The animation recording: how often a frame is taken, and how long each step is watched
FRAME_INTERVAL_MS = 120
STEP_RECORDING_MS = 2400
HOLD_FRAMES = 8                          # still frames at the start and on each step's end state, so a reader can look


# Build the example lesson with the skill's own build script, and return the page's path.
def build_example_page() -> Path:
    page_file = Path(tempfile.mkdtemp()) / "lesson.html"
    subprocess.run([sys.executable, str(SKILL / "scripts" / "build_page.py"),
                    str(SKILL / "assets" / "example-monty-blueprint.yaml"), "--out", str(page_file)],
                   check=True, capture_output=True)
    return page_file


# Open a fresh phone-sized tab in one colour theme, refusing every request that is not a local file.
def open_phone_tab(browser, theme: str):
    context = browser.new_context(viewport=PHONE_VIEWPORT, color_scheme=theme, device_scale_factor=SHOT_SCALE)
    context.route("**/*", lambda route: route.continue_() if route.request.url.startswith("file:") else route.abort())
    tab = context.new_page()
    return context, tab


# Take one screenshot of an element and return it as a picture.
def element_frame(element) -> Image.Image:
    return Image.open(io.BytesIO(element.screenshot())).convert("RGB")


# Record the ten-door animation: a still start, then each step as it plays, holding on each end state.
def record_ten_doors(tab, page_file: Path) -> list[Image.Image]:
    tab.goto(page_file.as_uri() + "#feel-it")
    tab.add_style_tag(content=".topbar { display: none !important; }")  # the sticky bar would cover the picture
    figure = tab.locator("#ten-doors")
    figure.scroll_into_view_if_needed()
    tab.wait_for_timeout(400)

    # The start: you have picked door 1
    frames = [element_frame(figure)] * HOLD_FRAMES

    # Each step plays its change one door at a time; watch it, then hold on where it ends
    for step_name in ["Host opens", "The offer"]:
        figure.get_by_role("button", name=step_name, exact=True).click()
        for _ in range(STEP_RECORDING_MS // FRAME_INTERVAL_MS):
            frames.append(element_frame(figure))
            tab.wait_for_timeout(FRAME_INTERVAL_MS)
        frames.extend([element_frame(figure)] * HOLD_FRAMES)
    return frames


# Save frames as a looping GIF, with one shared palette so the colours stay steady between frames.
def save_gif(frames: list[Image.Image], gif_file: Path) -> None:
    palette_source = frames[-1].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    paletted = [frame.quantize(palette=palette_source, dither=Image.Dither.NONE) for frame in frames]
    paletted[0].save(gif_file, save_all=True, append_images=paletted[1:], duration=FRAME_INTERVAL_MS, loop=0, optimize=True)


# Shoot the field guide from its top down to the end of the chapter list.
def shoot_field_guide(tab, page_file: Path, png_file: Path) -> None:
    tab.goto(page_file.as_uri() + "#field-guide")
    # Hide the sticky bar, and the learner's own score line, which reads 0 on a fresh page
    tab.add_style_tag(content=".topbar, .tally { display: none !important; }")
    tab.wait_for_timeout(400)
    clip = tab.evaluate("""() => {
        const top = document.querySelector('.hero').getBoundingClientRect();
        const bottom = document.querySelector('.guide-list').getBoundingClientRect();
        return {x: 0, y: top.y - 8 + window.scrollY, width: 390, height: bottom.bottom - top.y + 24};
    }""")
    tab.screenshot(path=str(png_file), full_page=True, clip=clip)


if __name__ == "__main__":
    page_file = build_example_page()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(args=["--no-sandbox"])
        for theme, suffix in [("light", ""), ("dark", "-dark")]:
            context, tab = open_phone_tab(browser, theme)

            # The ten doors, as a GIF
            gif_file = IMAGES / f"ten-doors{suffix}.gif"
            save_gif(record_ten_doors(tab, page_file), gif_file)
            print(f"Saved {gif_file}")

            # The field guide, as a PNG
            png_file = IMAGES / f"field-guide{suffix}.png"
            shoot_field_guide(tab, page_file, png_file)
            print(f"Saved {png_file}")
            context.close()
        browser.close()
