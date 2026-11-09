# Topic map: which components tell which story

For each kind of topic, which component carries each beat of the story, from hook to payoff, and the moving picture most worth proposing. Use it in step 3 (Plan), after the concept map and before choosing blocks. The components are in `components/`; the beats are in `chapter-design.md` section 0.

A map entry is a strong default, not a rule. Every picture still passes the five questions and the change test in `visual-design.md`, and every moving picture is proposed with its cost.

## How to use it

1. **Name the kind.** Read the big idea and ask what it is about: an order of steps, a cause, a chance, a setting and its outcome, a choice between options, a structure, similarity, rules, code, events in time, or size. Most lessons have one main kind; a chapter may borrow from a second (a pipeline lesson often has one setting-and-outcome chapter).
2. **Find the wrong belief.** Each kind below names the beliefs learners typically hold. Find the real one for your topic (`SKILL.md` step 2): the hook is built around it.
3. **Pick a component per beat.** Use the row for each beat your chapters have. Every chapter still opens with a predict and closes with a recap; the rows say what does the work in between.
4. **Check the picture budget.** Mark which pictures move and what each costs; propose those in the plan.

**Every kind uses these the same way:** a predict opens each chapter; a held guess (`text-and-questions.md` section 2) can carry the hook's question to the payoff; spot the mistake then the pitfall card repairs each misconception; explain in your own words suits the payoff.

---

## 1. A process or pipeline

*Examples: search over documents, a compiler, how a request is served, a manufacturing line.*

- **Hidden:** the order of steps, and which step decides the outcome.
- **Wrong beliefs:** "the last step does the work", "steps happen together", "the input arrives unchanged".
- **Hook:** a flow figure of the whole system, the deciding step highlighted; a predict on what comes out.
- **Intuition:** one concrete input followed through, with tokens, tiles or a code slice at each step.
- **Mechanism:** a growing pipeline, one part added per chapter; code slices and fill-the-blanks on the step itself.
- **Boundary:** compare choices on the same input, with the first step where they part ways.
- **Transfer:** an explain: choose a setting for a new case and defend the trade-off.
- **Worth moving:** travel along a path, when the learner must see that something passes through every step, or is read again.

## 2. Cause and mechanism

*Examples: attention in a language model, how a vaccine trains immunity, why prices rise.*

- **Hidden:** what pushes on what, and how strongly.
- **Wrong beliefs:** "one cause only", "it works by a fixed lookup", "the effect is all or nothing".
- **Hook:** a predict whose gut answer assumes the wrong mechanism.
- **Intuition:** a scatter or a still svg of the starting state, with the thing that will change highlighted.
- **Mechanism:** stepped frames between computed states; a pull scene when several causes weigh in at once.
- **Proof:** a grid of the weights, or bars before and after.
- **Boundary:** the same mechanism on a case where it fails or flips.
- **Worth moving:** pull (weights tug a point), when how much each cause counts is the idea.

## 3. Chance and statistics

*Examples: the Monty Hall problem, sampling error, an A/B test, a model's next-word odds.*

- **Hidden:** every case at once, and how often each one happens.
- **Wrong beliefs:** "two options means 50/50", "a small sample tells the truth", "the most likely outcome always happens".
- **Hook:** tiles of the setup, and a held guess.
- **Intuition:** a bigger version of the case (10 doors for 3) in animated frames, or a pour scene as a share moves.
- **Proof:** a play block, 10 or 100 deals, counts beside the expected share; an svg table of every case.
- **Mechanism:** fill-the-blanks on the rule that makes the cases unequal.
- **Boundary:** two play blocks under two rules, side by side.
- **Worth moving:** pour, when a share moves from one place to another; run trials, always worth proposing here.

## 4. A setting and its outcome

*Examples: temperature, a learning rate, an interest rate, a filter threshold, a dose.*

- **Hidden:** how the outcome reacts as the setting moves, including where it changes fast.
- **Wrong beliefs:** "more is better", "the setting changes what is possible, not how likely", "the effect is a straight line".
- **Hook:** a predict on an extreme setting.
- **Intuition:** frames with a slider over computed states.
- **Proof:** a strip-and-draws scene: the learner sets the slider and runs trials.
- **Mechanism:** a fill-the-blanks (text or code) on the formula that turns the setting into the outcome.
- **Transfer:** an explain: pick a setting for a stated goal.
- **Worth moving:** drive (slider) plus run trials; the outcome must react at once.

