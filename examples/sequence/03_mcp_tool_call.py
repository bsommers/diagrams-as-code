"""A Model Context Protocol tool call, as a UML sequence diagram.

The host application owns the model and one MCP client per server. The client
opens the session with ``initialize``, learns the server's tools with
``tools/list``, and later relays the model's tool call as ``tools/call``. The
server runs the tool and returns its result as content blocks; the host asks
the user first when a tool needs consent. Every request is JSON-RPC 2.0, so
each reply carries the id of its request.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.sequence import SequenceDiagram


def diagram() -> Diagram:
    seq = SequenceDiagram("MCP tool call", theme="iiot_light")
    user = seq.actor("User")
    host = seq.participant("Host (LLM app)")
    client = seq.participant("MCP client")
    server = seq.participant("MCP server")
    tool = seq.participant("Tool backend", kind="database")

    seq.note([client, server], "session setup, once per connection", side="over")
    seq.message(client, server, "initialize (protocolVersion, capabilities)", activate=True)
    seq.reply(server, client, "result: serverInfo, capabilities")
    seq.message(client, server, "notifications/initialized", style="async")
    seq.message(client, server, "tools/list", activate=True)
    seq.reply(server, client, "tools: name, description, inputSchema")
    seq.reply(client, host, "tool catalogue")

    seq.message(user, host, "“What is the weather in Oslo?”", activate=True)
    seq.message(host, host, "model picks get_weather")
    with seq.opt("tool needs consent"):
        seq.message(host, user, "allow get_weather?")
        seq.reply(user, host, "allow")
    seq.message(host, client, "call get_weather {city: Oslo}", activate=True)
    seq.message(client, server, "tools/call (id 7)", activate=True)
    seq.message(server, tool, "GET /forecast?q=Oslo", activate=True)
    seq.reply(tool, server, "200 forecast")
    with seq.alt("tool succeeded") as outcome:
        seq.reply(server, client, "result (id 7): content, isError false", deactivate=False)
        outcome.branch("tool failed")
        seq.reply(server, client, "result (id 7): content, isError true", deactivate=False)
    seq.deactivate(server)
    seq.reply(client, host, "tool result")
    seq.message(host, host, "model writes the answer")
    seq.reply(host, user, "“4 °C and light rain”")
    diag = seq.build()
    diag.caption("**Figure 3:** capability negotiation, tool discovery and one tools/call round trip",
                 small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/sequence") -> Path:
    return render_all(diagram(), output_dir, "03_mcp_tool_call")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/sequence")
    build_diagram(dest)
