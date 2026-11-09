# Components: real material and exercises

The blocks where the learner reads real material and produces something: a code slice to read, a comparison of choices, fill-the-blanks on code or text, an explanation in their own words, and an optional stretch. Card parts are the same as in `text-and-questions.md`.

## Contents

1. Code slice (read and run)
2. Compare choices
3. Fill the blanks: code
4. Fill the blanks: text (rules, formulas, prose)
5. Explain (AI-graded)
6. Stretch (optional, write from scratch)
7. Choosing the exercise

---

## 1. Code slice

- **For:** the real lines that carry the idea, read before the learner works with them.
- **Beats:** mechanism, transfer.
- **Learner role:** step (read, then press Run to see the recorded output).
- **Recipe:**

```yaml
- id: run-chunker
  type: code
  slice:
    language: python
    source: chunker.py, lines 12–24
    depends_on: [tokens is a list of words made by a tokenizer earlier in the pipeline]
    context_note: Before this, the page is split into tokens. After this, each chunk is turned into a vector.
    setup: |
      tokens = [f"word{i}" for i in range(1200)]   # a 1,200-token page
    code: |
      chunk_size = 500
      overlap = 50
      stride = chunk_size - overlap                  # how far each new chunk moves
      starts = list(range(0, len(tokens), stride))   # one start per stride
      print("starts:", starts)
    recorded_output: ""        # filled from a real run (building-the-page.md section 2)
  notice:
    - Look at how far apart the starts are.
```

- **Rules:** at most 15 code lines, at least one comment per 4 lines; hidden `setup` for imports and stubs; 1 to 3 `notice` prompts; the output comes from a real run; a chapter with a code slice has a fill-the-blanks exercise (`self-checks.md` sections 6, 7, 15).
- **Wrong pick when:** the idea is not in the code (a concept the code only uses). Teach the concept with an idea and a picture; show code when the learner will meet it.
- **Example:** `example-blueprint.yaml`, `run-chunker`.

## 2. Compare choices

- **For:** two or three options on the same input, and the first step where they part ways: two settings, two rules, two methods.
- **Beats:** mechanism, boundary.
- **Learner role:** step.
- **Recipe:**

```yaml
- id: compare-overlap
  type: compare
  input: A 1,200-token page, chunk size 500
  options:
    - {name: Overlap 0, steps: [start 0, start 500, start 1000]}
    - {name: Overlap 50, steps: [start 0, start 450, start 900]}
  differs_at: 2
  explanation: Overlap does not change a chunk's size. It shortens the step, so every later chunk starts earlier.
```

- **Rules:** at least 2 options; `differs_at` is the first step that differs (`self-checks.md` section 7).
- **Wrong pick when:** the options branch in space rather than in steps (draw paired traces as an svg, `diagrams.md` section 5.2), or only the end result differs (use bars or a frames figure).
- **Example:** `example-blueprint.yaml`, `compare-overlap`.

## 3. Fill the blanks: code

- **For:** the default exercise for code. The learner picks the key token, and every pick, right or wrong, shows what the code really prints with it.
- **Beats:** mechanism, transfer.
- **Learner role:** puzzle.
- **Recipe:**

```yaml
- id: fix-stride
  type: fill_blanks
  instructions: [Fill the blank so each chunk shares 50 tokens with the one before it.]
  language: python
  source: the chunker from Run above
  context_note: The same chunker, with the line that sets the step left blank.
  setup: |
    tokens = [f"word{i}" for i in range(1200)]
  code: |
    chunk_size = 500
    overlap = 50
    stride = {{stride}}                            # how far each new chunk moves
    starts = list(range(0, len(tokens), stride))   # one start per stride
    print("starts:", starts[:3])                   # the first three starts
  blanks:
    - id: stride
      options:
        - {text: chunk_size - overlap, correct: true, why_right: Each chunk moves its size minus the part it shares., output: ""}
        - {text: overlap, correct: false, why_wrong: That moves only 50 tokens, so every chunk nearly repeats the last., misconception: overlap-adds-tokens, output: ""}
        - {text: chunk_size + overlap, correct: false, why_wrong: That skips 50 tokens between chunks., misconception: overlap-adds-tokens, output: ""}
  hints: [Should the shared part make the step longer or shorter?]
```

- **Rules:** 1 to 3 blanks, each marked once; 3 or 4 options with one right; each wrong option names a real misconception and prints something different from the right one; every output from a real run; the right option is not written in the block just above (`self-checks.md` section 8, 10, 15).
- **Wrong pick when:** a wrong option prints the same as the right one (Run cannot show the mistake: print the value it changes), or the blank is a name the learner can only recall, not reason out.
- **Example:** `example-blueprint.yaml`, `fix-stride`.

