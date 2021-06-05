import flask
from flask import jsonify, request
import json
import os
import subprocess
import fcntl, os

app = flask.Flask(__name__)
app.config["DEBUG"] = True
peirce_bin = "/peirce/bin/peirce"
_temp_file_name = "/peirce/Peirce-vscode/temp.cpp"
temp_file_name = None
temp_input_file_name = "/peirce/Peirce-vscode-api/inputs.txt"
'''
peirce_bin = "/peirce/bin/peirce"
temp_file_name = "temp.cpp"
temp_input_file_name = "inputs.txt"

peirce_cmd = peirce_bin + " /peirce/ros_test_cases/new_test_cases/src/new_test_cases/src/time_test.cpp -extra-arg=-I/opt/ros/melodic/include/"


    #subprocess.Popen([peirce_bin,"/peirce/ros_test_cases/new_test_cases/src/new_test_cases/src/time_test.cpp", "-extra-arg=-I/opt/ros/melodic/include/"], \
    #subprocess.Popen(["/bin/bash","-c",peirce_cmd], \
import sys
ON_POSIX = 'posix' in sys.builtin_module_names
p = \
    subprocess.Popen([peirce_bin,"/peirce/ros_test_cases/new_test_cases/src/new_test_cases/src/time_test.cpp", "-extra-arg=-I/opt/ros/melodic/include/"], \
    bufsize=1,stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=ON_POSIX )
#fl = fcntl.fcntl(peirce_process.stdout.fileno(), fcntl.F_GETFL)
#fcntl.fcntl(peirce_process.stdout.fileno(), fcntl.F_SETFL, fl|os.O_NONBLOCK)
#import sys
from threading  import Thread

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty  # python 2.x

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

q = Queue()
t = Thread(target=enqueue_output, args=(p.stdout, q))
t.daemon = True # thread dies with the program
t.start()

# ... do other things here

# read line without blocking
try:  
    line = q.get(timeout=.1)
    print(line)
except Empty:
    print('no output yet')
else: # got line
    print('ok')

print('rpinting')
i = 0
try:  
    line = q.get_nowait() # or q.get(timeout=.1)
    print(line)
except Empty:
    print('no output yet')
print('comm')
data = p.communicate()
print('go')
print(data)

print('go')
for line_ in p.stdout:
    print(str(line_.decode('UTF-8')))


for line_ in p.stdout:
    print(str(line_.decode('UTF-8')))
'''

@app.route('/', methods=["GET"])
def home():
    return "<h1>Welcome to the Peirce VSCode Extension API!</h1>"

@app.route('/api', methods=["GET"])
def api_home():
    return "<h1>Welcome to the Peirce VSCode Extension API!</h1>"

def create_file(text):
    if (os.path.exists(_temp_file_name)):
        pass
        #os.remove(temp_file_name)
    try:
        f = open(_temp_file_name,"w")
        f.write(text)
        f.close()
        return 0
    except Exception as e:
        print('failed to create file')
        print(e)
        return 1

