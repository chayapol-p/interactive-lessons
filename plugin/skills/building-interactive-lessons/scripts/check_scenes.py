#!/usr/bin/env python3
"""Open every scene on the built page and check what a script can judge, then save one image per step.

Usage:
    pip install playwright   (or use a Playwright that is already installed)
    python scripts/check_scenes.py lesson.html [--scenes id ...] [--out shots]

For each scene (a figure of kind: scene, references/visual-design.md section 6) it taps through every step, then sets
every value of every slider or buttons control on the last step, and presses every run button. It does this at
390 px wide, in light and dark themes, once with motion and once with reduced motion. A scene fails when:
- its script throws, or it falls back to words;
- something it draws sits outside its box;
- it shows a number that is not in its data, a step caption, a step label or a control value (typed numbers);
- two steps in a row look the same (a step that changes nothing);
- a step ends in a different picture with motion than without (the motion must land where the jump lands);
- a run button gives no summary line.
It saves scene-<id>-<n>-<theme>.png for each step (with motion), so the scene can be read like a comic strip.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

PHONE_WIDTH = 390
PHONE_HEIGHT = 844
SETTLE_TIMEOUT_MS = 6000

SNAPSHOT = """(host) => {
  const svg = host.querySelector('svg.scene');
  if (!svg) return null;
  const box = svg.getBoundingClientRect();
  const scale = box.width / svg.viewBox.baseVal.width;
  const round = (text) => text.replace(/-?\\d+\\.\\d+/g, (n) => String(Math.round(Number(n) * 2) / 2));
  const outside = [], texts = [];
  for (const element of svg.querySelectorAll('*')) {
    if (element.closest('defs') || ['g', 'defs', 'title', 'tspan', 'linearGradient', 'stop', 'clipPath'].includes(element.tagName)) continue;
    const opacity = Number(getComputedStyle(element).opacity);
    const r = element.getBoundingClientRect();
    if (opacity === 0 || (r.width === 0 && r.height === 0)) continue;
    const slack = 1.5 * scale;
    if (r.left < box.left - slack || r.right > box.right + slack || r.top < box.top - slack || r.bottom > box.bottom + slack) {
      outside.push(`${element.tagName}${element.textContent ? ' "' + element.textContent.trim().slice(0, 20) + '"' : ''}`);
    }
    if (element.tagName === 'text' && element.textContent.trim()) {
      texts.push({ text: element.textContent.trim(), left: r.left, top: r.top, right: r.right, bottom: r.bottom });
    }
  }
  const visible = (element) => Number(getComputedStyle(element).opacity) > 0 && element.getAttribute('visibility') !== 'hidden';
  return {
    picture: round(svg.innerHTML),
    outside,
    texts: texts.map((t) => t.text),
    boxes: texts,
    error: host.dataset.sceneError || null,
    step: host.dataset.step,
  };
}"""


def serve_libraries_from(context, folder):
    """Answer the page's jsDelivr requests from a local folder (npm package folders such as animejs/ and gsap/), for
    machines that cannot reach the CDN. https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/gsap.min.js -> folder/gsap/dist/gsap.min.js"""
    root = Path(folder).resolve()

    def answer(route):
        path = route.request.url.split("/npm/", 1)[-1]
        package, _, rest = path.partition("/")
        local = root / re.sub(r"@[^/]+$", "", package) / rest
        if local.is_file():
            route.fulfill(path=str(local), content_type="application/javascript")
        else:
            route.abort()
    context.route("https://cdn.jsdelivr.net/npm/**", answer)


def find_browser():
    """Playwright's own Chromium if installed, else a system Chrome."""
    for name in ["google-chrome", "chromium", "chromium-browser"]:
        found = shutil.which(name)
        if found:
            return found
    return None


def numbers_in(value):
    """Every number inside a JSON value, as floats."""
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, dict):
        return [n for item in value.values() for n in numbers_in(item)] + [n for key in value for n in numbers_in_text(key)]
    if isinstance(value, list):
        return [n for item in value for n in numbers_in(item)]
    if isinstance(value, str):
        return numbers_in_text(value)
    return []


def numbers_in_text(text):
    return [float(found) for found in re.findall(r"-?\d+(?:\.\d+)?", str(text).replace(",", ""))]


def allowed(shown, known):
    """A shown number is fine when it is a known number at the precision shown, or a known share shown as a percent."""
    decimals = len(shown.split(".")[1]) if "." in shown else 0
    value = float(shown)
    for number in known:
        for candidate in (number, number * 100):
            if abs(round(candidate, decimals) - value) < 1e-9:
                return True
    return False


