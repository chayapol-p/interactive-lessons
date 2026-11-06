"""Check a lesson blueprint before any page is built.

The script reads a blueprint (YAML or JSON) and checks every rule the skill
states. Each rule in the reference files marked "(checked)" is enforced here;
the rest are judgement calls reviewed in step 5.

With --run-tests it also proves that every output the page will show is real:
it runs each code slice, and each fill-in-the-blanks exercise once per option,
with the real interpreter (python or node), and compares what prints with the
recorded output. The lesson page itself runs no code; it shows these outputs.

Usage:
    python check_blueprint.py lesson-blueprint.yaml
    python check_blueprint.py lesson-blueprint.yaml --run-tests

Exit code is 1 when there is at least one error, otherwise 0.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


# ===== Limits taken from the skill's rules =====

MOST_MUST_KNOW_IDEAS = 3
SHORTEST_CHAPTER_MINUTES = 5
LONGEST_CHAPTER_MINUTES = 15
LONGEST_LESSON_MINUTES = 90
SMALLEST_PRIMER_SHARE = 0.10          # a before-hands-on chapter gets at least 10% of its section's hands-on time
MOST_CHECKS_PER_CHAPTER = 2
MOST_STRETCHES_PER_CHAPTER = 1
MOST_IDEA_SENTENCES = 2
MOST_IDEA_WORDS = 45                  # the text budget: an idea is at most 2 sentences and about 45 words
MOST_FEEDBACK_SENTENCES = 1           # why_right and why_wrong: one sentence
MOST_CAPTION_WORDS = 25               # a picture's caption and each step's caption
FAIR_LENGTH_RATIO = 1.5               # a right option this much longer than every wrong one gives itself away
FAIR_LENGTH_GAP = 12                  # ...and at least this many characters longer
ARC_BEATS = ["hook", "intuition", "proof", "mechanism", "boundary", "transfer", "payoff"]
MOST_INSTRUCTION_LINES = 4
MOST_CODE_LINES = 15                  # code lines only: blank and comment-only lines do not count
CODE_LINES_PER_COMMENT = 4            # at least one comment for every 4 code lines
BLANK_COUNT_RANGE = (1, 3)
BLANK_OPTION_RANGE = (3, 4)
CHECK_OPTION_RANGE = (3, 4)
PREDICT_OPTION_RANGE = (2, 4)
HINT_LEVEL_RANGE = (1, 2)
RUN_TIME_LIMIT_SECONDS = 10
ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BLANK_PATTERN = re.compile(r"\{\{([a-z0-9-]+)\}\}")
FILE_PATH_PATTERN = re.compile(r"^[\w./-]+\.(txt|log|out|json)$")
LESSON_ROLES = {"before-hands-on", "standalone", "after-hands-on"}
DIAGRAM_SHAPES = {"flow", "structure", "change-over-time", "space", "comparison", "quantity"}
# A sentence promising that a later chapter adds to, extends or redraws something
PROMISE_PATTERN = re.compile(
    r"\b(later|next|following|each|every|future|coming|other)\s+chapters?\b[^.]{0,80}?\b(adds?|extends?|grows?|builds?|draws?|redraws?|completes?)\b"
    r"|\b(grows?|builds? up|is extended)\s+(across|over|through)\s+(the\s+)?(later\s+)?chapters\b"
    r"|\bchapter\s+\d+\s+(adds|extends|draws|completes)\b",
    re.IGNORECASE)
CODE_LANGUAGES = {"python", "javascript"}
TEXT_LANGUAGE = "text"                       # a fill-the-blanks passage of prose, a rule or a formula: nothing runs
TEXT_RESULT_ORIGINS = {"source", "worked"}   # where a text option's result comes from: a named source, or worked steps
TESTING_BLOCK_TYPES = {"predict", "check", "fill_blanks", "explain"}
TESTS_AFTER_TEACHING = {"check", "fill_blanks", "explain"}


# ===== The blueprint's shape: allowed and required keys for every kind of item =====
# Any key not listed here is an error, so a typo or a YAML line split into junk keys is caught.

ALLOWED_KEYS = {
    "top": {"lesson", "theme", "glossary", "known_ideas", "facts", "misconceptions", "shared_modules", "chapters"},
    "lesson": {"title", "role", "learner", "objectives", "source", "agreed_extras", "big_idea"},
    "learner": {"knows", "new_to", "wants_to", "time_minutes", "assumed", "assumption_note"},
    "objective": {"id", "text"},
    "glossary": {"term", "definition"},
    "known_idea": {"id", "idea"},
    "fact": {"id", "statement", "status", "source"},
    "misconception": {"id", "wrong_idea", "why_people_believe_it", "what_is_true", "source"},
    "chapter": {"id", "title", "minutes", "source_section", "source_minutes", "why_it_matters", "must_know",
                "must_get_right", "brings_in", "carries_forward", "misconceptions", "bridge_in", "bridge_out", "blocks",
                "beat", "milestone", "open_question"},
    "must_get_right": {"id", "can_do", "evidence", "objective", "tested_by"},
    "carried_idea": {"id", "idea", "used_in", "shown_by"},
    "bridge_in": {"text", "recalls"},
    "bridge_out": {"text", "points_to"},
    "answer_option": {"text", "correct", "why_right", "why_wrong"},
    "blank": {"id", "options"},
    "blank_option": {"text", "correct", "why_right", "why_wrong", "misconception", "output", "output_from", "output_source"},
    "diagram_brief": {"understand", "how_it_helps", "clearer_than_text"},
    "code_slice": {"language", "source", "depends_on", "context_note", "setup", "code", "recorded_output", "run_locally"},
    "run_locally": {"command", "why"},
    "compare_option": {"name", "steps"},
    "rubric_line": {"criterion", "passing"},
    "wrong_answer": {"answer", "misconception", "hint"},
    "predict": {"id", "type", "question", "options", "answer"},
    "idea": {"id", "type", "text", "key", "more"},
    "diagram": {"id", "type", "shape", "brief", "figure", "grows_in", "extends"},
    "diagram_extends": {"diagram", "adds"},
    "figure": {"kind", "parts", "links", "highlight", "bars", "max", "svg", "rows", "columns", "values", "highlight_row",
               "points", "x_label", "y_label", "frames", "control", "control_label", "computed_by", "label", "mark_below", "toy",
               "tiles", "animate"},
    "figure_tile": {"label", "state", "inside", "note", "group"},
    "figure_token_row": {"label", "tokens"},
    "figure_token": {"text", "id", "hot"},
    "figure_point": {"label", "x", "y", "group"},
    "figure_frame": {"label", "figure", "caption"},
    "computed_by": {"language", "code", "run_locally"},
    "figure_part": {"id", "label", "note", "row"},
    "figure_link": {"from", "to", "label"},
    "figure_bar": {"label", "value", "note"},
    "code": {"id", "type", "slice", "notice"},
    "compare": {"id", "type", "input", "options", "differs_at", "explanation"},
    "fill_blanks": {"id", "type", "instructions", "language", "source", "context_note", "setup", "code", "text", "blanks",
                    "hints", "run_locally"},
    "explain": {"id", "type", "instructions", "reference_solution", "rubric", "hints", "common_wrong_answers"},
    "stretch": {"id", "type", "kind", "language", "instructions", "reference_solution", "rubric", "hints"},
    "pitfall": {"id", "type", "misconception"},
    "check": {"id", "type", "purpose", "tests", "question", "options"},
    "recap": {"id", "type", "text", "sums_up"},
    "play": {"id", "type", "prompt", "deals", "outcomes", "computed_by", "cases", "sample"},
    "play_outcome": {"id", "label", "short", "hot"},
    "play_case": {"label", "weight", "outcome"},
    "play_sample": {"games", "seed", "counts"},
}

REQUIRED_KEYS = {
    "top": {"lesson", "known_ideas", "facts", "misconceptions", "chapters"},
    "lesson": {"title", "role", "learner", "objectives", "big_idea"},
    "learner": {"knows", "new_to", "wants_to", "time_minutes", "assumed"},
    "objective": {"id", "text"},
    "glossary": {"term", "definition"},
    "known_idea": {"id", "idea"},
    "fact": {"id", "statement", "status"},
    "misconception": {"id", "wrong_idea", "why_people_believe_it", "what_is_true", "source"},
    "chapter": {"id", "title", "minutes", "why_it_matters", "must_know", "must_get_right", "brings_in",
                "carries_forward", "misconceptions", "bridge_in", "bridge_out", "blocks", "beat", "milestone"},
    "must_get_right": {"id", "can_do", "evidence", "objective", "tested_by"},
    "carried_idea": {"id", "idea", "used_in", "shown_by"},
    "bridge_in": {"text", "recalls"},
    "bridge_out": {"text", "points_to"},
    "answer_option": {"text", "correct"},
    "blank": {"id", "options"},
    "blank_option": {"text", "correct", "output"},
    "diagram_brief": {"understand", "how_it_helps", "clearer_than_text"},
    "code_slice": {"language", "source", "context_note", "code", "recorded_output"},
    "run_locally": {"command", "why"},
    "compare_option": {"name", "steps"},
    "rubric_line": {"criterion", "passing"},
    "wrong_answer": {"answer", "misconception", "hint"},
    "predict": {"id", "type", "question"},
    "idea": {"id", "type", "text"},
    "diagram": {"id", "type", "shape", "brief", "figure"},
    "diagram_extends": {"diagram", "adds"},
    "figure": {"kind"},
    "figure_token_row": {"tokens"},
    "figure_token": {"text"},
    "figure_point": {"label", "x", "y"},
    "figure_frame": {"label", "figure"},
    "computed_by": {"language", "code"},
    "figure_part": {"id", "label", "row"},
    "figure_link": {"from", "to"},
    "figure_bar": {"label", "value"},
    "code": {"id", "type", "slice", "notice"},
    "compare": {"id", "type", "input", "options", "differs_at", "explanation"},
    "fill_blanks": {"id", "type", "instructions", "language", "source", "context_note", "blanks", "hints"},
    "explain": {"id", "type", "instructions", "reference_solution", "rubric", "hints"},
    "stretch": {"id", "type", "kind", "instructions", "reference_solution", "rubric", "hints"},
    "pitfall": {"id", "type", "misconception"},
    "check": {"id", "type", "purpose", "tests", "question", "options"},
    "recap": {"id", "type", "text", "sums_up"},
    "figure_tile": {"label", "state"},
    "play": {"id", "type", "prompt", "deals", "outcomes", "computed_by", "cases", "sample"},
    "play_outcome": {"id", "label", "short"},
    "play_case": {"label", "weight", "outcome"},
    "play_sample": {"games", "seed", "counts"},
}

BLOCK_TYPES = {"predict", "idea", "diagram", "code", "compare", "fill_blanks", "explain", "stretch", "pitfall", "check",
               "recap", "play"}

RETIRED_BLOCK_TYPES = {
    "your_turn": "was split in v0.2: code exercises are now 'fill_blanks' (default) or an optional 'stretch'; explain exercises are 'explain'",
}


# ===== Reading the blueprint file =====

def load_blueprint(blueprint_path):
    """Read a YAML or JSON blueprint. Duplicate keys in YAML are an error, not a silent overwrite."""
    text = Path(blueprint_path).read_text(encoding="utf-8")
    blueprint_path = str(blueprint_path)
    if blueprint_path.endswith(".json"):
        return json.loads(text)
    try:
        import yaml
    except ImportError:
        sys.exit("This blueprint is YAML, but PyYAML is not installed. Run: pip install pyyaml")

    class NoDuplicateKeysLoader(yaml.SafeLoader):
        pass

    def build_mapping_without_duplicates(loader, node, deep=False):
        seen_keys = set()
        for key_node, _ in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in seen_keys:
                raise yaml.constructor.ConstructorError(None, None, f"duplicate key '{key}'", key_node.start_mark)
            seen_keys.add(key)
        return loader.construct_mapping(node, deep)

    NoDuplicateKeysLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, build_mapping_without_duplicates)
    try:
        return yaml.load(text, Loader=NoDuplicateKeysLoader)
    except yaml.YAMLError as yaml_error:
        sys.exit(f"ERROR    the file is not valid YAML: {yaml_error}")


# ===== Collecting problems =====

class ProblemList:
    """Keeps errors (which block the build) apart from warnings (worth a look)."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, message):
        self.errors.append(f"{where}: {message}")

    def warning(self, where, message):
        self.warnings.append(f"{where}: {message}")


