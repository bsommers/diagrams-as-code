"""Two hosts' protocol stacks with a router between them.

Each layer talks to its peer (dashed), but the data actually travels down the
sender's stack, across each link, and up the receiver's (solid). The router
implements only the lower three layers, so the upper two are end-to-end. The
notes on the left name the protocol data unit at each layer.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

LAYERS = ("Application", "Transport", "Network", "Link", "Physical")
PDUS = ("message", "segment", "packet", "frame", "bits")
PEERS = ("HTTP", "TCP", "IP", "Ethernet")
W, H, PITCH, TOP = 150.0, 40.0, 66.0, 100.0
COLUMNS = {"Host A": 170.0, "Router": 440.0, "Host B": 710.0}
SHADES = ("#FFFFFF", "#F4F4F4", "#E9E9E9", "#DEDEDE", "#D3D3D3")
PATH = {"width": 2.0}
PEER = {"style": "dashed", "two_way": True, "width": 0.9, "head": "open", "tail": "open"}


def diagram() -> Diagram:
    with Diagram("Protocol stacks", theme="paper") as diag:
        stacks: dict[str, dict[str, object]] = {}
        for name, x in COLUMNS.items():
            names = LAYERS if name != "Router" else LAYERS[2:]
            diag.text(f"**{name}**", size=14).at(
                x + W / 2, TOP + PITCH * LAYERS.index(names[0]) - 12, anchor="bottom_center"
            )
            stacks[name] = {
                layer: diag.shape(
                    layer, W, H, style=Style(fill=SHADES[LAYERS.index(layer)], font_size=13)
                ).at(x, TOP + PITCH * LAYERS.index(layer))
                for layer in names
            }
        a, router, b = stacks["Host A"], stacks["Router"], stacks["Host B"]

        # Peer-to-peer protocols: end to end above the router, hop by hop below.
        for layer, protocol in zip(LAYERS, PEERS):
            via = ["Host A", "Router", "Host B"] if layer in router else ["Host A", "Host B"]
            for left, right in zip(via, via[1:]):
                source, target = stacks[left][layer], stacks[right][layer]
                source.anchor("right", 0.5) >> diag.edge(**PEER) >> target.anchor("left", 0.5)
                diag.text(protocol, size=12, padding=2).at(
                    (COLUMNS[left] + W + COLUMNS[right]) / 2,
                    TOP + PITCH * LAYERS.index(layer) + H / 2 - 5, anchor="bottom_center",
                )

        # The path the data takes: down, across, up and down in the router, across, up.
        for upper, lower in zip(LAYERS, LAYERS[1:]):
            a[upper].anchor("bottom", 0.5) >> diag.edge(**PATH) >> a[lower].anchor("top", 0.5)
            b[lower].anchor("top", 0.5) >> diag.edge(**PATH) >> b[upper].anchor("bottom", 0.5)
            if upper in router:
                router[lower].anchor("top", 0.3) >> diag.edge(**PATH) >> router[upper].anchor("bottom", 0.3)
                router[upper].anchor("bottom", 0.7) >> diag.edge(**PATH) >> router[lower].anchor("top", 0.7)
        a["Physical"].anchor("right", 0.5) >> diag.edge(**PATH) >> router["Physical"].anchor("left", 0.5)
        router["Physical"].anchor("right", 0.5) >> diag.edge(**PATH) >> b["Physical"].anchor("left", 0.5)

        # Protocol data units, beside the sender's stack.
        diag.text("**PDU**", size=12).at(COLUMNS["Host A"] - 20, TOP - 12, anchor="bottom_right")
        for layer, pdu in zip(LAYERS, PDUS):
            diag.text(pdu, size=12, italic=True, font="serif").at(
                COLUMNS["Host A"] - 20, TOP + PITCH * LAYERS.index(layer) + H / 2, anchor="right_center"
            )

        diag.bracket("end to end", side="right").spanning(b["Application"], b["Transport"], gap=12)
        diag.bracket("hop by hop", side="right").spanning(b["Network"], b["Physical"], gap=12)
        diag.caption(
            "**Figure 5:** Layered communication through a router; dashed lines join peer layers",
            small_caps=True,
        )
    return diag


def build_diagram(output_dir: Path | str = "output/technical") -> Path:
    return render_all(diagram(), output_dir, "05_protocol_stack")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/technical")
    build_diagram(dest)
