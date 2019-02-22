import requests
from time import sleep
from flask import Flask
from flask import render_template

import subprocess
from threading import Thread
from queue import Queue, Empty
import json

from flask import Markup


app = Flask(__name__)



class NonBlockingStreamReader:
    # from https://gist.github.com/EyalAr/7915597
    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''

        self._s = stream
        self._q = Queue()

        def _populateQueue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'quque'.
            '''

            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    raise UnexpectedEndOfStream

        self._t = Thread(target=_populateQueue,
                         args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()  # start collecting lines from the stream


    def readline(self, timeout=None):
        try:
            return self._q.get(block=timeout is not None,
                               timeout=timeout)
        except Empty:
            return None


class UnexpectedEndOfStream(Exception): pass



class Delft_Class(object):
    def __init__(self):
        """
        Initialize the subprocess that will receive the inputs from the user
        """
        self._tagger = subprocess.Popen('python3 greekClassifier.py classify', shell=True,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        sleep(10)

        self._nbsr = NonBlockingStreamReader(self._tagger.stdout)
        sleep(2)

    def get_result(self, text):


        results = list()

        self._tagger.stdin.write((text + '\n').encode('utf-8'))
        self._tagger.stdin.flush()
        output = self._nbsr.readline(0.1)
        result_tmp = json.load(output.strip())
        result = result_tmp['classifications'][0]['1']

        return result


Classifier = Delft_Class()

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
    probability = Classifier.get_result(data['text'])
    text = Markup(visualize_pubtator_data(data))
    return render_template('base.html', text=text, probability=probability)


@app.route('/')
def root():
    return '<html><body>Try here: <a href="triage/123">triage/123</a></body></html>'
