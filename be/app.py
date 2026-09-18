"""Backend Internals Explorer (BEI).

The whole application is in this one file so a beginner can read it top to
bottom. Each route does the same four things, in the same order, with nothing
hidden in between:

    read the request  ->  talk to the database or filesystem  ->  pack a response  ->  return it

Every handler narrates itself to the terminal while it works. Watch the terminal
and the browser side by side and you can trace one click all the way into SQLite
and back.

Run it with:

    python3 app.py
"""

import os
import sys
import json
from pathlib import Path

# Add the 'be' directory to the Python path so Vercel can find 'database.py'
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

import bottle
from bottle import get, post, request, response, run, static_file, template

try:
    import database
except ImportError:
    from be import database

if os.environ.get("VERCEL"):
    UPLOADS_DIR = Path("/tmp/uploads")
else:
    UPLOADS_DIR = BASE_DIR / "uploads"
    
STATIC_DIR = BASE_DIR / "static"

# Tell Bottle where the HTML templates live.
bottle.TEMPLATE_PATH.insert(0, str(BASE_DIR / "templates"))


# ---------------------------------------------------------------------------
# Terminal narration
#
# These two tiny functions only exist so the terminal output has a consistent
# shape. They contain no application logic.
# ---------------------------------------------------------------------------


def narrate_request(method, path, handler_name):
    """Print the banner that starts every request's story."""
    print()
    print("=" * 55)
    print("Incoming Request")
    print()
    print(method, path)
    print()
    print("Matched Route:")
    print(path, "->", handler_name)
    print()


def narrate(message):
    """Print one step of the story."""
    print(message)
    print()


# ---------------------------------------------------------------------------
# Route 1:  GET /
#
# The home page. Reads every song out of SQLite and renders the grid of cards.
# ---------------------------------------------------------------------------


@get("/")
def home():
    narrate_request("GET", "/", "home()")
    narrate("Loading songs...")

    songs = database.get_all_songs()

    narrate("Packing rows into template.")

    # The page shows a Backend Trace panel at the bottom. The server builds that
    # trace here and hands it to the template, so the panel describes the very
    # request that produced the page.
    trace = {
        "request": {
            "method": "GET",
            "url": "/",
            "headers": dict(request.headers),
            "body": "(a GET request has no body)",
        },
        "response": {
            "status": "HTTP 200 OK",
            "headers": {"Content-Type": "text/html; charset=UTF-8"},
        },
        "data": {"songs": songs},
        "explanation": [
            "Browser requested /",
            "Python matched home()",
            "SQLite query executed: SELECT ... FROM songs ORDER BY id DESC",
            "Returned " + str(len(songs)) + " rows, converted into dictionaries",
            "Dictionaries rendered into index.html",
            "HTTP 200 response returned",
        ],
    }

    narrate("Rendering index.html")
    narrate("Returning HTTP 200 OK")

    return template("index", songs=songs, trace_json=json.dumps(trace, indent=4))


# ---------------------------------------------------------------------------
# Route 2:  GET /upload
#
# The upload page. It only needs to send back an HTML form, so it touches
# neither the database nor the filesystem.
# ---------------------------------------------------------------------------


@get("/upload")
def upload_page():
    narrate_request("GET", "/upload", "upload_page()")
    narrate("No database work needed. This route only returns a form.")

    trace = {
        "request": {
            "method": "GET",
            "url": "/upload",
            "headers": dict(request.headers),
            "body": "(a GET request has no body)",
        },
        "response": {
            "status": "HTTP 200 OK",
            "headers": {"Content-Type": "text/html; charset=UTF-8"},
        },
        "data": {},
        "explanation": [
            "Browser requested /upload",
            "Python matched upload_page()",
            "No SQL was executed, this page only shows a form",
            "upload.html rendered",
            "HTTP 200 response returned",
            "Submitting the form will POST to /api/upload",
        ],
    }

    narrate("Rendering upload.html")
    narrate("Returning HTTP 200 OK")

    return template("upload", trace_json=json.dumps(trace, indent=4))


# ---------------------------------------------------------------------------
# Route 3:  GET /api/songs
#
# The same rows as the home page, but as JSON. Useful from the command line:
#
#     curl http://localhost:8080/api/songs
# ---------------------------------------------------------------------------


