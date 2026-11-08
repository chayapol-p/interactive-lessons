# User-test log: Stay or Switch? (0.4.0)

Method: one fresh persona agent per round, using the built page only through `scripts/phone_driver.py` (390 px phone screenshots and taps; no files, no Read-along, tutor off). Fixed report: moments, lost spots, teach-back, verdict, top 3 fixes, bugs. Pass bar: a correct teach-back and "I get it".

| Round | Person | Verdict | Teach-back |
|---|---|---|---|
| 1 | Dara, 41, teacher, sure it is 50/50 | I get it, fairly sure | correct, includes the guessing host |
| 2 | Arjun, 58, retired accountant, wants evidence | I get it, fairly sure | correct, includes the guessing host |
| 3 | Mai, 19, design student, never changes a first answer | I get it, fairly sure | correct, includes the guessing host |

**Stop:** the pass bar was met in every round; testing stopped after round 3, once two rounds in a row raised the same open design question (below).

## Round 1 (Dara): fixed
- Bugs in the template: no phone viewport tag (desktop width on a phone); a comma wrapping away from a glossary word; a chapter with no exercises ticked done; self-check could not count as done without the tutor.
- Lesson: wrong-guess feedback in chapter 1 made concrete; one quiz fewer in chapters 3 and 4; deals before the six-row table; two captions that contradicted their pictures; a repeated last line.
- Test tool: it reloaded the page on every tap (results "vanished"); now one page stays open.
- Added at the maintainer's request: ten doors as tiles, the host's goats opening one at a time.

## Round 2 (Arjun): fixed
- His "the dealer gives 60%" was checked and is not a bug (60 deals averaged 67.6; 600,000 games 66.6%; first deals in 15 fresh browsers 67.7). The page now shows how far a fair deal wanders.
- The opening guess is held (noted, not marked) until the last chapter; "he can always find a goat" moved into the main text; bars to one decimal; a sticky hover border after taps; idioms and a sentence with no verb rewritten.

## Round 3 (Mai): fixed
- The first guess came back before the last answer was written; "You can now…" showed before its test; the progress bar lagged; the other 9 doors looked like two groups; three questions in a row asked the same count; harder words ("learns nothing", "survived a cut", "not free to remove").
- Test-tool artifacts, not page bugs: a "page jump" (the tool centred each button before tapping it; fixed in the tool) and a placeholder it could not find.

## Open design question
- **Chapter 4's six-row table** (both hosts side by side). Two of three testers found it too much on a phone (Dara skimmed it, Mai asked for a picture like the chapter 3 bars); the third (Arjun, an accountant) said it convinced him more than anything. Options: keep it; replace it with bars of the six moves for each host; or keep the table and add the bars above it.
- **None of the three said "certain".** All three ended "fairly sure", each for a different reason (the guessing host's twist; a low deal; the six-row table).
