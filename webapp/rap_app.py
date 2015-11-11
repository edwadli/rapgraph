
from flask import Flask, send_file, send_from_directory, request, jsonify
app = Flask(__name__)



# splash page
@app.route('/')
def index():
    return send_file('static/index.html')
@app.route('/<path:path>')
def send_scripts(path):
    return send_from_directory('static', path)

# lyric analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    lyrics = request.form.get('lyrics', None)
    resp = { 'words': [], 'rhymes': [], 'inlines': []}
    if not lyrics:
        return jsonify(**resp)
    # TODO: do analysis
    resp['success'] = lyrics
    return jsonify(**resp)

if __name__ == "__main__":
    app.run()