@get("/api/songs")
def api_songs():
    narrate_request("GET", "/api/songs", "api_songs()")
    narrate("Loading songs...")

    songs = database.get_all_songs()

    narrate("Building JSON response")

    body = {
        "success": True,
        "data": {"songs": songs},
        "message": "Found " + str(len(songs)) + " songs.",
    }

    print(json.dumps(body, indent=4))
    print()
    narrate("Returning HTTP 200 OK")

    response.content_type = "application/json"
    return json.dumps(body)


# ---------------------------------------------------------------------------
# Route 4:  POST /api/upload
#
# The interesting one. A multipart form arrives carrying two text fields and one
# mp3 file. The file goes to the uploads folder, the three text values go into
# SQLite, and a JSON response goes back to the browser.
# ---------------------------------------------------------------------------


@post("/api/upload")
def upload_song():
    narrate_request("POST", "/api/upload", "upload_song()")

    narrate("Extracting Form Data...")

    # Text fields arrive in request.forms, the file arrives in request.files.
    # The browser packed all three into one multipart body.
    creator_name = request.forms.get("creator_name", "").strip()
    song_description = request.forms.get("song_description", "").strip()
    uploaded_file = request.files.get("song_file")

    print("creator_name       :", creator_name)
    print("song_description   :", song_description)
    print("uploaded filename  :", uploaded_file.filename if uploaded_file else None)
    print()

    # Minimal validation. Anything missing means we stop here and say why.
    if not creator_name or not song_description or uploaded_file is None:
        narrate("Validation failed.")
        narrate("Returning HTTP 400.")
        response.status = 400
        response.content_type = "application/json"
        return json.dumps(
            {
                "success": False,
                "data": {},
                "message": "Creator name, description and an MP3 file are all required.",
            }
        )

    narrate("Saving uploaded file...")

    # The file lives on disk, only its name lives in the database. Databases are
    # for small values; filesystems are for big blobs of bytes.
    UPLOADS_DIR.mkdir(exist_ok=True)
    file_name = Path(uploaded_file.filename).name
    destination = UPLOADS_DIR / file_name
    uploaded_file.save(str(destination), overwrite=True)

    print("uploads/" + file_name)
    print()
    narrate("Success")

    narrate("Preparing SQL")

    song_id = database.insert_song(creator_name, song_description, file_name)

    narrate("Building JSON response")

    body = {
        "success": True,
        "data": {"song_id": song_id, "file_name": file_name},
        "message": "Song uploaded.",
    }

    print(json.dumps(body, indent=4))
    print()
    narrate("Returning HTTP 200 OK")

    response.content_type = "application/json"
    return json.dumps(body)


# ---------------------------------------------------------------------------
# Route 5:  GET /songs/<filename>
#
# The audio player asks for this URL. No database is involved: the backend reads
# bytes off the disk and streams them back with an audio content type.
# ---------------------------------------------------------------------------


@get("/songs/<filename>")
def serve_song(filename):
    narrate_request("GET", "/songs/" + filename, "serve_song()")

    print("Requested File")
    print()
    print("uploads/" + filename)
    print()

    song_path = UPLOADS_DIR / filename

    if not song_path.exists():
        narrate("That file is not in the uploads folder.")
        narrate("Returning HTTP 404.")
        response.status = 404
        response.content_type = "application/json"
        return json.dumps(
            {"success": False, "data": {}, "message": "No such song file."}
        )

    narrate("Sending file...")

    # Read the whole file into memory and hand the bytes back. These are small
    # local files, so this stays simple: one read, one response, no streaming.
    song_bytes = song_path.read_bytes()

    narrate("Response")
    narrate("HTTP 200")
    narrate("Content-Type")
    narrate("audio/mpeg")

    response.content_type = "audio/mpeg"
    return song_bytes


# ---------------------------------------------------------------------------
# The stylesheet and the script.
#
# This route is not part of the application's API. It exists only because the
# browser must be able to download style.css and script.js.
# ---------------------------------------------------------------------------


@get("/static/<filename>")
def serve_static(filename):
    return static_file(filename, root=str(STATIC_DIR))


# ---------------------------------------------------------------------------
# Starting the server.
# ---------------------------------------------------------------------------

# Expose the WSGI app for Vercel
app = bottle.default_app()

# Initialize directories and database for Vercel
UPLOADS_DIR.mkdir(exist_ok=True)
database.create_table()

if __name__ == "__main__":
    print()
    print("Backend Internals Explorer starting up")
    print()

    print("Open http://localhost:8080/ in your browser")
    print("Watch this terminal while you click.")

    run(host="localhost", port=8080, debug=True)