def without_allowed_bounds(text, known):
    """Drop "<1%" and ">99%" when the data holds a share below 1% (above 0) or above 99% (below 1): the scene shows a
    tiny or near-certain share as a bound, so it never shows 0% or 100% for a share that is neither."""
    def is_allowed(match):
        bound = float(match.group(2)) / 100
        if match.group(1) == "<":
            return any(0 < number < bound for number in known)
        return any(bound < number < 1 for number in known)
    return re.sub(r"([<>])\s?(\d+(?:\.\d+)?)%", lambda match: "" if is_allowed(match) else match.group(0), text)


def overlapping(boxes):
    """Pairs of labels that cover each other by more than a third of the smaller one."""
    pairs = []
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            width = min(a["right"], b["right"]) - max(a["left"], b["left"])
            height = min(a["bottom"], b["bottom"]) - max(a["top"], b["top"])
            if width <= 0 or height <= 0:
                continue
            smaller = min((a["right"] - a["left"]) * (a["bottom"] - a["top"]), (b["right"] - b["left"]) * (b["bottom"] - b["top"]))
            if smaller and width * height > smaller / 3:
                pairs.append(f'"{a["text"]}" and "{b["text"]}"')
    return pairs


def settle(tab, host):
    """Wait until every move in the scene has finished."""
    tab.wait_for_timeout(60)
    tab.wait_for_function("(host) => host.dataset.sceneBusy === '0'", arg=host.element_handle(), timeout=SETTLE_TIMEOUT_MS)
    tab.wait_for_timeout(30)


def walk(tab, host, block):
    """Every state the learner can reach by tapping: each step, then each control value on the last step."""
    figure = block["figure"]
    states = []
    settle(tab, host)
    states.append(("step 1", tab.evaluate(SNAPSHOT, host.element_handle())))
    if states[0][1] is None or states[0][1]["error"]:
        return states   # the scene fell back to words: nothing to tap
    for index in range(1, len(figure["steps"])):
        host.locator(".scene-nav button", has_text="Next").click()
        settle(tab, host)
        states.append((f"step {index + 1}", tab.evaluate(SNAPSHOT, host.element_handle())))
    for control in figure.get("controls") or []:
        if control["kind"] == "run":
            continue
        row = host.locator(f'[data-control="{control["id"]}"]')
        for value_index, value in enumerate(control["values"]):
            if control["kind"] == "slider":
                row.locator("input").evaluate("(input, v) => { input.value = String(v); input.dispatchEvent(new Event('input')); }", value_index)
            else:
                row.locator("button").nth(value_index).click()
            settle(tab, host)
            states.append((f"{control['label']} = {value}", tab.evaluate(SNAPSHOT, host.element_handle())))
    return states


