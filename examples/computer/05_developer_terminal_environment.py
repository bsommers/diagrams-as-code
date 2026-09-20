"""Example architecture: Modern Developer Terminal Toolchain (COMPUTER domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from iiot_diagrams import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/computer") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "05_developer_terminal_environment.svg"
    readme_file = out / "05_developer_terminal_environment_README.md"

    with Diagram("Modern Developer Terminal Toolchain", theme="nord") as diag:
        with diag.group("User Shell") as g_1:
            terminal = diag.add(Shape("terminal", "GPU Accelerated Terminal", icon="terminal", emulator="Alacritty / WezTerm"))
            tmux = diag.add(Shape("tmux", "Tmux Session Multiplexer", icon="workflow", panes="Dev / Logs / Build"))
            tmux.below(terminal, margin=30)

        with diag.group("Developer Tools") as g_2:
            neovim = diag.add(Shape("neovim", "Neovim IDE Engine", icon="document", lsp="Pyright / Rust-Analyzer"))
            git_daemon = diag.add(Shape("git_daemon", "Git Version Control", icon="shield", signing="SSH Key Signed"))
            git_daemon.below(neovim, margin=30)

        with diag.group("Runtime Environment") as g_3:
            docker_sock = diag.add(Shape("docker_sock", "Docker Daemon Socket", icon="container", socket="/var/run/docker.sock"))
            local_db = diag.add(Shape("local_db", "Local PostgreSQL Container", icon="database", port="5432"))
            local_db.below(docker_sock, margin=30)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)

        # Establish inter-element connections with protocol annotations
        terminal >> diag.edge("Launch Terminal", style="solid") >> tmux
        tmux >> diag.edge("Active Pane", style="solid") >> neovim
        neovim >> diag.edge("Git Blame / Commit", style="dashed") >> git_daemon
        neovim >> diag.edge("Test Containers", style="dashed") >> docker_sock
        docker_sock >> diag.edge("Spin Up DB", style="solid") >> local_db

        diag.render_svg(svg_file)
        diag.generate_readme("05_developer_terminal_environment.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/computer")
    build_diagram(dest)
