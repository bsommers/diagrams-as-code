# Gantt charts and timelines

`diagrams_as_code.gantt` draws schedules and dated events on an ordinary `Diagram`. It has two parts:

- **`GanttChart`** schedules tasks from durations and dependencies, finds the critical path and draws the chart.
- **`Timeline`** puts dated events on a ruler. Its labels are stacked so that none overlap. Use it for incident timelines and release trains.

Both draw with the diagram's own text, polygons, paths and edges. A chart is therefore part of the figure, and it goes through `render_all`, themes, `diagrams-as-code lint`, the visual audit, SVG, PNG and PDF output, CLI rendering and MCP discovery like any other diagram. The module uses only the standard library.

Three worked examples are in [`examples/project_management/`](../examples/project_management/):

| Script | Shows |
|---|---|
| `01_gantt_critical_path.py` | A product launch: phases, progress, milestones, dependencies, the critical path and a status date. |
| `02_release_train_timeline.py` | A year of overlapping release trains, with releases above the ruler and code freezes below it. |
| `03_incident_timeline.py` | A minute-by-minute incident on a dark theme, with impact windows shaded. |

## 1. A Gantt chart

```python
from datetime import date
from diagrams_as_code import Diagram
from diagrams_as_code.gantt import GanttChart

with Diagram("Launch plan", theme="pastel_light") as diag:
    g = GanttChart(diag, today=date(2026, 3, 30))
    with g.phase("Discovery"):
        g.task("research", "User research", start=date(2026, 3, 2), duration=10, progress=1.0)
        g.task("spec", "Product spec", after="research", duration=5, progress=0.6)
    g.milestone("signoff", "Spec sign-off", after="spec")
    with g.phase("Build"):
        g.task("api", "Backend API", after="signoff", duration=20)
        g.task("ui", "Web client", after="signoff", end=date(2026, 4, 3), start=date(2026, 3, 20))
    g.milestone("ga", "General availability", after=["api", "ui"])
    layout = g.draw()        # or use `with GanttChart(diag) as g:`; leaving the block draws it
    print(layout.schedule.critical_path)
```

### Tasks, milestones and phases

| Call | Meaning |
|---|---|
| `task(id, label, start=, duration=, end=, after=, lag=, progress=, color=)` | A bar. Give `duration` in calendar days (at least 1), or an inclusive `end` together with a `start`. `after` is one id or a list of ids. `progress` runs from 0 to 1. |
| `milestone(id, label, date=, after=)` | A diamond with zero duration. It sits on `date`, or on the day its predecessors finish. |
| `with g.phase(label):` | A phase row with a summary bar that spans every task declared inside the block. Phases nest. |

Rows appear in declaration order. A task's label goes in the left column (italic for a milestone, bold for a phase). Its percent complete goes in a **Done** column. Labels accept the same markup as any other text, including `**bold**`, `*italic*` and `$math$` such as `$\frac{1}{2}$`. They are measured with the bundled text metrics, so the column fits them exactly. Pass `label_width=` to wrap long labels; a row grows to fit its label.

### Scheduling rules

- `start` is the first day of work. `duration` counts calendar days. There is no working-day calendar.
- A task's **finish** is the day after its last day, so the end is exclusive. A finish-to-start successor starts on its predecessor's finish date. The bar runs from the start date up to the finish date.
- `end=` is inclusive: `start=Mar 2, end=Mar 6` is 5 days.
- `lag=` adds days after every predecessor finishes. A negative lag is a lead.
- A `start` on a task that also has dependencies is a *start no earlier than* constraint. The task starts on whichever is later: that date, or its predecessors' finish.
- A task with no `start` and no dependencies starts on the chart's `start=`. If no chart start is given, scheduling raises an error.

### Critical path: the algorithm

`schedule(tasks)` (also available as `GanttChart.schedule()`) runs the critical path method using whole days:

