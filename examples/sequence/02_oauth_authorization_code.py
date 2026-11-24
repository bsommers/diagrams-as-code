"""The OAuth 2.0 authorization-code flow with PKCE, as a UML sequence diagram.

The client never sees the user's password. It sends the browser to the
authorization server with a code challenge $c = \\mathrm{SHA256}(v)$, gets a
one-time code back through a redirect, and trades the code and the verifier
$v$ for tokens on a back channel. The ``alt`` frame shows the server rejecting
a verifier that does not hash to the challenge.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all
from diagrams_as_code.sequence import SequenceDiagram


def diagram() -> Diagram:
    seq = SequenceDiagram("OAuth 2.0 authorization code flow with PKCE", theme="nord", autonumber=True)
    user = seq.actor("User")
    browser = seq.participant("Browser")
    app = seq.participant("Client app")
    auth = seq.participant("Authorization server")
    api = seq.participant("Resource server")

    seq.message(user, browser, "click Sign in")
    seq.message(browser, app, "GET /login", activate=True)
    seq.message(app, app, "make verifier $v$, challenge $c$")
    seq.reply(app, browser, "302 to /authorize?code_challenge=$c$")
    seq.message(browser, auth, "GET /authorize", activate=True)
    seq.reply(auth, browser, "login and consent page")
    seq.message(user, browser, "credentials, approve")
    seq.message(browser, auth, "POST /authorize")
    seq.note(auth, "code is single use\nand expires in 60 s", side="right")
    seq.reply(auth, browser, "302 to /callback?code=...")
    seq.message(browser, app, "GET /callback?code=...", activate=True)
    seq.message(app, auth, "POST /token (code, $v$)", activate=True)
    with seq.alt("$\\mathrm{SHA256}(v) = c$") as check:
        seq.reply(auth, app, "access + refresh tokens", deactivate=False)
        check.branch("verifier does not match")
        seq.reply(auth, app, "400 invalid_grant", deactivate=False)
    seq.deactivate(auth)
    seq.message(app, api, "GET /me, Bearer token", activate=True)
    seq.reply(api, app, "200 profile")
    seq.reply(app, browser, "session cookie, home page")
    diag = seq.build()
    diag.caption("**Figure 2:** authorization code grant with a proof key (RFC 7636)", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "examples/sequence") -> Path:
    return render_all(diagram(), output_dir, "02_oauth_authorization_code")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/sequence")
    build_diagram(dest)
