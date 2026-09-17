**Status:** Draft · **Domain:** `tiferet-flask` · **Code:** `tiferet_flask/` · **Branch:** `v1.x-proto`

# tiferet-flask: Domain Vision Statement

## The bet: a declared API should run on Flask without a second copy of the plumbing

A Flask API usually grows its own routing table, its own error-to-status map, and its own documentation page — three places that can disagree with each other the moment a route changes. tiferet-flask's bet is that "run this declared API on Flask" is one thin adapter: map declared routers onto Flask's own `Blueprint` primitive, inherit request and error handling from the session context this adapter extends, and serve one browsable documentation page from the same declaration that already drives the running routes. Nothing here re-decides what a route looks like, how an error maps to a status code, or how a specification is generated.

## What this domain makes real

tiferet-flask assembles a runnable `Flask` application from declared routers and routes. It turns each router into a Flask `Blueprint`, wires a single view function to every route on it, applies CORS from the session's own constants, and — when asked — serves a Swagger UI page backed by the generated specification. A developer who has already declared the API gets a working Flask server and a working documentation page from that declaration alone.

## What we get for it

**A Flask app is an assembly step, not a rewrite.** Building the app means walking declared routers and calling one Flask API (`add_url_rule`) per route. There is no parallel routing table, no Flask-specific request-shape validation, and no Flask-specific error-to-status mapping to keep in sync by hand.

**Request handling, error handling, and status-code resolution are inherited, not reimplemented.** This domain's context does not decide how an error becomes a status code or how a response is paired with one. That logic lives in the session context this adapter extends, so a change there is a change for every framework adapter at once. Flask's job is to catch the raised API error and return it as structured JSON with that status.

**A documentation page is available for the price of one flag.** Passing `swagger=True` is enough to get a browsable page and a machine-readable `openapi.json`, both taken from the declaration already driving the running routes — not a second document someone writes and forgets to update. The page is generated and registered once per app build.

**Framework-specific concerns stay framework-specific.** CORS, Flask's `Blueprint`/`Flask` app object, and how a view function reads `flask.request` are the only things this domain owns. Everything about what a route means is decided elsewhere and consumed here.

## The core of the work

Every Flask API surfaced through tiferet-flask goes through the same journey:

> **Resolve** the declared session → **assemble** a Flask application by mapping each router to a Blueprint and each route to a URL rule → **serve** requests through the session context that already knows how to parse, execute, and format them → **publish** a documentation page, generated once from the same declaration, and served without being regenerated or re-registered on every request or app build.

The design commitment underneath all four steps: tiferet-flask never re-derives a fact the declaration and session context already hold. If a route's shape, a status code, or a specification field is wrong, the fix belongs upstream. This domain's job is turning what has already been decided into a running Flask server.

## What it deliberately does not do

tiferet-flask does not declare, validate, or generate a route's shape — no domain objects, events, mappers, or repositories live in this package. That work belongs to the shared API-declaration layer this adapter depends on.

It does not decide how an error maps to a status code, or how a response is built from a completed request — that is the inherited session context's job.

It does not choose a documentation format or generate a specification. It renders the already-generated specification as a Flask-servable page.

It does not run business logic. A route's `view_func` dispatches to whatever feature the declared endpoint names; what that feature does is out of scope here.

---

*Companion document:* `docs/core-domain-distillation.md` — the detailed walkthrough of the domain's vocabulary, behaviors, and the relationships between its parts.
