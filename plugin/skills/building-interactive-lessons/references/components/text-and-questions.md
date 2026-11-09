# Components: text and questions

The blocks that carry words and quick choices: predict, idea, check, pitfall, recap, and the glossary. Every chapter uses most of them; `topic-map.md` says where each one does the most work.

Every card has the same parts: **For** (the shape of idea it fits), **Beats** (where in the story it helps most), **Learner role**, **Recipe**, **Rules** (the `self-checks.md` items that apply), **Wrong pick when**, and **Example** (a block in the example blueprints).

## Contents

1. Predict (a guess before teaching)
2. Held guess (a guess answered at the end)
3. Idea
4. Check: key idea
5. Check: spot the mistake, then the pitfall card
6. Recap
7. Glossary entry

---

## 1. Predict

- **For:** opening a chapter with the question it answers. The best predict has a gut answer most people get wrong.
- **Beats:** every chapter opens with one; it does the most work in the hook and the boundary.
- **Learner role:** bet.
- **Recipe:**

```yaml
- id: predict-page-match
  type: predict
  question: A user asks about refunds. The answer is one sentence on a 3,000-word policy page. Which is easier to find by meaning?
  options:
    - {text: The whole page, correct: false, why_wrong: The page's meaning is a blend of every topic on it, so the refund sentence is diluted.}
    - {text: A short passage around that sentence, correct: true, why_right: A short passage is mostly about refunds, so its meaning is close to the question.}
    - {text: Both match equally, correct: false, why_wrong: Search compares meanings, and a page about many things is far from any one question.}
```

- **Rules:** first block of its chapter; 2 to 4 options with one correct, or an `answer`; one-sentence feedback; the right answer is not in the chapter title, an objective, a milestone or a picture above it (`self-checks.md` sections 6, 7, 10).
- **Wrong pick when:** the question has no wrong gut answer (then it is a quiz, not a predict), or the answer needs a fact the learner has never met.
- **Example:** `example-blueprint.yaml`, `predict-page-match`.

## 2. Held guess

- **For:** a big question the whole lesson answers. The learner guesses in the hook and sees their guess marked only in the payoff.
- **Beats:** hook (asked), payoff (answered).
- **Learner role:** bet.
- **Recipe:** a predict with `hold: true`. The page keeps it unmarked and shows it again in the last chapter.

```yaml
- id: predict-stay-or-switch
  type: predict
  hold: true
  question: You picked door 1. The host opens door 3 and shows a goat. Should you switch to door 2?
  options:
    - {text: Switch, correct: true, why_right: Switching wins whenever your first pick was wrong, which is 2 times in 3.}
    - {text: Stay, correct: false, why_wrong: Your door kept its 1 in 3; the host's opening tells you nothing new about it.}
    - {text: It makes no difference, correct: false, why_wrong: The two doors left are not equally likely, because the host had to avoid the car.}
```

- **Rules:** only on a predict with options.
- **Wrong pick when:** the lesson's big idea is not one question with one answer.
- **Example:** `example-monty-blueprint.yaml`, first chapter.

## 3. Idea

- **For:** the explanation itself: one idea, tied to something the learner knows.
- **Beats:** all; in a mechanism chapter, one idea per moving part.
- **Learner role:** none on its own. Pair it with a picture or a test.
- **Recipe:**

```yaml
- id: stride-idea
  type: idea
  key: true
  text: Each chunk starts one stride after the last, and the stride is the chunk size minus the overlap. So more overlap means smaller steps, not bigger chunks.
  more: Overlap exists so a sentence cut at a chunk's edge still appears whole in one of the two chunks.
```

- **Rules:** at most 2 sentences and about 45 words; detail goes in `more`; `key: true` when a later chapter or the field guide needs it, and then a key check tests it (`self-checks.md` sections 6, 7, 10).
- **Wrong pick when:** it would be the third idea block in a row. Show it with a picture, or make the learner do something.
- **Example:** `example-blueprint.yaml`, `stride-idea`.

