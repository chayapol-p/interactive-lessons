# Contributing

Issues and pull requests are welcome.

## Set up

```bash
pip install pyyaml ruamel.yaml playwright
```

## Before you open a pull request

Run these from the repo root. All must pass.

```bash
python3 plugin/skills/building-interactive-lessons/scripts/check_blueprint.py plugin/skills/building-interactive-lessons/assets/example-blueprint.yaml --run-tests
python3 plugin/skills/building-interactive-lessons/scripts/check_blueprint.py plugin/skills/building-interactive-lessons/assets/example-concepts-blueprint.yaml --run-tests
python3 plugin/skills/building-interactive-lessons/scripts/check_blueprint.py plugin/skills/building-interactive-lessons/assets/example-monty-blueprint.yaml --run-tests
python3 tests/check_catches_breaks.py
python3 tests/check_scene_breaks.py   # needs Playwright
```

- **A new checker rule** gets a new break in `tests/check_catches_breaks.py`; a new scene check gets one in `tests/check_scene_breaks.py`.
- **A change to the page template** comes with phone screenshots, light and dark, from `scripts/screenshot_chapters.py`.
- **A change to a principle** updates both `VISION.md` and `SKILL.md`, so they keep saying the same thing.
- **Every change** bumps the version in `plugin/.claude-plugin/plugin.json` and in `SKILL.md`, and adds a line to `CHANGELOG.md`.
- **README pictures** change through `docs/diagram/build_pictures.py`, never by editing a PNG.

## Using AI to contribute

AI help is welcome. In the pull request, say:
- which model and tool you used;
- a summary of the change in your own words;
- the evidence: the output of the checks above.

## Names

The plugin and skill names never change after release.
