"""A TCP connection from handshake to teardown, as a message sequence chart.

Time runs downwards. Each segment is a slanted arrow, because it takes half a
round trip to arrive. The three-way handshake synchronises the initial
sequence numbers $x$ and $y$; one request and one response follow; then each
side closes its half of the connection with FIN. Every acknowledgement number
is the next byte expected, so a SYN or FIN counts as one byte. The connection
state of each end is written beside its lifeline where it changes.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

CLIENT_X, SERVER_X = 330.0, 830.0
TOP, BOTTOM = 130.0, 770.0
FLIGHT = 40.0  # one-way delay, in px of the time axis
# (time sent, from client?, label)
SEGMENTS = [
    (150, True, "**SYN**  $seq = x$"),
    (190, False, "**SYN, ACK**  $seq = y,\\ ack = x + 1$"),
    (230, True, "**ACK**  $ack = y + 1$"),
    (290, True, "**PSH, ACK**  $seq = x + 1,\\ len = 100$  (GET /)"),
    (330, False, "**PSH, ACK**  $seq = y + 1,\\ ack = x + 101,\\ len = 500$"),
    (370, True, "**ACK**  $ack = y + 501$"),
    (450, True, "**FIN, ACK**  $seq = x + 101$"),
    (490, False, "**ACK**  $ack = x + 102$"),
    (560, False, "**FIN, ACK**  $seq = y + 501$"),
    (600, True, "**ACK**  $ack = y + 502$"),
]
CLIENT_STATES = [(112, "CLOSED"), (150, "SYN-SENT"), (230, "ESTABLISHED"), (450, "FIN-WAIT-1"),
                 (530, "FIN-WAIT-2"), (600, "TIME-WAIT"), (740, "CLOSED")]
SERVER_STATES = [(112, "LISTEN"), (190, "SYN-RCVD"), (270, "ESTABLISHED"), (490, "CLOSE-WAIT"),
                 (560, "LAST-ACK"), (640, "CLOSED")]
LIFELINE = Style(stroke="#8A94A6", stroke_width=1.0, dash="6,4")
MSG = {"routing": "direct", "width": 1.4, "arrow_size": 0.9}
STATE = Style(fill="#EEF2F7", stroke="#5B6B82", font_size=11, radius=4, shadow=False)


def diagram() -> Diagram:
    with Diagram("TCP connection lifecycle sequence chart", theme="iiot_light") as diag:
        diag.shape("**Client**\n10.0.0.2:51514", 170, 60, icon="laptop").at(CLIENT_X, 40, anchor="top_center")
        diag.shape("**Server**\n192.0.2.10:443", 170, 60, icon="server").at(SERVER_X, 40, anchor="top_center")
        for x in (CLIENT_X, SERVER_X):
            diag.polyline([(x, TOP - 30), (x, BOTTOM)], style=LIFELINE, obstacle=False)

        for sent, from_client, label in SEGMENTS:
            x1, x2 = (CLIENT_X, SERVER_X) if from_client else (SERVER_X, CLIENT_X)
            diag.connect((x1, sent), (x2, sent + FLIGHT), **MSG)
            mid_x, mid_y = (x1 + x2) / 2, sent + FLIGHT / 2
            diag.text(label, size=12).at(mid_x, mid_y - 13, anchor="bottom_center")

        for when, name in CLIENT_STATES:
            diag.shape(name, 108, 24, style=STATE).at(CLIENT_X - 16, when, anchor="right_center")
        for when, name in SERVER_STATES:
            diag.shape(name, 108, 24, style=STATE).at(SERVER_X + 16, when, anchor="left_center")

        # Phases on the far left, timers on the far right.
        phase_x = 40.0
        for label, start, end in (("**three-way**\n**handshake**", 150, 270), ("**data**\n**transfer**", 290, 410),
                                  ("**teardown**", 450, 640)):
            diag.bracket(label, side="left", length=end - start).at(phase_x, start)
        diag.bracket("TIME-WAIT lasts $2 \\cdot \\mathrm{MSL}$, so late\nsegments die before the port is reused",
                     side="right", length=116).at(CLIENT_X + 12, 618)
        diag.bracket("1 RTT", side="right", length=80).at(SERVER_X + 140, 190)
        diag.text(
            "*ISNs* $x$, $y$ are random 32-bit numbers.\n"
            "The handshake costs one RTT before\nthe first request can be sent.",
            size=12, font="serif", italic=True,
        ).at(SERVER_X + 16, 680)
        diag.text("time", size=11, italic=True, color="#5B6B82").at(SERVER_X + 160, 330, anchor="bottom_center")
        diag.connect((SERVER_X + 160, 334), (SERVER_X + 160, 440), routing="direct", width=1.0,
                     color="#5B6B82")
        diag.caption("**Figure 8:** TCP three-way handshake, one request and response, and the four-segment close",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/computer_science") -> Path:
    return render_all(diagram(), output_dir, "08_tcp_connection_lifecycle")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer_science")
    build_diagram(dest)