def main():
    parser = argparse.ArgumentParser(description="Check every scene on the built page, and save one image per step.")
    parser.add_argument("page", help="the built lesson.html")
    parser.add_argument("--scenes", nargs="+", metavar="ID", help="check only these scenes")
    parser.add_argument("--libraries", metavar="FOLDER", help="serve motion libraries from this folder instead of jsDelivr (for machines without the CDN)")
    parser.add_argument("--out", default="shots", help="folder for the images (default: shots)")
    arguments = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("check_scenes.py needs Playwright: pip install playwright")

    page_path = Path(arguments.page).resolve()
    out_folder = Path(arguments.out)
    out_folder.mkdir(parents=True, exist_ok=True)
    problems, notes = [], []
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(args=["--no-sandbox"])
        except Exception:
            browser = playwright.chromium.launch(executable_path=find_browser(), args=["--no-sandbox"])
        probe_context = browser.new_context()
        if arguments.libraries:
            serve_libraries_from(probe_context, arguments.libraries)
        probe = probe_context.new_page()
        probe.goto(page_path.as_uri())
        scenes = probe.evaluate("""() => LESSON.chapters.flatMap((chapter) => chapter.blocks
            .filter((block) => block.type === 'diagram' && block.figure.kind === 'scene')
            .map((block) => ({ chapter: chapter.id, block })))""")
        probe.close()
        if arguments.scenes:
            scenes = [scene for scene in scenes if scene["block"]["id"] in arguments.scenes]
        if not scenes:
            print("No scenes on this page.")
            return
        for item in scenes:
            block, chapter = item["block"], item["chapter"]
            figure = block["figure"]
            known = numbers_in(figure.get("data") or {})
            for step in figure["steps"]:
                known += numbers_in_text(step.get("caption", "")) + numbers_in_text(step.get("label", ""))
            for control in figure.get("controls") or []:
                known += [n for value in control.get("values") or [] for n in numbers_in_text(value)]
            results = {}
            for theme in ["light", "dark"]:
                for motion in ["no-preference", "reduce"]:
                    context = browser.new_context(viewport={"width": PHONE_WIDTH, "height": PHONE_HEIGHT}, color_scheme=theme,
                                                  reduced_motion=motion, device_scale_factor=2)
                    if arguments.libraries:
                        serve_libraries_from(context, arguments.libraries)
                    tab = context.new_page()
                    tab.set_default_timeout(8000)
                    logged = []
                    tab.on("pageerror", lambda error, logged=logged: logged.append(str(error)))
                    # Errors, and the warnings a motion library gives when it skips a move (a property it does not know)
                    tab.on("console", lambda message, logged=logged: logged.append(message.text) if (message.type == "error" and not message.text.startswith("Failed to load resource"))
                           or (message.type == "warning" and re.search(r"invalid property|not found|missing plugin|target .* not", message.text, re.I)) else None)
                    tab.goto(page_path.as_uri() + "#" + chapter)
                    host = tab.locator(f'[data-scene="{block["id"]}"]')
                    host.scroll_into_view_if_needed()
                    tab.wait_for_timeout(150)
                    label = f"{block['id']} ({theme}, motion {'reduced' if motion == 'reduce' else 'on'})"
                    try:
                        states = walk(tab, host, block)
                    except Exception as error:   # a scene that never settles, or a control that is missing
                        problems.append(f"{label}: could not tap through it: {str(error).splitlines()[0]}")
                        context.close()
                        continue
                    drew = states and states[0][1] is not None and not states[0][1]["error"]
                    if motion == "no-preference" and drew:
                        # One image per step, taken again from the start so the images follow the storyboard (a fresh load)
                        tab.goto(page_path.as_uri() + "?again#" + chapter)
                        tab.wait_for_timeout(150)
                        host = tab.locator(f'[data-scene="{block["id"]}"]')
                        host.scroll_into_view_if_needed()
                        for index in range(len(figure["steps"])):
                            if index:
                                host.locator(".scene-nav button", has_text="Next").click()
                            settle(tab, host)
                            image = out_folder / f"scene-{block['id']}-{index + 1}-{theme}.png"
                            host.screenshot(path=str(image))
                            print(f"SHOT     {image}")
                        for control in figure.get("controls") or []:
                            if control["kind"] != "run":
                                continue
                            for index, trials in enumerate(control["trials"]):
                                host.locator(f'[data-control="{control["id"]}"] button').nth(index).click()
                                tab.wait_for_timeout(100)
                                summary = host.locator(".scene-result").inner_text().strip()
                                if not summary:
                                    problems.append(f"{label}: the run button for {trials} gives no summary line (scene.run must return one)")
                    results[(theme, motion)] = states
                    for name, state in states:
                        if state is None or state["error"]:
                            problems.append(f"{label}, {name}: the scene could not draw ({(state or {}).get('error') or 'no picture'})")
                            continue
                        if state["outside"]:
                            problems.append(f"{label}, {name}: drawn outside the box: {', '.join(state['outside'][:4])}")
                        for text in state["texts"]:
                            text = without_allowed_bounds(text, known)
                            for shown in re.findall(r"-?\d+(?:\.\d+)?", text.replace(",", "")):
                                if not allowed(shown, known):
                                    problems.append(f"{label}, {name}: shows {shown} (in \"{text}\"), which is not in its data, captions or control values; read numbers from scene.data")
                        if theme == "light" and motion == "reduce":
                            for pair in overlapping(state["boxes"]):
                                notes.append(f"{block['id']}, {name}: labels overlap: {pair}")
                    step_states = [state for name, state in states if name.startswith("step ")]
                    for index in range(1, len(step_states)):
                        if step_states[index] and step_states[index - 1] and step_states[index]["picture"] == step_states[index - 1]["picture"]:
                            problems.append(f"{label}: step {index + 1} looks the same as step {index}; every step must change something")
                    for message in logged:
                        problems.append(f"{label}: page error: {message}")
                    context.close()
            for theme in ["light", "dark"]:
                moving, still = results.get((theme, "no-preference")), results.get((theme, "reduce"))
                if not moving or not still:
                    continue
                for (name, a), (_, b) in zip(moving, still):
                    if a and b and a["picture"] != b["picture"]:
                        problems.append(f"{block['id']} ({theme}), {name}: ends in a different picture with motion than without; "
                                        "scene.move must reach the same values the jump sets")
                        break
        browser.close()

    for note in sorted(set(notes)):
        print(f"NOTE     {note}")
    for problem in dict.fromkeys(problems):
        print(f"PROBLEM  {problem}")
    print(f"\n{len(set(problems))} problems. Read the step images in order, like a comic strip: does each step show one change, "
          "and does the caption say where to look?")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
