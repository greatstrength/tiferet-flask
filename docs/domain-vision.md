**Status:** Draft · **Domain:** `tiferet-flask` · **Code:** `tiferet_flask/` · **Branch:** `v1.x-proto`

# tiferet-flask: Domain Vision Statement

## The bet: a declared API should run on Flask without anyone writing Flask-specific plumbing twice

tiferet-openapi lets a team declare an API's routes, shapes, and error mapping once and derive the running service, the specification, and the documentation from that single declaration. That bet only pays off if turning the declaration into an actual, running web server is itself a thin, repeatable step — not a place where a Flask-specific reimplementation of routing, error handling, or documentation serving quietly grows back.

tiferet-flask's bet is that "run this declared API on Flask" should cost exactly one small adapter: map `ApiRouter`/`ApiRoute` onto Flask's own `Blueprint` primitive, hand request/response/error handling to the framework-agnostic session context that already implements it correctly, and expose the same generated specification through a concrete, browsable documentation page. Nothing here should re-decide what a route's shape is, how an error maps to a status code, or how a specification is generated — those facts were already settled once, upstream.

## What this domain makes real

tiferet-flask is the Flask-specific adapter that assembles a real, runnable `Flask` application from the same `ApiRouter`/`ApiRoute` declarations and the same session context tiferet-openapi already defines. It turns each declared router into a Flask `Blueprint`, wires a single view function to every route on it, enables CORS, and — when asked — serves a CDN-hosted Swagger UI page backed by the same generated OpenAPI document tiferet-openapi produces. A developer who has already declared an API through tiferet-openapi gets a working Flask server and a working documentation page from that declaration alone.

## What we get for it

**A Flask app is an assembly step, not a rewrite.** Building the app means walking declared routers and calling one Flask API (`add_url_rule`) per route — there is no parallel routing table, no Flask-specific request-shape validation, and no Flask-specific error-to-status mapping to maintain independently of tiferet-openapi's.

**Request handling, error handling, and status-code resolution are inherited, not reimplemented.** tiferet-flask's context does not decide how an error becomes a status code or how a response is paired with one — that logic lives once in the shared session context this domain extends, so a fix or a behavior change made there is a fix made for every framework adapter at once.

**A documentation page is available for the price of one flag.** Passing `swagger=True` is enough to get a browsable page and a machine-readable `openapi.json`, both generated from the declaration already driving the running routes — not a second document a developer writes and forgets to update.

**Framework-specific concerns stay framework-specific.** CORS, Flask's `Blueprint`/`Flask` app object, and how a view function reads `flask.request` are the only things this domain owns. Everything about what a route means is decided elsewhere and simply consumed here.

## The core of the work

Every Flask API surfaced through tiferet-flask goes through the same journey:

> **Resolve** the declared session (routers, routes, event collaborators) → **assemble** a Flask application by mapping each router to a Blueprint and each route to a URL rule → **serve** requests through a session context that already knows how to parse, execute, and format them → **publish** a documentation page, generated once from the same declaration, and served without being regenerated or re-registered on every request or app build.

The design commitment underneath all four steps: tiferet-flask never re-derives a fact tiferet-openapi already derived. If a route's shape, a status code, or a specification field is wrong, the fix belongs upstream — this domain's only job is faithfully turning what's already been decided into a running Flask server.

## What it deliberately does not do

tiferet-flask does not declare, validate, or generate anything about a route's shape — no domain objects, events, mappers, or repositories live in this package; all of that is tiferet-openapi's job, consumed here as a dependency.

It does not decide how an error maps to a status code, or how a response is built from a completed request — that is the shared session context's job, inherited rather than reimplemented.

It does not choose a documentation *format* — it does not reinvent OpenAPI generation. It renders the specification tiferet-openapi already generated, through a Flask-servable page.

It does not run business logic. A route's `view_func` dispatches to whatever feature the declared endpoint names; what that feature does is out of scope here, exactly as it is out of scope for tiferet-openapi.

---

*Companion document:* `docs/core-domain-distillation.md` — the detailed walkthrough of the domain's vocabulary, behaviors, and current gap against the session-context shape it is expected to extend.