def run_peirce(fname = None):
    try:
        print("running...")

        ## I have been having an extremely difficult time with Bash trying to
        ## extract both coordinates and location in one run...
        ## but I've needed to resort to running Peirce twice! :(
        ## This can and should be fixed in the future.

        ## Running grab_peirce_coords.sh
        print(temp_file_name)
        
        stream = os.popen('bash /peirce/Peirce-vscode-api/bin/grab_peirce_coords.sh ' + temp_file_name)
        coordinates = stream.read().strip()
        print("Coordinates from Peirce:")
        print(coordinates)

        ## Running grab_peirce_interps.sh
        stream = os.popen('bash /peirce/Peirce-vscode-api/bin/grab_peirce_interps.sh ' + temp_file_name)
        interps = stream.read().strip()
        print("Interpretations from Peirce:")
        print(interps)

    

        ## Running grab_peirce_types.sh
        stream = os.popen('bash /peirce/Peirce-vscode-api/bin/grab_peirce_types.sh ' + temp_file_name)
        types = stream.read().strip()
        print("Types from Peirce:")
        print(types)
        coord_array = coordinates.splitlines()
        interp_array = interps.splitlines()
        type_array = types.splitlines()
        data = [None] * len(coord_array)
        for i in range(len(coord_array)):
            begin = coord_array[i].split("Begin: ")[1].split("\t")[0]
            begin_line = int(begin.split("line ")[1].split(",")[0])-1
            begin_col = int(begin.split("column ")[1])-1
            end = coord_array[i].split("End:")[1]
            end_line = int(end.split("line ")[1].split(",")[0])-1
            end_col = int(end.split("column ")[1])
            data[i] = {"coords": {"begin": {"line": begin_line, "character": begin_col}, "end": {"line": end_line, "character": end_col}}, "interp": interp_array[i].split("Existing Interpretation: ")[1], "type": type_array[i]}
        print(json.dumps(data, indent=4, sort_keys=True))

        
        #stream = os.popen('bash /peirce/Peirce-vscode-api/bin/grab_peirce_types.sh ' + temp_file_name)
        stream = os.popen('bash /peirce/Peirce-vscode-api/bin/grab_peirce_constructor_interps.sh ' + temp_file_name)
        peirce_cinterps = coordinates = stream.read().strip().splitlines()
        print('construcotr interps : ')
        print(peirce_cinterps)
        stream = os.popen('bash /peirce/Peirce-vscode-api/bin/grab_peirce_constructor_names.sh ' + temp_file_name)
        peirce_cnames = stream.read().strip().splitlines()
        print('constructor names : ')
        print(peirce_cnames)
        stream = os.popen('bash /peirce/Peirce-vscode-api/bin/grab_peirce_constructor_types.sh ' + temp_file_name)
        peirce_ctypes = stream.read().strip().splitlines()
        print('constructor types')
        print(peirce_ctypes)
        cdata = [None] * len(peirce_cinterps)
        for i in range(len(peirce_cinterps)):
            cdata[i] = { \
                "interp": peirce_cinterps[i].split("Existing Interpretation: ")[1],\
                         "type": peirce_ctypes[i], \
                "name": peirce_cnames[i].split("Snippet: ")[1]        }
        print('PRINTING C DATA')
        print(cdata)
        return data, cdata
    except Exception as e:
        print(e)

@app.route('/api/populate', methods=["POST"])
def populate():
    content = request.get_json()
    print(content)
    print(json.dumps(content, indent=4, sort_keys=True))
    print("Notes?")
    print(content["notes"])
    file_text = content["file"]
    file_name = content["fileName"]
    print("FILE NAME")
    print(file_name)
    print("TEMP FILE NAME : ")
    print(_temp_file_name)
    if (create_file(file_text) != 0):
        response = app.response_class(
            status=500,
        )
        return response
    global temp_file_name
    temp_file_name = file_name if file_name else _temp_file_name 
    data = {}
    data, cdata = run_peirce()
    notes = content["notes"]
    response = app.response_class(
        response=json.dumps({'data':data,'cdata':cdata}),
        status=200,
        mimetype='application/json'
    )
    print(json.dumps(data))
    return response

def hash_space(space):
    return hash(json.dumps(space, sort_keys=True))

