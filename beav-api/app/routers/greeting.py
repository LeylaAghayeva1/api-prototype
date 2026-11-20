"""
GET /api/v1/greeting: an HTML page (not JSON) that introduces the API.
The page content is kept in the lists below, so updating a name, an ID
or an endpoint means editing data, not HTML.
"""

from html import escape
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api/v1", tags=["Greeting"])

PROJECT = {
    "name": "beav",
    "tagline": "Volunteer registration made simple",
    "description": (
        "beav is a platform where organizations create volunteer registration "
        "forms, collect applications and see participation analytics, and where "
        "volunteers discover opportunities and join community groups. "
        "This prototype exposes the registration forms API with mocked data."
    ),
    "audience": "Organizations that run volunteer programs, and the volunteers who join them.",
    "version": "v1",
}

TEAM = [
    {
        "name": "Nuray Aghayeva",
        "student_id": "00000",
        "built": "Error handling and response envelope, app setup, forms CRUD routes and ownership rules",
    },
    {
        "name": "Leyla Aghayeva",
        "student_id": "00000",
        "built": "Mock data, token authentication, validation schemas, duplicate-title check, greeting page, Postman collection",
    },
]

ENDPOINTS = [
    ("GET",    "/api/v1/greeting",        "This page: project info, team and endpoints"),
    ("GET",    "/api/v1/forms",           "List forms (own forms, or all for admin); supports page, perPage, status"),
    ("GET",    "/api/v1/forms/{form_id}", "Get one form by its id"),
    ("POST",   "/api/v1/forms",           "Create a form owned by the caller"),
    ("PUT",    "/api/v1/forms/{form_id}", "Replace a form's details and questions"),
    ("DELETE", "/api/v1/forms/{form_id}", "Delete a form"),
]

TOKENS = [
    ("user-a-token", "User A, manages only their own forms"),
    ("user-b-token", "User B, manages only their own forms"),
    ("admin-token",  "Platform admin, manages all forms"),
]

STYLE = """
:root {
  --bg: #f6f7f4; --card: #ffffff; --text: #1d2320; --muted: #5d6762;
  --line: #e2e6e1; --accent: #2f7d5b; --accent-soft: #e6f2ec;
  --get: #2f6fb0; --post: #2f7d5b; --put: #b07a1f; --delete: #b0413e;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  line-height: 1.55;
}
.wrap { max-width: 920px; margin: 0 auto; padding: 40px 20px 56px; }
header { margin-bottom: 28px; }
.status {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--accent-soft); color: var(--accent);
  font-size: 0.85rem; font-weight: 600; padding: 4px 12px; border-radius: 999px;
}
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }
h1 { font-size: 2.4rem; margin: 14px 0 4px; letter-spacing: -0.02em; }
.tagline { font-size: 1.15rem; color: var(--muted); margin: 0; }
section {
  background: var(--card); border: 1px solid var(--line); border-radius: 14px;
  padding: 24px; margin-top: 20px;
}
h2 { font-size: 1.1rem; margin: 0 0 14px; }
p { margin: 0 0 10px; }
.muted { color: var(--muted); }
.team { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; }
.member { border: 1px solid var(--line); border-radius: 10px; padding: 16px; }
.member strong { display: block; font-size: 1.05rem; }
.member .id { font-size: 0.85rem; color: var(--muted); }
.member p { margin: 8px 0 0; font-size: 0.95rem; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 10px 8px; border-top: 1px solid var(--line); vertical-align: top; }
th { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); border-top: none; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.9rem; }
.method {
  display: inline-block; min-width: 64px; text-align: center; color: #fff;
  font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;
}
.GET { background: var(--get); } .POST { background: var(--post); }
.PUT { background: var(--put); } .DELETE { background: var(--delete); }
footer { margin-top: 28px; font-size: 0.85rem; color: var(--muted); text-align: center; }
a { color: var(--accent); }

/* Phones: stack each endpoint row instead of squeezing a table */
@media (max-width: 600px) {
  h1 { font-size: 1.9rem; }
  section { padding: 18px; }
  thead { display: none; }
  table, tbody, tr, td { display: block; width: 100%; }
  tr { border-top: 1px solid var(--line); padding: 10px 0; }
  td { border: none; padding: 3px 0; }
  code { word-break: break-all; }
}
"""

def _render_page() -> str:
    team_html = "".join(
        f"""<div class="member">
              <strong>{escape(m["name"])}</strong>
              <span class="id">Student ID: {escape(m["student_id"])}</span>
              <p>{escape(m["built"])}</p>
            </div>"""
        for m in TEAM
    )
    endpoint_rows = "".join(
        f"""<tr>
              <td><span class="method {method}">{method}</span></td>
              <td><code>{escape(path)}</code></td>
              <td>{escape(desc)}</td>
            </tr>"""
        for method, path, desc in ENDPOINTS
    )
    token_rows = "".join(
        f"<tr><td><code>Bearer {escape(t)}</code></td><td>{escape(who)}</td></tr>"
        for t, who in TOKENS
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{PROJECT["name"]} API</title>
  <style>{STYLE}</style>
</head>
<body>
  <div class="wrap">
    <header>
      <span class="status"><span class="dot"></span>API is running · {PROJECT["version"]}</span>
      <h1>Welcome to {PROJECT["name"]}</h1>
      <p class="tagline">{PROJECT["tagline"]}</p>
    </header>

    <section>
      <h2>About the project</h2>
      <p>{escape(PROJECT["description"])}</p>
      <p class="muted"><strong>Who it is for:</strong> {escape(PROJECT["audience"])}</p>
    </section>

    <section>
      <h2>Team</h2>
      <div class="team">{team_html}</div>
    </section>

    <section>
      <h2>Available endpoints</h2>
      <table>
        <thead><tr><th>Method</th><th>Path</th><th>Description</th></tr></thead>
        <tbody>{endpoint_rows}</tbody>
      </table>
    </section>

    <section>
      <h2>Try it</h2>
      <p class="muted">Send one of these in the <code>Authorization</code> header.
      Data is mocked in memory and resets when the server restarts.</p>
      <table><tbody>{token_rows}</tbody></table>
      <p class="muted" style="margin-top:12px">Interactive docs: <a href="/docs">/docs</a></p>
    </section>

    <footer>{PROJECT["name"]} API {PROJECT["version"]} · CSCI 3509 · Team 14</footer>
  </div>
</body>
</html>"""

@router.get("/greeting", response_class=HTMLResponse, summary="HTML greeting page")
def greeting():
    # HTMLResponse sends Content-Type: text/html; charset=utf-8
    return HTMLResponse(content=_render_page())