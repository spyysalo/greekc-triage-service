import requests

from flask import Flask
from flask import render_template
from flask import Markup


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


def textbound_annotation(index, ann):
    type_ = ann['obj'].split(':')[0]    # e.g. "Gene:4363" -> "Gene"
    begin, end = ann['span']['begin'], ann['span']['end']
    return 'T{}\t{}\t{}\t{}\tTODO'.format(index, type_, begin, end)


def visualize_pubtator_data(data):
    ann = []
    for i, a in enumerate(data['denotations']):
        ann.append(textbound_annotation(i, a))
    return """<div class="visualization">
<pre><code class="language-ann">{}
{}
</code></pre>
</div>""".format(data['text'], '\n'.join(ann))


@app.route('/triage/<pmid>')
def triage(pmid):
    data = get_pubtator_data(pmid)
    #text = data['text'] + str(data['denotations'])
    text = Markup(visualize_pubtator_data(data))
    return render_template('base.html', text=text)


@app.route('/')
def root():
    return '<html><body>Try here: <a href="triage/123">triage/123</a></body></html>'