## 4. Check: key idea

- **For:** proving the learner can use a key idea on a new case, not repeat it.
- **Beats:** intuition, mechanism, transfer.
- **Learner role:** bet.
- **Recipe:**

```yaml
- id: stride-check
  type: check
  purpose: key
  tests: stride-idea
  question: Chunk size 400, overlap 100. Where does the third chunk start?
  options:
    - {text: "600", correct: true, why_right: The stride is 400 − 100 = 300, so starts are 0, 300, 600.}
    - {text: "800", correct: false, why_wrong: That steps by the full chunk size and ignores the overlap.}
    - {text: "1000", correct: false, why_wrong: That adds the overlap to each step instead of taking it away.}
```

- **Rules:** 3 or 4 options, one correct; `tests` names a key idea in this chapter; at most 2 checks per chapter, never two side by side; options similar in length; no example detail as an option (`self-checks.md` sections 6, 7, 10).
- **Wrong pick when:** the answer is a fact from the text above (that tests reading); ask for a new case instead.
- **Example:** `example-blueprint.yaml`, `stride-check`.

## 5. Check: spot the mistake, then the pitfall card

- **For:** a real misconception learners hold. The learner meets it as a question first; the card then explains it as feedback.
- **Beats:** intuition, mechanism, boundary.
- **Learner role:** puzzle.
- **Recipe:** a check with `purpose: pitfall`, right before the `pitfall` block for the same misconception. The card stays folded until the check is answered.

```yaml
- id: overlap-check
  type: check
  purpose: pitfall
  tests: overlap-adds-tokens
  question: "A teammate says: 'Overlap 50 makes each chunk 550 tokens long.' What is wrong?"
  options:
    - {text: Chunks stay 500; overlap only shortens the step, correct: true, why_right: Overlap changes where the next chunk starts, not how long each one is.}
    - {text: Nothing; that is how overlap works, correct: false, why_wrong: That is the misconception: no chunk grows.}
    - {text: Chunks become 450 tokens long, correct: false, why_wrong: 450 is the stride, the distance between starts, not a chunk's length.}
- id: overlap-pitfall
  type: pitfall
  misconception: overlap-adds-tokens
```

The card's words come from the misconception itself (`misconceptions` list: `wrong_idea`, `why_people_believe_it`, `what_is_true`, `source`).

- **Rules:** every misconception a chapter lists has a pitfall card; the pitfall check sits right before its card; no two cards side by side (`self-checks.md` sections 3, 6).
- **Wrong pick when:** the "misconception" is one you invented. Find a real one: docs' warnings, issue trackers, error messages, FAQs, or say it comes from your own knowledge.
- **Example:** `example-blueprint.yaml`, `overlap-pitfall`.

## 6. Recap

- **For:** the one line the learner keeps. All recaps form the field guide at the end.
- **Beats:** the end of every chapter.
- **Learner role:** none.
- **Recipe:**

```yaml
- id: stride-recap
  type: recap
  text: The stride is chunk size minus overlap; overlap shortens the step and never lengthens a chunk.
  sums_up: [stride-idea, run-chunker, fix-stride]
```

- **Rules:** one per chapter; `sums_up` names this chapter's teaching blocks; every concept it names appears in them (`self-checks.md` section 5).
- **Wrong pick when:** it repeats the idea word for word. Say it the way the learner would use it.
- **Example:** `example-blueprint.yaml`, `stride-recap`.

## 7. Glossary entry

- **For:** a term the learner meets more than once. The page links each use to its definition, and the bridges and recaps are checked against glossary terms.
- **Recipe:**

```yaml
glossary:
  - {term: stride, definition: How far each new chunk starts after the one before; chunk size minus overlap.}
```

- **Rules:** every term appears in the lesson; put every key concept here, so bridges and recaps can be checked against it (`self-checks.md` sections 3, 5).
- **Wrong pick when:** the term is used once. Explain it in brackets where it appears.
