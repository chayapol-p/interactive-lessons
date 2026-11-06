# Chapter design

How to plan a chapter and its blocks. Every part has a reason; if a part's reason does not apply to a chapter, leave the part out.

## Contents

1. The chapter card
2. Connecting chapters
3. Block types
4. Tagging key concepts and pitfalls
5. Code slices
6. Comparing choices
7. Length, pace and scope

---

## 1. The chapter card

Fill these fields for every chapter before choosing blocks.

**`why_it_matters`**: the problem this chapter solves for the learner, in one or two sentences.
- Why: a learner who cannot see the problem treats the idea as trivia and forgets it.

**`must_know`**: the 1 to 3 ideas the chapter teaches.
- Why: more than 3 ideas in one chapter overloads a learner. If you have more, split the chapter.

**`must_get_right`**: what the learner must be able to *do* correctly by the end. Each item is observable: a prediction, a choice, a fix, a short explanation.
- Why: "knows X" cannot be checked. "Predicts how many chunks a 1,200-token page gives" can.
- Each item has an `id` and a `tested_by` list naming the blocks that check it.

**`evidence`** (inside each `must_get_right` item): how the check proves the learner can do it. One line.
- Why: writing the evidence exposes weak tests. If the evidence is "they picked option B", ask whether a guess could pick B too.

**`brings_in`**: ids of ideas carried forward by earlier chapters that this chapter uses.
- Why: it forces the order to be right and tells the bridge what to recall.

**`carries_forward`**: ideas this chapter hands on, each with an `id`, a one-line `idea`, `used_in` (later chapter ids, or `beyond` if it is used after the lesson), and `shown_by` (the blocks here that teach it). Everything the idea names must appear in those blocks (checked).
- Why: it shows the learner why the idea matters later, and lets the checker catch ideas that lead nowhere.

**`misconceptions`**: ids from the misconception list that this chapter must repair.
- Why: pitfall quizzes and grader hints are built from these, so they target real wrong ideas.

**`bridge_in`** and **`bridge_out`**: one sentence each, with a link. In: "Last chapter you saw X; now we need Y because Z", plus `recalls` (the ideas it reminds the learner of). Out: "You will use this when…", plus `points_to` (the chapter that uses it).
- A bridge names only what the chapters it points to really show (checked). A bridge that promises "you will use the stride rule" sends the learner looking for something that is not there.
- Why: these two sentences connect the dots for the learner. They are the cheapest way to stop chapters feeling like separate islands.

## 2. Connecting chapters

- Order chapters so every `brings_in` id was carried forward by an earlier chapter.
- Each chapter carries at least one idea forward, unless it is the last (checked).
- The first chapter's `brings_in` lists only what the learner profile says they already know (use ids starting `known-`).
- The last chapter carries at least one idea forward with `used_in: [beyond]`, and its `bridge_out` says what to build or learn next (checked).
- Why: learning sticks when each new idea hooks onto one the learner already holds.
- **Introduce the example before you use it.** When chapters teach through an example (a lab, a codebase, a rule book), the first chapter that uses it opens with an `idea` block: what the example is, why this lesson uses it, and the details later blocks rely on. Never assume the learner knows the example; see `checks-and-quizzes.md` section 5.

## 3. Block types

A chapter is a short sequence of blocks. Use only the blocks the chapter needs.

**`predict`**: one question the learner answers before being told, plus a confidence rating (unsure, fairly sure, certain).
- Why: committing to a prediction makes the explanation land. Confidence shows where a wrong idea feels solid.
- Put it first in the chapter (checked). It shows what the learner knew before, so it never counts as the only test of a goal (checked).

**`idea`**: the explanation. At most 3 sentences, tied to something the learner knows. A `more` panel may hold detail for the curious.
- Why: short text keeps attention on the one idea. The `more` panel keeps depth available without forcing it on everyone.

**`diagram`**: only with a brief (see `diagrams.md`).
- Why: a diagram is for mechanisms that words explain badly.

**`code`**: a code slice the learner reads, with line comments, and a Run button that shows the output recorded from a real run. Plus 1 to 3 "notice" prompts that tell them what to look at in the output.
- Why: real code with its real output connects the idea to something concrete. Without notice prompts, learners look at the wrong part of the output.

**`compare`**: two or more choices run on the same input, with the step where they differ marked and explained (see section 6).
- Why: learners need to see what makes one choice behave differently, not only that the outputs differ.

**`fill_blanks`**: the default exercise. The real slice with 1 to 3 key tokens turned into blanks; each blank offers 3 or 4 options, and each wrong option is a real misconception. Run shows what each choice really prints.
- Why: choosing between the right line and the lines people really write tests the idea, not typing speed. The recorded output of a wrong choice shows its consequence.

