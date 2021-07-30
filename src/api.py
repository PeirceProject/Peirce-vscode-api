from typing import ValuesView
import flask
from flask import jsonify, request
import json
import os
import subprocess
import fcntl, os
import time
import re

from flask.helpers import send_from_directory
import peirce_constants

app = flask.Flask(__name__)
app.config["DEBUG"] = True
peirce_bin = "/peirce/bin/peirce"
_temp_file_name = "/peirce/Peirce-vscode/temp.cpp"
temp_file_name = None
temp_input_file_name = "/peirce/Peirce-vscode-api/inputs.txt"

peirce_bin = "/peirce/bin/peirce"
temp_file_name = "temp.cpp"
temp_input_file_name = "inputs.txt"

file_name = None
p = None

def list_print(str_list):
    for ln_ in str_list:
        print(ln_)

def read_data():
    global p
    lns_ = []
    while(len(lns_)==0):#don't call this unless you're getting output
        for ln_ in p.stdout:
            lns_.append(ln_.decode('utf-8'))
        if(len(lns_)==0):
            time.sleep(.25)
    return lns_

def send_cmd(cmd, wait = True):
    print(cmd)
    global p
    p.stdin.write(cmd.encode('utf-8'))
    p.stdin.flush()
    if(wait):
        time.sleep(6)


def get_state_process(f_name):
    global p
    global file_name
    #if(is_running_file(f_name)):
    #    return
    if p is not None:
        p.kill()
    print('running peirce on file' + f_name)
    print('old file')
    print(file_name)
    file_name = f_name
    #peirce_cmd = "valgrind --leak-check=yes " + peirce_bin + " " + f_name + " -extra-arg=-I/opt/ros/melodic/include/"
    peirce_cmd = "" + peirce_bin + " " + f_name + " -extra-arg=-I/opt/ros/melodic/include/"
    
    p = \
        subprocess.Popen(peirce_cmd+"", shell = True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)#, close_fds=ON_POSIX)
    fl = fcntl.fcntl(p.stdout.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, fl|os.O_NONBLOCK)
    time.sleep(3)
    read_data()
    print('ran peirce')
def is_running_file(f_name):
    global file_name
    return file_name == f_name

@app.route('/', methods=["GET"])
def home():
    return "<h1>Welcome to the Peirce VSCode Extension API!</h1>"

@app.route('/api', methods=["GET"])
def api_home():
    return "<h1>Welcome to the Peirce VSCode Extension API!</h1>"

