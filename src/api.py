import flask
from flask import jsonify, request
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=["GET"])
def home():
    return "<h1>Welcome to the Peirce VSCode Extension API!</h1>"

@app.route('/api', methods=["GET"])
def api_home():
    return "<h1>Welcome to the Peirce VSCode Extension API!</h1>"

@app.route('/api/peirce', methods=["POST"])
def peirce():
    content = request.get_json()
    content[0]["received?"] = "yes"
    print(content)
    print(json.dumps(content, indent=4, sort_keys=True))
    response = app.response_class(
        response=json.dumps(content),
        status=200,
        mimetype='application/json'
    )
    return response

app.run(host="0.0.0.0", port=8080)
