#!/usr/bin/env python3
"""Run every code slice and every blank option, and write the real outputs into the blueprint.

Usage:
    pip install pyyaml ruamel.yaml
    python scripts/record_outputs.py lesson-blueprint.yaml [--only block-id ...] [--dry-run]

Each program runs with the real interpreter (python, or node for JavaScript), exactly as
check_blueprint.py --run-tests runs it:
    - a code slice: slice.setup, then slice.code  -> slice.recorded_output
    - a blank option: setup, then code with that option in its blank and every other blank
      right  -> that option's output
Blocks with run_locally are skipped: record those on a machine that has the service.

The file is edited in place, keeping its comments and layout. Outputs are never typed by hand.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_blueprint import build_runs, computed_figure_data, figure_runs, load_blueprint, normalise_output, run_program  # noqa: E402

try:
    from ruamel.yaml import YAML
    from ruamel.yaml.scalarstring import LiteralScalarString
except ImportError:
    sys.exit("record_outputs.py needs ruamel.yaml to keep the blueprint's comments: pip install ruamel.yaml")


def as_yaml_text(output):
    """Many-line outputs as a | block, so the blueprint stays readable."""
    output = normalise_output(output)
    return LiteralScalarString(output + "\n") if "\n" in output else output


def main():
    parser = argparse.ArgumentParser(description="Record real outputs into the blueprint.")
    parser.add_argument("blueprint")
    parser.add_argument("--only", nargs="+", metavar="BLOCK_ID", help="record only these blocks (a revise round)")
    parser.add_argument("--dry-run", action="store_true", help="show what would change, write nothing")
    arguments = parser.parse_args()

    blueprint_path = Path(arguments.blueprint)
    plain = load_blueprint(blueprint_path)  # the strict loader: duplicate keys and bad YAML stop here
    text = blueprint_path.read_text(encoding="utf-8")
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    # Keep the file's own list indent: "key:\n  - item" (indented) or "key:\n- item" (flush)
    indented_lists = re.search(r"^\w[\w-]*:\s*\n  - ", text, re.M) is not None
    yaml.indent(mapping=2, sequence=4 if indented_lists else 2, offset=2 if indented_lists else 0)
    document = yaml.load(text)

    changed = 0
    for run in build_runs(plain):
        block_id = run["name"].split(":")[0]
        if arguments.only and block_id not in arguments.only:
            continue
        output, finished = run_program(run["language"], run["code"], plain.get("shared_modules"))
        same = normalise_output(output) == normalise_output(run["claimed_output"])
        status = "same" if same else "UPDATED"
        print(f"{status:8} {run['name']}{'' if finished else '  (the program failed; its error line is recorded)'}")
        if same:
            continue
        changed += 1
        target = run["target"]
        block = document["chapters"][target[0]]["blocks"][target[1]]
        if len(target) == 2:
            block["slice"]["recorded_output"] = as_yaml_text(output)
        else:
            block["blanks"][target[2]]["options"][target[3]]["output"] = as_yaml_text(output)

    # Pictures whose numbers come from computed_by
    for run in figure_runs(plain):
        block_id = run["name"].split(":")[0]
        if (arguments.only and block_id not in arguments.only) or run["skip"]:
            continue
        data, printed = computed_figure_data(run, plain.get("shared_modules"))
        if data is None:
            print(f"FAILED   {run['name']}: computed_by did not print JSON:\n{printed}")
            continue
        actual = {field: data.get(field) for field in run["fields"]}
        same = json.dumps(actual, sort_keys=True) == json.dumps(run["claimed"], sort_keys=True, default=str)
        print(f"{'same' if same else 'UPDATED':8} {run['name']}")
        if not same:
            changed += 1
            figure = document["chapters"][run["target"][0]]["blocks"][run["target"][1]]["figure"]
            for field in run["fields"]:
                figure[field] = actual[field]

    if changed and not arguments.dry_run:
        with blueprint_path.open("w", encoding="utf-8") as blueprint_file:
            yaml.dump(document, blueprint_file)
    print(f"\n{changed} outputs {'would change' if arguments.dry_run else 'recorded'}. "
          "Next: python scripts/check_blueprint.py " + str(blueprint_path) + " --run-tests")


if __name__ == "__main__":
    main()
