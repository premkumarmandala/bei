# Backend Internals Explorer (BEI)

A tiny song-upload app whose only purpose is to show what a backend actually does.
Watch the terminal and the browser at the same time: every click prints the request
that arrived, the function that ran, the SQL that was executed, what SQLite returned,
and how the response was packed.

## Run it

```
python3 app.py
```

Then open <http://localhost:8080/>.

`songs.db` and `uploads/` are created on the first run.

## Routes

| Route                  | What it does                                        |
| ---------------------- | --------------------------------------------------- |
| `GET /`                | Song grid, rendered from a `SELECT`                 |
| `GET /upload`          | The upload form                                     |
| `GET /api/songs`       | The same songs as JSON                              |
| `POST /api/upload`     | Multipart form, saves the file, runs an `INSERT`    |
| `GET /songs/<file>`    | Streams an mp3 from `uploads/`                      |

Every API response uses the same shape:

```json
{ "success": true, "data": {}, "message": "..." }
```

## Try it from the command line

```
curl http://localhost:8080/api/songs

curl -X POST http://localhost:8080/api/upload \
     -F "creator_name=Alice" \
     -F "song_description=Relaxing piano" \
     -F "song_file=@music.mp3"
```

## Files

```
app.py            every route, and the terminal narration
database.py       sqlite3 access, prints the SQL and the results
templates/        index.html, upload.html
static/           style.css, script.js
uploads/          the mp3 files
songs.db          the database
```

