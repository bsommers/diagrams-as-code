"""Three CPU schedulers on the same four processes, as Gantt charts.

Every chart is produced by simulating the scheduler in the script: first come
first served, shortest remaining time first (preemptive SJF) and round robin
with a quantum of 2. Arrivals are marked above the time axis. The table on the
right gives the average waiting and turnaround time of each policy, so the
trade-off is visible: SRTF minimises average waiting time, round robin bounds
the response time, FCFS is simplest and suffers the convoy effect.
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

PROCESSES = {"P1": (0, 5), "P2": (1, 3), "P3": (2, 1), "P4": (3, 2)}  # name: (arrival, burst)
COLOURS = {"P1": "#AFCBEF", "P2": "#F6C6A8", "P3": "#BFE3C0", "P4": "#E3C6EE"}
QUANTUM = 2
X0, UNIT, ROW_Y, ROW_H, ROW_GAP = 250.0, 46.0, 120.0, 40.0, 92.0
CELL = Style(fill="#FFFFFF", font_size=12, radius=0, shadow=False)
HEAD = Style(fill="#ECE7F4", font_size=12, radius=0, shadow=False)


def fcfs():
    t, out = 0, []
    for name, (arrival, burst) in sorted(PROCESSES.items(), key=lambda p: p[1][0]):
        t = max(t, arrival)
        out.append((name, t, t + burst))
        t += burst
    return out


def srtf():
    left = {n: b for n, (_, b) in PROCESSES.items()}
    t, out = 0, []
    while any(left.values()):
        ready = [n for n in left if left[n] and PROCESSES[n][0] <= t]
        if not ready:
            t += 1
            continue
        run = min(ready, key=lambda n: (left[n], PROCESSES[n][0]))
        left[run] -= 1
        if out and out[-1][0] == run and out[-1][2] == t:
            out[-1] = (run, out[-1][1], t + 1)
        else:
            out.append((run, t, t + 1))
        t += 1
    return out


def round_robin(q: int):
    order = sorted(PROCESSES, key=lambda n: PROCESSES[n][0])
    left = {n: PROCESSES[n][1] for n in order}
    queue, t, out, arrived = deque(), 0, [], 0
    while arrived < len(order) or queue:
        while arrived < len(order) and PROCESSES[order[arrived]][0] <= t:
            queue.append(order[arrived])
            arrived += 1
        if not queue:
            t = PROCESSES[order[arrived]][0]
            continue
        run = queue.popleft()
        span = min(q, left[run])
        out.append((run, t, t + span))
        t += span
        left[run] -= span
        # Processes that arrived during the slice queue ahead of the preempted one.
        while arrived < len(order) and PROCESSES[order[arrived]][0] <= t:
            queue.append(order[arrived])
            arrived += 1
        if left[run]:
            queue.append(run)
    return out


def metrics(schedule):
    finish = {name: end for name, _, end in schedule}
    turnaround = {n: finish[n] - PROCESSES[n][0] for n in PROCESSES}
    waiting = {n: turnaround[n] - PROCESSES[n][1] for n in PROCESSES}
    k = len(PROCESSES)
    return sum(waiting.values()) / k, sum(turnaround.values()) / k


def diagram() -> Diagram:
    policies = [("FCFS", fcfs()), ("SRTF", srtf()), (f"Round robin, $q = {QUANTUM}$", round_robin(QUANTUM))]
    horizon = max(end for _, sched in policies for _, _, end in sched)
    with Diagram("CPU scheduling Gantt charts", theme="pastel_light") as diag:
        # Arrivals, once, above the first chart.
        diag.text("arrivals", size=11, italic=True).at(X0 - 14, ROW_Y - 34, anchor="right_center")
        for name, (arrival, _) in PROCESSES.items():
            x = X0 + arrival * UNIT
            diag.connect((x, ROW_Y - 46), (x, ROW_Y - 4), routing="direct", width=1.0, arrow_size=0.6)
            diag.text(name, size=11).at(x + 4, ROW_Y - 40, anchor="left_center")

        for row, (title, schedule) in enumerate(policies):
            y = ROW_Y + row * ROW_GAP
            diag.text(f"**{title}**", size=13).at(X0 - 14, y + ROW_H / 2, anchor="right_center")
            for name, start, end in schedule:
                diag.shape(name, (end - start) * UNIT, ROW_H,
                           style=Style(fill=COLOURS[name], radius=0, shadow=False, font_size=12),
                           fit_label=False).at(X0 + start * UNIT, y)
            for t in range(horizon + 1):
                diag.text(str(t), size=10).at(X0 + t * UNIT, y + ROW_H + 4, anchor="top_center")

        # The process table and the averages.
        tx = X0 + horizon * UNIT + 70
        cols = (64.0, 64.0, 64.0)
        diag.text("**Workload**", size=13).at(tx, ROW_Y - 40, anchor="bottom_left")
        for c, text in enumerate(("process", "arrival", "burst")):
            diag.shape(text, cols[c], 26, style=HEAD, fit_label=False).at(tx + sum(cols[:c]), ROW_Y - 34)
        for r, (name, (arrival, burst)) in enumerate(PROCESSES.items(), start=1):
            values = (name, str(arrival), str(burst))
            for c, text in enumerate(values):
                style = Style(fill=COLOURS[name], radius=0, shadow=False, font_size=12) if c == 0 else CELL
                diag.shape(text, cols[c], 26, style=style, fit_label=False).at(tx + sum(cols[:c]), ROW_Y - 34 + r * 26)

        my = ROW_Y + 2 * ROW_GAP - 30
        mcols = (110.0, 70.0, 70.0)
        diag.text("**Averages**", size=13).at(tx, my - 6, anchor="bottom_left")
        for c, text in enumerate(("policy", "$W_{\\mathrm{avg}}$", "$T_{\\mathrm{avg}}$")):
            diag.shape(text, mcols[c], 26, style=HEAD, fit_label=False).at(tx + sum(mcols[:c]), my)
        best = min(metrics(schedule)[0] for _, schedule in policies)
        for r, (title, schedule) in enumerate(policies, start=1):
            wait, turn = metrics(schedule)
            short = title.split(",")[0]
            mark = "**" if wait == best else ""
            for c, text in enumerate((short, f"{mark}{wait:.2f}{mark}", f"{mark}{turn:.2f}{mark}")):
                diag.shape(text, mcols[c], 26, style=CELL, fit_label=False).at(tx + sum(mcols[:c]), my + r * 26)

        diag.text(
            "Waiting time $W_i = T_i - b_i$, turnaround $T_i = c_i - a_i$\n"
            "($a$ arrival, $b$ burst, $c$ completion). Context switches are taken as free.",
            size=12, font="serif", italic=True,
        ).at(X0, ROW_Y + 3 * ROW_GAP - 10)
        diag.caption("**Figure 9:** One workload under FCFS, SRTF and round robin; time in scheduler ticks",
                     small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/computer_science") -> Path:
    return render_all(diagram(), output_dir, "09_cpu_scheduling_gantt")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer_science")
    build_diagram(dest)
