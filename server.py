import os
import bottle

app = application = bottle.Bottle()

docs_path = os.path.join(os.path.dirname(__file__), "docs/")
static_path = os.path.join(os.path.dirname(__file__), "static/")
languages = "en cn".split()


@app.get("/")
def index():
    bottle.redirect("/docs/dev/")


@app.get("/docs/<version>/")
@app.get("/docs/<version>/<filename:path>")
def docs(version, filename="index.html"):
    filename = version + "/" + (filename or "index.html")
    return bottle.static_file(filename, root=docs_path)


@app.get("/commit/:hash#[a-zA-Z0-9]+#")
def commit(hash):
    url = "https://github.com/SantiiRepair/quotexpy/commit/%s"
    bottle.redirect(url % hash.lower())


@app.get("/<filename:path>")
def static(filename):
    return bottle.static_file(filename, root=static_path)


# Start server
if __name__ == "__main__":
    import sys

    bottle.run(app, port=int(sys.argv[1]), debug="debug" in sys.argv)