def generate_input(notes, spaces, constructors):
    order_of_spaces = {}
    dict_count = 1
    input=""
    for space in spaces:
        input+="2\n"
        if(space["space"] == "Classical Time Coordinate Space"):
            input+="1\n"

        elif(space["space"] == "Classical Geom1D Coordinate Space"):
            input+="2\n"

        if (space["parent"] == None):
            input+="1\n"
            input+=space["label"]+"\n"
            order_of_spaces[hash_space(space)] = dict_count
            dict_count+=1
        else:
            input+="2\n"
            input+=space["label"]+"\n"
            input+=(str(order_of_spaces[hash_space(space["parent"])])+"\n")
            input+=str(space["origin"])+"\n"
            input+=str(space["basis"])+"\n"
            order_of_spaces[hash_space(space)] = dict_count
            dict_count+=1
    for i in range(len(notes)):
        note = notes[i]
        interp = note["interpretation"]
        if (interp == None):
            continue;
        name = interp["name"]
        form = interp["form"]
        space = interp["space"]
        value = interp["value"]
        node_type = interp["type"]
        input+=str(7+i)+"\n"
        if (form == "Duration"):
            input+="2\n"
        elif(form == "Time"):
            input+="3\n"
        elif(form=="Scalar"):
            input+="4\n"
        elif(form=="Time Transform"):
            input+="5\n"
        elif(form=="Position1D"):
            input+="7\n"
        elif(form=="Displacement1D"):
            input+="6\n"
        elif(form=="Geom1D Transform"):
            input+="8\n"
        if "IDENT" not in node_type:
            input+=name+"\n"
        input+=(str(order_of_spaces[hash_space(space)])+"\n")
        input+=str(value)+"\n"
    input+="5\n"
    for i in range(len(constructors)):
        cons = constructors[i]
        interp = cons["interpretation"]
        if (interp == None):
            continue
        input+=str(2+i)+"\n"
        name = interp["name"]
        form = interp["form"]
        space = interp["space"]
        value = interp["value"]
        node_type = interp["type"]
        if (form == "Duration"):
            input+="2\n"
        elif(form == "Time"):
            input+="3\n"
        elif(form=="Scalar"):
            input+="4\n"
        elif(form=="Time Transform"):
            input+="5\n"
        elif(form=="Position1D"):
            input+="7\n"
        elif(form=="Displacement1D"):
            input+="6\n"
        elif(form=="Geom1D Transform"):
            input+="8\n"
        input+=(str(order_of_spaces[hash_space(space)])+"\n")
        input+=str(value)+"\n"
    input+="1\n" 
        
    input+="4\n"
    input+="0\n"
    input+="3\n"
    #print('INPUT!!!')
    #print(input)
    #print(order_of_spaces)
    return input, order_of_spaces

def generate_input_and_check(notes, spaces, constructors):
    try:
        print("generating input...")
        print(notes)

        if (os.path.exists(temp_input_file_name)):
            #os.remove(temp_input_file_name)
            pass
        try:
            f = open(temp_input_file_name,"w")
            f2 = open('/peirce/Peirce-vscode-api/inputs2.txt','w')
            inputs_ = generate_input(notes, spaces, constructors)[0]
            f.write(inputs_)
            f2.write(inputs_)
        except OSError as e:
            print(e)
            return {}, 1;
        finally:
            f.close()
            f2.close()
        ## Running check_peirce_interps.sh
        global temp_file_name
        print(temp_file_name)
        stream = os.popen('bash /peirce/Peirce-vscode-api/bin/check_peirce_interps.sh ' + temp_file_name)
        interps = stream.read().strip()
        print("Interpretations from Peirce:")
        print(interps)
        interp_array = interps.splitlines()
        data = notes
        for i in range(len(interp_array)):
            data[i]["text"] = interp_array[i].split("Existing Interpretation: ")[1]

        ## Running check_peirce_errors.sh
        stream = os.popen('bash /peirce/Peirce-vscode-api/bin/check_peirce_errors.sh ' + temp_file_name)
        errors = stream.read().strip()
        print("Errors from Peirce:")
        print(errors)

        error_array = errors.splitlines()
        data = notes
        for i in range(len(error_array)):
            data[i]["error"] = error_array[i].split("Error Message: ")[1]
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
    file_name = content["fileName"]
    global temp_file_name
    temp_file_name = file_name if file_name else _temp_file_name 
    #print(content["file"])
    print("Notes?")
    print(content["notes"])
    print("Spaces?")
    print(content["spaces"])
    print("constructors?")
    print(content["constructors"])
    file_text = content["file"]
    data = {}

    notes = content["notes"]
    spaces = content["spaces"]
    constructors = content["constructors"]
    data, error = generate_input_and_check(notes, spaces, constructors)
    print("error?")
    print(error)
    if (error == 1):
        response = app.response_class(
            status=500,
        )
        return response
    print(data)
    print(error)

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

app.run(host="0.0.0.0", port=8080)
