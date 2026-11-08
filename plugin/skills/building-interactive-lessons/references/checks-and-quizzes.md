# Checks and quizzes

How to test what the learner must get right, fairly and usefully. Rules marked **(checked)** are enforced by `scripts/check_blueprint.py`. The rest are judgement calls: read them against the blueprint in step 5.

## Contents

1. Match the check to the claim
2. Test after teaching
3. Fill the blanks
4. Quiz questions
5. Test the idea, not the example
6. Explain and stretch exercises
7. Hints and solutions
8. Confidence and the field guide

---

## 1. Match the check to the claim

Pick the check from what `must_get_right` says the learner can do.

- **Recognise** ("can tell which of these is X") → a `check` with options.
- **Predict** ("can predict what happens") → a `check` that asks for an outcome in a new situation.
- **Apply** ("can choose the right code for Y") → a `fill_blanks` exercise on the real code.
- **Explain** ("can explain why") → an `explain` exercise graded against a rubric.
- **Write from scratch** → an optional `stretch`. It never counts as the required test **(checked)**.

Judgement call: could a learner pass this check by guessing, by matching words, or by recall alone? If yes, and the claim is higher than recall, change the check.

## 2. Test after teaching

- Every `must_get_right` item lists, in `tested_by`, at least one `check`, `fill_blanks` or `explain` placed after the chapter's first `idea` block **(checked)**.
- Every chapter has at least one of those after its first `idea` block **(checked)**.
- A `predict` block may also appear in `tested_by`, but never alone **(checked)**. It comes before the teaching, so it shows what the learner knew before, not what they learned.

## 3. Fill the blanks

**Rules**
- A chapter that shows code has a `fill_blanks` exercise **(checked)**. A chapter with no code can use a text one (`language: text`).
- A text option's result names where it comes from: `output_from: source` or `worked`, with `output_source` **(checked)**. A wrong option must lead somewhere different from the right one **(checked)**.
- 1 to 3 blanks, each marked once in the code as `{{blank-id}}` **(checked)**.
- Each blank has 3 or 4 options and exactly one right option **(checked)**.
- Every option has a recorded output **(checked)**, and with `--run-tests` that output is what the code really prints with that option **(checked)**.
- A wrong option prints something different from the right one **(checked)**. If it prints the same, Run cannot show the learner what goes wrong: change the code (for example, print the value that the mistake changes) or pick another option.
- Each wrong option names a misconception and gives a one-line reason **(checked)**.
- The code keeps its line comments: at least one per 4 code lines, at most 15 code lines **(checked)**.

**Judgement calls**
- Blank the token that carries the idea (the operator, the argument, the condition), not a name the learner could guess from context.
- Each wrong option is a mistake real learners make, not a typo.
- The printed output makes the difference visible. Print the value the idea is about.

## 4. Quiz questions

**Rules**
- A `check` has 3 or 4 options; a `predict` has 2 to 4 **(checked)**.
- Exactly one option is correct **(checked)**.
- The correct option has `why_right`: the insight, not praise. Each wrong option has `why_wrong`, naming the specific mistake **(checked)**.
- A `check` has a purpose **(checked)**:
  - `key` tests a `key: true` idea in the same chapter, and every key idea has one **(checked)**;
  - `pitfall` tests a defined misconception **(checked)**.
- At most 2 `check` blocks per chapter **(checked)**, never two side by side **(checked)**.
- **Test, then reveal:** a `pitfall` check comes right before the pitfall card for the misconception it tests **(checked)**. The card stays folded until the check is answered, then opens as feedback.

**Judgement calls**
- A key-idea check gives a situation the chapter did not show. If a learner can only answer the chapter's own example, they memorised it.
- A pitfall check shows code or a statement containing the misconception and asks what is wrong.
- Options are similar in length and style. No "all of the above", no trick wording. The right option is never much longer than the wrong ones **(checked)**.
- A guess's right answer never shows before the guess **(checked)**, and a blank's right option is never written in the block just above it **(checked)**. See `chapter-design.md` section 8.

**After an answer**: mark the choice right or wrong, reveal the correct option, show the picked option's explanation first, then the correct one's.

## 5. Test the idea, not the example

A lesson often teaches through an example: a lab, a codebase, a rule book, a dataset. The learner came for the idea, and may know nothing about the example yet.

**Rules**
- A `predict` or `check` question names an example detail (a section number such as 9.1.6 or Law 13, a lab, a file name) only if an earlier block already showed it, or the question explains it in brackets right after it: "9.1.6 (the service height rule)" **(checked)**.
- No option is only an example detail: "9.1.6" or "Law 16.7" as an answer tests memory of the example. Write what that choice means instead: "the rule on how high you may serve" **(checked)**.

**Judgement calls**
- Introduce the example before the first block that uses it: what it is, why this lesson uses it, and the few details later blocks need. One `idea` block is usually enough.
- A learner who knows the idea but has never seen the example could answer every quiz. Read each question as that learner.
- Use example details as evidence inside a question, never as the thing to recall.

## 6. Explain and stretch exercises

**Rules**
- 1 to 4 instruction lines **(checked)**. Each says what to achieve.
- `explain` and `stretch` have a rubric of `{criterion, passing}` lines **(checked)**.
- At most 1 `stretch` per chapter, and it is never in `tested_by` **(checked)**.
- A code stretch's reference solution has at most 15 code lines and line comments **(checked)**.

**Grading**
- `explain`: the AI grader checks the answer against the rubric and names the first unmet criterion.
- `stretch`: the learner compares their answer with the solution, side by side; the AI grader adds a rubric verdict when it is available.
- Without AI, both show the rubric as a self-check.

## 7. Hints and solutions

- 1 or 2 hint levels per exercise **(checked)**. Level 1 points to the part of the problem. Level 2 goes about half way. A hint never contains the solution.
- **Hint** and **Show solution** are two separate buttons on every exercise, always available, plus a read-along mode that opens every solution (see `page-contract.md` section 3). The learner chooses when to open the solution.
- The **tutor** never hands over a solution. When asked for one, it gives a hint or a leading question and points to the Show solution button.
- Feedback names the **first** problem only, in one sentence **(checked for `why_right` and `why_wrong`)**. A success message states the insight, not praise.

## 8. Confidence and the field guide

- `predict` blocks and quiz questions record the learner's confidence with their answer.
- The final page lists each chapter's recap line (the field guide), every answer the learner was "certain" about and got wrong, with a link back, and which exercises were solved or read from the solution.
- Why: confident mistakes are the most important ones to revisit, and learners rarely notice them alone.
