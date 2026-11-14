"""Free text, a caption and brackets (PRIM-01)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Text, caption and brackets", theme="paper") as diag:
        diag.text("**Scheduler queues**", size=15).at(60, 40)
        ready = diag.shape("Ready", 110, 44).at(60, 80)
        waiting = diag.shape("Waiting", 110, 44).below(ready, margin=16)
        blocked = diag.shape("Blocked", 110, 44).below(waiting, margin=16)
        done = diag.shape("Done", 110, 44).below(blocked, margin=40)

        # A brace along the three live queues, and a square bracket under the lot.
        diag.bracket("runnable or\nwaiting on I/O", side="right").spanning(ready, blocked)
        diag.bracket("all states", side="bottom", shape="square").spanning(ready, done, gap=14)
        diag.bracket(side="left", shape="round").spanning(ready, blocked)

        diag.text(
            "A task leaves *Blocked* when its resource is released;\n"
            "the wait is bounded by $t_{max} = \\sum_{i} c_i$.",
            size=12, max_width=260,
        ).right_of(waiting, margin=150)
        diag.text("serif italic, for remarks", font="serif", italic=True).right_of(done, margin=150)
        diag.caption("**Figure 1:** Task states of the scheduler", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/primitives") -> Path:
    return render_all(diagram(), output_dir, "01_text_caption_bracket")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/primitives")
    build_diagram(dest)
