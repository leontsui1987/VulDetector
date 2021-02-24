#!/bin/python

# =================================================================================
# Copyright 2020 IIE, CAS
#
# Author: Lei Cui
# Contact: cuilei@iie.ac.cn
# =================================================================================

import sys
import re
import csv
import copy
import commands


DEBUG = 1

def safe_exec(cmd):
    try:
        os.system(cmd)
    except Exception, err:
        return 0

def extract_include_dir(src_dir):
    # TODO: need to modify here for directory format change!!
    top = extract_top_dir(src_dir)
    upper = os.path.join(top, 'include')
    if os.path.exists(upper): return upper
    return src_dir

def extract_top_dir(src_dir):
    return src_dir

def handle_one_file(src_file, temp_file, header_dir):
    pa_dir=re.compile("(.*)/.*?/.*?")
    top_dir = extract_top_dir(header_dir)
    default_include_dir = extract_include_dir(header_dir)
    cmd1="clang -Xclang -ast-dump %s -I %s -I %s " % (src_file, top_dir, default_include_dir)
    print cmd1
    #print commands.getstatusoutput(cmd1)[0]

    included_dir = []
    included_dir.append(default_include_dir)
    included_dir.append(top_dir)

    depth = 0
    old_cmd1 = ""
    #while False:
    while(commands.getstatusoutput(cmd1)[0]==256):
        depth += 1
        if depth == 20:
            print("error: TOO much depth, cannot find lib_name")
            return commands.getstatusoutput(cmd1)
        output1=commands.getstatusoutput(cmd1)
        if old_cmd1 == cmd1:
            if DEBUG:
                print "Clang command is unchanged"
            break # return None # TODO: Cannot get new headers any more, different from CFGDump
        old_cmd1 = cmd1
        if DEBUG:
            print("Execute CMD1: %s , Ret: %s" % (cmd1, output1[0]))
        lib_name_set=list(re.findall(r"(fatal\s+error\:\s+\'[\w\/]*\.h\')",output1[1]))
        if len(lib_name_set) != 1: continue

        lib_name_set=set(re.findall(r"([\w\/]*\.h)",lib_name_set[0]))
        #print lib_name_set
        dir_path=top_dir
        lib_name = None
        if(lib_name_set and dir_path):
            for lib_name in lib_name_set:
                cmd2="find " + dir_path +" -type f | grep "+ lib_name
                if DEBUG: print "CMD2: ", lib_name, cmd2
                output2=commands.getstatusoutput(cmd2)
                if DEBUG: print("Execute CMD2: %s" % (output2[0]))
                # New method,
                lib_path = output2[1].strip()
                lib_path = lib_path[:len(lib_path)-len(lib_name.strip())]
                #print "Lib_path: ", lib_path
                if lib_path not in included_dir:
                    cmd1=cmd1+" -I " + lib_path
                    included_dir.append(lib_path)
                #print included_dir
        else:
            if(not lib_name):
                if DEBUG:
                    print("error:cannot find lib_name")
                break #return None
            if(not dir_path):
                if DEBUG:
                    print("error:cannot find dir_path")
                break #return None
            break
    cmd1 += ' > %s' % temp_file
    #print cmd1
    return commands.getstatusoutput(cmd1)
##########################


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "extract_func.py <input_folder> <output_folder> <header_folder>\n"
        exit(-1)

    global input_foler
    global src_directory
    src_directory = sys.argv[3]
