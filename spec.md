# Backend Internals Explorer (BEI)

### A Minimal Backend Application to Understand How a Web Backend Actually Works

---

# Objective

The purpose of **Backend Internals Explorer (BEI)** is **education**, not production.

Most backend tutorials hide what actually happens internally behind frameworks, middleware, ORMs, abstractions, authentication systems, dependency injection, and dozens of libraries.

This project does the opposite.

Every request should make it obvious:

1. What request arrived.
2. Which route handled it.
3. Which Python function executed.
4. What SQL query was generated.
5. What SQLite returned.
6. How the backend constructed the response.
7. What HTTP response was sent back.
8. How the browser received and displayed it.

The student should be able to watch both the browser and terminal and mentally trace every step.

---

# Design Philosophy

The application should intentionally remain extremely small.

No authentication.

No authorization.

No pagination.

No sessions.

No cookies.

No middleware.

No ORM.

No API versioning.

No caching.

No async programming.

No JavaScript frameworks.

No CSS frameworks.

No production optimizations.

No logging frameworks.

No configuration management.

No environment variables.

No Docker.

No cloud deployment.

Only enough code to explain how a backend communicates with a browser and a database.

---

# Learning Goals

After reading the code, a beginner should understand:

* HTTP Request
* HTTP Response
* Routes
* GET vs POST
* HTML Forms
* Multipart File Upload
* SQLite
* SQL INSERT
* SQL SELECT
* File Storage
* JSON Response
* Request Headers
* Response Headers
* Browser → Backend communication
* Backend → Database communication
* Backend → Filesystem communication

---

# Technology Stack

Backend

* Python
* Bottle (or Flask if Bottle becomes limiting)
* sqlite3 (Python standard library)
* pathlib
* json
* os

Frontend

* Plain HTML
* CSS
* Vanilla JavaScript

Database

* SQLite

Uploads

```
uploads/
    song1.mp3
    song2.mp3
```

Database

```
songs.db
```

---

# External Dependencies

Keep dependencies extremely small.

```
bottle
```

Everything else should come from Python's standard library.

---

# Project Structure

```
backend_internals/

    app.py

    database.py

    templates/

        index.html

        upload.html

    static/

        style.css
        script.js

    uploads/

    songs.db

    README.md
```

---

# Database

Single table.

```
songs

id
creator_name
song_description
file_name
created_at
```

---

# Routes

Only two HTML routes.

```
GET /
GET /upload
```

Plus the minimum API routes needed.

```
GET /api/songs

POST /api/upload

GET /songs/<filename>
```

No other APIs.

---

# Route 1

```
GET /
```

Purpose:

Show every uploaded song.

Display them as cards.

Each card shows

* creator
* description
* audio player

---

When page loads

Browser sends

```
GET /
```

Backend prints

```
======================================
Incoming Request

GET /

Matched Route:
/ -> home()

Loading songs...

Calling:

database.get_all_songs()

SQL:

SELECT
    id,
    creator_name,
    song_description,
    file_name
FROM songs
ORDER BY id DESC;
```

Database returns

```
3 rows
```

Backend prints

```
Packing rows into template.

Rendering index.html

Returning HTTP 200 OK
```

---

Browser page

Below the song grid, an expandable section called

```
Backend Trace
```

contains

Request

```
GET /
```

Response

```
HTTP 200
```

Returned Data

```
{
    songs : [
        ...
    ]
}
```

This is educational only.

---

# Song Playback

Each card contains

```
Play
```

Browser requests

```
GET /songs/music.mp3
```

Backend prints

```
Incoming Request

GET /songs/music.mp3

Requested File

uploads/music.mp3

Sending file...

Response

HTTP 200

Content-Type

audio/mpeg
```

Frontend also displays

```
GET /songs/music.mp3

↓

HTTP 200

↓

Audio Stream
```

---

# Upload Page

```
GET /upload
```

Contains

```
Creator Name

Song Description

Choose MP3

Upload
```

Nothing else.

---

# Upload Request

Browser sends

```
POST /api/upload
```

Multipart form.

Browser page displays

Expandable

