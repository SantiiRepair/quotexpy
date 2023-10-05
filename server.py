import os
import sys
from bottle import run, redirect, static_file, Bottle

app = Bottle()

docs_path = os.path.join(os.path.dirname(__file__), "build/docs/")
static_path = os.path.join(os.path.dirname(__file__), "build/static/")
languages = "en cn".split()


@app.get("/")
def index():
    redirect("/docs/dev/")


@app.get("/docs/<version>/")
@app.get("/docs/<version>/<filename:path>")
def docs(version, filename="index.html"):
    filename = f"{version}/{filename or 'index.html'}"
    return static_file(filename, root=docs_path)


@app.get("/commit/:hash#[a-zA-Z0-9]+#")
def commit(hash):
    url = "https://github.com/SantiiRepair/quotexpy/commit/%s"
    redirect(url % hash.lower())


@app.get("/<filename:path>")
def static(filename):
    return static_file(filename, root=static_path)


# Start server
if __name__ == "__main__":
    run(app, port=int(sys.argv[1]), debug="debug" in sys.argv)
