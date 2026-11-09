# AI tutor and grader

How the page asks Claude for help: the tutor answers questions, the grader checks open answers. Both use the artifact's `sample` capability in claude.ai.

The page template (`assets/page-template.md`) already implements everything here (functions `contextPacket`, `TUTOR_RULES`, `graderPrompt`, `openTutor`). Read this file to understand the design, to review the template, or to fix it for every lesson. If the environment offers an `artifact-capabilities` skill, load it before changing that code. Its type definitions win over the snippets here.

## Contents

1. Facts about `sample` that shape the design
2. The context packet
3. Tutor prompt
4. Grader prompt and result shape
5. Page code
6. When AI is unavailable

---

## 1. Facts about `sample` that shape the design

- **Memoryless:** Claude sees only what the page sends in each call. The page must send the lesson context every time.
- **Costs the viewer:** each call uses the viewer's own Claude usage. The first call asks the viewer to allow it.
- **Can be absent:** `await claude.use("sample")` resolves `null` where the page cannot ask Claude. A viewer can also decline; then every call rejects `not_granted`.
- **One failure shape:** calls reject with `{code, message, text?}`. Branch on `code`. Never retry from a loop.
- **Caching:** identical calls within 5 minutes replay the stored answer. Tutor chat turns pass `cache: false`; grading may keep the default.
- **Calls run on a click,** never on load or from a timer.
- **Answers are Markdown.** The page renders code blocks, inline code, bold, links, headings and lists, from text only (never as HTML). In the chat box, Enter sends and Shift+Enter adds a line; Enter never sends while an input method is composing (Thai, Japanese).

## 2. The context packet

Build this from the blueprint for the block the learner is on. Keep it under a few thousand characters.

```
LESSON: <lesson title>, for <learner profile, one line>
CHAPTER: <chapter title>
WHY IT MATTERS: <why_it_matters>
MUST KNOW: <must_know, one per line>
THIS BLOCK: <block type and its text>
CODE SLICE (if any):
<the slice>
CODE AROUND IT: <context_note>
IT DEPENDS ON: <depends_on lines>
EARLIER IDEAS THE LEARNER HAS: <brings_in ideas, one line each>
MISCONCEPTIONS TO WATCH FOR: <misconception statements for this chapter>
```

Why each part: the title and profile set the level; `must_know` keeps answers on the chapter's goal; `context_note` and `depends_on` let the tutor show "the code before this" accurately; `brings_in` lets it build from what the learner already has; misconceptions let it spot a known wrong idea in a question.

## 3. Tutor prompt

Send as the leading user turn, followed by the chat turns the page keeps (drop the oldest turns as the chat grows, never this one).

```
You are a patient tutor inside an interactive lesson. Use the lesson context below.

Rules:
- Answer only about this lesson's topic. For anything else, say it is outside this lesson in one line.
- Start with a one-sentence answer. Add at most 3 short sentences or one small code example. Offer to go deeper.
- Build from the EARLIER IDEAS the learner has. Use their words.
- The learner may not know the lesson's example (a lab, a codebase, a rule book). When a question is about the example, explain what it is and why it is here, then link it back to the idea.
- If the question shows one of the MISCONCEPTIONS, name it gently and give the correct idea.
- If asked for the code before or after the slice, show a short version based on CODE AROUND IT and IT DEPENDS ON. Say it is simplified.
- Never give an exercise's solution, even when asked directly. Give a hint that goes about half way, or ask a question that leads there, and say the learner can open it any time with the Show solution button.
- If the learner says they still do not get it, explain from a different starting point (a new example or comparison), not a longer version of the last answer.
- If something is not in the context and you are unsure, say so.

<the context packet>
```

## 4. Grader prompt and result shape

Use `sample.json` so the page gets data back. The grader is used for `explain` exercises and for the optional `stretch`. Fill-the-blanks exercises need no AI: each option is marked right or wrong in the blueprint.

```
You grade one answer in an interactive lesson. Be fair and specific.

Exercise: <exercise instructions>
Reference solution: <reference_solution>
Rubric (each criterion: what a passing answer shows):
<rubric lines>
Known wrong answers and what they reveal:
<common_wrong_answers, each with its misconception>

Learner's answer:
<answer>

Reply with only this JSON:
{"verdict": "pass" | "partial" | "fail",
 "criteria": [{"criterion": "<name>", "met": true | false}],
 "first_problem": "<the first unmet criterion, in one sentence, or empty>",
 "hint": "<a hint that goes about half way, never the solution, or empty>",
 "misconception": "<id from the known wrong answers, or empty>",
 "insight": "<one sentence the learner should take away if they passed, or empty>"}
Rules: judge the meaning, not the wording. A code answer passes when it does what the reference does, even if it is written differently.
```

Why this shape: `first_problem` keeps feedback to one issue; `hint` and `insight` map straight onto the page's feedback rules; `misconception` lets the page show the matching pitfall card; `criteria` shows the learner what was met.

## 5. Page code

```js
// Ask Claude for the tutor and the grader. Both features hide themselves when Claude is unavailable.

// Find out whether this page can ask Claude at all. Call once after the page renders; never block first paint on it.
let claudeSample = null;
let canAskClaude = false;
async function connectToClaude() {
  claudeSample = window.claude ? await window.claude.use("sample") : null;
  canAskClaude = claudeSample !== null;
  if (canAskClaude) showAllAiFeatures();
}

// Turn a failure code into a short message for the learner, and hide AI features for good when needed
const permanentFailureCodes = ["not_granted", "sampling_disabled", "not_declared", "capability_disabled", "capability_removed"];
function handleClaudeFailure(failure, messageElement) {
  if (failure.code === "cancelled") return;
  if (permanentFailureCodes.includes(failure.code)) {
    canAskClaude = false;
    hideAllAiFeatures();
    return;
  }
  const learnerMessages = {
    rate_limited: "Claude is busy for you right now. Try again in a minute.",
    session_expired: "Please sign in again to use the tutor.",
    invalid_json: "The grader's reply could not be read. Try again.",
  };
  messageElement.textContent = learnerMessages[failure.code] || "Something went wrong. Try again.";
}

// Tutor: send the rules, the lesson context and the chat so far, and stream the answer
async function askTutor(chatTurns, contextPacket, answerElement, stopSignal) {
  answerElement.textContent = "Thinking...";
  // The rules and context join the learner's first message, so the turns alternate user, assistant, user
  const [firstTurn, ...laterTurns] = chatTurns;
  const tutorInput = [{ role: "user", content: TUTOR_RULES + "\n\n" + contextPacket + "\n\nLearner: " + firstTurn.content }, ...laterTurns];
  const { text } = await claudeSample(tutorInput, {
    cache: false,
    signal: stopSignal,
    onText: ({ text: answerSoFar }) => { answerElement.textContent = answerSoFar; },
  });
  return text;
}

// Grader: ask for a JSON verdict and check the fields before using them
async function gradeAnswer(graderPrompt) {
  const result = await claudeSample.json(graderPrompt);
  const allowedVerdicts = ["pass", "partial", "fail"];
  if (!result || !allowedVerdicts.includes(result.verdict)) {
    throw { code: "invalid_json", message: "missing verdict" };
  }
  return result;
}
```

Use a new `AbortController` for each call and wire it to a Stop button on the tutor.

## 6. When AI is unavailable

- Hide the tutor box and the "Explain it another way" button.
- Fill-the-blanks exercises work as normal: they need no AI.
- Explain and stretch exercises show the reference solution and the rubric after the learner submits, so they can check themselves.
- One quiet line at the top says the AI tutor is off for this view. No repeated prompts, no retry buttons.
