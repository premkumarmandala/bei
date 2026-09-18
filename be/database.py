"""All SQLite access for BEI.

Nothing here is clever on purpose. Every function opens a connection, prints the
exact SQL it is about to run, prints the parameters that will be substituted for
the "?" placeholders, runs it, prints what SQLite handed back, and closes the
connection.

The printing is the point: a student reading the terminal should be able to see
the SQL statement that their click produced.
"""

import sqlite3
from pathlib import Path

# The database file sits next to this Python file, so the app can be started
# from any directory and still find it.
DB_FILE = Path(__file__).parent / "songs.db"


def connect():
    """Open a connection to songs.db.

    row_factory is set so that rows behave like dictionaries (row["creator_name"])
    instead of tuples (row[1]). That keeps the packing code below readable.
    """
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    """Create the single table this application uses, if it is not there yet.

    Called once when the server starts, so a fresh clone works immediately.
    """
    sql = """
CREATE TABLE IF NOT EXISTS songs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_name     TEXT NOT NULL,
    song_description TEXT NOT NULL,
    file_name        TEXT NOT NULL,
    created_at       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""
    print("Calling:")
    print()
    print("database.create_table()")
    print()
    print("SQL:")
    print(sql)

    connection = connect()
    connection.execute(sql)
    connection.commit()
    connection.close()

    print("Database file ready:", DB_FILE)
    print()


def get_all_songs():
    """Read every song row, newest first, and return a list of plain dictionaries."""
    sql = """
SELECT
    id,
    creator_name,
    song_description,
    file_name
FROM songs
ORDER BY id DESC
"""
    print("Calling:")
    print()
    print("database.get_all_songs()")
    print()
    print("SQL:")
    print(sql)
    print("Parameters:")
    print()
    print("[]")
    print()

    connection = connect()
    rows = connection.execute(sql).fetchall()
    connection.close()

    print("Database returned")
    print()
    print(len(rows), "rows")
    print()

    # sqlite3.Row objects cannot be turned into JSON, so copy each one into a
    # dictionary. This is the "packing" step the trace panel talks about.
    songs = []
    for row in rows:
        songs.append(
            {
                "id": row["id"],
                "creator_name": row["creator_name"],
                "song_description": row["song_description"],
                "file_name": row["file_name"],
            }
        )
    return songs


def insert_song(creator_name, song_description, file_name):
    """Insert one song row and return the id SQLite generated for it."""
    sql = """
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
"""
    parameters = [creator_name, song_description, file_name]

    print("Calling:")
    print()
    print("database.insert_song()")
    print()
    print("SQL:")
    print(sql)
    print("Parameters:")
    print()
    print(parameters)
    print()

    connection = connect()
    cursor = connection.execute(sql, parameters)
    # Without commit() the row would disappear when the connection closes,
    # because sqlite3 opens a transaction for us automatically.
    connection.commit()

    rows_affected = cursor.rowcount
    new_id = cursor.lastrowid
    connection.close()

    print("Rows affected")
    print()
    print(rows_affected)
    print()
    print("Last inserted ID")
    print()
    print(new_id)
    print()

    return new_id
