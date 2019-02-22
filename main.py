import requests

from flask import Flask


app = Flask(__name__)


@app.route('/triage/<pmid>')
def triage(pmid):
    r = requests.get('https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/Chemical/{}/JSON/'.format(pmid))
    return str(r.json())


@app.route('/')
def root():
    return '<html><body>Try here: <a href="triage/123">triage/123</a></body></html>'