def is_missing(value):
    """True when a field is absent, empty, or only whitespace."""
    return value is None or (isinstance(value, str) and not value.strip()) or value == [] or value == {}


def count_sentences(text):
    """Roughly count sentences by their closing punctuation."""
    return len(re.findall(r"[.!?](\s|$)", text.strip()))


def split_code_lines(code, language):
    """Return (code lines, comment count): blank lines are skipped, comment-only lines count as comments."""
    comment_marker = "#" if language == "python" else "//"
    code_lines, comment_count = [], 0
    inside_block_comment = False
    for line in (code or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # JavaScript /* ... */ comments, on one line or several, count as comments, not code
        if language == "javascript" and (inside_block_comment or stripped.startswith("/*")):
            comment_count += 1
            inside_block_comment = "*/" not in stripped
            continue
        if stripped.startswith(comment_marker):
            comment_count += 1
            continue
        code_lines.append(line)
        # An inline comment: the marker after some code, with a space before it
        if re.search(r"\s" + re.escape(comment_marker) + r"\s", line):
            comment_count += 1
    return code_lines, comment_count


def normalise_output(text):
    """Compare outputs line by line, ignoring trailing spaces and blank lines at the ends."""
    return "\n".join(line.rstrip() for line in str(text or "").strip().splitlines())


# ===== Shape checks: every item has only known keys, every required key, and no empty values =====

def check_item_shape(item, kind, where, problems):
    if not isinstance(item, dict):
        problems.error(where, f"should be a mapping of fields, got {type(item).__name__}")
        return
    for key in item:
        if key not in ALLOWED_KEYS[kind]:
            problems.error(where, f"unknown field '{key}' (allowed: {', '.join(sorted(ALLOWED_KEYS[kind]))}). "
                                  "A YAML line with an unquoted comma can also split into a junk field like this")
    for key in REQUIRED_KEYS[kind]:
        if key not in item:
            problems.error(where, f"is missing required field '{key}'")
    for key, value in item.items():
        if value is None and key in ALLOWED_KEYS[kind]:
            problems.error(where, f"field '{key}' is empty; quote values that contain commas or colons")


def item_label(item):
    if not isinstance(item, dict):
        return ""
    label = item.get("id") or item.get("term") or item.get("text") or item.get("name") or item.get("criterion")
    return f" ({str(label)[:40]})" if label else ""


def check_list_shape(items, kind, where, problems):
    for position, item in enumerate(items or [], start=1):
        check_item_shape(item, kind, f"{where} item {position}{item_label(item)}", problems)


def check_blueprint_shape(blueprint, problems):
    """Walk the whole blueprint and check every item's fields."""
    check_item_shape(blueprint, "top", "blueprint", problems)
    lesson = blueprint.get("lesson") or {}
    check_item_shape(lesson, "lesson", "lesson", problems)
    check_item_shape(lesson.get("learner") or {}, "learner", "lesson.learner", problems)
    check_list_shape(lesson.get("objectives"), "objective", "lesson.objectives", problems)
    check_list_shape(blueprint.get("glossary"), "glossary", "glossary", problems)
    check_list_shape(blueprint.get("known_ideas"), "known_idea", "known_ideas", problems)
    check_list_shape(blueprint.get("facts"), "fact", "facts", problems)
    check_list_shape(blueprint.get("misconceptions"), "misconception", "misconceptions", problems)

    for chapter in blueprint.get("chapters") or []:
        chapter_id = chapter.get("id", "chapter")
        check_item_shape(chapter, "chapter", chapter_id, problems)
        check_list_shape(chapter.get("must_get_right"), "must_get_right", f"{chapter_id}.must_get_right", problems)
        check_list_shape(chapter.get("carries_forward"), "carried_idea", f"{chapter_id}.carries_forward", problems)
        for bridge_field in ["bridge_in", "bridge_out"]:
            if bridge_field in chapter:
                check_item_shape(chapter[bridge_field] or {}, bridge_field, f"{chapter_id}.{bridge_field}", problems)
        for block in chapter.get("blocks") or []:
            block_type = block.get("type")
            block_id = block.get("id", f"{chapter_id} block")
            if block_type in RETIRED_BLOCK_TYPES:
                problems.error(block_id, f"block type '{block_type}' {RETIRED_BLOCK_TYPES[block_type]}")
                continue
            if block_type not in BLOCK_TYPES:
                problems.error(block_id, f"unknown block type '{block_type}'")
                continue
            check_item_shape(block, block_type, block_id, problems)
            if block_type in {"predict", "check"}:
                check_list_shape(block.get("options"), "answer_option", f"{block_id}.options", problems)
            if block_type == "diagram":
                check_item_shape(block.get("brief") or {}, "diagram_brief", f"{block_id}.brief", problems)
                if "extends" in block:
                    check_item_shape(block["extends"] or {}, "diagram_extends", f"{block_id}.extends", problems)
                figure = block.get("figure") or {}
                check_item_shape(figure, "figure", f"{block_id}.figure", problems)
                if isinstance(figure, dict):
                    check_list_shape(figure.get("parts"), "figure_part", f"{block_id}.figure.parts", problems)
                    check_list_shape(figure.get("links"), "figure_link", f"{block_id}.figure.links", problems)
                    check_list_shape(figure.get("bars"), "figure_bar", f"{block_id}.figure.bars", problems)
                    check_data_figure_shape(figure, f"{block_id}.figure", problems)
            if block_type == "code":
                code_slice = block.get("slice") or {}
                check_item_shape(code_slice, "code_slice", f"{block_id}.slice", problems)
                if "run_locally" in code_slice:
                    check_item_shape(code_slice["run_locally"] or {}, "run_locally", f"{block_id}.slice.run_locally", problems)
            if block_type == "compare":
                check_list_shape(block.get("options"), "compare_option", f"{block_id}.options", problems)
            if block_type == "fill_blanks":
                for blank in block.get("blanks") or []:
                    blank_where = f"{block_id} blank '{blank.get('id', '?') if isinstance(blank, dict) else '?'}'"
                    check_item_shape(blank, "blank", blank_where, problems)
                    check_list_shape(blank.get("options") if isinstance(blank, dict) else [], "blank_option", f"{blank_where} option", problems)
                if "run_locally" in block:
                    check_item_shape(block["run_locally"] or {}, "run_locally", f"{block_id}.run_locally", problems)
            if block_type == "play":
                check_list_shape(block.get("outcomes"), "play_outcome", f"{block_id}.outcomes", problems)
                check_list_shape(block.get("cases"), "play_case", f"{block_id}.cases", problems)
                if isinstance(block.get("sample"), dict):
                    check_item_shape(block["sample"], "play_sample", f"{block_id}.sample", problems)
                if isinstance(block.get("computed_by"), dict):
                    check_item_shape(block["computed_by"], "computed_by", f"{block_id}.computed_by", problems)
            if block_type in {"explain", "stretch"}:
                check_list_shape(block.get("rubric"), "rubric_line", f"{block_id}.rubric", problems)
                check_list_shape(block.get("common_wrong_answers"), "wrong_answer", f"{block_id}.common_wrong_answers", problems)


# ===== Checks on the lesson as a whole =====

def check_ids(blueprint, problems):
    """Every id is unique across the blueprint and written as plain hyphenated words."""
    seen_ids = {}
    id_sources = [("objective", item) for item in (blueprint.get("lesson") or {}).get("objectives") or []]
    id_sources += [("known idea", item) for item in blueprint.get("known_ideas") or []]
    id_sources += [("fact", item) for item in blueprint.get("facts") or []]
    id_sources += [("misconception", item) for item in blueprint.get("misconceptions") or []]
    for chapter in blueprint.get("chapters") or []:
        id_sources.append(("chapter", chapter))
        id_sources += [("block", item) for item in chapter.get("blocks") or []]
        id_sources += [("must_get_right item", item) for item in chapter.get("must_get_right") or []]
        id_sources += [("carried idea", item) for item in chapter.get("carries_forward") or []]
    for kind, item in id_sources:
        item_id = item.get("id") if isinstance(item, dict) else None
        if is_missing(item_id):
            continue
        if not ID_PATTERN.match(str(item_id)):
            problems.error(item_id, "ids must be lowercase words joined by hyphens")
        if item_id in seen_ids:
            problems.error(item_id, f"id is used twice ({seen_ids[item_id]} and {kind})")
        seen_ids[item_id] = kind
    for known_idea in blueprint.get("known_ideas") or []:
        if not str(known_idea.get("id", "")).startswith("known-"):
            problems.error(known_idea.get("id", "known idea"), "known idea ids must start with 'known-'")


def check_lesson_and_scope(blueprint, problems):
    """Learner, role, objectives and time budget; the lesson fits the scope rule."""
    lesson = blueprint.get("lesson") or {}
    learner = lesson.get("learner") or {}
    if lesson.get("role") not in LESSON_ROLES:
        problems.error("lesson.role", f"must be one of: {', '.join(sorted(LESSON_ROLES))}")
    if learner.get("assumed") not in (True, False):
        problems.error("lesson.learner", "assumed must be true or false")
    if learner.get("assumed") is True and is_missing(learner.get("assumption_note")):
        problems.error("lesson.learner", "an assumed learner needs an assumption_note saying who should confirm it")

    objectives = lesson.get("objectives") or []
    if not 3 <= len(objectives) <= 5:
        problems.error("lesson.objectives", "write 3 to 5 objectives")
    for objective in objectives:
        objective_text = str(objective.get("text", ""))
        if not objective_text.startswith("After this, you can"):
            problems.error(objective.get("id", "objective"), "objective text must start 'After this, you can'")
        if "understand" in objective_text.lower():
            problems.error(objective.get("id", "objective"), "uses 'understand'; use a verb a check can observe (predict, choose, write, fix, explain)")

    chapters = blueprint.get("chapters") or []
    total_minutes = sum(chapter.get("minutes") for chapter in chapters if isinstance(chapter.get("minutes"), (int, float)))
    if total_minutes > LONGEST_LESSON_MINUTES:
        problems.error("lesson", f"chapters add up to {total_minutes} minutes; one lesson holds at most {LONGEST_LESSON_MINUTES}. Split the source into several lessons")
    time_available = learner.get("time_minutes")
    if "time_minutes" in learner and not isinstance(time_available, (int, float)):
        problems.error("lesson.learner", "time_minutes must be a number of minutes")
    elif isinstance(time_available, (int, float)) and total_minutes > time_available:
        problems.error("lesson", f"chapters add up to {total_minutes} minutes, more than the learner's {time_available}")

    for chapter in chapters:
        chapter_id = chapter.get("id", "chapter")
        minutes = chapter.get("minutes")
        if not isinstance(minutes, (int, float)) or not SHORTEST_CHAPTER_MINUTES <= minutes <= LONGEST_CHAPTER_MINUTES:
            problems.error(chapter_id, f"minutes must be {SHORTEST_CHAPTER_MINUTES} to {LONGEST_CHAPTER_MINUTES}; split a longer chapter")
        source_minutes = chapter.get("source_minutes")
        if source_minutes is not None and not isinstance(source_minutes, (int, float)):
            problems.error(chapter_id, "source_minutes must be a number")
        elif lesson.get("role") == "before-hands-on" and isinstance(source_minutes, (int, float)) and isinstance(minutes, (int, float)):
            if minutes < SMALLEST_PRIMER_SHARE * source_minutes:
                problems.error(chapter_id, f"{minutes} minutes cannot prepare {source_minutes} minutes of hands-on work; "
                                           f"give it at least {int(SMALLEST_PRIMER_SHARE * source_minutes + 0.99)} minutes or split it into 2 chapters")
        if lesson.get("role") == "before-hands-on" and is_missing(chapter.get("source_section")):
            problems.error(chapter_id, "a before-hands-on lesson names the source_section each chapter prepares for")


def check_facts_misconceptions_glossary(blueprint, problems):
    """Facts say how they are known; every misconception is used; every glossary term appears in the lesson."""
    for fact in blueprint.get("facts") or []:
        if fact.get("status") not in {"confirmed", "inferred"}:
            problems.error(fact.get("id", "fact"), "status must be 'confirmed' or 'inferred'")
        if fact.get("status") == "confirmed" and is_missing(fact.get("source")):
            problems.error(fact.get("id", "fact"), "a confirmed fact needs a source")

    used_misconceptions = {item for chapter in blueprint.get("chapters") or [] for item in chapter.get("misconceptions") or []}
    for misconception in blueprint.get("misconceptions") or []:
        if misconception.get("id") not in used_misconceptions:
            problems.error(misconception.get("id", "misconception"), "no chapter repairs this misconception; use it or remove it")

    all_lesson_text = blocks_text(blueprint.get("chapters") or []).lower()
    for entry in blueprint.get("glossary") or []:
        term = str(entry.get("term", "")).lower()
        if term and term not in all_lesson_text:
            problems.error(f"glossary '{entry.get('term')}'", "the term never appears in the lesson; remove it or use it")


def check_every_objective_is_served(blueprint, problems):
    objective_ids = {objective.get("id") for objective in (blueprint.get("lesson") or {}).get("objectives") or []}
    served = set()
    for chapter in blueprint.get("chapters") or []:
        for item in chapter.get("must_get_right") or []:
            served.add(item.get("objective"))
            if item.get("objective") not in objective_ids:
                problems.error(item.get("id", "must_get_right item"), f"names objective '{item.get('objective')}', which is not defined")
    for objective_id in objective_ids - served:
        problems.error(objective_id, "no chapter's must_get_right item serves this objective")


# ===== Checks on how chapters connect =====

CODE_NAME_PATTERN = re.compile(r"`([^`]+)`|\b([A-Za-z]\w*_\w+|\w+\(\))")


def named_concepts(text, glossary_terms):
    """The concepts a sentence names: glossary terms it uses, and code names (`backticked`, snake_case, call())."""
    lowered = str(text or "").lower()
    names = {term for term in glossary_terms if re.search(r"\b" + re.escape(term) + r"s?\b", lowered)}
    for backticked, bare in CODE_NAME_PATTERN.findall(str(text or "")):
        names.add((backticked or bare).lower())
    return names


def missing_concepts(text, shown_text, glossary_terms):
    """Concepts named in text that the blocks it points to never show."""
    shown_lowered = str(shown_text).lower()
    return sorted(name for name in named_concepts(text, glossary_terms)
                  if not re.search(r"\b" + re.escape(name.rstrip("()")) + r"s?\b", shown_lowered))


# Fields that hold ids, links or settings, not words a learner reads
STRUCTURAL_FIELDS = {"id", "type", "grows_in", "extends", "sums_up", "tests", "purpose", "correct", "misconception",
                     "language", "shape", "recalls", "points_to", "used_in", "shown_by", "tested_by", "objective"}


def blocks_text(blocks):
    """The words a learner reads in these blocks, without ids and link fields (a chapter id is not teaching)."""
    collected = []

    def collect(value, key=None):
        if key in STRUCTURAL_FIELDS:
            return
        if isinstance(value, dict):
            for inner_key, inner_value in value.items():
                collect(inner_value, inner_key)
        elif isinstance(value, list):
            for item in value:
                collect(item, key)
        elif value is not None:
            collected.append(str(value))

    collect(blocks)
    return "\n".join(collected)


# ===== Test the idea, not the example =====

# Details that belong to an example, not to the idea: section numbers (9.1.6, Law 13, clause 1.4), file names,
# lab numbers. Plain numbers such as scores (0.81) are not example details.
EXAMPLE_DETAIL_PATTERN = re.compile(
    r"\b(?:(?:law|lab|rule|clause|section|article|step|chapter)\s+\d+(?:\.\d+)*|\d+\.\d+\.\d+(?:\.\d+)?|[\w-]+\.(?:py|js|mjs|ts|md|yaml|yml|json|csv|pdf|txt))\b",
    re.I)


def example_details(text):
    """Example details a sentence names, without those it explains right away in brackets."""
    found = []
    for match in EXAMPLE_DETAIL_PATTERN.finditer(str(text or "")):
        after = str(text)[match.end():match.end() + 3]
        if not after.lstrip().startswith("("):
            found.append(match.group(0))
    return found


def check_example_details(blueprint, problems):
    """A quiz must be answerable by a learner who learned the idea, without knowing the example by heart.

    - A predict or check question may name an example detail (a clause number, a file, a lab) only if an
      earlier block, in this chapter or an earlier one, already showed it, or the question explains it in brackets.
    - No answer option may be only an example detail: picking "9.1.6" tests memory of the example, not the idea.
    """
    shown_before = ""
    for chapter in blueprint.get("chapters") or []:
        for block in chapter.get("blocks") or []:
            if block.get("type") in ("predict", "check"):
                question = str(block.get("question") or "")
                for detail in example_details(question):
                    if detail.lower() not in shown_before.lower():
                        problems.error(block.get("id"), f"the question names '{detail}', which no earlier block explains. "
                                       "Explain the example first (what it is, and this detail), or say it in brackets "
                                       "right after it, for example '9.1.6 (the service height rule)'")
                for option in block.get("options") or []:
                    option_text = str(option.get("text") or "").strip()
                    leftover = EXAMPLE_DETAIL_PATTERN.sub("", option_text).strip(" .,:;-()")
                    if EXAMPLE_DETAIL_PATTERN.search(option_text) and len(leftover) < 4:
                        problems.error(block.get("id"), f"option '{option_text}' is only a detail of the example, "
                                       "so it tests memory of the example, not the idea. Write the option as what that choice means")
            shown_before += "\n" + blocks_text([block])


def check_bridges_and_recaps(blueprint, problems):
    """Bridges, carried ideas and recaps name only what the blocks they point to actually show."""
    chapters = blueprint.get("chapters") or []
    chapter_positions = {chapter.get("id"): position for position, chapter in enumerate(chapters)}
    glossary_terms = {str(entry.get("term", "")).lower() for entry in blueprint.get("glossary") or [] if entry.get("term")}
    known_ideas = {idea.get("id"): idea for idea in blueprint.get("known_ideas") or []}
    carried_ideas = {}                 # idea id -> (chapter, carried item, the blocks that show it)

    # Each carried idea is shown by named blocks in its own chapter, and those blocks show what it names
    for chapter in chapters:
        blocks_by_id = {block.get("id"): block for block in chapter.get("blocks") or []}
        for carried in chapter.get("carries_forward") or []:
            shown_by = carried.get("shown_by") or []
            if not shown_by:
                problems.error(carried.get("id"), "needs shown_by: the blocks in this chapter that show this idea")
            showing_blocks = []
            for block_id in shown_by:
                if block_id not in blocks_by_id:
                    problems.error(carried.get("id"), f"shown_by names '{block_id}', which is not a block in chapter '{chapter.get('id')}'")
                elif blocks_by_id[block_id].get("type") == "recap":
                    problems.error(carried.get("id"), f"shown_by names the recap '{block_id}'; name the blocks that teach it")
                else:
                    showing_blocks.append(blocks_by_id[block_id])
            for name in missing_concepts(carried.get("idea"), blocks_text(showing_blocks), glossary_terms) if showing_blocks else []:
                problems.error(carried.get("id"), f"names '{name}', but its shown_by blocks never show it")
            carried_ideas[carried.get("id")] = (chapter, carried, showing_blocks)

    for chapter in chapters:
        chapter_id = chapter.get("id")
        blocks = chapter.get("blocks") or []

        # bridge_in recalls ideas this chapter brings in, and names only what their chapters showed
        bridge_in = chapter.get("bridge_in") or {}
        if isinstance(bridge_in, dict):
            recalled = bridge_in.get("recalls") or []
            if not recalled:
                problems.error(chapter_id, "bridge_in needs recalls: the brought-in ideas it reminds the learner of")
            recalled_text = []
            for idea_id in recalled:
                if idea_id not in (chapter.get("brings_in") or []):
                    problems.error(chapter_id, f"bridge_in recalls '{idea_id}', which is not in brings_in")
                if idea_id in known_ideas:
                    recalled_text.append(known_ideas[idea_id])
                elif idea_id in carried_ideas:
                    recalled_text.append(carried_ideas[idea_id][1])
                    recalled_text.extend(carried_ideas[idea_id][2])
            for name in missing_concepts(bridge_in.get("text"), blocks_text(recalled_text), glossary_terms):
                problems.error(chapter_id, f"bridge_in names '{name}', but no recalled idea or the blocks that showed it mention it")

        # bridge_out points to a later chapter (or beyond) that really shows what it names
        bridge_out = chapter.get("bridge_out") or {}
        if isinstance(bridge_out, dict):
            target = bridge_out.get("points_to")
            is_last_chapter = chapter_positions.get(chapter_id) == len(chapters) - 1
            if target == "beyond":
                if not is_last_chapter:
                    problems.error(chapter_id, "bridge_out points_to 'beyond', but only the last chapter may")
            elif target not in chapter_positions:
                problems.error(chapter_id, f"bridge_out points_to '{target}', which is not a chapter (or 'beyond')")
            elif chapter_positions[target] <= chapter_positions[chapter_id]:
                problems.error(chapter_id, f"bridge_out points_to '{target}', which does not come later")
            else:
                target_blocks = chapters[chapter_positions[target]].get("blocks") or []
                for name in missing_concepts(bridge_out.get("text"), blocks_text(target_blocks), glossary_terms):
                    problems.error(chapter_id, f"bridge_out names '{name}', but chapter '{target}' never shows it")

        # Each recap sums up named blocks of this chapter and names only what they show
        blocks_by_id = {block.get("id"): block for block in blocks}
        for block in blocks:
            if block.get("type") != "recap":
                continue
            summed_blocks = []
            for block_id in block.get("sums_up") or []:
                if block_id not in blocks_by_id or blocks_by_id[block_id].get("type") == "recap":
                    problems.error(block.get("id"), f"sums_up names '{block_id}', which is not a teaching block in this chapter")
                else:
                    summed_blocks.append(blocks_by_id[block_id])
            if not block.get("sums_up"):
                problems.error(block.get("id"), "needs sums_up: the blocks of this chapter it summarises")
            for name in missing_concepts(block.get("text"), blocks_text(summed_blocks), glossary_terms) if summed_blocks else []:
                problems.error(block.get("id"), f"names '{name}', but the blocks it sums up never show it")


FIGURE_KINDS = {"flow", "bars", "svg", "tokens", "scatter", "grid", "frames", "tiles"}
DATA_FIGURE_KINDS = {"bars", "tokens", "scatter", "grid", "tiles"}   # kinds a frames figure can step through
# The data fields of each kind: computed_by must print exactly these, as JSON
FIGURE_DATA_FIELDS = {"bars": ["bars"], "tokens": ["rows"], "scatter": ["points"], "grid": ["rows", "columns", "values"],
                      "frames": ["frames"], "tiles": ["tiles"]}
TILE_STATES = {"closed", "open", "picked", "hot"}
MOST_TILES = 12
MOST_TILE_LABEL = 10        # characters: a tile is about 50 px wide at phone width
EXTRAS = {"animation", "play"}  # picture-ladder steps 3 and 4: built only after the author says yes in Discover
PLAY_DEALS = {10, 100}
PLAY_OUTCOME_RANGE = (2, 4)
PLAY_CASE_RANGE = (2, 12)
MOST_SCATTER_POINTS = 12
MOST_GRID_SIDE = 8
FRAME_COUNT_RANGE = (2, 8)
LONGEST_FRAME_BUTTON = 12   # characters: frame buttons share one row at phone width


def check_data_figure_shape(figure, where, problems):
    """Field shapes inside tokens, scatter, grid and frames figures."""
    if figure.get("kind") == "tokens":
        check_list_shape(figure.get("rows"), "figure_token_row", f"{where}.rows", problems)
        for index, row in enumerate(figure.get("rows") or []):
            if isinstance(row, dict):
                check_list_shape(row.get("tokens"), "figure_token", f"{where}.rows item {index + 1}.tokens", problems)
    if figure.get("kind") == "scatter":
        check_list_shape(figure.get("points"), "figure_point", f"{where}.points", problems)
    if figure.get("kind") == "tiles":
        check_list_shape(figure.get("tiles"), "figure_tile", f"{where}.tiles", problems)
    if figure.get("kind") == "frames":
        check_list_shape(figure.get("frames"), "figure_frame", f"{where}.frames", problems)
        for index, frame in enumerate(figure.get("frames") or []):
            if isinstance(frame, dict) and isinstance(frame.get("figure"), dict):
                check_item_shape(frame["figure"], "figure", f"{where}.frames item {index + 1}.figure", problems)
                check_data_figure_shape(frame["figure"], f"{where}.frames item {index + 1}.figure", problems)
    if "computed_by" in figure:
        check_item_shape(figure.get("computed_by") or {}, "computed_by", f"{where}.computed_by", problems)


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_data_figure(diagram_id, figure, problems, inside_frames=False):
    """Rules for the picture kinds that show data: tokens, scatter, grid, bars and frames."""
    kind = figure.get("kind")
    if kind == "tokens":
        rows = figure.get("rows") or []
        if not rows:
            problems.error(diagram_id, "a tokens figure needs rows: each a list of tokens, with an optional label")
        hot = sum(1 for row in rows for token in (row.get("tokens") or []) if token.get("hot"))
        if hot > MOST_HIGHLIGHTED_BOXES:
            problems.error(diagram_id, f"{hot} tokens are hot; highlight at most {MOST_HIGHLIGHTED_BOXES}")
    elif kind == "scatter":
        points = figure.get("points") or []
        if not 2 <= len(points) <= MOST_SCATTER_POINTS:
            problems.error(diagram_id, f"a scatter figure needs 2 to {MOST_SCATTER_POINTS} points; it has {len(points)}")
        for point in points:
            if not (is_number(point.get("x")) and is_number(point.get("y"))):
                problems.error(diagram_id, f"point '{point.get('label')}' needs number x and y")
        labels = [point.get("label") for point in points]
        for label in figure.get("highlight") or []:
            if label not in labels:
                problems.error(diagram_id, f"highlight '{label}' is not a point label")
        if len(figure.get("highlight") or []) > MOST_HIGHLIGHTED_BOXES:
            problems.error(diagram_id, f"highlight at most {MOST_HIGHLIGHTED_BOXES} points")
    elif kind == "grid":
        rows, columns, values = figure.get("rows") or [], figure.get("columns") or [], figure.get("values") or []
        if not (1 <= len(rows) <= MOST_GRID_SIDE and 1 <= len(columns) <= MOST_GRID_SIDE):
            problems.error(diagram_id, f"a grid figure needs 1 to {MOST_GRID_SIDE} rows and columns, so it reads at phone width")
        if len(values) != len(rows) or any(not isinstance(row, list) or len(row) != len(columns) for row in values):
            problems.error(diagram_id, "grid values must have one row per row label and one number per column label")
        elif any(not is_number(value) or not 0 <= value <= 1 for row in values for value in row):
            problems.error(diagram_id, "grid values must be numbers from 0 to 1 (they set each cell's shade)")
        if figure.get("highlight_row") is not None and figure.get("highlight_row") not in rows:
            problems.error(diagram_id, f"highlight_row '{figure.get('highlight_row')}' is not a row label")
    elif kind == "tiles":
        tiles = figure.get("tiles") or []
        if not 1 <= len(tiles) <= MOST_TILES:
            problems.error(diagram_id, f"a tiles figure needs 1 to {MOST_TILES} tiles; it has {len(tiles)}")
        for tile in tiles:
            if tile.get("state") not in TILE_STATES:
                problems.error(diagram_id, f"tile '{tile.get('label')}' needs state: one of {', '.join(sorted(TILE_STATES))}")
            if len(str(tile.get("label", ""))) > MOST_TILE_LABEL:
                problems.error(diagram_id, f"tile label '{tile.get('label')}' is longer than {MOST_TILE_LABEL} characters; it will not fit a tile on a phone")
        if sum(1 for tile in tiles if tile.get("state") == "hot") > MOST_HIGHLIGHTED_BOXES:
            problems.error(diagram_id, f"highlight at most {MOST_HIGHLIGHTED_BOXES} tiles as hot")
    elif kind == "frames":
        if inside_frames:
            problems.error(diagram_id, "a frame cannot hold another frames figure")
            return
        frames = figure.get("frames") or []
        if not FRAME_COUNT_RANGE[0] <= len(frames) <= FRAME_COUNT_RANGE[1]:
            problems.error(diagram_id, f"a frames figure needs {FRAME_COUNT_RANGE[0]} to {FRAME_COUNT_RANGE[1]} frames")
        if figure.get("control") not in ("slider", "buttons"):
            problems.error(diagram_id, "a frames figure needs control: slider (an ordered setting, such as temperature) or buttons (separate cases)")
        if is_missing(figure.get("control_label")):
            problems.error(diagram_id, "a frames figure needs control_label: what the control changes, such as 'Temperature'")
        if figure.get("control") == "buttons":
            for frame in frames:
                if len(str(frame.get("label", ""))) > LONGEST_FRAME_BUTTON:
                    problems.error(diagram_id, f"frame label '{frame.get('label')}' is longer than {LONGEST_FRAME_BUTTON} characters, "
                                   "so the buttons cannot share one row on a phone; shorten it")
            if len(frames) > 3:
                problems.error(diagram_id, "more than 3 frames will not fit as buttons on a phone; use control: slider")
        kinds = {(frame.get("figure") or {}).get("kind") for frame in frames}
        if not kinds <= DATA_FIGURE_KINDS or len(kinds) > 1:
            problems.error(diagram_id, f"every frame holds the same kind of figure, one of: {', '.join(sorted(DATA_FIGURE_KINDS))}")
        for frame in frames:
            check_data_figure(f"{diagram_id} frame '{frame.get('label')}'", frame.get("figure") or {}, problems, inside_frames=True)
        if "animate" in figure and not isinstance(figure.get("animate"), bool):
            problems.error(diagram_id, "animate must be true or false")
    computed_by = figure.get("computed_by")
    if computed_by is not None:
        if kind not in FIGURE_DATA_FIELDS:
            problems.error(diagram_id, f"computed_by works for {', '.join(sorted(FIGURE_DATA_FIELDS))} figures")
        elif computed_by.get("language") != "python":
            problems.error(diagram_id, "computed_by runs python")
    elif not inside_frames and kind in ("scatter", "grid", "frames"):
        problems.error(diagram_id, "the numbers in this picture need computed_by: python that prints them as JSON, so they come "
                       "from a real computation, not from hand")
MOST_FIGURE_BOXES = 9          # density about 4 out of 10: more boxes is two diagrams
MOST_FIGURE_ARROWS = 10
MOST_HIGHLIGHTED_BOXES = 2     # per stage: the highlight list plus the boxes a later stage adds


def check_figures(blueprint, problems):
    """Every diagram has a figure the template can draw, and a growing figure only adds to its earlier stages."""
    diagrams = {block.get("id"): block for chapter in blueprint.get("chapters") or [] for block in chapter.get("blocks") or []
                if block.get("type") == "diagram"}

    def stage_chain(diagram_id, seen=()):
        """The diagram's stages from the first one to this one."""
        block = diagrams.get(diagram_id)
        if block is None or diagram_id in seen:
            return []
        parent_id = (block.get("extends") or {}).get("diagram")
        return (stage_chain(parent_id, seen + (diagram_id,)) if parent_id else []) + [block]

    for diagram_id, block in diagrams.items():
        figure = block.get("figure")
        if not isinstance(figure, dict) or "kind" not in figure:
            continue  # the shape check already reports a missing figure or kind
        kind = figure.get("kind")
        if kind not in FIGURE_KINDS:
            problems.error(diagram_id, f"figure kind must be one of: {', '.join(sorted(FIGURE_KINDS))}")
            continue
        chain = stage_chain(diagram_id)
        first_kind = (chain[0].get("figure") or {}).get("kind") if chain else kind
        if first_kind in FIGURE_KINDS and first_kind != kind:
            problems.error(diagram_id, f"a later stage must keep its first stage's figure kind ('{first_kind}')")
            continue

        if kind == "flow":
            merged_part_ids = []
            for stage in chain:
                for part in (stage.get("figure") or {}).get("parts") or []:
                    if part.get("id") in merged_part_ids:
                        problems.error(diagram_id, f"figure part '{part.get('id')}' is defined twice across its stages")
                    merged_part_ids.append(part.get("id"))
                    row = part.get("row")
                    if stage is block and "row" in part and (not isinstance(row, int) or isinstance(row, bool) or row < 0):
                        problems.error(diagram_id, f"figure part '{part.get('id')}' needs row: a whole number from 0 (top)")
            own_parts = figure.get("parts") or []
            if not own_parts and "extends" not in block:
                problems.error(diagram_id, "a flow figure needs parts")
            if "extends" in block and not own_parts and not figure.get("links"):
                problems.error(diagram_id, "a later stage must add at least one part or link")
            for link in figure.get("links") or []:
                for end in ["from", "to"]:
                    if link.get(end) not in merged_part_ids:
                        problems.error(diagram_id, f"figure link {end} '{link.get(end)}' is not a part of this figure or its earlier stages")
            for part_id in figure.get("highlight") or []:
                if part_id not in merged_part_ids:
                    problems.error(diagram_id, f"figure highlight '{part_id}' is not a part of this figure")
            merged_link_count = sum(len((stage.get("figure") or {}).get("links") or []) for stage in chain)
            if len(merged_part_ids) > MOST_FIGURE_BOXES:
                problems.error(diagram_id, f"the picture has {len(merged_part_ids)} boxes across its stages; keep it to "
                               f"{MOST_FIGURE_BOXES} (cut boxes that always travel together, or make two diagrams)")
            if merged_link_count > MOST_FIGURE_ARROWS:
                problems.error(diagram_id, f"the picture has {merged_link_count} arrows across its stages; keep it to "
                               f"{MOST_FIGURE_ARROWS} (drop arrows the layout already shows)")
            own_part_ids = {part.get("id") for part in own_parts}
            highlighted = set(figure.get("highlight") or []) | (own_part_ids if "extends" in block else set())
            if len(highlighted) > MOST_HIGHLIGHTED_BOXES:
                problems.error(diagram_id, f"this stage highlights {len(highlighted)} boxes ({', '.join(sorted(map(str, highlighted)))}); "
                               f"highlight at most {MOST_HIGHLIGHTED_BOXES}, and a later stage adds at most {MOST_HIGHLIGHTED_BOXES} boxes")

        elif kind == "bars":
            if "extends" in block:
                problems.error(diagram_id, "a bars figure cannot grow; give the later chapter its own figure")
            bars = figure.get("bars") or []
            check_data_figure(diagram_id, figure, problems)
            if not bars:
                problems.error(diagram_id, "a bars figure needs bars")
            for bar in bars:
                if not isinstance(bar.get("value"), (int, float)) or isinstance(bar.get("value"), bool):
                    problems.error(diagram_id, f"bar '{bar.get('label')}' needs a number value")

        elif kind in ("tokens", "scatter", "grid", "frames", "tiles"):
            if "extends" in block or block.get("grows_in"):
                problems.error(diagram_id, f"a {kind} figure cannot grow; use a frames figure to step through states")
            check_data_figure(diagram_id, figure, problems)

        if "animate" in figure and kind != "frames":
            problems.error(diagram_id, "animate works only on a frames figure: it moves between the computed steps")

        if kind == "svg":
            if "extends" in block or block.get("grows_in"):
                problems.error(diagram_id, "an svg figure cannot grow; use a flow figure for a diagram that grows")
            if not str(figure.get("svg", "")).strip().startswith("<svg"):
                problems.error(diagram_id, "an svg figure needs svg: the full <svg ...> markup")


def check_growing_diagrams(blueprint, problems):
    """Every promised diagram stage exists in the chapter it names, and every stage was promised."""
    chapters = blueprint.get("chapters") or []
    chapter_positions = {chapter.get("id"): position for position, chapter in enumerate(chapters)}
    diagram_homes = {}                 # diagram id -> (chapter id, block)
    for chapter in chapters:
        for block in chapter.get("blocks") or []:
            if block.get("type") == "diagram":
                diagram_homes[block.get("id")] = (chapter.get("id"), block)

    def first_stage_of(diagram_id, seen=()):
        """Follow extends links back to the diagram's first stage."""
        home = diagram_homes.get(diagram_id)
        if home is None or diagram_id in seen:
            return None
        parent = (home[1].get("extends") or {}).get("diagram")
        return diagram_id if parent is None else first_stage_of(parent, seen + (diagram_id,))

    # Each later stage: names an earlier diagram, says what it adds, and was promised by the first stage
    stages_by_first_stage = {}
    for diagram_id, (chapter_id, block) in diagram_homes.items():
        extends = block.get("extends")
        if extends is None:
            continue
        parent_id = (extends or {}).get("diagram")
        if parent_id not in diagram_homes:
            problems.error(diagram_id, f"extends '{parent_id}', which is not a diagram block")
            continue
        parent_chapter = diagram_homes[parent_id][0]
        if chapter_positions.get(parent_chapter, 0) >= chapter_positions.get(chapter_id, 0):
            problems.error(diagram_id, f"extends '{parent_id}', which is not in an earlier chapter")
        if is_missing((extends or {}).get("adds")):
            problems.error(diagram_id, "extends needs 'adds': what this stage draws on top of the earlier one")
        root_id = first_stage_of(diagram_id)
        if root_id is None:
            problems.error(diagram_id, "its extends links loop back on themselves")
            continue
        stages_by_first_stage.setdefault(root_id, set()).add(chapter_id)
        if chapter_id not in (diagram_homes[root_id][1].get("grows_in") or []):
            problems.error(diagram_id, f"extends '{root_id}', but '{root_id}' does not list '{chapter_id}' in grows_in")

    # Each first stage: every chapter it promises has a stage that extends it
    for diagram_id, (chapter_id, block) in diagram_homes.items():
        if "grows_in" in block and "extends" in block:
            problems.error(diagram_id, "only a diagram's first stage lists grows_in; later stages use extends")
        for promised_chapter in block.get("grows_in") or []:
            if promised_chapter not in chapter_positions:
                problems.error(diagram_id, f"grows_in names '{promised_chapter}', which is not a chapter")
            elif chapter_positions[promised_chapter] <= chapter_positions[chapter_id]:
                problems.error(diagram_id, f"grows_in names '{promised_chapter}', which does not come later")
            elif promised_chapter not in stages_by_first_stage.get(diagram_id, set()):
                problems.error(diagram_id, f"promises a stage in '{promised_chapter}', but that chapter has no diagram with extends: {{diagram: {diagram_id}}}")

    # A promise written only in prose: the build cannot see it, so it must become grows_in and extends
    for chapter in chapters:
        promising_diagrams = {block.get("id") for block in chapter.get("blocks") or []
                              if block.get("type") == "diagram" and block.get("grows_in")}
        for block in chapter.get("blocks") or []:
            block_text = json.dumps({key: value for key, value in block.items() if key not in {"id", "type", "grows_in", "extends"}}, ensure_ascii=False)
            match = PROMISE_PATTERN.search(block_text)
            if match and not promising_diagrams:
                problems.error(block.get("id"), f"promises something for later chapters in prose (\"{match.group(0)}\"); "
                                                "write it as grows_in on the first diagram and extends on each later stage, or remove the promise")


def check_chapter_links(blueprint, problems):
    """brings_in comes from earlier; carried ideas lead somewhere later; the last chapter points beyond."""
    chapters = blueprint.get("chapters") or []
    chapter_positions = {chapter.get("id"): position for position, chapter in enumerate(chapters)}
    available_ideas = {known_idea.get("id") for known_idea in blueprint.get("known_ideas") or []}

    for position, chapter in enumerate(chapters):
        chapter_id = chapter.get("id", f"chapter {position + 1}")
        for idea_id in chapter.get("brings_in") or []:
            if idea_id not in available_ideas:
                problems.error(chapter_id, f"brings_in '{idea_id}', but no earlier chapter carries it forward and it is not a known idea")
        is_last_chapter = position == len(chapters) - 1
        carried_ideas = chapter.get("carries_forward") or []
        if not carried_ideas and not is_last_chapter:
            problems.error(chapter_id, "carries nothing forward; name what a later chapter uses from it")
        if is_last_chapter and not any("beyond" in (carried.get("used_in") or []) for carried in carried_ideas):
            problems.error(chapter_id, "the last chapter must carry at least one idea forward with used_in: [beyond]")
        for carried in carried_ideas:
            if not carried.get("used_in"):
                problems.error(carried.get("id", chapter_id), "used_in is empty; name a later chapter or 'beyond'")
            for target in carried.get("used_in") or []:
                if target == "beyond":
                    continue
                if target not in chapter_positions:
                    problems.error(carried.get("id", chapter_id), f"used_in names '{target}', which is not a chapter")
                elif chapter_positions[target] <= position:
                    problems.error(carried.get("id", chapter_id), f"used_in names '{target}', which does not come later")
            available_ideas.add(carried.get("id"))


# ===== Checks inside each chapter =====

def check_chapter_teaching_and_tests(chapter, misconception_ids, problems):
    """Opening prediction, tests after teaching, key ideas checked, misconceptions repaired, counts."""
    chapter_id = chapter.get("id", "chapter")
    blocks = chapter.get("blocks") or []
    block_positions = {block.get("id"): position for position, block in enumerate(blocks)}
    blocks_by_id = {block.get("id"): block for block in blocks}
    block_types = [block.get("type") for block in blocks]

    must_know = chapter.get("must_know") or []
    if not 1 <= len(must_know) <= MOST_MUST_KNOW_IDEAS:
        problems.error(chapter_id, f"has {len(must_know)} must_know ideas; keep 1 to {MOST_MUST_KNOW_IDEAS} and split the chapter otherwise")

    # The chapter opens with a prediction and teaches before it tests
    if not block_types or block_types[0] != "predict":
        problems.error(chapter_id, "must open with a predict block")
    first_idea_position = next((position for position, block_type in enumerate(block_types) if block_type == "idea"), None)
    if first_idea_position is None:
        problems.error(chapter_id, "has no idea block, so it never teaches")
        first_idea_position = len(blocks)
    if not any(position > first_idea_position and block_type in TESTS_AFTER_TEACHING for position, block_type in enumerate(block_types)):
        problems.error(chapter_id, "has no check, fill_blanks or explain after the teaching; a prediction before teaching alone does not count")
    if "code" in block_types and "fill_blanks" not in block_types:
        problems.error(chapter_id, "shows code but has no fill_blanks exercise; fill-in-the-blanks is the default exercise for code")
    if "recap" not in block_types:
        problems.error(chapter_id, "has no recap block for the field guide")
    if block_types.count("check") > MOST_CHECKS_PER_CHAPTER:
        problems.error(chapter_id, f"has {block_types.count('check')} quiz checks; keep at most {MOST_CHECKS_PER_CHAPTER}")
    if block_types.count("stretch") > MOST_STRETCHES_PER_CHAPTER:
        problems.error(chapter_id, f"has {block_types.count('stretch')} stretch exercises; keep at most {MOST_STRETCHES_PER_CHAPTER}")

    # Every must_get_right item is tested at least once after the teaching
    for item in chapter.get("must_get_right") or []:
        item_id = item.get("id", chapter_id)
        tested_by = item.get("tested_by") or []
        for block_id in tested_by:
            block = blocks_by_id.get(block_id)
            if block is None:
                problems.error(item_id, f"tested_by names '{block_id}', which is not a block in this chapter")
            elif block.get("type") == "stretch":
                problems.error(item_id, f"tested_by names '{block_id}', an optional stretch; a required goal needs a required test")
            elif block.get("type") not in TESTING_BLOCK_TYPES:
                problems.error(item_id, f"tested_by names '{block_id}', a {block.get('type')} block, which cannot test anything")
        later_tests = [block_id for block_id in tested_by
                       if block_id in blocks_by_id and blocks_by_id[block_id].get("type") in TESTS_AFTER_TEACHING
                       and block_positions[block_id] > first_idea_position]
        if not later_tests:
            problems.error(item_id, "needs a check, fill_blanks or explain after the teaching in tested_by; a prediction alone measures what the learner knew before")

    # Every key idea gets an application check, and every key check tests a key idea in this chapter
    key_idea_ids = {block.get("id") for block in blocks if block.get("type") == "idea" and block.get("key") is True}
    key_check_targets = {block.get("tests") for block in blocks if block.get("type") == "check" and block.get("purpose") == "key"}
    for idea_id in key_idea_ids - key_check_targets:
        problems.error(idea_id, "is a key idea with no check that tests it (add a check with purpose: key and tests: this id)")
    for block in blocks:
        if block.get("type") == "check" and block.get("purpose") == "key" and block.get("tests") not in key_idea_ids:
            problems.error(block.get("id"), f"tests '{block.get('tests')}', which is not a key idea block in this chapter")
        if block.get("type") == "idea" and "key" in block and not isinstance(block.get("key"), bool):
            problems.error(block.get("id"), "key must be true or false")

    # Every misconception the chapter lists gets a pitfall card here
    pitfall_targets = {block.get("misconception") for block in blocks if block.get("type") == "pitfall"}
    for misconception_id in chapter.get("misconceptions") or []:
        if misconception_id not in misconception_ids:
            problems.error(chapter_id, f"lists misconception '{misconception_id}', which is not defined")
        elif misconception_id not in pitfall_targets:
            problems.error(chapter_id, f"lists misconception '{misconception_id}' but has no pitfall block for it")
    for block in blocks:
        if block.get("type") == "pitfall" and block.get("misconception") not in (chapter.get("misconceptions") or []):
            problems.error(block.get("id"), "its misconception must be listed in the chapter's misconceptions")


# ===== Checks on each block, by type =====

def check_block_rhythm(chapter, problems):
    """Test, then reveal: a pitfall check comes right before the pitfall card it opens, and no two pitfalls or two
    checks sit side by side."""
    blocks = chapter.get("blocks") or []
    for before, after in zip(blocks, blocks[1:]):
        if before.get("type") == after.get("type") and before.get("type") in ("pitfall", "check"):
            problems.error(after.get("id"), f"two {before.get('type')} blocks in a row ('{before.get('id')}' and '{after.get('id')}'); "
                           "put each pitfall check right before the card it opens, and space the rest with other blocks")
    for index, block in enumerate(blocks):
        if block.get("type") == "check" and block.get("purpose") == "pitfall":
            following = blocks[index + 1] if index + 1 < len(blocks) else {}
            if not (following.get("type") == "pitfall" and following.get("misconception") == block.get("tests")):
                problems.error(block.get("id"), f"a pitfall check comes right before the pitfall card for '{block.get('tests')}': "
                               "the learner answers first, then the card opens as feedback (test, then reveal)")


def check_answer_options(block_id, options, allowed_range, problems):
    """Options: the right number, exactly one correct, and every option explains itself."""
    smallest, largest = allowed_range
    if not smallest <= len(options or []) <= largest:
        problems.error(block_id, f"has {len(options or [])} options; use {smallest} to {largest}")
    correct_count = sum(1 for option in options or [] if isinstance(option, dict) and option.get("correct") is True)
    if options and correct_count != 1:
        problems.error(block_id, f"has {correct_count} correct options; exactly 1 is needed")
    for option in options or []:
        if not isinstance(option, dict):
            continue
        explanation_field = "why_right" if option.get("correct") is True else "why_wrong"
        if is_missing(option.get(explanation_field)):
            problems.error(block_id, f"option '{str(option.get('text'))[:40]}' needs {explanation_field}")


def check_code_text(where, code, language, problems):
    """Length and comments for code a learner reads: slices, blank exercises and shown solutions."""
    code_lines, comment_count = split_code_lines(code, language)
    if len(code_lines) > MOST_CODE_LINES:
        problems.error(where, f"has {len(code_lines)} code lines; keep it to {MOST_CODE_LINES} (blank and comment lines do not count)")
    needed_comments = max(1, len(code_lines) // CODE_LINES_PER_COMMENT)
    if code_lines and comment_count < needed_comments:
        problems.error(where, f"has {comment_count} comments for {len(code_lines)} code lines; add short line comments (at least 1 per {CODE_LINES_PER_COMMENT} lines)")


def check_recorded_output(where, output, problems):
    if FILE_PATH_PATTERN.match(str(output or "").strip()):
        problems.error(where, "the recorded output looks like a file path; paste the printed text itself so the page can show it")


TEXT_LIST_KEYS = {"beat", "instructions", "hints", "must_know", "notice", "knows", "depends_on", "steps",
                  "recalls", "brings_in", "misconceptions", "tested_by", "used_in", "shown_by", "sums_up", "grows_in", "highlight"}


def check_text_lists(value, where, problems, key=None):
    """Lists of sentences or ids hold plain text. A colon or comma in an unquoted YAML line turns an item into a mapping."""
    if isinstance(value, dict):
        where = str(value["id"]) if isinstance(value.get("id"), str) else where
        for child_key, child in value.items():
            check_text_lists(child, f"{where}.{child_key}" if where else str(child_key), problems, child_key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            if key in TEXT_LIST_KEYS and not isinstance(item, (str, int, float)):
                problems.error(where, f"item {index + 1} should be plain text, got {type(item).__name__}. "
                               "A YAML line with an unquoted ': ' split it; put the line in quotes")
            else:
                check_text_lists(item, where, problems)


def check_hints(block, problems):
    hints = block.get("hints") or []
    if not HINT_LEVEL_RANGE[0] <= len(hints) <= HINT_LEVEL_RANGE[1]:
        problems.error(block.get("id"), f"needs {HINT_LEVEL_RANGE[0]} or {HINT_LEVEL_RANGE[1]} hint levels")


def check_instructions(block, problems):
    instructions = block.get("instructions") or []
    if not 1 <= len(instructions) <= MOST_INSTRUCTION_LINES:
        problems.error(block.get("id"), f"needs 1 to {MOST_INSTRUCTION_LINES} instruction lines")


def check_fill_blanks(block, misconception_ids, problems):
    """Blanks are marked once, each has one right option, and every option has a real result.

    Code (python, javascript): the blanks sit in `code`, and each option's output is recorded from a real run.
    Text: the blanks sit in `text` (a sentence, a rule, a formula). Nothing runs, so each option's result
    names where it comes from: `output_from: source` with the source in `output_source`, or
    `output_from: worked` with the steps in `output_source`.
    """
    block_id = block.get("id", "fill_blanks")
    language = block.get("language")
    is_text = language == TEXT_LANGUAGE
    if language not in CODE_LANGUAGES | {TEXT_LANGUAGE}:
        problems.error(block_id, f"language must be one of: {', '.join(sorted(CODE_LANGUAGES | {TEXT_LANGUAGE}))}")
    check_instructions(block, problems)
    check_hints(block, problems)
    if is_text:
        if "code" in block or "setup" in block or "run_locally" in block:
            problems.error(block_id, "a text exercise holds its passage in `text`; code, setup and run_locally are for code")
        code = block.get("text") or ""
        if not code.strip():
            problems.error(block_id, "needs `text`: the passage with its blanks")
    else:
        if "text" in block:
            problems.error(block_id, "a code exercise holds its code in `code`; `text` is for language: text")
        code = block.get("code") or ""
        if not code.strip():
            problems.error(block_id, "needs `code`: the slice with its blanks")
        check_code_text(f"{block_id} code", BLANK_PATTERN.sub("_", code), language, problems)

    blanks = [blank for blank in block.get("blanks") or [] if isinstance(blank, dict)]
    if not BLANK_COUNT_RANGE[0] <= len(blanks) <= BLANK_COUNT_RANGE[1]:
        problems.error(block_id, f"has {len(blanks)} blanks; use {BLANK_COUNT_RANGE[0]} to {BLANK_COUNT_RANGE[1]} on the lines that carry the idea")
    marked_blank_ids = BLANK_PATTERN.findall(code)
    for blank in blanks:
        if marked_blank_ids.count(blank.get("id")) != 1:
            problems.error(block_id, f"blank '{blank.get('id')}' must appear exactly once in the code as {{{{{blank.get('id')}}}}}")
    for marked_id in set(marked_blank_ids) - {blank.get("id") for blank in blanks}:
        problems.error(block_id, f"the {'text' if is_text else 'code'} marks {{{{{marked_id}}}}}, but no blank has that id")

    correct_outputs = set()
    for blank in blanks:
        blank_where = f"{block_id} blank '{blank.get('id')}'"
        options = [option for option in blank.get("options") or [] if isinstance(option, dict)]
        if not BLANK_OPTION_RANGE[0] <= len(options) <= BLANK_OPTION_RANGE[1]:
            problems.error(blank_where, f"has {len(options)} options; use {BLANK_OPTION_RANGE[0]} to {BLANK_OPTION_RANGE[1]}")
        correct_options = [option for option in options if option.get("correct") is True]
        if len(correct_options) != 1:
            problems.error(blank_where, f"has {len(correct_options)} right options; exactly 1 is needed")
        for option in options:
            option_where = f"{blank_where} option '{str(option.get('text'))[:30]}'"
            if is_missing(option.get("output")):
                problems.error(option_where, "needs its result: what this choice leads to" if is_text
                               else "needs the output recorded from a real run with this option")
            check_recorded_output(option_where, option.get("output"), problems)
            origin = option.get("output_from", None if is_text else "run")
            if is_text:
                if origin not in TEXT_RESULT_ORIGINS:
                    problems.error(option_where, "needs output_from: source (quoted from a named source) or worked (worked out step by step)")
                if is_missing(option.get("output_source")):
                    problems.error(option_where, "needs output_source: the source (with its section) or the steps that give this result")
            elif origin != "run" or "output_source" in option:
                problems.error(option_where, "a code option's output comes from a run; leave out output_from and output_source")
            if option.get("correct") is True:
                if is_missing(option.get("why_right")):
                    problems.error(option_where, "needs why_right")
                if len(correct_options) == 1:
                    correct_outputs.add(normalise_output(option.get("output")))
            else:
                if is_missing(option.get("why_wrong")) or "\n" in str(option.get("why_wrong", "")).strip():
                    problems.error(option_where, "needs why_wrong: a one-line reason")
                if option.get("misconception") not in misconception_ids:
                    problems.error(option_where, "a wrong option must name a defined misconception")
        right_output = normalise_output(correct_options[0].get("output")) if len(correct_options) == 1 else None
        for option in options:
            if option.get("correct") is not True and right_output is not None and normalise_output(option.get("output")) == right_output:
                problems.error(f"{blank_where} option '{str(option.get('text'))[:30]}'",
                               "leads to the same result as the right option, so the learner cannot see what goes wrong; change the passage or the option"
                               if is_text else
                               "prints the same as the right option, so Run cannot show the learner what goes wrong; change the code or the option")
    if len(correct_outputs) > 1:
        problems.error(block_id, "the right options of different blanks record different outputs; with every blank right the program prints one output")


def check_block(block, misconception_ids, problems):
    block_id = block.get("id", "block")
    block_type = block.get("type")

    if block_type == "predict":
        if "options" in block:
            check_answer_options(block_id, block["options"], PREDICT_OPTION_RANGE, problems)
        elif is_missing(block.get("answer")):
            problems.error(block_id, "needs options or an answer")

    elif block_type == "idea":
        if count_sentences(str(block.get("text", ""))) > MOST_IDEA_SENTENCES:
            problems.error(block_id, f"has more than {MOST_IDEA_SENTENCES} sentences; move detail into 'more'")

    elif block_type == "diagram":
        if block.get("shape") not in DIAGRAM_SHAPES:
            problems.error(block_id, f"shape must be one of: {', '.join(sorted(DIAGRAM_SHAPES))}")

    elif block_type == "code":
        code_slice = block.get("slice") or {}
        if code_slice.get("language") not in CODE_LANGUAGES:
            problems.error(block_id, f"slice language must be one of: {', '.join(sorted(CODE_LANGUAGES))}")
        check_code_text(f"{block_id} slice", code_slice.get("code"), code_slice.get("language"), problems)
        check_recorded_output(block_id, code_slice.get("recorded_output"), problems)
        if not 1 <= len(block.get("notice") or []) <= 3:
            problems.error(block_id, "needs 1 to 3 notice prompts telling the learner what to look at")

    elif block_type == "compare":
        check_compare(block, problems)

    elif block_type == "fill_blanks":
        check_fill_blanks(block, misconception_ids, problems)

    elif block_type == "explain":
        check_instructions(block, problems)
        check_hints(block, problems)
        if is_missing(block.get("rubric")):
            problems.error(block_id, "an explain exercise needs a rubric for AI grading")
        for wrong_answer in block.get("common_wrong_answers") or []:
            if wrong_answer.get("misconception") not in misconception_ids:
                problems.error(block_id, f"wrong answer names misconception '{wrong_answer.get('misconception')}', which is not defined")

    elif block_type == "stretch":
        check_instructions(block, problems)
        check_hints(block, problems)
        if block.get("kind") not in {"code", "explain"}:
            problems.error(block_id, "kind must be 'code' or 'explain'")
        if is_missing(block.get("rubric")):
            problems.error(block_id, "a stretch needs a rubric for AI grading")
        if block.get("kind") == "code":
            if block.get("language") not in CODE_LANGUAGES:
                problems.error(block_id, f"a code stretch needs language: {', '.join(sorted(CODE_LANGUAGES))}")
            check_code_text(f"{block_id} reference_solution", block.get("reference_solution"), block.get("language"), problems)

    elif block_type == "play":
        check_play(block, problems)

    elif block_type == "check":
        if block.get("purpose") not in {"key", "pitfall"}:
            problems.error(block_id, "purpose must be 'key' or 'pitfall'; quiz only key ideas and pitfalls")
        if block.get("purpose") == "pitfall" and block.get("tests") not in misconception_ids:
            problems.error(block_id, "a pitfall check must test a defined misconception")
        check_answer_options(block_id, block.get("options"), CHECK_OPTION_RANGE, problems)


def check_play(block, problems):
    """A play block deals games from a case table that code worked out; the page shows the learner's counts beside the
    expected share. The cases and the seeded sample deal come from computed_by, so no chance is typed by hand."""
    block_id = block.get("id", "play")
    deals = block.get("deals") or []
    if not deals or not set(deals) <= PLAY_DEALS or len(set(deals)) != len(deals):
        problems.error(block_id, f"deals lists how many games a tap deals: 10, 100 or both")
    outcomes = [outcome for outcome in block.get("outcomes") or [] if isinstance(outcome, dict)]
    outcome_ids = [outcome.get("id") for outcome in outcomes]
    if not PLAY_OUTCOME_RANGE[0] <= len(outcomes) <= PLAY_OUTCOME_RANGE[1]:
        problems.error(block_id, f"a play block counts {PLAY_OUTCOME_RANGE[0]} to {PLAY_OUTCOME_RANGE[1]} outcomes; it has {len(outcomes)}")
    if len(set(outcome_ids)) != len(outcome_ids):
        problems.error(block_id, "outcome ids must be unique")
    for outcome in outcomes:
        if not 1 <= len(str(outcome.get("short", ""))) <= 2:
            problems.error(block_id, f"outcome '{outcome.get('id')}' needs short: 1 or 2 characters shown in each dealt game, so it never relies on colour")
    if sum(1 for outcome in outcomes if outcome.get("hot")) > 1:
        problems.error(block_id, "mark at most one outcome hot: the one the lesson is about")
    computed_by = block.get("computed_by")
    if not isinstance(computed_by, dict) or computed_by.get("language") != "python":
        problems.error(block_id, "a play block needs computed_by: python that prints its cases and a seeded sample deal as JSON, "
                       "so every chance comes from code, not from hand")
    cases = [case for case in block.get("cases") or [] if isinstance(case, dict)]
    if not PLAY_CASE_RANGE[0] <= len(cases) <= PLAY_CASE_RANGE[1]:
        problems.error(block_id, f"a play block needs {PLAY_CASE_RANGE[0]} to {PLAY_CASE_RANGE[1]} cases; it has {len(cases)} (run record_outputs.py)")
    weights = [case.get("weight") for case in cases]
    if any(not is_number(weight) or weight <= 0 for weight in weights):
        problems.error(block_id, "every case needs a weight above 0: its chance")
    elif cases and abs(sum(weights) - 1) > 1e-6:
        problems.error(block_id, f"the case weights add up to {sum(weights):.4f}, not 1; every game must land in exactly one case")
    for case in cases:
        if case.get("outcome") not in outcome_ids:
            problems.error(block_id, f"case '{case.get('label')}' counts '{case.get('outcome')}', which is not an outcome")
    for outcome_id in set(outcome_ids) - {case.get("outcome") for case in cases}:
        problems.error(block_id, f"no case leads to outcome '{outcome_id}'")
    sample = block.get("sample") if isinstance(block.get("sample"), dict) else {}
    counts = sample.get("counts") if isinstance(sample.get("counts"), dict) else {}
    if sample.get("games") not in set(deals):
        problems.error(block_id, "sample.games must be one of the deal sizes: the seeded deal shown in screenshots and read-along")
    elif set(counts) - set(outcome_ids) or sum(value for value in counts.values() if is_number(value)) != sample.get("games"):
        problems.error(block_id, "sample.counts must count each outcome, adding up to sample.games")


def check_extras(blueprint, problems):
    """Picture-ladder steps 3 and 4 (animation, play) cost build time, so they are built only after the author agreed in Discover."""
    agreed = (blueprint.get("lesson") or {}).get("agreed_extras") or []
    for extra in agreed:
        if extra not in EXTRAS:
            problems.error("lesson.agreed_extras", f"'{extra}' is not an extra; use {', '.join(sorted(EXTRAS))}")
    for chapter in blueprint.get("chapters") or []:
        for block in chapter.get("blocks") or []:
            figure = block.get("figure") if isinstance(block.get("figure"), dict) else {}
            if figure.get("animate") is True and "animation" not in agreed:
                problems.error(block.get("id"), "an animated picture is built only after a yes in Discover: ask, then add 'animation' to lesson.agreed_extras")
            if block.get("type") == "play" and "play" not in agreed:
                problems.error(block.get("id"), "a play block is built only after a yes in Discover: ask, then add 'play' to lesson.agreed_extras")


# ===== The lesson arc and the text budget =====

def words_in(text):
    return len(re.findall(r"[\w'’,.%-]+", str(text or "")))


def check_arc(blueprint, problems):
    """One story with milestones: a big idea, a beat per chapter in arc order, a milestone, and an open question that
    the next chapter answers."""
    chapters = blueprint.get("chapters") or []
    big_idea = (blueprint.get("lesson") or {}).get("big_idea")
    if big_idea is not None and count_sentences(big_idea) > 1:
        problems.error("lesson.big_idea", "the big idea is one sentence: what the learner should still say a month later")
    last_position = -1
    for position, chapter in enumerate(chapters):
        chapter_id = chapter.get("id", "chapter")
        beats = chapter.get("beat")
        beats = beats if isinstance(beats, list) else [beats] if beats is not None else []
        for beat in beats:
            if beat not in ARC_BEATS:
                problems.error(chapter_id, f"beat '{beat}' is not a beat of the arc: {', '.join(ARC_BEATS)}")
            else:
                if ARC_BEATS.index(beat) < last_position:
                    problems.error(chapter_id, f"beat '{beat}' comes back after a later beat; keep the arc in order ({' → '.join(ARC_BEATS)})")
                last_position = max(last_position, ARC_BEATS.index(beat))
        if position == 0 and beats and "hook" not in beats:
            problems.error(chapter_id, "the first chapter is the hook: it opens the question the lesson answers")
        if position == len(chapters) - 1 and beats and "payoff" not in beats:
            problems.error(chapter_id, "the last chapter is the payoff: it answers the first question")
        milestone = chapter.get("milestone")
        if milestone is not None and not str(milestone).startswith("I can "):
            problems.error(chapter_id, "milestone starts 'I can ': what the learner can do at the end of this chapter")
        open_question = chapter.get("open_question")
        is_last = position == len(chapters) - 1
        if is_last and open_question:
            problems.error(chapter_id, "the last chapter closes the story: it answers questions, so it leaves no open_question")
        elif not is_last and is_missing(open_question):
            problems.error(chapter_id, "needs open_question: the question this chapter leaves open, which the next chapter answers")
        elif open_question and not str(open_question).strip().endswith("?"):
            problems.error(chapter_id, "open_question is a question: end it with '?'")


def picture_text(block):
    """The words a picture shows before anyone taps: its caption, step captions, and text drawn in an svg (a totals row)."""
    pieces = []
    figure = block.get("figure") if isinstance(block.get("figure"), dict) else {}
    pieces.append(str((block.get("brief") or {}).get("understand", "")))
    for frame in figure.get("frames") or []:
        pieces.append(str(frame.get("caption", "")))
        inner = frame.get("figure") or {}
        pieces += [str(tile.get("inside", "")) + " " + str(tile.get("note", "")) for tile in inner.get("tiles") or []]
    pieces += [str(tile.get("inside", "")) + " " + str(tile.get("note", "")) for tile in figure.get("tiles") or []]
    pieces += re.findall(r">([^<>]+)<", str(figure.get("svg", "")))
    return " \n ".join(pieces)


RATIO_PATTERN = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:times\s+)?(?:in|of|out of)\s+(?:every\s+)?\d+\b|\b\d+(?:\.\d+)?\s*%")


def plain(text):
    return re.sub(r"\s+", " ", re.sub(r"[^\w%,.\s-]", " ", str(text or "").lower())).strip()


def check_text_budget(blueprint, problems):
    """Ideas at most 2 sentences and about 45 words; feedback one sentence; captions about 25 words."""
    for chapter in blueprint.get("chapters") or []:
        for block in chapter.get("blocks") or []:
            block_id = block.get("id", "block")
            if block.get("type") == "idea" and words_in(block.get("text")) > MOST_IDEA_WORDS:
                problems.error(block_id, f"the idea has {words_in(block.get('text'))} words; keep it to about {MOST_IDEA_WORDS} (move detail into 'more')")
            options = list(block.get("options") or []) if block.get("type") in ("predict", "check") else []
            for blank in block.get("blanks") or [] if block.get("type") == "fill_blanks" else []:
                options += [option for option in (blank.get("options") or []) if isinstance(option, dict)]
            for option in options:
                if not isinstance(option, dict):
                    continue
                for field in ("why_right", "why_wrong"):
                    if option.get(field) and count_sentences(option[field]) > MOST_FEEDBACK_SENTENCES:
                        problems.error(block_id, f"{field} of '{str(option.get('text'))[:30]}' is more than one sentence; feedback says one thing")
            if block.get("type") == "diagram":
                captions = [("caption", (block.get("brief") or {}).get("understand"))]
                captions += [(f"step '{frame.get('label')}' caption", frame.get("caption")) for frame in (block.get("figure") or {}).get("frames") or []]
                for name, caption in captions:
                    if caption and words_in(caption) > MOST_CAPTION_WORDS:
                        problems.error(block_id, f"the {name} has {words_in(caption)} words; keep it to about {MOST_CAPTION_WORDS}, so the picture does the talking")


def check_no_early_answers(blueprint, problems):
    """Nothing gives a guess's answer away before the guess: not a title, a goal, a milestone, nor a caption or totals
    row above it in the same chapter. A chance or count in the right option ("2 in 3") that no wrong option shares is
    the giveaway; so is the whole right option when it is three words or more."""
    chapters = blueprint.get("chapters") or []
    lesson = blueprint.get("lesson") or {}
    everywhere = [("a chapter title", chapter.get("title")) for chapter in chapters]
    everywhere += [("an objective", objective.get("text")) for objective in lesson.get("objectives") or []]
    for position, chapter in enumerate(chapters):
        shown = everywhere + [(f"the milestone of '{earlier.get('id')}'", earlier.get("milestone")) for earlier in chapters[:position + 1]]
        for block in chapter.get("blocks") or []:
            if block.get("type") == "predict" and block.get("options"):
                right = next((option for option in block["options"] if isinstance(option, dict) and option.get("correct")), None)
                wrong_text = plain(" ".join(str(option.get("text")) for option in block["options"] if isinstance(option, dict) and not option.get("correct")))
                if right:
                    giveaways = [ratio for ratio in RATIO_PATTERN.findall(str(right.get("text"))) if plain(ratio) not in wrong_text]
                    if len(plain(right.get("text")).split()) >= 3:
                        giveaways.append(str(right.get("text")))
                    for giveaway in giveaways:
                        for where, text in shown:
                            if text and re.search(r"(?<![\w])" + re.escape(plain(giveaway)) + r"(?![\w])", plain(text)):
                                problems.error(block.get("id"), f"its answer '{giveaway}' already shows in {where}, before the guess; "
                                               "reword that text so the guess is still a guess")
            if block.get("type") == "diagram":
                shown = shown + [(f"the picture '{block.get('id')}'", picture_text(block))]


def check_no_copying(blueprint, problems):
    """A blank's right option is never written word for word in the block just above it: the blank would test copying."""
    for chapter in blueprint.get("chapters") or []:
        blocks = chapter.get("blocks") or []
        for index, block in enumerate(blocks):
            if block.get("type") != "fill_blanks" or index == 0:
                continue
            above = plain(blocks_text([blocks[index - 1]]) + " " + (picture_text(blocks[index - 1]) if blocks[index - 1].get("type") == "diagram" else ""))
            for blank in block.get("blanks") or []:
                for option in blank.get("options") or []:
                    if not isinstance(option, dict) or not option.get("correct"):
                        continue
                    phrase = plain(option.get("text"))
                    if len(phrase) >= 4 and re.search(r"(?<![\w])" + re.escape(phrase) + r"(?![\w])", above):
                        problems.error(block.get("id"), f"the right option '{option.get('text')}' is written word for word in "
                                       f"'{blocks[index - 1].get('id')}' just above; the blank would test copying, not the idea")


def check_fair_options(blueprint, problems):
    """The right option is not much longer than the wrong ones, so length never gives it away."""
    for chapter in blueprint.get("chapters") or []:
        for block in chapter.get("blocks") or []:
            groups = [block.get("options") or []] if block.get("type") in ("predict", "check") else []
            if block.get("type") == "fill_blanks":
                groups += [blank.get("options") or [] for blank in block.get("blanks") or [] if isinstance(blank, dict)]
            for options in groups:
                options = [option for option in options if isinstance(option, dict)]
                right = [len(str(option.get("text"))) for option in options if option.get("correct")]
                wrong = [len(str(option.get("text"))) for option in options if not option.get("correct")]
                if right and wrong and right[0] > FAIR_LENGTH_RATIO * max(wrong) and right[0] - max(wrong) >= FAIR_LENGTH_GAP:
                    problems.error(block.get("id"), f"the right option is {right[0]} characters, the longest wrong one {max(wrong)}; "
                                   "a learner can guess it by length. Shorten it, or make a wrong option as full")


def check_compare(block, problems):
    """differs_at is the number of the first step where the options part ways."""
    block_id = block.get("id", "compare")
    options = [option for option in block.get("options") or [] if isinstance(option, dict)]
    if len(options) < 2:
        problems.error(block_id, "a compare block needs at least 2 options")
    differs_at = block.get("differs_at")
    if not isinstance(differs_at, int) or isinstance(differs_at, bool) or differs_at < 1:
        problems.error(block_id, "differs_at must be a step number (1 for the first step)")
        return
    step_lists = [option.get("steps") or [] for option in options]
    if any(len(steps) < differs_at for steps in step_lists):
        problems.error(block_id, f"differs_at is {differs_at}, but an option has fewer steps")
        return
    if len({str(steps[differs_at - 1]) for steps in step_lists}) < 2:
        problems.error(block_id, f"the options do not differ at step {differs_at}")
    for step_number in range(1, differs_at):
        if len({str(steps[step_number - 1]) for steps in step_lists}) > 1:
            problems.error(block_id, f"the options already differ at step {step_number}; differs_at must name the first differing step")
            break


# ===== Running the code at build time to prove the recorded outputs =====

def run_program(language, code, shared_modules):
    """Run one program with the real interpreter and return what it printed, plus the error line if it failed."""
    with tempfile.TemporaryDirectory() as work_folder:
        for module_name, source in (shared_modules or {}).items():
            Path(work_folder, f"{module_name}.py").write_text(source, encoding="utf-8")
        if language == "python":
            program_path = Path(work_folder, "program.py")
            command = [sys.executable, "-E", "-s", str(program_path)]
        else:
            program_path = Path(work_folder, "program.mjs")
            command = ["node", str(program_path)]
        program_path.write_text(code, encoding="utf-8")
        try:
            completed = subprocess.run(command, cwd=work_folder, capture_output=True, text=True, timeout=RUN_TIME_LIMIT_SECONDS)
        except subprocess.TimeoutExpired:
            return f"timed out after {RUN_TIME_LIMIT_SECONDS} s", False
    output = completed.stdout
    if completed.returncode != 0:
        error_lines = [line for line in completed.stderr.splitlines() if line.strip()]
        error_line = next((line for line in reversed(error_lines) if re.match(r"^\w*(Error|Exception)\b", line.strip())), error_lines[-1] if error_lines else "error")
        output = (output.rstrip("\n") + "\n" + error_line.strip()).strip()
    return output, completed.returncode == 0


def build_runs(blueprint):
    """Every program the page will show the output of, with the output it claims."""
    runs = []
    for chapter_index, chapter in enumerate(blueprint.get("chapters") or []):
        for block_index, block in enumerate(chapter.get("blocks") or []):
            block_id = block.get("id")
            if block.get("type") == "code":
                code_slice = block.get("slice") or {}
                if "run_locally" not in code_slice:
                    runs.append({"name": f"{block_id}: slice", "language": code_slice.get("language"),
                                 "code": "\n".join(part for part in [code_slice.get("setup"), code_slice.get("code")] if part),
                                 "claimed_output": code_slice.get("recorded_output"),
                                 "target": (chapter_index, block_index)})
            if block.get("type") == "fill_blanks" and "run_locally" not in block and block.get("language") != TEXT_LANGUAGE:
                blanks = [blank for blank in block.get("blanks") or [] if isinstance(blank, dict)]
                right_text = {}
                for blank in blanks:
                    for option in blank.get("options") or []:
                        if option.get("correct") is True:
                            right_text[blank.get("id")] = str(option.get("text"))
                for blank_index, blank in enumerate(blanks):
                    for option_index, option in enumerate(blank.get("options") or []):
                        # Fill this blank with the option and every other blank with its right answer
                        chosen = dict(right_text, **{blank.get("id"): str(option.get("text"))})
                        filled_code = BLANK_PATTERN.sub(lambda match: chosen.get(match.group(1), match.group(0)), block.get("code") or "")
                        runs.append({"name": f"{block_id}: blank '{blank.get('id')}' = {str(option.get('text'))[:30]}",
                                     "language": block.get("language"),
                                     "code": "\n".join(part for part in [block.get("setup"), filled_code] if part),
                                     "claimed_output": option.get("output"),
                                     "target": (chapter_index, block_index, blank_index, option_index)})
    return runs


def figure_runs(blueprint):
    """Every picture whose numbers come from computed_by: the code, and the data the blueprint claims."""
    runs = []
    for chapter_index, chapter in enumerate(blueprint.get("chapters") or []):
        for block_index, block in enumerate(chapter.get("blocks") or []):
            if block.get("type") == "play" and isinstance(block.get("computed_by"), dict):
                # A play block's cases and seeded sample live on the block itself
                fields = ["cases", "sample"]
                runs.append({"name": f"{block.get('id')}: play", "code": block["computed_by"].get("code") or "", "fields": fields,
                             "claimed": {field: block.get(field) for field in fields}, "in_figure": False,
                             "skip": block["computed_by"].get("run_locally"), "target": (chapter_index, block_index)})
                continue
            figure = block.get("figure") if block.get("type") == "diagram" else None
            if not isinstance(figure, dict) or not isinstance(figure.get("computed_by"), dict):
                continue
            computed_by = figure["computed_by"]
            fields = FIGURE_DATA_FIELDS.get(figure.get("kind"), [])
            runs.append({"name": f"{block.get('id')}: figure", "code": computed_by.get("code") or "", "fields": fields,
                         "claimed": {field: figure.get(field) for field in fields}, "in_figure": True,
                         "skip": computed_by.get("run_locally"), "target": (chapter_index, block_index)})
    return runs


def computed_figure_data(run, shared_modules):
    """Run a figure's code and read the JSON it prints. Returns (data or None, the printed text)."""
    printed, _ = run_program("python", run["code"], shared_modules)
    try:
        data = json.loads(printed)
    except ValueError:
        return None, printed
    return data, printed


def run_tests(blueprint, problems):
    """Run every program and compare what it prints with what the blueprint claims."""
    for run in figure_runs(blueprint):
        if run["skip"]:
            print(f"SKIP     {run['name']}: run_locally ({run['skip'].get('why', '')})")
            continue
        data, printed = computed_figure_data(run, blueprint.get("shared_modules"))
        if data is None:
            problems.error(run["name"], "computed_by must print one JSON object. It printed:\n" + "\n".join("           | " + line for line in printed.splitlines()[-5:]))
            continue
        actual = {field: data.get(field) for field in run["fields"]}
        matches = json.dumps(actual, sort_keys=True) == json.dumps(run["claimed"], sort_keys=True, default=str)
        print(f"RUN      {run['name']}: {'data matches' if matches else 'DATA DIFFERS'}")
        if not matches:
            problems.error(run["name"], ("the numbers are not what computed_by prints" if run["in_figure"] else "the cases or the sample deal are not what computed_by prints") + "; run record_outputs.py")
    for run in build_runs(blueprint):
        actual_output, _ = run_program(run["language"], run["code"], blueprint.get("shared_modules"))
        matches = normalise_output(actual_output) == normalise_output(run["claimed_output"])
        print(f"RUN      {run['name']}: {'output matches' if matches else 'OUTPUT DIFFERS'}")
        if not matches:
            problems.error(run["name"], "the recorded output is not what the code prints. Real output:\n"
                           + "\n".join("           | " + line for line in normalise_output(actual_output).splitlines()))


# ===== Running every check and reporting =====

def check_blueprint(blueprint, run_code=False):
    """Run every rule and return the collected problems."""
    problems = ProblemList()
    if not isinstance(blueprint, dict) or "lesson" not in blueprint:
        problems.error("blueprint", "must start with a 'lesson' section")
        return problems
    check_blueprint_shape(blueprint, problems)
    check_text_lists(blueprint.get("chapters"), "", problems)
    from theme import theme_problems
    for theme_problem in theme_problems(blueprint.get("theme")):
        problems.error("theme", theme_problem)
    check_ids(blueprint, problems)
    check_lesson_and_scope(blueprint, problems)
    check_facts_misconceptions_glossary(blueprint, problems)
    check_every_objective_is_served(blueprint, problems)
    check_chapter_links(blueprint, problems)
    check_growing_diagrams(blueprint, problems)
    check_bridges_and_recaps(blueprint, problems)
    check_figures(blueprint, problems)
    check_example_details(blueprint, problems)
    check_extras(blueprint, problems)
    check_arc(blueprint, problems)
    check_text_budget(blueprint, problems)
    check_no_early_answers(blueprint, problems)
    check_no_copying(blueprint, problems)
    check_fair_options(blueprint, problems)
    misconception_ids = {item.get("id") for item in blueprint.get("misconceptions") or []}
    for chapter in blueprint.get("chapters") or []:
        check_chapter_teaching_and_tests(chapter, misconception_ids, problems)
        check_block_rhythm(chapter, problems)
        for block in chapter.get("blocks") or []:
            if block.get("type") in BLOCK_TYPES:
                check_block(block, misconception_ids, problems)
    if run_code:
        run_tests(blueprint, problems)
    return problems


def check_page_is_current(blueprint, page_path, problems):
    """The page must carry exactly this blueprint, so nobody publishes a stale or hand-edited page."""
    page_file = Path(page_path)
    if not page_file.exists():
        problems.error("page", f"{page_path} does not exist. Build it: python scripts/build_page.py <blueprint> --out {page_path}")
        return
    found = re.search(r"/\*LESSON_DATA_START\*/(.*?)/\*LESSON_DATA_END\*/", page_file.read_text(encoding="utf-8"), re.S)
    if not found:
        problems.error("page", f"{page_path} was not built by build_page.py. Never hand-write the page: build it from the blueprint")
        return
    embedded = json.loads(found.group(1))
    current = json.loads(json.dumps(blueprint, default=str))
    if json.dumps(embedded, sort_keys=True) != json.dumps(current, sort_keys=True):
        problems.error("page", f"{page_path} is stale: it was built from an older blueprint. Rebuild it with build_page.py")
    else:
        print(f"PAGE     {page_path} carries this blueprint")


def main():
    parser = argparse.ArgumentParser(description="Check a lesson blueprint.")
    parser.add_argument("blueprint")
    parser.add_argument("--run-tests", action="store_true", help="run every slice and every blank option, and compare outputs")
    parser.add_argument("--page", help="the built lesson.html: check it was built from this blueprint (not stale)")
    options = parser.parse_args()

    blueprint = load_blueprint(options.blueprint)
    problems = check_blueprint(blueprint, run_code=options.run_tests)
    if options.page:
        check_page_is_current(blueprint, options.page, problems)
    for error in problems.errors:
        print(f"ERROR    {error}")
    for warning in problems.warnings:
        print(f"WARNING  {warning}")
    print(f"\n{len(problems.errors)} errors, {len(problems.warnings)} warnings")
    sys.exit(1 if problems.errors else 0)


if __name__ == "__main__":
    main()
