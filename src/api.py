import flask
from flask import jsonify, request
import json
import os

app = flask.Flask(__name__)
app.config["DEBUG"] = True

PEIRCE_ROOT = "/home/charlie/Peirce"
API_ROOT = "/home/charlie/vscode-peirce-api"
temp_file_name = "temp.cpp"
temp_input_file_name = "inputs.txt"

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
            begin_line = int(begin.split("line ")[1].split(",")[0])-1
            begin_col = int(begin.split("column ")[1])-1
            end = coord_array[i].split("End:")[1]
            end_line = int(end.split("line ")[1].split(",")[0])-1
            end_col = int(end.split("column ")[1])
            data[i] = {"coords": {"begin": {"line": begin_line, "character": begin_col}, "end": {"line": end_line, "character": end_col}}, "interp": interp_array[i].split("Existing Interpretation: ")[1]}
        print(json.dumps(data, indent=4, sort_keys=True))
        return data
    except Exception as e:
        print(e)

@app.route('/api/populate', methods=["POST"])
def populate():
    content = request.get_json()
    print(content)
    print(json.dumps(content, indent=4, sort_keys=True))
    print("File?")
    print(content["file"])
    print("Notes?")
    print(content["notes"])
    file_text = content["file"]
    data = {}
    if (create_file(file_text) != 0):
        response = app.response_class(
            status=500,
        )
        return response
    data = run_peirce()
    notes = content["notes"]
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

def generate_input(notes, spaces):
    order_of_spaces = {}
    dict_count = 1
    input=""
    for space in spaces:
        input+="2\n"
        input+="1\n"
        if (space["parent"] == None):
            input+="1\n"
            input+=space["label"]+"\n"
            print(space)
            order_of_spaces[hash(tuple(sorted(space)))] = dict_count
            dict_count+=1
        else:
            input+="2\n"
            input+=space["label"]+"\n"
            input+=(str(order_of_spaces[hash(tuple(sorted(space["parent"])))])+"\n")
            input+=str(space["origin"])+"\n"
            input+=str(space["basis"])+"\n"
            print(space)
            order_of_spaces[hash(tuple(sorted(space)))] = dict_count
            dict_count+=1
    for i in range(len(notes)):
        note = notes[i]
        interp = note["interpretation"]
        print(interp)
        if (interp == None):
            continue;
        name = interp["name"]
        form = interp["form"]
        space = interp["space"]
        value = interp["value"]
        input+=str(4+i)+"\n"
        if (form == "Duration"):
            input+="2\n"
        else:
            input+="3\n"
        input+=(str(order_of_spaces[hash(tuple(sorted(space)))])+"\n")
        input+=str(value)+"\n"
    input+="0\n"
    input+="3\n"
    return input, order_of_spaces

def generate_input_and_check(notes, spaces):
    try:
        print("generating input...")
        print(notes)

        if (os.path.exists(temp_input_file_name)):
            os.remove(temp_input_file_name)
        try:
            f = open(temp_input_file_name,"w+")
            f.write(generate_input(notes, spaces)[0])
        except OSError as e:
            print(e)
            return {}, 1;
        finally:
            f.close()

        ## Running grab_peirce_interps.sh
        stream = os.popen('docker run -it --cap-add=SYS_PTRACE --rm --security-opt seccomp=unconfined --name peirce_docker -v llvm-build:/llvm/build -v '+ PEIRCE_ROOT + ':/peirce -v '+ API_ROOT+':/api andrewe8/peirce_docker:latest bash /api/bin/check_peirce_interps.sh ' + temp_file_name)
        interps = stream.read().strip()
        print("Interpretations from Peirce:")
        print(interps)
        interp_array = interps.splitlines()
        data = notes
        for i in range(len(interp_array)):
            data[i]["text"] = interp_array[i].split("Existing Interpretation: ")[1]
        print(json.dumps(data, indent=4, sort_keys=True))
        return data, 0
    except Exception as e:
        print(e)
        return {}, 1

@app.route('/api/check', methods=["POST"])
def check():
    content = request.get_json()
    print(content)
    print(json.dumps(content, indent=4, sort_keys=True))
    print("File?")
    print(content["file"])
    print("Notes?")
    print(content["notes"])
    print("Spaces?")
    print(content["spaces"])
    file_text = content["file"]
    data = {}

    notes = content["notes"]
    spaces = content["spaces"]
    data, error = generate_input_and_check(notes, spaces)
    print("error?")
    print(error)
    if (error == 1):
        response = app.response_class(
            status=500,
        )
        return response
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

app.run(host="0.0.0.0", port=8080)