**`explain`**: a short answer in the learner's own words, graded by AI against a rubric.
- Why: it tests whether the learner can say why, which a picker cannot.

**`stretch`**: an optional "write it yourself" exercise, collapsed by default, at most one per chapter. Checked against the solution, plus AI grading when available.
- Why: some learners want to write the code. Keeping it optional stops it from blocking learners who came to understand, not to type.

**`play`**: the learner deals 10 or 100 games from a computed case table and counts the outcomes beside the expected share. Only with a yes from Discover (`diagrams.md` section 0).
- Why: a sceptic who will not believe a chance from a table believes the count they made themselves.

**`check`**: a quiz question (see `checks-and-quizzes.md`).
- Why: a fast test of one key concept or one pitfall.

**`pitfall`**: a card naming one real misconception, why people fall for it, and what is actually true. When a `check` tests it, the check comes first and the card opens after the answer.
- Why: a learner who first tries the trap, then reads why it is a trap, remembers it; a card read first just hands over the check's answer.

**`recap`**: one line that goes into the final field guide, with `sums_up` naming the blocks it summarises. It names only what those blocks show (checked).
- Why: the field guide is what the learner keeps after the lesson.

**Typical order:** predict → idea → diagram (if briefed) → code → compare (if choices exist) → fill_blanks or explain → stretch (optional) → check (spot the mistake) → pitfall → recap.

**The answer waits for the guess:** the first `idea` after the predict is folded on the page until the guess is made (`page-contract.md` section 2). Make that block the one that answers the guess.

**Teach, then test (checked):** every chapter has a `check`, `fill_blanks` or `explain` after its first `idea`, and every `must_get_right` item is tested by one of them.

## 4. Tagging key concepts and pitfalls

- Tag an `idea` block `key: true` when a later chapter or the field guide depends on it. Every key idea gets a `check` with `purpose: key` that tests it (checked).
- Every misconception a chapter lists gets a `pitfall` block in that chapter (checked), and every defined misconception is used by some chapter (checked).
- Pitfalls get a "spot the mistake" check, or a wrong option in a blank. A pitfall check comes right **before** its card (checked): the learner answers first, then the card opens as feedback. Read first, the card gives the answer away.
- Do not quiz anything that is neither key nor a pitfall.
- Why: quizzes are expensive attention. Spending them on what matters trains judgement, not recall.

## 5. Code slices

- A slice is the real code that carries the idea: at most 15 code lines, and as few as it needs (checked). There is no minimum; never pad a slice to reach a length.
- Give the slice short line comments, at least one per 4 code lines (checked). The comments say what each step does, so a learner can read the slice alone.
- Put imports, fixtures and stubs in `setup`, not in the lines the learner reads. Label stubs as stubs.
- Record for each slice: `source` (file and line range), `depends_on` (what earlier code it needs, in one line each), and `context_note` (a short summary of the code around it).
- The tutor receives `depends_on` and `context_note`, so a learner can ask "what does the code before this look like?" and get a short, accurate answer.
- Every output the page shows is recorded from a real run at build time (checked with `--run-tests`). Steps that need a database, an API key or a large model are recorded on a machine that has them, and carry `run_locally` with the command.
- Why: a small slice keeps the learner's attention on the idea. The context path means a small slice never leaves them lost.

## 6. Comparing choices

Use a `compare` block only when the chapter really has options: two cleaning rules, two settings, two search methods.

- Run every option on the same input.
- Break each option into named steps. Mark the first step where the options produce different results.
- Under the marked step, explain in one or two sentences what makes the options different there.
- Let the learner switch options and see the marked step move with them.
- Why: a before and after shows a change. Learners need the cause of the difference, and the marked step is that cause.

Do not use step logs for code that has only one path. A plain `code` block with notice prompts is clearer.

## 7. Length, pace and scope

- A chapter takes 5 to 15 minutes, and states its time (checked).
- A chapter teaches 1 to 3 `must_know` ideas (checked). More means split the chapter.
- An `idea` block has at most 3 sentences (checked). Detail goes in `more` panels.
- At most 2 `check` blocks and 1 `stretch` per chapter (checked).
- One lesson holds at most 90 minutes of chapters, and fits the learner's `time_minutes` (checked). A longer source becomes several lessons.
- For a `before-hands-on` lesson, each chapter names its `source_section` and gets at least 10% of that section's hands-on minutes (checked). A 90-minute lab needs a chapter of at least 9 minutes, or two chapters.
- Why: short, labelled chapters let learners plan their time and finish what they start.
