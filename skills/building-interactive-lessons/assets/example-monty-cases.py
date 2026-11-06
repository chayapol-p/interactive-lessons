"""Draw the two case tables for the Monty Hall lesson (chapters 2 and 4) as SVG markup that uses the lesson template's classes.

Every row is worked out by listing the cases, so nothing in the pictures is typed by hand.
Run: python3 assets/example-monty-cases.py   (prints both SVGs as JSON, ready to paste into example-monty-blueprint.yaml)
"""
import json

DOORS = [1, 2, 3]
YOUR_PICK = 1


# One small door: its number above, what is behind it inside. An opened door is drawn as a ghost.
def door(x, y, number, behind, opened):
    look = "ghost" if opened else ("hot" if behind == "car" else "")
    text_look = "small dim" if opened else "small"
    return (f'<rect x="{x}" y="{y}" width="34" height="30" rx="4" class="svg-box {look}"/>'
            f'<text x="{x + 17}" y="{y + 19}" text-anchor="middle" class="svg-text {text_look}">{"open" if opened else behind}</text>')


def mark(x, y, wins):
    return f'<text x="{x}" y="{y}" text-anchor="middle" class="svg-text{" hot" if wins else " dim"}">{"✓ wins" if wins else "✗"}</text>'


# Table 1: the host knows. One row for each place the car can be (each 1 in 3); you always pick door 1.
def host_knows_table():
    rows, stay_total, switch_total = [], 0, 0
    for row, car in enumerate(DOORS):
        y = 44 + row * 52
        goat_doors = [d for d in DOORS if d != YOUR_PICK and d != car]
        opened = goat_doors[0] if car != YOUR_PICK else None        # with the car behind door 1 he may open 2 or 3
        stay_wins, switch_wins = car == YOUR_PICK, car != YOUR_PICK
        stay_total += stay_wins
        switch_total += switch_wins
        parts = [f'<text x="4" y="{y + 19}" class="svg-text small">Car: {car}</text>']
        for column, number in enumerate(DOORS):
            behind = "car" if number == car else "goat"
            parts.append(door(64 + column * 40, y, number, behind, number == opened))
        note = "opens 2 or 3 (one case)" if opened is None else f"must open {opened}"
        parts.append(f'<text x="64" y="{y + 44}" class="svg-text small dim">{note}</text>')
        parts.append(mark(232, y + 19, stay_wins))
        parts.append(mark(300, y + 19, switch_wins))
        rows.append("".join(parts))
    header = ('<text x="64" y="22" class="svg-text small">Door 1 · 2 · 3 (you pick 1)</text>'
              '<text x="232" y="22" text-anchor="middle" class="svg-text small">Stay</text>'
              '<text x="300" y="22" text-anchor="middle" class="svg-text small">Switch</text>')
    # No totals row: the learner counts the ticks in each column in the next exercise
    total_y = 44 + 3 * 52
    totals = ""
    label = (f"You pick door 1. Car behind door 1: the host opens 2 or 3, still one case, and staying wins. Car behind door 2: the host opens 3, switching wins. "
             f"Car behind door 3: the host opens 2, switching wins.")
    return (f'<svg viewBox="0 0 340 {total_y + 4}" role="img" aria-label="{label}">' + header + "".join(rows) + totals + "</svg>",
            stay_total, switch_total)


# Table 2: the same 6 equally likely moves for both hosts. Each case (1 in 3) splits into 2 moves (1 in 6): the door
# the host goes for. A guessing host opens it, even if it hides the car; a host who knows opens the other door instead.
def host_guesses_table():
    rows = []
    guess_stay = guess_switch = kept = know_stay = know_switch = 0
    pairs = [(car, aimed) for car in DOORS for aimed in DOORS if aimed != YOUR_PICK]
    for row, (car, aimed) in enumerate(pairs):
        y = 44 + row * 40
        # The guessing host opens the door he went for
        guess_other = [d for d in DOORS if d not in (YOUR_PICK, aimed)][0]
        if aimed == car:
            guess_cell = ('<text x="132" y="{0}" class="svg-text small dim">shows the car</text>'
                          '<text x="132" y="{1}" class="svg-text small dim">game over</text>')
        else:
            kept += 1
            guess_stay += car == YOUR_PICK
            guess_switch += car == guess_other
            guess_cell = mark_cell(132, y, car == YOUR_PICK)
        # The host who knows never opens the car's door: he opens the other one
        opened = [d for d in DOORS if d not in (YOUR_PICK, car)][0] if aimed == car else aimed
        know_other = [d for d in DOORS if d not in (YOUR_PICK, opened)][0]
        know_stay += car == YOUR_PICK
        know_switch += car == know_other
        know_cell = mark_cell(240, y, car == YOUR_PICK, f"skips it, opens {opened}" if aimed == car else "")
        parts = [f'<text x="4" y="{y}" class="svg-text small">Car {car}, host</text>',
                 f'<text x="4" y="{y + 14}" class="svg-text small">picks door {aimed}</text>',
                 guess_cell.format(y, y + 14) if aimed == car else guess_cell, know_cell]
        rows.append("".join(parts))
    header = ('<text x="4" y="18" class="svg-text small">Car / host picks</text>'
              '<text x="132" y="18" class="svg-text small">Host guesses</text>'
              '<text x="240" y="18" class="svg-text small">Host knows</text>')
    total_y = 44 + len(pairs) * 40
    totals = (f'<line x1="4" y1="{total_y - 18}" x2="336" y2="{total_y - 18}" class="svg-line dim"/>'
              f'<text x="4" y="{total_y + 2}" class="svg-text small">Wins</text>'
              f'<text x="132" y="{total_y + 2}" class="svg-text small">stay {guess_stay}, switch {guess_switch}</text>'
              f'<text x="132" y="{total_y + 16}" class="svg-text small dim">of {kept} games left</text>'
              f'<text x="240" y="{total_y + 2}" class="svg-text small hot">stay {know_stay}, switch {know_switch}</text>'
              f'<text x="240" y="{total_y + 16}" class="svg-text small dim">of {len(pairs)}</text>')
    label = (f"The same 6 equally likely moves for two hosts. A host who guesses shows the car in 2 of them, so those games end; "
             f"of the {kept} left, staying wins {guess_stay} and switching {guess_switch}. A host who knows opens the other door "
             f"in those 2 moves, so they become switching wins: staying {know_stay}, switching {know_switch} of 6.")
    return (f'<svg viewBox="0 0 340 {total_y + 24}" role="img" aria-label="{label}">' + header + "".join(rows) + totals + "</svg>",
            guess_stay, guess_switch, kept)


# One result cell: who wins, and an optional small note under it.
def mark_cell(x, y, stay_wins, note=""):
    words = "stay ✓" if stay_wins else "switch ✓"
    cell = f'<text x="{x}" y="{y}" class="svg-text small{"" if stay_wins else " hot"}">{words}</text>'
    if note:
        cell += f'<text x="{x}" y="{y + 14}" class="svg-text small">{note}</text>'
    return cell


if __name__ == "__main__":
    knows_svg, knows_stay, knows_switch = host_knows_table()
    guesses_svg, guess_stay, guess_switch, kept = host_guesses_table()
    print(json.dumps({"knows": knows_svg, "guesses": guesses_svg,
                      "counts": [knows_stay, knows_switch, guess_stay, guess_switch, kept]}))
