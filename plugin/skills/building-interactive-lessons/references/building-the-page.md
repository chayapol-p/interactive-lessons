# Building the page

How a finished blueprint becomes the lesson page: record every real result into the blueprint, then fill the page template with it. You do both with your own code tool (in claude.ai, Claude Code or Cowork). The skill ships no scripts; the steps and short code below are what to run.

## Contents

1. What you need
2. Record every result
3. Fill the page template
4. Publish
5. After a change

---

## 1. What you need

- The blueprint, saved as `lesson-blueprint.yaml`, passing `self-checks.md` sections 1 to 14.
- A code tool that runs Python 3 (and Node, for a JavaScript slice), with PyYAML. Install it if missing: `pip install pyyaml`.
- The skill's folder, to read `assets/page-template.md`. In claude.ai, skills sit under `/mnt/skills/`; elsewhere, find the folder that holds this file.

Never type a result by hand, and never write or edit the page by hand. If you cannot run code at all, stop and tell the author: the lesson needs real results.

## 2. Record every result

Every output the page shows comes from a real run. Leave each `recorded_output`, option `output`, figure data field and play `cases`/`sample` empty (`""`, `[]` or `{}`) while planning, then fill them from runs.

**What to run, and where the result goes:**

| Program | Run | Write what it prints into |
|---|---|---|
| A code slice | `slice.setup`, then `slice.code` | `slice.recorded_output` |
| A blank option (code) | `setup`, then `code` with this option in its blank and every other blank's right option in the others | that option's `output` |
| A figure's `computed_by` | its `code` | the figure's data fields: `bars`; `rows` (tokens); `points` (scatter); `rows`, `columns`, `values` (grid); `frames`; `tiles`; `data` (scene) |
| A play block's `computed_by` | its `code` | the block's `cases` and `sample` |

**How to run each program:**
- Use the real interpreter: `python3` for python, `node` for javascript (save it as a `.mjs` file).
- Run it in an empty folder that holds one file per `shared_modules` entry (`<name>.py` with that source), so `from toy_llm import …` works.
- Stop it after 10 seconds.
- Keep what it prints, without trailing spaces or blank lines at the ends. If it fails, add its last error line (for example `NameError: name 'stride' is not defined`).
- A `computed_by` must print one JSON object; read the fields above from it.
- A text exercise (`language: text`) runs nothing: each option's result comes from its named source or its worked steps.
- A block with `run_locally` runs only on a machine with the service it needs; record it there, and say so in the work log.