def get_state(fname = None):
    try:
        print("running...")

        ## I have been having an extremely difficult time with Bash trying to
        ## extract both coordinates and location in one run...
        ## but I've needed to resort to running Peirce twice! :(
        ## This can and should be fixed in the future.

        ## Running grab_peirce_coords.sh
        print(temp_file_name)
        
        #stream = os.popen('bash /peirce/Peirce-vscode-api/bin/grab_peirce_coords.sh ' + temp_file_name)
        #coordinates = stream.read().strip()
        #print("Coordinates from Peirce:")
        #print(coordinates)

        send_cmd(peirce_constants.print_table_ + '\n', False)
        resp = read_data()
        print('get coords response:::')
        list_print(resp)
        #print()
        coords2 = []
        interps2 = []
        types2 = []
        error_msgs = []
        for resp_ in resp:
            #print(resp_)
            if 'Existing Interpretation' in resp_:
            #    print(' existing')
                interps2.append(resp_.strip())
            else :
                pass 
            #    print('not existing')
            if 'Begin' in resp_ and 'End' in resp_:
            #    print(' beginning')
                coords2.append(resp_.strip())
            else:
                pass
            #    print('not beginning')
            m = re.search('Node Type : ([\w]*),',resp_)
            if m :
                #print(' type')
                types2.append(m.group(1).strip())
            else:
                pass
            
            if "Error Message: " in resp_:
                print('found error')
                error_msgs.append(resp_.strip().split("Error Message: ")[1])
                print(error_msgs[-1])
                #print('not type')

        send_cmd(peirce_constants.print_all_terms_+'\n', False)
        resp = read_data()
        #print('ALL DATA DUMP:')
        #list_print(resp)
        print('get coords response:::')
        #print()
        all_coords = []
        all_names = []
        all_interps = []
        all_types = []
        all_error_msgs = []
        for resp_ in resp:
            #print(resp_)
            if 'Existing Interpretation' in resp_:
            #    print(' existing')
                all_interps.append(resp_.strip())
            else :
                pass 
            
            m = re.search('Snippet: (.*)',resp_)
            if m:
                all_names.append(m.group(1).strip()[0:-1])
            #    print('not existing')
            if 'Begin' in resp_ and 'End' in resp_:
            #    print(' beginning')
                all_coords.append(resp_.strip())
            else:
                pass
            #    print('not beginning')
            m = re.search('Node Type : ([\w]*),',resp_)
            if m :
                #print(' type')
                all_types.append(m.group(1).strip())
            else:
                pass
            
            if "Error Message: " in resp_:
                print('found error')
                all_error_msgs.append(resp_.strip().split("Error Message: ")[1])
                print(all_error_msgs[-1])
                #print('not type')

        print('exited this part')

        coord_array = coords2#coordinates.splitlines()
        interp_array = interps2#interps.splitlines()
        type_array = types2#types.splitlines()

        #print('TERM RESULTS:')
        #print(resp_)
        #print(coord_array)
        #print(interp_array)
        #print(type_array)
        #print(error_msgs)

        data = [None] * len(coord_array)
        for i in range(len(coord_array)):
            begin = coord_array[i].split("Begin: ")[1].split("\t")[0]
            begin_line = int(begin.split("line ")[1].split(",")[0])-1
            begin_col = int(begin.split("column ")[1])-1
            end = coord_array[i].split("End:")[1]
            end_line = int(end.split("line ")[1].split(",")[0])-1
            end_col = int(end.split("column ")[1])
            data[i] = \
                {
                    "coords": {
                        "begin": {"line": begin_line, "character": begin_col}, 
                        "end": {"line": end_line, "character": end_col}}, 
                    "interp": interp_array[i].split("Existing Interpretation: ")[1], 
                    "node_type": type_array[i],
                    "error": error_msgs[i],
                    "name": all_names[i]
                }
        
        print('proceeding to alldata')
        all_data = [None] * len(all_coords)
        for i in range(len(all_coords)):
            begin = all_coords[i].split("Begin: ")[1].split("\t")[0]
            begin_line = int(begin.split("line ")[1].split(",")[0])-1
            begin_col = int(begin.split("column ")[1])-1
            end = all_coords[i].split("End:")[1]
            end_line = int(end.split("line ")[1].split(",")[0])-1
            end_col = int(end.split("column ")[1])
            all_data[i] = \
                {
                    "coords": {
                        "begin": {"line": begin_line, "character": begin_col}, 
                        "end": {"line": end_line, "character": end_col}}, 
                    "interp": all_interps[i].split("Existing Interpretation: ")[1], 
                    "node_type": all_types[i],
                    "error": all_error_msgs[i]
                }
        #print('ALL TERMS:')
        #for at_ in all_data:
        #    print(at_)
        #print('printed all terms')

        send_cmd("5\n0\n1\n", False)
        cons_str = read_data()
        #print(cons_str)
        peirce_cinterps = []
        peirce_cnames = []
        peirce_ctypes = []
        for resp_ in cons_str:
            if 'Existing Interpretation' in resp_:
                peirce_cinterps.append(resp_.strip())
            m = re.search('Snippet: (.*)',resp_)
            if m:
                peirce_cnames.append(m.group(1).strip())
            m = re.search('Type : (.*), Ann',resp_)
            if m :
                peirce_ctypes.append(m.group(1).strip())


        #for data_ in cons_str:
        #    print(data_)

        #print('CONSTRUCTOR RESULTS:')
        #print(peirce_cinterps)
        #print(peirce_cnames)
        #print(peirce_ctypes)


        cdata = [None] * len(peirce_cinterps)
        for i in range(len(peirce_cinterps)):
            cdata[i] = { \
                "interp": peirce_cinterps[i].split("Existing Interpretation: ")[1],\
                         "node_type": peirce_ctypes[i], \
                "name": peirce_cnames[i]        }
        #print('PRINTING C DATA')
        #print(cdata)

        print('RETURNING')


        return data, cdata, all_data
    except Exception as e:
        print(e)