```
Request
```

Showing

Headers

Body

Multipart parts

Uploaded filename

---

Backend terminal prints

```
======================================
Incoming Request

POST /api/upload

Matched Route

upload_song()
```

Then

```
Extracting Form Data...
```

Print

```
creator_name

song_description

uploaded filename
```

Then

```
Saving uploaded file...
```

Print

```
uploads/music.mp3

Success
```

Then

```
Preparing SQL
```

Show actual SQL

```
INSERT INTO songs
(
creator_name,
song_description,
file_name
)

VALUES

(
?,
?,
?
)
```

Print parameters

```
[
"Alice",

"Relaxing piano",

"music.mp3"
]
```

Execute SQL.

Print

```
Rows affected

1
```

Print

```
Last inserted ID

5
```

Then

```
Building JSON response
```

Show

```
{
    success:true,

    song_id:5,

    message:"Song uploaded."
}
```

Finally

```
Returning

HTTP 200
```

---

Frontend

Below upload form

Always show

```
Latest Request
```

Expandable.

Contains

Method

Headers

Body

Multipart fields

---

Then

```
Latest Response
```

Expandable.

Contains

Status

Headers

JSON

---

# API Response Format

Always consistent.

Example

```
{
    "success": true,

    "data": {

    },

    "message": "..."
}
```

No exceptions.

---

# Terminal Logging Style

Terminal output is educational.

Not logging.

Think of it as narration.

Example

```
=================================================

Received HTTP Request

↓

Matched Route

↓

Reading Form Data

↓

Saving Uploaded File

↓

Preparing SQL

↓

Executing SQL

↓

Database Returned

↓

Packing Response

↓

Returning HTTP Response
```

This narration is one of the core features.

---

# Frontend Trace Panel

Every page permanently contains a bottom panel.

```
Backend Trace
```

Sections

```
▼ HTTP Request

▼ HTTP Response

▼ Backend Explanation
```

Backend Explanation

Shows human-readable steps.

Example

```
1.
Browser requested /

2.
Python matched home()

3.
SQLite query executed

4.
Rows converted into dictionary

5.
Dictionary rendered into HTML

6.
HTTP response returned
```

---

# SQL Visibility

Students should always see the SQL.

Even if parameterized.

Example

```
SQL

SELECT *

FROM songs

WHERE id=?
```

Parameters

```
[3]
```

Result

```
1 row
```

---

# Simplicity Rules

Do not hide logic inside helpers.

A beginner should open `app.py` and understand the complete application.

Small functions are preferred.

Maximum function length:

~30 lines.

---

Avoid clever abstractions.

Prefer

```
read form

↓

save file

↓

insert row

↓

return response
```

instead of reusable generic layers.

---

# Error Handling

Minimal.

Show errors clearly.

Example

```
No file uploaded

↓

HTTP 400

↓

{
    success:false,
    message:"No MP3 file received."
}
```

Backend explains

```
Validation failed.

Returning HTTP 400.
```

---

# Educational Visualizations

Every page should include collapsible sections for:

* HTTP Request
* HTTP Response
* Backend Processing Steps
* SQL Query
* Database Result

Students should never need browser developer tools to understand what happened.

---

# Code Style

* One responsibility per function.
* Use descriptive variable names.
* Prefer explicit code over reusable abstractions.
* Add comments explaining *why* each step exists, not what Python syntax does.
* Keep files small enough to read in one sitting.

---

# Future Extensions (Out of Scope)

The following are intentionally **not implemented** in this project but can serve as follow-up exercises after students understand the fundamentals:

* Edit song metadata
* Delete songs
* Search
* Pagination
* Authentication
* User accounts
* REST API versioning
* File validation
* ORM (SQLAlchemy)
* Middleware
* JWT
* Sessions
* Cookies
* Deployment
* Docker
* Nginx
* Reverse proxy
* Cloud storage
* Caching
* Async I/O
* Background jobs

These omissions are deliberate. The goal is to expose the core mechanics of a backend with as little abstraction as possible, allowing students to see every step from the browser, through Python, into SQLite, and back again.

