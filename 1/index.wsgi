import os

from bottle import Bottle, run, static_file
# sae no include python markdown library, we need
# put the marddown in root dir
import markdown

import sae
from sae.storage import Bucket

app = Bottle()
app_root = os.path.dirname(__file__)

# the bottle on sae is 0.9.6
# the style of route is :argvs, not <argvs>
@app.route('/css/:filename')
def server_static(filename):
    return static_file(filename,
                    root=os.path.join(app_root, "css"),
                    mimetype='text/css')

@app.route('/')
def hello():
    head_html = """
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="utf-8">
        <link type="text/css"
        rel="stylesheet"
        href="/css/mdstyle.css" />
    </head>
    <body>
    """
    tail_html = """
    </body>
    </html>
    """
    bkt = Bucket("blog")
    articles = []
    ## list all article in blog bucket in storage
    for i in bkt.list():
        if i.name.endswith(".md"):
            article = bkt.get_object_contents(i.name)
            article = markdown.markdown(article.decode("UTF-8"))
            articles.append(article)
    if len(articles) == 0:
        articles = ["No Article"]
    body_html = "<hr/>".join(articles)
    html = head_html + body_html + tail_html
    return html

application = sae.create_wsgi_app(app)