@app.route('/api/getState', methods=["POST"])
def populate():
    print("PRINTING")
    content = request.get_json()
    
    file_text = content["file"]
    file_name = content["fileName"]


    #if not is_running_file(file_name):
    get_state_process(file_name)


    print("FILE NAME")
    print(file_name)

    global temp_file_name
    temp_file_name = file_name if file_name else _temp_file_name 

    data, cdata, all_data = get_state()
    while(len(data) > 100):
        data, cdata, all_data = get_state()

    notes = content["terms"]
    response = app.response_class(
        response=json.dumps({'data':data,'cdata':cdata,'adata':all_data}),
        status=200,
        mimetype='application/json'
    )
    
    print('DATA:')
    print(len(data))
    list_print(data)
    print('CDATA:')
    print(len(cdata))
    list_print(cdata)
    print('ALL DATA:')
    print(len(all_data))
    list_print(all_data)
    #print('alldataresult:')
    #for ad_ in all_data:
    #    print(ad_)
    #print(json.dumps({'data':data,'cdata':cdata, 'adata':all_data}))
    return response


@app.route('/api/createSpace', methods=["POST"])
def createSpaceInterpretation():
    content = request.get_json()
    space = content["space"]
    send_cmd(peirce_constants.create_space_+"\n", False)
    
    list_print(read_data())

    if(space["space"] == "Classical Time Coordinate Space"):
        send_cmd("1\n", False)
        list_print(read_data())

    elif(space["space"] == "Classical Geom1D Coordinate Space"):
        send_cmd("2\n", False)
        list_print(read_data())

    elif(space["space"] == "Classical Geom3D Coordinate Space"):
        send_cmd("3\n", False)
        list_print(read_data())

    if (space["parent"] == None):
        send_cmd("1\n", False)
        list_print(read_data())
        send_cmd(space["label"]+"\n", False)
        list_print(read_data())
    else:
        print('DERIVED SP')
        send_cmd("2\n", False)
        list_print(read_data())
        send_cmd(space["label"]+"\n", False)
        parent_prompt = read_data()
        print(parent_prompt)
        options = []
        for ln_ in parent_prompt:
            m = re.search(' - ([\w]*) ',ln_)
            if(m):
                options.append(m.groups(1)[0])
        print('parent options')
        print(options)
        for i in range(len(options)):
            if options[i] == space["parent"]["label"]:
                send_cmd(str(i+1)+"\n",False)
                read_data()
                break

        for i in range(len(space["origin"])):
            send_cmd(str(space["origin"][i])+"\n",False)
            list_print(read_data())
        for i in range(len(space["basis"])):
            send_cmd(str(space["basis"][i])+"\n",False)
            list_print(read_data())

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/api/createTermInterpretation', methods=["POST"])
def createTermInterpretation():
    content = request.get_json()
    term = content["term"]
    idx = int(peirce_constants.annotate_start_)
    print('STARTING CREATE')
    data, cdata, adata = get_state()
    print('DATA:')
    print(len(data))
    list_print(data)
    print('CDATA:')
    print(len(cdata))
    list_print(cdata)
    print('ALL DATA:')
    print(len(adata))
    list_print(adata)

    for i in range(len(data)):
        term_ = data[i]
        if \
            term_["coords"]["begin"]["line"] == term["positionStart"]["line"] and \
            term_["coords"]["begin"]["character"] == term["positionStart"]["character"] and \
            term_["coords"]["end"]["line"] == term["positionEnd"]["line"] and \
            term_["coords"]["end"]["character"] == term["positionEnd"]["character"] and \
            term_["node_type"] == term["node_type"]:
            idx += i
            break

    print(idx)
    print('TERM : ')
    print(term)

    send_cmd(str(idx)+"\n",False)
    list_print(read_data())


    interp = term["interpretation"]
    name = interp["name"]
    interp_type = interp["interp_type"]
    space = interp["space"] if "space" in interp else None
    domain = interp["domain"] if "domain" in interp else None
    codomain = interp["codomain"] if "codomain" in interp else None
    value = interp["value"] if "value" in interp else None
    node_type = term["node_type"]
    if peirce_constants.timestamped_ in interp_type:
        name = value['name']


    print('sending option....')
    print(interp_type)
    #print(str(peirce_constants.interp_type_to_menu_index[interp_type]))
    if peirce_constants.timeseries_ in interp_type:
        send_cmd(peirce_constants.interp_type_to_menu_index[peirce_constants.timeseries_]+"\n",False)
        list_print(read_data())
        send_cmd(str(peirce_constants.time_series_map[interp_type])+"\n",False)
        time_space = interp["time_space"]
        space = interp["space"] if "space" in interp else None
        domain = interp["domain"] if "domain" in interp else None
        codomain = interp["codomain"] if "codomain" in interp else None

        #list_print(read_data())
        space_prompt = read_data()
        list_print(space_prompt)
        options = []
        for ln_ in space_prompt:
                m = re.search(' - (.*) ', ln_.strip())
                print('AT LINE : ' + ln_)
                if(m):
                    options.append(m.groups(1)[0])
                    print('found option  ')
                    print(m.groups(1)[0])
                else:
                    print('no option')
        print('parent options')
        print(options)
        print('space target?')
        print(time_space)
        for i in range(len(options)):
            if options[i] == time_space["label"]:
                print('found!')
                send_cmd(str(i+1)+"\n",False)
                #list_print(read_data())
                break
            else:
                print('not found!')
        if space:
            space_prompt = read_data()
            list_print(space_prompt)
            options = []
            for ln_ in space_prompt:
                    m = re.search(' - (.*) ', ln_.strip())
                    print('AT LINE : ' + ln_)
                    if(m):
                        options.append(m.groups(1)[0])
                        print('found option  ')
                        print(m.groups(1)[0])
                    else:
                        print('no option')
            print('parent options')
            print(options)
            print('space target?')
            print(space)
            for i in range(len(options)):
                if options[i] == space["label"]:
                    print('found!')
                    send_cmd(str(i+1)+"\n",False)
                    list_print(read_data())
                    break
                else:
                    print('not found!')
        if domain:
            space_prompt = read_data()
            list_print(space_prompt)
            options = []
            for ln_ in space_prompt:
                    m = re.search(' - (.*) ', ln_.strip())
                    print('AT LINE : ' + ln_)
                    if(m):
                        options.append(m.groups(1)[0])
                        print('found option  ')
                        print(m.groups(1)[0])
                    else:
                        print('no option')
            print('parent options')
            print(options)
            print('space target?')
            print(domain)
            for i in range(len(options)):
                if options[i] == domain["label"]:
                    print('found!')
                    send_cmd(str(i+1)+"\n",False)
                    break
                else:
                    print('not found!')
        if codomain:
            space_prompt = read_data()
            list_print(space_prompt)
            options = []
            for ln_ in space_prompt:
                    m = re.search(' - (.*) ', ln_.strip())
                    print('AT LINE : ' + ln_)
                    if(m):
                        options.append(m.groups(1)[0])
                        print('found option  ')
                        print(m.groups(1)[0])
                    else:
                        print('no option')
            print('parent options')
            print(options)
            print('space target?')
            print(codomain)
            for i in range(len(options)):
                if options[i] == codomain["label"]:
                    print('found!')
                    send_cmd(str(i+1)+"\n",False)
                    list_print(read_data())
                    break
                else:
                    print('not found!')

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    else:
        send_cmd(str(peirce_constants.interp_type_to_menu_index[interp_type])+"\n",False)

    if interp_type == peirce_constants.timeseries_value_:
        time_series = interp['time_series']
        time_value = interp['time_value'] if 'time_value' in interp else None
        ts_prompt = read_data()
        list_print(ts_prompt)
        options = []
        for ln_ in ts_prompt:
                m = re.search(' - (.*) ', ln_.strip())
                print('AT LINE : ' + ln_)
                if(m):
                    options.append(m.groups(1)[0])
                    print('found option  ')
                    print(m.groups(1)[0])
                else:
                    print('no option')
        print('parent options')
        print(options)
        print('space target?')
        print(time_series)
        for i in range(len(options)):
            if options[i] == time_series["name"]:
                print('found!')
                send_cmd(str(i+1)+"\n",False)
                list_print(read_data())
                break
            else:
                print('not found!')

        if time_value:
            send_cmd('2\n',False)
            send_cmd(str(time_value)+'\n',True)
        else:
            send_cmd('1\n',True)

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


    if "IDENT" not in node_type: #this doesnt need to be here. check the prompts. 
        print('sending name cmd...')
        print(read_data())
        send_cmd(name+"\n", False)
        print('sent?')
    if space:
        space_prompt = None
        space_prompt = read_data()
        list_print(space_prompt)
        options = []
        for ln_ in space_prompt:
                m = re.search(' - (.*) ', ln_.strip())
                print('AT LINE : ' + ln_)
                if(m):
                    options.append(m.groups(1)[0])
                    print('found option  ')
                    print(m.groups(1)[0])
                else:
                    print('no option')
        print('parent options')
        print(options)
        print('space target?')
        print(space)
        for i in range(len(options)):
            if options[i] == space["label"]:
                print('found!')
                send_cmd(str(i+1)+"\n",False)
                list_print(read_data())
                break
            else:
                print('not found!')
    elif domain and codomain:
        space_prompt = None
        space_prompt = read_data()
        list_print(space_prompt)
        options = []
        for ln_ in space_prompt:
                m = re.search(' - (.*) ', ln_.strip())
                print('AT LINE : ' + ln_)
                if(m):
                    options.append(m.groups(1)[0])
                    print('found option  ')
                    print(m.groups(1)[0])
                else:
                    print('no option')
        print('parent options')
        print(options)
        print('space target?')
        print(domain)
        for i in range(len(options)):
            if options[i] == domain["label"]:
                print('found!')
                send_cmd(str(i+1)+"\n",False)
                list_print(read_data())
                break
            else:
                print('not found!')
        print('space target?')
        print(codomain)
        for i in range(len(options)):
            if options[i] == codomain["label"]:
                print('found!')
                send_cmd(str(i+1)+"\n",True)
                list_print(read_data())
                break
            else:
                print('not found!')
    
    if peirce_constants.timestamped_ in interp_type:
        print('entering logic block')
        timestamp = interp['timestamp']
        tsname = timestamp['space']['label']
        space_prompt = None
        space_prompt = read_data()
        list_print(space_prompt)
        options = []
        for ln_ in space_prompt:
                m = re.search(' - (.*) ', ln_.strip())
                print('AT LINE : ' + ln_)
                if(m):
                    options.append(m.groups(1)[0])
                    print('found option  ')
                    print(m.groups(1)[0])
                else:
                    print('no option')
        print('parent options')
        print(options)
        print('space target?')
        print(space)
        for i in range(len(options)):
            if options[i] == tsname:
                print('found!')
                send_cmd(str(i+1)+"\n",False)
                break
            else:
                print('not found!')
        list_print(read_data())
        print('entering timestamp...')
        send_cmd(str(timestamp['value'][0])+'\n',False)

        space = value['space'] if 'space' in value else None
        domain = value["domain"] if "domain" in value else None
        codomain = value["codomain"] if "codomain" in value else None
        value = value["value"] if "value" in value else None
            
        if space:
            space_prompt = None
            space_prompt = read_data()
            list_print(space_prompt)
            options = []
            for ln_ in space_prompt:
                    m = re.search(' - (.*) ', ln_.strip())
                    print('AT LINE : ' + ln_)
                    if(m):
                        options.append(m.groups(1)[0])
                        print('found option  ')
                        print(m.groups(1)[0])
                    else:
                        print('no option')
            print('parent options')
            print(options)
            print('space target?')
            print(space)
            for i in range(len(options)):
                if options[i] == space["label"]:
                    print('found!')
                    send_cmd(str(i+1)+"\n",False)
                    list_print(read_data())
                    break
                else:
                    print('not found!')
        elif domain and codomain:
            space_prompt = None
            space_prompt = read_data()
            list_print(space_prompt)
            options = []
            for ln_ in space_prompt:
                    m = re.search(' - (.*) ', ln_.strip())
                    print('AT LINE : ' + ln_)
                    if(m):
                        options.append(m.groups(1)[0])
                        print('found option  ')
                        print(m.groups(1)[0])
                    else:
                        print('no option')
            print('parent options')
            print(options)
            print('space target?')
            print(domain)
            for i in range(len(options)):
                if options[i] == domain["label"]:
                    print('found!')
                    send_cmd(str(i+1)+"\n",False)
                    list_print(read_data())
                    break
                else:
                    print('not found!')
            print('space target?')
            print(codomain)
            for i in range(len(options)):
                if options[i] == codomain["label"]:
                    print('found!')
                    send_cmd(str(i+1)+"\n",True)
                    list_print(read_data())
                    break
                else:
                    print('not found!')
        else:
            list_print(read_data())
        if value:
            print('sending value')
            print(value)
            value = value or [0]
            for i in range(len(value)):
                print('sending value')
                print(value)
                if i == len(value)-1:
                    send_cmd(str(value[i]) + "\n",True)
                else:
                    send_cmd(str(value[i]) + "\n",False)
                print(read_data())
    elif value:
        print('sending value')
        print(value)
        value = value or [0]
        for i in range(len(value)):
            print('sending value')
            print(value)
            if i == len(value)-1:
                send_cmd(str(value[i]) + "\n",True)
            else:
                send_cmd(str(value[i]) + "\n",False)
            print(read_data())

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    

