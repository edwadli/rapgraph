
from flask import Flask, send_file, send_from_directory, request, jsonify, Response, json
import time

# Server Sent Event: http://mzl.la/UPFyxY
# taken from http://flask.pocoo.org/snippets/116/
class ServerSentEvent(object):
    def __init__(self, data, event=None):
        self.data = data
        self.event = event
        self.desc_map = { self.data : "data", self.event : "event" }
    def encode(self):
        # assuming self.data has no new lines
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k) for k, v in self.desc_map.iteritems() if k]
        return "%s\n\n" % "\n".join(lines)


# server app
app = Flask(__name__)

# splash page
@app.route('/')
def index():
    return send_file('static/index.html')
@app.route('/<path:path>')
def send_scripts(path):
    return send_from_directory('static', path)

def analysis_gen(lyrics):
    # TODO load rapper.py
    for c in lyrics:
        yield c
        time.sleep(0.5)


# lyric analysis, yield partial results
@app.route('/analyze', methods=['GET'])
def analyze():
    lyrics = request.args.get('lyrics', None)
    def online_results():
        if lyrics:
        # run analysis on lyrics
            for partial_result in analysis_gen(lyrics):
                ev = ServerSentEvent(json.dumps(partial_result), "partial")
                yield ev.encode()
        ev = ServerSentEvent(" ", "__EOF__")
        yield ev.encode()
    return Response(online_results(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(threaded=True, debug=True)

