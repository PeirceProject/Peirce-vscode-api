import flask
from flask import jsonify, request
import json
import os

app = flask.Flask(__name__)
app.config["DEBUG"] = True

PEIRCE_ROOT = "/home/charlie/Peirce"
API_ROOT = "/home/charlie/vscode-peirce-api"
temp_file_name = "temp.cpp"

@app.route('/', methods=["GET"])
def home():
    return "<h1>Welcome to the Peirce VSCode Extension API!</h1>"

@app.route('/api', methods=["GET"])
def api_home():
    return "<h1>Welcome to the Peirce VSCode Extension API!</h1>"

def create_file(text):
    if (os.path.exists(temp_file_name)):
        os.remove(temp_file_name)
    try:
        f = open(temp_file_name,"w+")
        f.write(text)
        f.close()
        return 0
    except Exception as e:
        print(e)
        return 1

def run_peirce():
    try:
        print("running...")

        ## I have been having an extremely difficult time with Bash trying to
        ## extract both coordinates and location in one run...
        ## but I've needed to resort to running Peirce twice! :(
        ## This can and should be fixed in the future.

        ## Running grab_peirce_coords.sh
        stream = os.popen('docker run -it --cap-add=SYS_PTRACE --rm --security-opt seccomp=unconfined --name peirce_docker -v llvm-build:/llvm/build -v '+ PEIRCE_ROOT + ':/peirce -v '+ API_ROOT+':/api andrewe8/peirce_docker:latest bash /api/bin/grab_peirce_coords.sh ' + temp_file_name)
        coordinates = stream.read().strip()
        print("Coordinates from Peirce:")
        print(coordinates)

        ## Running grab_peirce_interps.sh
        stream = os.popen('docker run -it --cap-add=SYS_PTRACE --rm --security-opt seccomp=unconfined --name peirce_docker -v llvm-build:/llvm/build -v '+ PEIRCE_ROOT + ':/peirce -v '+ API_ROOT+':/api andrewe8/peirce_docker:latest bash /api/bin/grab_peirce_interps.sh ' + temp_file_name)
        interps = stream.read().strip()
        print("Interpretations from Peirce:")
        print(interps)
        coord_array = coordinates.splitlines()
        interp_array = interps.splitlines()
        data = [None] * len(coord_array)
        for i in range(len(coord_array)):
            begin = coord_array[i].split("Begin: ")[1].split("\t")[0]
            begin_line = begin.split("line ")[1].split(",")[0]
            begin_col = begin.split("column ")[1]
            end = coord_array[i].split("End:")[1]
            end_line = begin.split("line ")[1].split(",")[0]
            end_col = begin.split("column ")[1]
            data[i] = {"coords": {"begin": {"line": begin_line, "character": begin_col}, "end": {"line": end_line, "character": end_col}}, "interp": interp_array[i].split("Existing Interpretation: ")[1]}
        print(json.dumps(data, indent=4, sort_keys=True))
        return data
    except Exception as e:
        print(e)

@app.route('/api/peirce', methods=["POST"])
def peirce():
    content = request.get_json()
    print(content)
    print(json.dumps(content, indent=4, sort_keys=True))
    print("File?")
    print(content["file"])
    print("Notes?")
    print(content["notes"])
    file_text = content["file"]
    data = {}
    if (create_file(file_text) == 0):
        data = run_peirce()
    notes = content["notes"]
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

app.run(host="0.0.0.0", port=8080)