1. **Topological order.** Kahn's algorithm uses a heap keyed on declaration index, so the order is the same on every run. If tasks remain once the heap is empty, they lie on or downstream of a cycle. A walk along their unfinished predecessors finds the cycle, and it is reported as `dependency cycle: a -> b -> a`.
2. **Forward pass.** Early start = the maximum of (each predecessor's early finish + lag) and the start constraint. Early finish = early start + duration. The project finish is the largest early finish.
3. **Backward pass**, in reverse order. Late finish = the minimum of (each successor's late start − that successor's lag), or the project finish for a task with no successors. Late start = late finish − duration.
4. **Slack** = late start − early start. Tasks with zero slack are **critical**. Without start constraints these are exactly the tasks on a longest path through the dependency graph. All the arithmetic is in integers, so ties are exact: every tied longest path is critical.
5. **Critical links** are dependencies whose two ends are both critical and where the predecessor's finish plus lag equals the successor's start. That is, the link actually drives the successor. These arrows are drawn in the critical colour.
6. `Schedule.paths()` lists every chain of critical links. A chain starts at a critical task with no critical predecessor and ends at one that finishes on the project finish. Chains are listed in declaration order. `Schedule.critical_path` is the first of them, so declaration order breaks ties.

A start constraint can make a predecessor non-critical: if `b` may not start before day 5 but `a` finishes on day 3, `a` has two days of slack.

### What the chart draws

- **Date header in two tiers.** The lower tier has one cell per day, week (starting Monday), month or year. The upper tier names the month or year. With `scale="auto"` the chart picks the finest scale whose every cell can hold its label, and falls back to a coarser step (every 2 weeks, every quarter) only when no whole-step scale fits. Days are used for charts of up to 45 days. The date range is snapped to whole periods. A label that does not fit its cell is left out, so header labels never overlap.
- **Bars.** A bar has a light fill, with a darker fill from the left for the completed share. Critical bars have a red outline and fill.
- **Milestones** are diamonds, with the date to the right.
- **Phase summary bars** run over each phase row.
- **Today line.** `today=` draws a dashed line labelled under the rows. It is drawn only when the date falls inside the chart.
- **Legend.** A legend under the chart lists the mark types that are used. Pass `legend=False` to leave it off.
- **Dependency arrows** are orthogonal. The router tries these candidates in order:
  1. An **L**: down out of the predecessor's bottom edge, then right along the successor's row into its left end.
  2. For a milestone successor, a drop into the diamond's top vertex.
  3. A five-segment route along the gap between two rows.

  Each candidate is tried first against every mark, then with phase summary bars allowed to be crossed. A candidate is rejected if any segment enters a bar, a diamond or a label (inflated by 3 px), or runs along an earlier arrow that shares neither of its ends. Arrows that leave the same predecessor reuse its exit point, so they share a trunk. Critical links are routed first, so they get the cleanest lines, and drawn last, so a shared trunk shows the critical colour. The rows are visited in a fixed order, so the result is deterministic. If no candidate is clear, the arrow is drawn anyway, `layout.warnings` records it, and a `UserWarning` is raised, which `lint` reports.

Arrows are diagram edges with fixed waypoints, and their ends are named points (`<task>-finish`, `<task>-start`). The visual audit and the bill of materials therefore see them like any other connection.

### Options

| Option | Default | Meaning |
|---|---|---|
| `origin` | `(40, 40)` | Top-left corner of the chart, in pixels. |
| `width` | `720` | Width of the date area in pixels. |
| `day_width` | none | Pixels per day. Overrides `width`. |
| `scale` | `"auto"` | `days`, `weeks`, `months` or `years`. |
| `start`, `end` | none | Widen the date range. `start` is also the default task start. |
| `today` | none | Status date line. |
| `row_height`, `font_size` | `28`, `12` | Row height and text size. |
| `critical` | `True` | Highlight critical bars and links. |
| `palette` | none | Override colours by `Palette` field: `bar`, `bar_stroke`, `progress`, `critical`, `critical_fill`, `milestone`, `phase`, `grid`, `header`, `band`, `today`, `arrow`, `event`, `span`. |

`draw()` returns a `GanttLayout` with the schedule, scale, ticks, bar and label boxes and arrow waypoints, which tests can inspect.

## 2. A timeline

```python
from datetime import datetime
from diagrams_as_code.gantt import Timeline

with Diagram("Incident", theme="nord") as diag:
    t = Timeline(diag, width=1000, label_width=160)
    t.span(datetime(2026, 4, 14, 14, 2), datetime(2026, 4, 14, 14, 52), "Customer impact")
    t.event(datetime(2026, 4, 14, 14, 2), "**Alert:** p99 latency > 2 s")
    t.event(datetime(2026, 4, 14, 14, 10), "Status page: investigating", side="below", marker="diamond")
    t.draw()
```

- `event(when, label, side="above"|"below", marker="dot"|"diamond", color=, bold=)`. `when` is a `date` or a naive `datetime`. A timezone-aware datetime is rejected, because the module has no timezone logic.
- `span(start, end, label, color=)` shades a period behind the chart. Its label sits in a lane under the chart. Overlapping spans take separate lanes, and a lane is reserved for the wider of the span and its label.
- The ruler is a band with tick labels inside it, so stems never cross a tick label. The scale (`minutes`, `hours`, `days`, `weeks`, `months`, `years`) and its step (for example every 15 minutes or every 3 months) are the finest whose centred labels keep 10 px apart. Hour ticks at midnight show the date. Labels that would stick out of the ruler's ends are left off.

### Label stacking: `pack_levels`

Each event is a stem at `x` with a flag label to its right. `pack_levels(items)` assigns each event a level, where level 0 is nearest the ruler, and guarantees two things:

- No two labels overlap.
- No stem crosses another event's label.

It places events from right to left. Each event goes on the lowest level `k` whose label ends (plus an 8 px gap) before every stem already placed on level `k` or higher. Two facts make this enough:

- A label placed later always lies to the left of the stems already placed, so it can only collide with them on its own level or below a taller stem.
- A stem placed later is left of every placed label, so it crosses none of them.

The result is a staircase: in a crowd of close events, the earliest climbs highest, and the timeline reads top to bottom in time order. Events at the same instant keep their declaration order from top to bottom. Each side of the ruler is packed separately.

## 3. Determinism

Layout uses integer day and second arithmetic, a fixed declaration-order tie-break everywhere, and the same text metrics as the rest of the engine. Rendering the same script twice gives byte-identical SVG, and so does rendering it in separate processes with different hash seeds (`tests/test_gantt.py` checks both).

## 4. Limits

- Calendar days only: there are no working-day calendars, holidays or resource levelling.
- Only finish-to-start dependencies; dependencies on a phase are not supported. Start-to-start and finish-to-finish links are not modelled.
- A Gantt chart takes `datetime.date` only. A timeline also takes naive `datetime`. There is no timezone logic.
- Colours are resolved when `draw()` runs. If the theme is changed afterwards, for example with `diagrams-as-code render --theme`, the text and canvas follow the new theme but the chart keeps its palette.
- The arrow router is a search over candidate routes, not a general maze router. On dense random charts about 0.5% of dependencies find no clear candidate; they are drawn anyway and reported as a warning.