## 5. Comparing options

*Examples: keyword search against vector search, two sorting methods, two policies, two diets.*

- **Hidden:** the first step where the options part ways, and the case where each one wins.
- **Wrong beliefs:** "one option is always better", "they differ everywhere", "the newer one replaces the older".
- **Hook:** the same input, two results; a predict on which one is right.
- **Mechanism:** a compare block with `differs_at`; paired traces as an svg when the options branch in space.
- **Proof:** bars or a grid of results on several inputs.
- **Boundary:** the input where the usual winner loses.
- **Transfer:** a key check: a new case, which option and why.
- **Worth moving:** rarely; a stepped picture usually carries a comparison.

## 6. Structure or architecture

*Examples: the parts of a system, a data model, an organisation, the layers of a network.*

- **Hidden:** which part talks to which, and why a part exists.
- **Wrong beliefs:** "every part sees everything", "the parts are independent", "more parts means better".
- **Hook:** the smallest working version as a flow figure.
- **Mechanism:** a growing pipeline, one part per chapter, each stage saying what it adds and why.
- **Proof:** a sequence svg of one request through the parts.
- **Boundary:** what breaks when a part is removed (a predict, then the flow without it).
- **Worth moving:** travel along a path for one request, when the route itself is the lesson.

## 7. Similarity and meaning

*Examples: word embeddings, clustering customers, recommendations, image search.*

- **Hidden:** distance as meaning, and how context moves a point.
- **Wrong beliefs:** "a word has one fixed meaning", "close on the map means identical", "the map's directions have names".
- **Hook:** tokens or a scatter showing that the same item gets the same number everywhere.
- **Intuition:** a scatter with a toy map, axes named for what they mean.
- **Mechanism:** a grid of weights, then a pull scene.
- **Boundary:** a case where nearness misleads.
- **Worth moving:** pull, when context moves a point.

## 8. Rules and policy cases

*Examples: a sport's rule book, a law, a style guide, an expense policy.*

- **Hidden:** the condition that decides a case, and the exception that overrides it.
- **Wrong beliefs:** "the rule says what it seems to say", "the strictest reading wins", "a clause number is the rule".
- **Hook:** a real case and a predict on the ruling. Explain the rule book before quizzing on it.
- **Intuition:** fill-the-blanks on the real sentence of the rule (`language: text`, with `output_from: source`).
- **Proof:** an svg table of cases: one row per situation, the ruling in each.
- **Boundary:** the exception, as a spot-the-mistake check before its pitfall card.
- **Transfer:** a key check on a new case, worded without clause numbers.
- **Worth moving:** rarely; tables and stepped cases carry rules.

## 9. Code behaviour

*Examples: what a function returns, an off-by-one bug, how an API call retries.*

- **Hidden:** the value each line produces, and the line a mistake changes.
- **Wrong beliefs:** the real mistakes in the code's issues and error messages.
- **Hook:** a predict on what the slice prints.
- **Mechanism:** a code slice with notice prompts, then fill-the-blanks where each wrong option prints its real, different output.
- **Boundary:** compare two versions of the line on the same input.
- **Transfer:** a stretch: write it from scratch.
- **Worth moving:** stepped frames of the state after each line, when a loop or a window is the idea.

## 10. A sequence of events in time

*Examples: a network handshake, an agent calling tools, a retry, a historical chain of events.*

- **Hidden:** who acts when, and what each step waits for.
- **Wrong beliefs:** "it happens all at once", "the reply comes back on the same path", "the loop runs once".
- **Hook:** a predict on the order.
- **Mechanism:** a sequence svg (actors, lifelines, calls and dashed replies, a loop frame); a scene with steps when the learner must watch one message move.
- **Boundary:** the failure path, framed as `ALT`.
- **Worth moving:** travel along a path, staggered, when order and waiting are the idea.

## 11. Size and scale

*Examples: how fast an algorithm slows down, orders of magnitude, a budget, a model's size.*

- **Hidden:** how much bigger, on one shared scale.
- **Wrong beliefs:** "twice the input, twice the time", "big numbers are all about the same".
- **Hook:** a predict on a size the learner cannot picture.
- **Intuition:** bars on one scale; a grid when two things grow together.
- **Proof:** frames with a slider for the input size.
- **Transfer:** a key check on a new size.
- **Worth moving:** drive, when where the curve bends is the idea.
