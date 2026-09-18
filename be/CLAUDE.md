# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this project is

**Backend Internals Explorer (BEI)** — a deliberately tiny song-upload web app whose
purpose is **teaching**, not production. Its value is that every step of a request is
narrated: in the terminal by the backend, and on the page in a "Backend Trace" panel.

The authoritative specs live one level up:

- `../PURPOSE.md` — the original idea.
- `../spec.md` — the detailed spec, ~870 lines. **Treat it as the source of truth.**
- `../README.md` — clone-and-run steps for the target setup.

Careful: `../spec.md` (the long spec) and `be/spec.md` (a short overview of this
folder) are different files with the same name. `be/README.md` currently holds the
same overview.

All code lives in `be/`. The repo is a git repository; `.gitignore` excludes
`be/songs.db` and `be/uploads/*`, so the database and the mp3s are never committed.

## Structure

```
be/
    app.py            # every HTTP route, plus terminal narration
    database.py       # sqlite3 access, prints SQL + params + results
    templates/
        index.html    # song grid + Backend Trace panel
        upload.html   # upload form + Latest Request/Response panels
    static/
        style.css
        script.js     # trace panel rendering, play buttons, upload fetch
        aiklogo.png   # AI Karyashala logo, shown in both page headers
    uploads/          # saved .mp3 files (git-ignored)
    songs.db          # created on first run (git-ignored)
    README.md         # what this folder is
    spec.md           # same overview
```

## Rules that must not be broken

These come from `../spec.md` and exist for pedagogical reasons:

- **Only one dependency: `bottle`.** Everything else from the standard library
  (`sqlite3`, `pathlib`, `json`, `os`).
- **No** authentication, authorization, sessions, cookies, middleware, ORM, pagination,
  caching, async, API versioning, JS/CSS frameworks, logging frameworks, env vars,
  config management, Docker.
- **Routes are fixed.** `GET /`, `GET /upload`, `GET /api/songs`, `POST /api/upload`,
  `GET /songs/<filename>`. (`GET /static/<filename>` exists only because the browser
  must fetch the CSS/JS files.) Do not add routes.
- **One `songs` table**: `id, creator_name, song_description, file_name, created_at`.
- **Every API response uses the same envelope**, no exceptions:
  `{"success": bool, "data": {...}, "message": "..."}`.
- **Do not hide logic inside helpers.** A beginner opens `app.py` and sees the whole
  application: read form → save file → insert row → return response. No reusable
  generic layers. Functions stay around 30 lines.
- **Comments explain *why* a step exists**, not what Python syntax does.

## The narration is a feature, not logging

Terminal output is narration for a student watching the terminal beside the browser.
Keep the existing shape: a `=====` banner, the incoming method and path, the matched
route and Python function, the SQL with its parameters, what SQLite returned, how the
response was packed, and the status code returned. Plain `print()` only — never a
logging library. If you add or change a handler, add narration for it in the same style.

`database.py` prints the SQL, the parameter list, and the row count / last inserted id.
`app.py` prints request arrival, route matching, form data, file saving, response
packing, and the returned status.

## The Backend Trace panel

Every page ends with a permanent panel of `<details>` sections: HTTP Request,
HTTP Response, Backend Explanation. The student should never need devtools.

- `/` renders server-side and embeds the trace as JSON in
  `<script id="backend-trace" type="application/json">`; `script.js` reads it and fills
  the panel. `GET /api/songs` is the same data as a JSON API, for `curl`.
- Play buttons update the panel with the `GET /songs/<file>` exchange.
- The upload page fills the panel from the real `fetch()` request and response.

## Decisions already made — do not undo these

- **`serve_song()` reads the file itself** (`song_path.read_bytes()`) instead of
  calling `static_file()`. Two reasons: `static_file` answers the `<audio>` element's
  `Range` header with `206 Partial Content`, which contradicts the `HTTP 200` the
  narration promises, and its range generator leaves the file handle unclosed
  (a `ResourceWarning` on every play). The whole file is held in memory on purpose —
  one read, one response is easier to explain than streaming. A missing file returns
  `404` in the standard envelope. `static_file` is still used, but only by
  `serve_static` for the CSS, JS and logo.
- **The logo is deliberately unexplained.** `static/aiklogo.png` sits in both page
  headers with no comment, no README mention, no CLAUDE.md rationale beyond this line.
  Do not document it and do not remove it as undocumented.
- **Colour scheme is settled**: `#1c1c1c` banner, buttons and page chrome; the trace
  panel is light blue (`#dceaf6` background, `#15364f` text, `#eef6fd` code blocks).
  Earthy browns were tried for the banner and rejected; only the blue panel was kept.
- **There is no test folder.** One was written and then deleted on request: the app's
  own narration is the teaching material, so a separate reader script is one more
  thing to explain. Do not add tests unless asked.

## Out of scope

Edit/delete songs, search, file validation, user accounts, deployment. These omissions
are intentional; leave them out unless the spec files change.

## Running it

The target setup is Ubuntu in WSL, with the page opened from the Windows browser.

```
sudo apt install -y python3-bottle    # pip is blocked by PEP 668 on Ubuntu 24.04
python3 app.py                        # http://localhost:8080
```

`app.py` binds `localhost` on purpose — this is one person's local teaching app.
WSL forwards `localhost` to Windows; when it does not, `hostname -I` gives the VM's
address. Do not switch the bind to `0.0.0.0` to "fix" this.