@app.route('/api/createConstructorInterpretation', methods=["POST"])
def createConstructorInterpretation():
    content = request.get_json()
    constructor = content["constructor"]
    idx = 2
    data, cdata, adata = get_state()
    print('CONSTRUCTOR : ')
    print(constructor)
    send_cmd(peirce_constants.annotate_constructors_+"\n", False)
    list_print(read_data())
    for i in range(len(cdata)):
        cons_ = cdata[i]
        print('cons_i')
        print(cons_)
        
        if \
            cons_["name"] == constructor["name"]:
            print('found term!')
            idx += i
            break
        else: 
            print('term not found!')

    send_cmd(str(idx)+"\n",False)
    print(read_data())


    interp = constructor["interpretation"]
    name = interp["name"]
    interp_type = interp["interp_type"]
    space = interp["space"] if "space" in interp else None
    domain = interp["domain"] if "domain" in interp else None
    codomain = interp["codomain"] if "codomain" in interp else None
    value = interp["value"] if "value" in interp else None
    node_type = constructor["node_type"]

    
    send_cmd(str(peirce_constants.interp_type_to_menu_index[interp_type])+"\n",False)

    if space:
        space_prompt = None
        
        space_prompt = read_data()
        list_print(space_prompt)
        options = []
        for ln_ in space_prompt:
                m = re.search(' - (.*) ', ln_.strip())
                print('AT LINE : ' + ln_)
                if(m):
                    options.append(m.groups(1)[0])
                    print('found option  ')
                    print(m.groups(1)[0])
                else:
                    print('no option')
        print('parent options')
        print(options)
        print('space target?')
        print(space)
        for i in range(len(options)):
            if options[i] == space["label"]:
                print('found!')
                send_cmd(str(i+1)+"\n",False)
                list_print(read_data())
                break
            else:
                print('not found!')
    
    if value:
        print('sending value')
        print(value)
        send_cmd(str(value) + "\n",True)
        print(read_data())

    send_cmd("1\n",False)

    list_print(read_data())

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/api/check2', methods=["POST"])
def check2():
    content = request.get_json()
    terms = content["terms"]
    data, cdata, adata = get_state()
    print('terms!!!')
    print(terms)
    print('end terms!!')
    for i in range(len(terms)):
        #not sure why I had to do this...but
        #remove this soon :) 
        print('set term i...,.')
        if len(data) > i:
            terms[i]["error"] = data[i]["error"]
        elif len(data) > 0:
            terms[i]["error"] = data[0]["error"]
        else:
            terms[i]["error"] = "No Error Detected"
    print('returning...')
    print(terms)
    response = app.response_class(
        response=json.dumps(terms),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/api/check3', methods=["POST"])
def check3():
    content = request.get_json()
    
    data, cdata, adata = get_state()

    print('RETURNING ADATA')
    list_print(adata)

    response = app.response_class(
        response=json.dumps(adata),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/api/createTimeSeries', methods=["POST"])
def createTimeSeries():
    content = request.get_json()

    interp = content["time_series"]
    name = interp["name"]
    interp_type = interp["interp_type"]
    time_space = interp["time_space"]
    space = interp["space"] if "space" in interp else None
    domain = interp["domain"] if "domain" in interp else None
    codomain = interp["codomain"] if "codomain" in interp else None

    send_cmd(peirce_constants.create_time_series_+'\n',False)
    list_print(read_data())
    if interp_type == 'Pose3D Time Series':
        send_cmd('1\n',False)
    elif interp_type == 'Geom3D Transform Time Series':
        send_cmd('2\n',False)
    list_print(read_data())
    send_cmd(name+'\n',False)
    space_prompt = read_data()
    list_print(space_prompt)
    options = []
    for ln_ in space_prompt:
            m = re.search(' - (.*) ', ln_.strip())
            print('AT LINE : ' + ln_)
            if(m):
                options.append(m.groups(1)[0])
                print('found option  ')
                print(m.groups(1)[0])
            else:
                print('no option')
    print('parent options')
    print(options)
    print('space target?')
    print(time_space)
    for i in range(len(options)):
        if options[i] == time_space["label"]:
            print('found!')
            send_cmd(str(i+1)+"\n",False)
            #list_print(read_data())
            break
        else:
            print('not found!')
    if space:
        space_prompt = read_data()
        list_print(space_prompt)
        options = []
        for ln_ in space_prompt:
                m = re.search(' - (.*) ', ln_.strip())
                print('AT LINE : ' + ln_)
                if(m):
                    options.append(m.groups(1)[0])
                    print('found option  ')
                    print(m.groups(1)[0])
                else:
                    print('no option')
        print('parent options')
        print(options)
        print('space target?')
        print(space)
        for i in range(len(options)):
            if options[i] == space["label"]:
                print('found!')
                send_cmd(str(i+1)+"\n",False)
                list_print(read_data())
                break
            else:
                print('not found!')
    if domain:
        space_prompt = read_data()
        list_print(space_prompt)
        options = []
        for ln_ in space_prompt:
                m = re.search(' - (.*) ', ln_.strip())
                print('AT LINE : ' + ln_)
                if(m):
                    options.append(m.groups(1)[0])
                    print('found option  ')
                    print(m.groups(1)[0])
                else:
                    print('no option')
        print('parent options')
        print(options)
        print('space target?')
        print(domain)
        for i in range(len(options)):
            if options[i] == domain["label"]:
                print('found!')
                send_cmd(str(i+1)+"\n",False)
                break
            else:
                print('not found!')
    if codomain:
        space_prompt = read_data()
        list_print(space_prompt)
        options = []
        for ln_ in space_prompt:
                m = re.search(' - (.*) ', ln_.strip())
                print('AT LINE : ' + ln_)
                if(m):
                    options.append(m.groups(1)[0])
                    print('found option  ')
                    print(m.groups(1)[0])
                else:
                    print('no option')
        print('parent options')
        print(options)
        print('space target?')
        print(codomain)
        for i in range(len(options)):
            if options[i] == codomain["label"]:
                print('found!')
                send_cmd(str(i+1)+"\n",False)
                list_print(read_data())
                break
            else:
                print('not found!')

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


#andrew start here in morning
@app.route('/api/addValueToTimeSeries', methods=["POST"])
def createTimeSeriesValue():
    content = request.get_json()
    #content = content["data"]
    interp = content["interpretation"]
    print(interp)
    name = interp["name"]
    interp_type = interp["interp_type"]
    time_series = interp['series_name']#content["time_series"]
    timestamp = interp["timestamp"]
    value = interp["value"]
    time_series = interp['series_name']
    values = value["value"] if 'value' in value else []

    send_cmd(peirce_constants.add_timeseries_value_+'\n',False)
    ts_prompt = read_data()
    list_print(ts_prompt)
    options = []
    for ln_ in ts_prompt:
            m = re.search(' - (.*) ', ln_.strip())
            print('AT LINE : ' + ln_)
            if(m):
                options.append(m.groups(1)[0])
                print('found option  ')
                print(m.groups(1)[0])
            else:
                print('no option')
    print('parent options')
    print(options)
    print('space target?')
    print(time_series)
    for i in range(len(options)):
        if options[i] == time_series:
            print('found!')
            if(len(values) == 0):
                send_cmd(str(i+1)+"\n",True)
            else:
                send_cmd(str(i+1)+"\n",False)
            list_print(read_data())
            break
        else:
            print('not found!')

    send_cmd(str(timestamp["value"][0])+"\n",False)
    list_print(read_data())

    if len(values) > 0:
        #send_cmd(str(value["value"][0])+"\n",False)
        for i in range(len(values)):
            print('sending value')
            print(values)
            if i == len(values)-1:
                send_cmd(str(values[i]) + "\n",True)
            else:
                send_cmd(str(values[i]) + "\n",False)
            list_print(read_data())

    #if(interp_type == "TimeStamped Pose3D")

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    
app.run(host="0.0.0.0", port=8080)
