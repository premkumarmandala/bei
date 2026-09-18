# Run it

In your Ubuntu terminal in WSL:

```
sudo apt install -y git python3-bottle
git clone git@github.com:rohinibarla/bei.git
cd bei/be
python3 app.py
```

On Windows, open <http://localhost:8080/> in your browser.

> Keep the Ubuntu terminal visible while you click.  

Stop the server with `Ctrl-C`.

# What you will see

Two pages: a grid of songs, and a form to upload one.

At the bottom of both, a **Backend Trace** box shows the request the browser
sent, the response it got back, and the steps in between.

Keep the Ubuntu terminal visible while you click. It tells the same story from
the inside: the request that arrived, the Python function that ran, the SQL it
wrote, what SQLite answered, and what went back to the browser.

Upload a song and watch both sides describe the same click.
