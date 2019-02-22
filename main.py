import requests

from flask import Flask


app = Flask(__name__)


def pubtator_url(pmid, concept='BioConcept', format_='JSON'):
    u = 'https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/'\
        '{}/{}/{}/'.format(concept, pmid, format_)
    return u


def get_pubtator_data(pmid):
    url = pubtator_url(pmid)
    try:
        r = requests.get(url)
    except:
        raise    # TODO
    try:
        data = r.json()
    except:
        raise    # TODO
    if isinstance(data, list):
        data = data[0]
    return data


@app.route('/triage/<pmid>')
def triage(pmid):
    data = get_pubtator_data(pmid)
    return data['text']


@app.route('/')
def root():
    return '<html><body>Try here: <a href="triage/123">triage/123</a></body></html>'
