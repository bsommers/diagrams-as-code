"""Endpoint-native composition enforcement: a four-layer figure in the style of a paper.

A reproduction of a reference figure, laid out by hand. Its coordinates were
measured off the reference at 2000 px wide and are scaled by ``U``. Where the
reference slipped (a label used twice, "Taint Tracking Tracker", an unbalanced
bracket, an unexplained frame behind one box), this figure is corrected.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all
from diagrams_as_code.solids import Solid, oblique

U = 0.55  # the reference is 2000 px wide; this figure is 1100

BODY = 14.0
PAD = 10.0
# The titles sit beside the content, not above it, so the bands keep no header strip.
BAND = {"padding": PAD, "header_height": 0.0}
PANEL = Style(fill="#E9E9EC", stroke="#14213D", stroke_width=1.6)
BOX = Style(font_size=BODY)
SPINE = {"width": 3.0, "arrow_size": 0.9}
GLASS = Style(fill="#C9D3E6", fill_opacity=0.5, stroke="#1F2F57", stroke_width=1.2)


def u(*values: float) -> tuple[float, ...]:
    return tuple(round(v * U, 1) for v in values)


def diagram() -> Diagram:
    with Diagram("Composition enforcement architecture", theme="paper") as diag:

        def text(body: str, x: float, y: float, anchor: str = "top_left", **kw):
            kw.setdefault("size", BODY)
            return diag.text(body, **kw).at(*u(x, y), anchor=anchor)

        def box(label: str, x0: float, y0: float, x1: float, y1: float, **kw):
            kw.setdefault("style", BOX)
            return diag.shape(label, *u(x1 - x0, y1 - y0), **kw).at(*u(x0, y0))

        def nested(shape, panel_xy: tuple[float, float], x: float, y: float):
            return shape.inside(panel, "top_left", *u(x - panel_xy[0], y - panel_xy[1]))

        def frame(y0: float, y1: float) -> None:
            # Two empty texts at opposite corners: every band then spans the same
            # width and the height the reference gives it, whatever it holds.
            diag.text("").at(30 * U + PAD, y0 * U + PAD)
            diag.text("").at(1978 * U - PAD, y1 * U - PAD, anchor="bottom_left")

        # ── 1. Strategic governance ──────────────────────────────────────────
        with diag.band("1. Strategic Governance Layer", **BAND):
            frame(25, 325)
            text("**Intent Registry Specification**", 68, 118, size=15)
            text("Exact formal definition: $(I, C, D, T, E, P)$", 68, 170)
            intent = box(
                "Registered Intent ($I$)\n[Objective, Requester, Delegation\nLimits, Scoped Tool Catalog,\n"
                "Data Class Boundaries]",
                678, 130, 1215, 287,
            )
            invariant = box(
                "Red Thread Invariant (Verification)\n$\\forall a_i,\\; a_i \\leadsto I$\n"
                "*Verifiable Provenance Path:*\n"
                "Valid$(a_i, I)$ = Provenance$(a_i, I) \\land$ Capability$(a_i, I)$\n"
                "$\\land$ Trajectory$(a_i, T) \\land$ Constraint$(a_i, D)$",
                1247, 85, 1953, 307,
            )

        # ── 2. Enabling substrate ────────────────────────────────────────────
        with diag.band("2. Enabling Substrate Layer", **BAND) as substrate:
            frame(348, 660)
            text("Define the 6-tuple:", 72, 415)
            text("$X = (I, C, D, T, E, P)$", 68, 452, size=20)
            text("Super Permission Set\n(Allowed Region, $A \\subseteq X$)", 290, 530, "top_center", align="center")
            origin = (570, 367)
            panel = box("", 570, 367, 1573, 638, style=PANEL)
            nested(
                diag.text("Capabilities &\nTool Primitives ($C$)", size=BODY, align="center"), origin, 608, 392
            )
            trajectory = nested(diag.shape("Execution\nTrajectory ($T$)", *u(303, 102), style=BOX), origin, 915, 385)
            provenance = nested(diag.shape("Dynamic\nProvenance ($D$)", *u(267, 102), style=BOX), origin, 618, 517)
            environment = nested(diag.shape("Task\nEnvironment ($E$)", *u(276, 102), style=BOX), origin, 908, 517)
            topology = nested(
                diag.cuboid(
                    "", *u(210, 135, 110), projection=oblique(47, 0.6),
                    style=Style(fill="#DADADD", stroke="#555555"), hidden="none",
                ),
                origin, 1290, 440,
            )
            # The cuboid's label sits on its front face.
            diag.text("Allowed Task\nTopology\n($T_{\\mathrm{valid}}$)", size=BODY, align="center").inside(
                topology, "bottom_left", *u(10, -14)
            )
            text(
                "Allowed Task Topology\n($T_{\\mathrm{valid}}$)\n(positive Capability Space)",
                1765, 478, "top_center", align="center",
            )

        # ── 3. Clipping engine ───────────────────────────────────────────────
        with diag.band("3. Trajectory & Lineage\nClipping Engine", **BAND) as clipping:
            frame(682, 1022)
            text("(Enforces Constraints)", 59, 795)
            region = diag.solid(
                Solid.hull([
                    (-100, 20, -60), (100, 40, -60), (120, 10, 70), (-80, -10, 80),
                    (-60, -120, -10), (60, -110, 20), (10, 130, 10),
                ]),
                projection=oblique(35, 0.55), scale=0.66, style=GLASS,
                cut=((0, 5, 0), (0.25, 1, 0.1)), cut_size=125, cut_fill="#3A4560",
            ).at(*u(975, 850), anchor="center")
            note = {"size": BODY}
            diag.leader("Clipping Plane", u(838, 790), at=u(712, 705), anchor="top_right", **note)
            diag.leader("Section through the\nallowed region", u(1000, 800), at=u(1236, 700), **note)
            diag.leader("Multi-dimensional\nboundary space", u(790, 822), at=u(712, 800), anchor="top_right",
                        align="right", **note)
            text("Sinks and sources flow\nacross boundary limits", 712, 932, "top_right", align="right")
            evaluated = box(
                "Evaluated Sequence vs. clipping planes:\nread(.env_secrets) → encode(interpreter) →\n"
                "network(post_to_external_api)",
                1253, 845, 1948, 968, style=Style(fill="#DCDCDC", font_size=BODY),
            )
            text("*Compositional Trajectory Evaluation*", 1600, 974, "top_center")
            text("Inequality Clipping Constraints\n$g_k(I, C, D, T) \\leq 0$", 1705, 722, "top_center", align="center")

        # ── 4. Endpoint runtime ──────────────────────────────────────────────
        with diag.band("4. Endpoint Runtime & Execution Control", **BAND):
            frame(1044, 1405)
            origin = (262, 1098)
            panel = runtime = box("", 262, 1098, 1578, 1383, style=PANEL)
            nested(diag.text("**Local Agent Runtime**", size=BODY), origin, 402, 1108)
            agents = [
                nested(diag.shape(label, *u(560, 58), style=BOX), origin, 285, y)
                for label, y in (
                    ("Agentic Runtime & Local Orchestrator", 1153),
                    ("Dispatched AI Agents / Swarms", 1228),
                    ("Provenance / Taint Tracker", 1303),
                )
            ]
            nested(
                diag.text("Proposed\nTransition\n($E_t \\to E_{t+1}$)", size=BODY, align="center"),
                origin, 880, 1112,
            )
            nested(diag.text("2-way", size=BODY), origin, 906, 1258)
            policy = nested(
                diag.shape(
                    "**Policy Decision Function**\n$\\Pi(E_t, E_{t+1}) \\to \\{\\mathrm{allow}, \\mathrm{deny}\\}$",
                    *u(522, 97), style=BOX,
                ),
                origin, 1033, 1153,
            )
            nested(
                diag.text(
                    "Compute safe execution space\n"
                    "$\\Omega_{\\mathrm{safe}} = \\Omega_{\\mathrm{capability}} \\cap "
                    "(\\bigcap_{k} \\Omega_{\\mathrm{constraint},k}) \\cap \\Omega_{\\mathrm{intent}}$",
                    size=BODY, align="center",
                ),
                origin, 1040, 1262,
            )
            approved = text(
                "Approved Execution\n/ Side Effects\n(State $E_{t+1} \\in \\Omega_{\\mathrm{safe}}$)",
                1808, 1158, "top_center", align="center", padding=4,
            )
            truncation = text("Deterministic\nTruncation", 1802, 1305, "top_center", align="center", padding=4)

        # ── Lines ────────────────────────────────────────────────────────────
        # The heavy spine down the middle of the figure.
        spine = 1000
        fx = (spine - 678) / (1215 - 678)
        intent.anchor("bottom", fx) >> diag.edge(**SPINE) >> substrate_anchor(diag, spine, 367)
        diag.connect(u(spine, 638), u(spine, 706), routing="direct", **SPINE)
        diag.connect(u(spine, 1000), u(spine, 1098), routing="direct", **SPINE)

        # Verification loop between the intent and its invariant.
        diag.connect(
            intent.anchor("top", 0.45), invariant.anchor("left", 0.06), routing="direct",
            via=[u(920, 98)], width=1.6,
        )
        invariant.anchor("left", 0.5) >> diag.edge(width=1.6) >> intent.anchor("right", 0.42)

        # The trajectory fans out to what it is built from.
        for target in (provenance.anchor("top", 1.0), environment.anchor("top", 0.5),
                       topology.anchor("left", 0.37)):
            diag.connect(trajectory.anchor("bottom", 0.0 if target.element is provenance else 0.6),
                         target, routing="direct", arrow_head=False, width=1.0)
        environment >> diag.edge(ellipsis=True, width=1.2) >> topology.anchor("left", 0.72)

        # Trajectories through the allowed region; two leave it.
        curve = {"routing": "spline", "width": 3.0, "z": 5}
        diag.connect(u(952, 925), u(740, 975), via=[u(870, 958)], **curve)
        diag.connect(u(1000, 910), u(1205, 825), via=[u(1085, 885), u(1150, 858)], **curve)
        diag.connect(u(1000, 910), u(1170, 985), via=[u(1070, 950)], **curve)

        diag.connect(u(1528, 772), u(1212, 818), routing="direct", width=0.75, head="open", arrow_size=0.8)
        diag.connect(u(1528, 772), u(1165, 858), routing="direct", width=0.75, arrow_head=False)
        evaluated.anchor("left", 0.5) >> diag.edge(routing="direct", width=0.75, arrow_head=False) >> diag.point(
            *u(1105, 912)
        )

        # Runtime to policy and out.
        diag.bracket(side="right", shape="square", depth=6).spanning(agents[0], agents[2], gap=5)
        diag.connect(u(868, 1240), policy.anchor("left", 0.9), routing="direct", two_way=True, width=2.0,
                     color="#555555")
        policy.anchor("right", 0.62) >> diag.edge(width=2.2) >> approved
        policy.anchor("right", 0.95) >> diag.edge(width=2.2, corner_radius=0) >> truncation

        diag.caption(
            "FIGURE 1: Endpoint-Native Composition Enforcement Architecture for Agentic Trajectories",
            size=22, gap=18,
        )
    return diag


def substrate_anchor(diag: Diagram, x: float, y: float):
    """The point on the substrate panel's top edge under the spine."""
    return diag.point(*u(x, y))


def build_diagram(output_dir: Path | str = "output/technical") -> Path:
    return render_all(diagram(), output_dir, "01_composition_enforcement")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/technical")
    build_diagram(dest)