A short way to do it in your code tool (adapt freely; it is yours, not the skill's):

```python
# Run one program the way the page's results must come from: real interpreter, shared modules beside it
import json, subprocess, tempfile
from pathlib import Path

def run_program(language: str, code: str, shared_modules: dict) -> str:
    with tempfile.TemporaryDirectory() as work_folder:
        for module_name, source in (shared_modules or {}).items():
            Path(work_folder, f"{module_name}.py").write_text(source)
        program = Path(work_folder, "program.py" if language == "python" else "program.mjs")
        program.write_text(code)
        command = ["python3", str(program)] if language == "python" else ["node", str(program)]
        completed = subprocess.run(command, cwd=work_folder, capture_output=True, text=True, timeout=10)
    printed = "\n".join(line.rstrip() for line in completed.stdout.splitlines()).strip("\n")
    if completed.returncode != 0:
        error_lines = [line for line in completed.stderr.splitlines() if line.strip()]
        printed = (printed + "\n" + (error_lines[-1].strip() if error_lines else "error")).strip()
    return printed

# A blank option: this option in its blank, the right option in every other blank
def fill_blanks(code: str, chosen_text_by_blank: dict) -> str:
    for blank_id, text in chosen_text_by_blank.items():
        code = code.replace("{{" + blank_id + "}}", text)
    return code
```

**Writing results back:** edit the blueprint's YAML in place, so its comments stay. Write a many-line output as a `|` block. Then work through `self-checks.md` section 15: every wrong option must print something different from the right one, and every recorded value must match a fresh run.

## 3. Fill the page template

The template is the one html block in `assets/page-template.md` (fenced with four backticks). It has two placeholders, each exactly once:

| Placeholder | Replace with |
|---|---|
| `/*__LESSON_DATA__*/null` | the whole blueprint as JSON, on one line |
| `<!--__SCENE_SCRIPTS__-->` | the motion library tags, then one script element per scene, in page order; nothing if the lesson has no scene |

**The JSON:** dump the blueprint with every field, as it is. Make it safe inside a script element: replace `</` with `<\/`, and the characters U+2028 and U+2029 with `\u2028` and `\u2029`.

**Motion library tags**, once each, only for libraries a scene names in `library`:

```html
<!-- anime -->
<script src="https://cdn.jsdelivr.net/npm/animejs@4.5.0/dist/bundles/anime.umd.min.js"></script>
<!-- gsap -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/MotionPathPlugin.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/DrawSVGPlugin.min.js"></script>
```

**One script element per scene**, so a scene with a bug cannot stop the page or another scene. `SCENE_ID` is the diagram block's id as a JSON string, and the body is the figure's `script` as it is:

```html
<script>
"use strict";
(window.LESSON_SCENES = window.LESSON_SCENES || {})["SCENE_ID"] = function (scene) {
  // the figure's script, unchanged
};
</script>
```

A short way to do all of it:

```python
# Fill the page template from the blueprint (references/building-the-page.md section 3)
import json, shutil, yaml
from pathlib import Path

LIBRARY_TAGS = {
    "anime": ["https://cdn.jsdelivr.net/npm/animejs@4.5.0/dist/bundles/anime.umd.min.js"],
    "gsap": ["https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/gsap.min.js",
             "https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/MotionPathPlugin.min.js",
             "https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/DrawSVGPlugin.min.js"],
}

def build_page(skill_folder: Path, blueprint_path: Path, page_path: Path) -> None:
    # The template: the html block in assets/page-template.md
    guide = (skill_folder / "assets" / "page-template.md").read_text()
    page = guide.split("````html\n", 1)[1].split("\n````", 1)[0]
    blueprint = yaml.safe_load(blueprint_path.read_text())

    # The scenes, in page order, and the libraries they name
    scenes = [block for chapter in blueprint["chapters"] for block in chapter["blocks"]
              if block["type"] == "diagram" and block["figure"].get("kind") == "scene"]
    libraries = []
    for block in scenes:
        if block["figure"].get("library") and block["figure"]["library"] not in libraries:
            libraries.append(block["figure"]["library"])
    parts = [f'<script src="{url}"></script>' for library in libraries for url in LIBRARY_TAGS[library]]
    for block in scenes:
        parts.append('<script>\n"use strict";\n(window.LESSON_SCENES = window.LESSON_SCENES || {})['
                     + json.dumps(block["id"]) + '] = function (scene) {\n' + block["figure"]["script"] + "\n};\n</script>")

    # The blueprint as JSON that is safe inside a script element
    data = json.dumps(blueprint, ensure_ascii=False, separators=(",", ":"), default=str)
    data = data.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")

    # Fill both placeholders, write the page, and keep the blueprint beside it for publishing
    page = page.replace("<!--__SCENE_SCRIPTS__-->", "\n".join(parts)).replace("/*__LESSON_DATA__*/null", data)
    page_path.write_text(page)
    shutil.copyfile(blueprint_path, page_path.with_name("lesson-blueprint.txt"))
```

**Then check the build itself:**
- The page has neither placeholder left, and opens with no script error.
- The page's title, theme and fonts come from the blueprint: the page sets them when it loads.

## 4. Publish

- In claude.ai, load the environment's artifact skills before publishing, and check the page against their current rules; their rules win over the template.
- Publish `lesson.html` as an artifact with the capabilities in `page-contract.md`, and `lesson-blueprint.txt` beside it (`.yaml` is not a served type).
- Republish to the same artifact and path, so the link stays.

## 5. After a change

1. Edit the blueprint, never the page.
2. Record again only the programs whose code changed (section 2).
3. Build the whole page again (section 3). It takes seconds.
4. Review only what changed: list the chapters whose blocks changed, and give that list to the reviewers (`lesson-review.md`). A change to the theme, the glossary or a shared misconception touches every chapter that shows it.
