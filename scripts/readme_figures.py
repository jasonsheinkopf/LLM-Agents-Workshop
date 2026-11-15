"""Draw the README figures as SVG, once for GitHub's light theme and once for dark.

    repo $ uv run python scripts/readme_figures.py      # writes docs/img/readme/*.svg

The figures use the viewer's system font and a transparent background, so they sit on the page
like text does. Numbers in the scoreboard come from SCORES below: change them there, not in the SVG.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs" / "img" / "readme"
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
W = 1200

THEMES = {
    "light": dict(ink="#1f2328", muted="#59636e", faint="#818b98", line="#d1d9e0", panel="#f6f8fa",
                  blue="#2a78d6", orange="#eb6834", aqua="#1baf7a", rest="#d1d9e0", on="#ffffff", page="#ffffff"),
    "dark": dict(ink="#f0f6fc", muted="#9198a1", faint="#656c76", line="#3d444d", panel="#151b23",
                 blue="#3987e5", orange="#d95926", aqua="#199e70", rest="#3d444d", on="#ffffff", page="#0d1117"),
}

# Judge pass rate over the same 19 test calls: (label, what changed, score, note).
SCORES = [
    ("Prompt v1", "careful, wordy", 0.26, ""),
    ("Prompt v2", '"be brief"', 0.21, "fails the honesty and safety cases"),
    ("Prompt v3", "brief, keeps the rules", 0.26, ""),
    ("v3 + memory", "the handbook, retrieved", 0.84, "knowledge 0/8 to 8/8"),
    ("v3 + memory + tools", "schedule and booking", 0.90, "booking 3/6 to 5/6"),
]
# The working day in minutes (390 without lunch and breaks).
TIME = [("Explain and demo", 70, "blue"), ("Build", 242, "aqua"), ("Check and debrief", 78, "orange")]
BLOCKS = [("1", "First agent", "It holds a conversation"), ("2", "Traces", "You can see every step"),
          ("3", "Evals", "You can measure it"), ("4", "Memory", "It knows the handbook"),
          ("5", "Tools", "It acts, behind guardrails"), ("6", "MCP", "Other agents can use it")]


class Svg:
    def __init__(self, h: int, t: dict, title: str) -> None:
        self.h, self.t, self.parts = h, t, []
        self.title = title

    def text(self, x, y, s, size=18, fill="ink", weight=400, anchor="start", font=FONT, spacing=None, style=""):
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        st = f' font-style="{style}"' if style else ""
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
                          f'fill="{self.t.get(fill, fill)}" text-anchor="{anchor}"{ls}{st}>{escape(s)}</text>')

    def rect(self, x, y, w, h, fill="panel", stroke=None, r=12, sw=1.5, opacity=None):
        st = f' stroke="{self.t.get(stroke, stroke)}" stroke-width="{sw}"' if stroke else ""
        op = f' fill-opacity="{opacity}"' if opacity is not None else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{self.t.get(fill, fill)}"{op}{st}/>')

    def line(self, x1, y1, x2, y2, stroke="line", sw=2, dash=None, cap="round"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{self.t.get(stroke, stroke)}" '
                          f'stroke-width="{sw}" stroke-linecap="{cap}"{d}/>')

    def circle(self, x, y, r, fill="blue", stroke=None, sw=2):
        st = f' stroke="{self.t.get(stroke, stroke)}" stroke-width="{sw}"' if stroke else ""
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{self.t.get(fill, fill)}"{st}/>')

    def path(self, d, fill="none", stroke=None, sw=2):
        st = f' stroke="{self.t.get(stroke, stroke)}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' if stroke else ""
        self.parts.append(f'<path d="{d}" fill="{self.t.get(fill, fill)}"{st}/>')

    def arrow(self, x1, y, x2, stroke="faint"):
        self.line(x1, y, x2 - 2, y, stroke, 2)
        self.path(f"M{x2 - 9},{y - 6} L{x2},{y} L{x2 - 9},{y + 6}", stroke=stroke, sw=2)

    def save(self, name: str, theme: str) -> None:
        body = "\n  ".join(self.parts)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {self.h}" width="{W}" height="{self.h}" '
               f'role="img" aria-label="{escape(self.title)}">\n  <title>{escape(self.title)}</title>\n  {body}\n</svg>\n')
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"{name}-{theme}.svg").write_text(svg)


def hero(t: dict, theme: str) -> None:
    s = Svg(400, t, "One phone call, answered a little better after each of six blocks")
    s.text(0, 30, "THE CALL THE WHOLE DAY IS BUILT AROUND", 15, "muted", 600, spacing="1.6")
    # the caller's question
    s.rect(0, 52, 760, 118, "panel", "line", 18)
    s.path("M56,170 L56,196 L88,170 Z", fill="panel", stroke="line", sw=1.5)
    s.rect(54, 164, 38, 8, "panel", r=0)
    s.text(34, 100, "“Can my 8-year-old take the belay class on Saturday?", 27, "ink", 600)
    s.text(34, 138, "And can you book us in?”", 27, "ink", 600)
    # before and after
    s.text(800, 84, "9:30", 17, "muted", 600, font=MONO)
    s.text(800, 110, "The agent cannot answer.", 20, "ink")
    s.text(800, 144, "3:40", 17, "muted", 600, font=MONO)
    s.text(800, 170, "It answers from the handbook, books", 20, "ink")
    s.text(800, 196, "after a yes, and you can prove it.", 20, "ink")
    # six blocks on one track
    y, x0, step = 268, 30, 204
    s.line(x0, y, x0 + step * 5, y, "line", 3)
    for i, (n, name, does) in enumerate(BLOCKS):
        x = x0 + step * i
        s.circle(x, y, 19, "blue")
        s.text(x, y + 7, n, 19, "on", 700, "middle")
        s.text(x - 19, y + 54, name, 21, "ink", 700)
        words = does.split(" ")
        cut = next((k for k in range(len(words), 0, -1) if len(" ".join(words[:k])) <= 17), len(words))
        s.text(x - 19, y + 82, " ".join(words[:cut]), 16.5, "muted")
        if words[cut:]:
            s.text(x - 19, y + 104, " ".join(words[cut:]), 16.5, "muted")
    s.save("hero", theme)


def backward(t: dict, theme: str) -> None:
    s = Svg(300, t, "The workshop was designed backward: learner, outcomes, evidence, exercises, then the agenda")
    steps = [("Learner", ["Engineers who have", "called an LLM API"]),
             ("Outcomes", ["Build, diagnose,", "measure, guard, transfer"]),
             ("Evidence", ["Green tests, scoreboard,", "red-team record, canvas"]),
             ("Exercises", ["Seven labs, each ending", "in a checkpoint"]),
             ("Agenda", ["Six blocks,", "9:00 to 5:00"])]
    s.text(0, 30, "DESIGNED IN THIS ORDER", 15, "muted", 600, spacing="1.6")
    cw, gap, y = 216, 30, 58
    for i, (name, lines) in enumerate(steps):
        x = i * (cw + gap)
        last = i == len(steps) - 1
        s.rect(x, y, cw, 150, "panel", "blue" if not last else "line", 14, 2 if not last else 1.5)
        s.circle(x + 30, y + 34, 15, "blue" if not last else "faint")
        s.text(x + 30, y + 40, str(i + 1), 16, "on", 700, "middle")
        s.text(x + 56, y + 41, name, 22, "ink", 700)
        for k, ln in enumerate(lines):
            s.text(x + 18, y + 86 + k * 24, ln, 15.5, "muted")
        if not last:
            s.arrow(x + cw + 5, y + 75, x + cw + gap - 5)
    s.text(0, 250, "The agenda was the fifth decision, not the first.", 19, "ink", 600)
    s.text(0, 278, "A block that produced none of the five outcomes was cut, however interesting.", 17, "muted")
    s.save("designed-backward", theme)


def time_and_help(t: dict, theme: str) -> None:
    s = Svg(380, t, "Where the working day goes, and how the help on the page shrinks from block to block")
    # left: the loop and where the time goes
    s.text(0, 30, "EVERY BLOCK RUNS THE SAME LOOP", 15, "muted", 600, spacing="1.6")
    loop, x = [("Explain", 92), ("Demo", 78), ("Build", 76), ("Debrief", 94)], 0
    for i, (name, w) in enumerate(loop):
        s.rect(x, 52, w, 40, "panel", "line", 20)
        s.text(x + w / 2, 78, name, 17, "ink", 600, "middle")
        x += w
        if i < len(loop) - 1:
            s.arrow(x + 8, 72, x + 34)
            x += 42
    s.text(0, 142, "WHERE THE WORKING DAY GOES", 15, "muted", 600, spacing="1.6")
    total, x, bw, by, bh = sum(m for _, m, _ in TIME), 0, 560, 162, 64
    for _, mins, col in TIME:
        w = bw * mins / total
        s.rect(x, by, w - 3, bh, col, r=8)
        s.text(x + 14, by + 27, f"{round(100 * mins / total)}%", 21, "on", 700)
        s.text(x + 14, by + 50, f"{mins} min", 15, "on", 500)
        x += w
    x = 0
    for name, _, col in TIME:  # legend: the first segment is too narrow to carry its own name
        s.rect(x, by + bh + 16, 14, 14, col, r=3)
        s.text(x + 22, by + bh + 28, name, 16, "ink", 600)
        x += 22 + len(name) * 9.2 + 26
    s.text(0, 312, "No explanation runs longer than 15 minutes.", 17, "muted")
    s.text(0, 338, "Everyone is writing code 25 minutes after the day starts.", 17, "muted")
    # right: scaffolding comes down
    ox = 660
    s.text(ox, 30, "THE HELP ON THE PAGE SHRINKS", 15, "muted", 600, spacing="1.6")
    tiers = [("Blocks 1 and 2", "Code-along", "Every line you write is on the page", 1.0),
             ("Blocks 3 to 5", "Pairs build", "The key parts are described, not given", 0.58),
             ("Red team, last block", "Challenge", "An outcome and constraints, no steps", 0.18)]
    for i, (when, mode, what, frac) in enumerate(tiers):
        y = 56 + i * 96
        s.rect(ox, y, 540, 78, "panel", "line", 12)
        s.rect(ox + 16, y + 56, 508, 8, "rest", r=4)
        s.rect(ox + 16, y + 56, 508 * frac, 8, "blue", r=4)
        s.text(ox + 16, y + 28, mode, 19, "ink", 700)
        s.text(ox + 524, y + 28, when, 15, "muted", 500, "end")
        s.text(ox + 16, y + 48, what, 15, "muted")
    s.text(ox, 364, "Bar length: how much of the solution the lab page hands you.", 15, "faint")
    s.save("time-and-help", theme)


def scoreboard(t: dict, theme: str) -> None:
    s = Svg(96 + 62 * len(SCORES) + 66, t, "Judge pass rate over 19 test calls for five versions of the agent")
    s.text(0, 30, "JUDGE PASS RATE, SAME 19 TEST CALLS", 15, "muted", 600, spacing="1.6")
    x0, bw, y0 = 300, 560, 62
    base = y0 + 62 * len(SCORES) - 8
    s.line(x0, base, x0 + bw, base, "line", 1.5)
    for g in (0, 0.25, 0.5, 0.75, 1.0):  # ticks only: gridlines would run through the value labels
        gx = x0 + bw * g
        s.line(gx, base, gx, base + 6, "line", 1.5)
        s.text(gx, base + 24, f"{int(g * 100)}%", 14, "faint", 400, "middle")
    for i, (label, what, v, note) in enumerate(SCORES):
        y = y0 + 62 * i
        s.text(0, y + 18, label, 19, "ink", 700)
        s.text(0, y + 40, what, 15, "muted")
        w = bw * v
        s.path(f"M{x0},{y + 4} h{w - 5} a5,5 0 0 1 5,5 v24 a5,5 0 0 1 -5,5 h-{w - 5} Z", fill="blue")
        s.text(x0 + w + 12, y + 28, f"{v:.2f}", 20, "ink", 700, font=MONO)
        if note:
            s.text(x0 + w + 72, y + 28, note, 15, "muted")
    s.line(x0, y0 - 6, x0, base, "faint", 1.5)
    s.text(0, s.h - 22, "One recorded run on gpt-5-mini. Re-runs differ by a few cases, and v2 varies most.", 15, "faint")
    s.save("scoreboard", theme)


def main() -> None:
    for theme, t in THEMES.items():
        for draw in (hero, backward, time_and_help, scoreboard):
            draw(t, theme)
    print(f"wrote {len(list(OUT.glob('*.svg')))} files to {OUT.relative_to(OUT.parents[2])}")


if __name__ == "__main__":
    main()
