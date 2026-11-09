# Contributing

Issues and pull requests are welcome.

## Two editions, two branches

- **`main`** is the directory edition: the plugin folder holds only Markdown, text, JSON, YAML and images, because Anthropic's plugin directory accepts nothing else from publishers that are not Verified. Agents record, build and review each lesson by following the skill.
- **`full`** is the scripted edition: the same skill with scripts that record, build and check, and tests that break the examples on purpose.

A change to how lessons are made goes to both. Write it for `main` first, then port it to `full` with its script check and its break test.

## Before you open a pull request

- **Into `main`:** the CI checks must pass (file types, YAML and JSON, the template build, versions). Run one example lesson through `references/lesson-review.md` and attach the reviewers' reports.
- **Into `full`:** follow `CONTRIBUTING.md` on that branch; its scripts and break tests must pass.
- **A new rule** goes in the reference that explains it, marked (checked), and in `references/self-checks.md`.
- **A new component** gets a card in `references/components/` (for, beats, role, recipe, rules, wrong pick, example) and a line in `references/topic-map.md` where it fits.
- **A new scene recipe** is built on a real page and passes the scene review in light and dark, with motion on and off, before it goes in `components/scenes.md`.
- **A change to the page template** goes in `assets/page-template.md` on `main` and `assets/template.html` on `full`, with phone screenshots, light and dark.
- **A change to a principle** updates `VISION.md`, `SKILL.md` and `references/principles.md`, so they keep saying the same thing.
- **Every change** bumps the version in `plugin/.claude-plugin/plugin.json`, `SKILL.md` and `evals/evals.json`, and adds a line to `CHANGELOG.md`.
- **README pictures** change through `docs/diagram/build_pictures.py`, never by editing a PNG.

## Using AI to contribute

AI help is welcome. In the pull request, say:
- which model and tool you used;
- a summary of the change in your own words;
- the evidence: the CI result and the review reports.

## Names

The plugin and skill names never change after release.