## 4. Fill the blanks: text

- **For:** the same exercise on a sentence, a rule, a policy or a formula. Each option's result is worked out in steps or quoted from a named source.
- **Beats:** any; it is the default exercise for a topic without code.
- **Learner role:** puzzle.
- **Recipe:**

```yaml
- id: temperature-blank
  type: fill_blanks
  instructions: [Fill the blank using the temperature slider above.]
  language: text
  source: the toy next-word odds
  context_note: The odds for the word after "The bank by the river was".
  text: Turning the temperature down from 1.0 to 0.2 makes flooded {{effect}}.
  blanks:
    - id: effect
      options:
        - text: almost certain to be picked
          correct: true
          why_right: Low temperature sharpens the odds, so the top word takes nearly all of them.
          output: Flooded's chance goes from 0.60 at 1.0 to 1.00 at 0.2.
          output_from: worked
          output_source: worked out with the toy model behind this chapter's pictures
        - text: less likely to be picked
          correct: false
          why_wrong: Low temperature makes the top word more likely, not less.
          misconception: temperature-is-intelligence
          output: "The opposite happens: flooded rises from 0.60 to 1.00."
          output_from: worked
          output_source: worked out with the toy model behind this chapter's pictures
        - text: replaced by a better word
          correct: false
          why_wrong: Temperature reshapes the same odds; no new word appears.
          misconception: temperature-is-intelligence
          output: The same 5 words keep their order at every temperature.
          output_from: worked
          output_source: worked out with the toy model behind this chapter's pictures
  hints: [Slide to 0.2 and read flooded's share.]
```

- **Rules:** the passage is in `text`; every option has `output`, `output_from` (`source` or `worked`) and `output_source`; the rest as for code blanks (`self-checks.md` section 8).
- **Wrong pick when:** the right word can be copied from the picture's caption or the block above.
- **Example:** `example-concepts-blueprint.yaml`, `temperature-blank`.

## 5. Explain

- **For:** an idea the learner must put in their own words: a trade-off, a reason, a choice for their own case. The grader (AI) marks it against a rubric and names the first problem.
- **Beats:** transfer, payoff; also the mechanism of an idea with no single right token.
- **Learner role:** explore.
- **Recipe:**

```yaml
- id: defend-size-choice
  type: explain
  instructions:
    - Your users ask "how do I…" questions whose answers take a paragraph.
    - Pick small (200), medium (500) or big (1,500) chunks, and explain the trade-off in two sentences.
  reference_solution: Medium chunks. A paragraph-length answer needs its context kept together, but big chunks mix several answers and weaken the match.
  rubric:
    - {criterion: Fits the question type, passing: The choice keeps a paragraph-length answer in one chunk.}
    - {criterion: States the trade-off, passing: Names the context gained and the precision lost or kept.}
  hints: [How long is a typical answer? What else would a 1,500-token chunk hold?]
  common_wrong_answers:
    - {answer: "Big, because more context is always safer.", misconception: bigger-is-safer, hint: Ask what else ends up in a 1,500-token chunk.}
```

- **Rules:** a rubric of `{criterion, passing}` lines; 1 or 2 hints; every common wrong answer names a defined misconception (`self-checks.md` section 7). Try it with a right, a wrong and a half-right answer; the grader's verdicts must match (`ai-tutor-and-grader.md`).
- **Wrong pick when:** the answer is one token or number. Use a blank or a check; they need no AI.
- **Example:** `example-blueprint.yaml`, `defend-size-choice`.

## 6. Stretch

- **For:** a learner who wants more: write the code or the argument from scratch. Never required.
- **Beats:** transfer.
- **Learner role:** puzzle.
- **Recipe:** like an explain, with `kind: code` (and a `language`) or `kind: explain`; a code reference solution keeps the code-slice limits.
- **Rules:** at most one per chapter; never in `tested_by` (`self-checks.md` sections 6, 9).
- **Wrong pick when:** it is the chapter's only real test.
- **Example:** `example-blueprint.yaml`, `write-chunk-starts`.

## 7. Choosing the exercise

| The learner must… | Use |
|---|---|
| pick the right token, value or word, and see what each choice leads to | fill the blanks |
| apply an idea to a new case with a clear answer | a key check (`text-and-questions.md` section 4) |
| catch a real misconception | spot the mistake, then the card |
| state a reason or a trade-off in their own words | explain |
| believe a number | run trials (`trials.md`) |
| write something whole | a stretch, on top of one of the above |
