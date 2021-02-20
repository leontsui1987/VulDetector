#/bin/python
# This file extract the descired code part of a function for similarity computation
# It works in two modes:  
#	 1. Extract only the code part of a function, used for string based comparision
#	 2. Extract the code part with include, function declarations, etc, used for Clang CFG based comparision

# Input: Directory a project
# Output: A set file of functions, format: c_file_name#function_name.c
##


import os
import sys
import re
import csv
import copy
import commands

from search_include import handle_one_file

# Only get the code part of function 
# or associated LLVM compilation parts of function
SMALL_FUNC = 1

re_ansi = re.compile(r'\x1b[^m]*m')
file_types = ['.c', '.cpp', '.c#vul', '.c#fixed']

global header_directory
input_folder = ''

DEBUG = 0

def safe_exec(cmd):
	try:
		os.system(cmd)
	except Exception, err:
		return 0

def correct_file_types(file_name):
	ret = os.path.splitext(file_name)
	if len(ret) == 0:
		return False
	if ret[1] not in file_types:
		return False
	return True


def line_to_delete(line_index, funcs_to_delete):
	for item in funcs_to_delete:
		line_start = item[2]
		line_end = item[3]
		#print line_start, line_end
		if line_index >= line_start and line_index <= line_end:
			return 1
	return 0

def delete_funcs_from_line(input_file, funcs_to_delete, output_file):
	return 
	with open(output_file, "w") as fp_out:
		with open(input_file, "r") as fp:
			line_index = 0
			for line in fp:
				line_index += 1
		if line_to_delete(line_index, funcs_to_delete):
					continue
				else:	 
					fp_out.write(line)
	

# NOTE: Delete codes of functions from a file, used for graph based methods (Build Graph)
# Save the code part of the desired function, and other parts including 'include, Define, global_variable, etc.'
def delete_funcs_from_file(file_path, version, output_folder):
	return 
	func_list = get_ast(file_path, "test.log")
	#print func_list
	assert os.path.isfile(file_path), 'FATAL: %s is not a file' % file_path

	funcs_to_delete = []
	if len(func_list) != 0:
		for index in range(len(func_list)):
			item = func_list[index]
			func_list_bkup = copy.deepcopy(func_list)
			#print item
			#line_start = item[2]
			#line_end = item[3]
			func_name = item[1]
			#print func_name
			#funcs_to_delete = list( set(func_list) - set(item) )
			start_line = func_list_bkup[index][2]
			del func_list_bkup[index]
			funcs_to_delete = func_list_bkup
			#print funcs_to_delete
			output_file = os.path.join(output_folder, "temp.cpp")
			delete_funcs_from_line(file_path, funcs_to_delete, output_file)

		cmd = 'mv %s %s ' % (output_file, os.path.join(output_folder, version + "#" + func_name + "#" + str(start_line) + ".c") )
			safe_exec(cmd)

			#change_style = "clang-format -style=llvm " + output_file + " > " + os.path.join(output_folder, version + "#" + func_name + "_all.cpp")
			#safe_exec(change_style)


def extract_func_from_line(input_file, line_start, line_end, output_file):
	with open(output_file, "w") as fp_out:
		with open(input_file, "r") as fp:
			line_index = 0
			for line in fp:
				line_index += 1
				if line_index >= line_start and line_index <= line_end:
					fp_out.write(line)


# NOTE: Extract the codes of a function from a file, used for string based ML method
# Only save the code part of the function
def extract_func_from_file(file_path, version, output_folder):

	print "Extract func ", file_path
	func_list = get_ast(file_path, "test.log")
	#print func_list
	assert os.path.isfile(file_path), 'FATAL: %s is not a file' % file_path

	if len(func_list) != 0:
		for item in func_list:
	#for item in func_list:
			#print item
			line_start = item[2]
			line_end = item[3]
			func_name = item[1]
			output_file = os.path.join(output_folder, "temp.cpp")
			extract_func_from_line(file_path, line_start, line_end, output_file)

			#change_style = "clang-format -style=llvm " + output_file + " > " + os.path.join(output_folder, version + "#" + func_name + ".cpp")
			cmd = 'mv %s %s ' % (output_file, os.path.join(output_folder, version + "#small#" + func_name + "#" + str(line_start) + ".c") )
			#print cmd
			safe_exec(cmd)

def get_ast(input_file, temp_file):
	global input_folder
	global header_directory
	if os.path.exists(temp_file):
		os.remove(temp_file)

	header_folder = os.path.join(input_folder, 'include')

	DEBUG = 0
	cmd = ''
	ret = handle_one_file(input_file, temp_file, header_directory)
	#if ret == None or ret[0] != 0:
		#print "Handle one file fail"
		#return []
	
	if not os.path.exists(temp_file):
		print 'Generate results fail'
		return []

	#print 'Start to analyze results'
	ast_list = []
	with open(temp_file, "r") as fp:
		for line in fp:
			if "FunctionDecl" in line:
				line = line.strip()
				ast_list.append(re_ansi.sub('', line))
	#print 'AST list, ', ast_list

	result_list = []

	for func_str in ast_list:
		if func_str.endswith("extern"):
			continue
		if DEBUG:
			print 'Func_str:  ', func_str
		#m = re.findall(r"(\<.*\,\sline.*\>\s[a-zA-Z0-9_]*)", func_str)
		#m = re.findall(r"(\<.*\,\sline.*\>\sline[a-zA-z0-9:]*\s[a-zA-Z0-9_]*)", func_str)
		m = re.findall(r"(\<.*\,\sline.*\>\s[a-zA-z0-9:]*\s[a-zA-Z0-9_]*)", func_str)
		if m:
			func_info = (re.sub('\'|\"', '', m[0])).split(' ')
			if DEBUG:
				print 'Func_info ', func_info
			func_name = (func_info[-1]).strip().lower()
			if func_name == '':
				func_name = (func_info[-2]).lower()
			if DEBUG:
				print 'Func_name ', func_name
   
			if func_name in ['used', 'invalid']: # THe func name is after 'used'
				m = re.findall(r"(\<.*\,\sline.*\>\s[a-zA-z0-9:]*\s%s\s[a-zA-Z0-9_]*)" % func_name, func_str)
				assert m != None, 'Wrong expression'
				func_info = (re.sub('\'|\"', '', m[0])).split(' ')
				func_name = func_info[-1].lower()
			   
			if func_info[0][1:4] == 'col': # TODO: some functions are 'col:1'
				continue

			start_line = int((func_info[0]).split(':')[1])
			end_line = int((func_info[1]).split(':')[1])
			# TODO: may uncomment for small functions
		#if end_line - start_line <= 3: # small function
			#	 continue

			if DEBUG: #print func_str
			print func_name, start_line, end_line, '\n\n'

		# Ensure it is indeed a function definition
			cmd = 'grep -in %s %s | grep %d' % (func_name, input_file , start_line)
			ret = commands.getstatusoutput(cmd)
			if DEBUG:
			print 'Cmd: %s, Ret: %s ' % (cmd, ret)
			if ret[0] != 0: 
				cmd = 'grep -in %s %s | grep %d' % (func_name, input_file , start_line+1) # Case: func_type and func_name are in different lines 
				ret = commands.getstatusoutput(cmd)
				if ret[0] != 0:
					continue

			# Ensure it is not a function declaration
			cmd = 'grep -in \'%s\' %s | grep -w %d' % (';', input_file, end_line) #	 function declaration ends with ;
			ret = commands.getstatusoutput(cmd)
			if DEBUG:
			print 'Cmd: %s, Ret: %s ' % (cmd, ret)
			if ret[0] == 0:
				cmd = 'grep -in \'%s\' %s | grep -w %d | grep \'}\'' % (';', input_file, end_line) # function definition ends with ;}
				print cmd
				ret = commands.getstatusoutput(cmd)
				if ret[0] != 0:
					print ret
					continue
			
		#print func_name, start_line, end_line
			result_list.append([input_file, func_name, start_line, end_line, end_line - start_line + 1])
		else:
			pass #print 'not'
		if DEBUG:
			print '\n\n'

	#print result_list
	#for item in result_list:
	#	 print item
	return result_list


def extract_funcs(input_folder, output_folder):
	if os.path.isdir(input_folder):
		file_list = os.listdir(input_folder)
	else:
		#file_list = [input_folder]
		file_name = input_folder.split('/')[-1].strip()
		if not correct_file_types(file_name):
			return
	# TODO:
		if SMALL_FUNC: 
			extract_func_from_file(input_folder, file_name, output_folder)
	delete_funcs_from_file(input_folder, file_name, output_folder)
		print 'Extract funcs is done\n'
		return

	if not os.path.exists(output_folder):
		os.system("mkdir %s" %(output_folder))

	#print file_list
	index = 0
	for file_name in file_list:
		file_folder = os.path.join(input_folder, file_name)
		if os.path.isdir(file_folder):
			for subdir, _, file_list in os.walk(file_folder):
				for file_one in file_list:
					file_path = os.path.join(subdir, file_one)
					if not correct_file_types(file_one):
						continue
					#TODO:
					if SMALL_FUNC:
						extract_func_from_file(file_path, file_one, output_folder) # File_One
					delete_funcs_from_file(file_path, file_one, output_folder) # File_One
	else:
			if not correct_file_types(file_name):
				continue
		#TODO:
			if SMALL_FUNC:
				extract_func_from_file(file_folder, file_name, output_folder)
		delete_funcs_from_file(file_folder, file_name, output_folder)
		
	print("Extract funcs is done\n" )


# Just for test
def extract_ret_cfg(ret_dir):
	include_dir = "/home/cuilei/test_codes/openssl/openssl-0.9.7/openssl-0.9.7"
	file_list = os.listdir(ret_dir)
	header_1 = os.path.join(include_dir, 'include')
	header_2 = os.path.join(include_dir, 'apps')
	for s_file in file_list:
		file_path = os.path.join(ret_dir, s_file)
		tmp_file_path = os.path.join('/tmp/ret', s_file+'tmp')
		cmd	 = "clang_old  --analyze -Xanalyzer -analyzer-checker=debug.DumpCFG	 %s	 -I %s -I %s  -I %s &> %s " % (file_path, include_dir, header_1, header_2, tmp_file_path)
		#print cmd
		safe_exec(cmd)


if __name__ == '__main__':
#	 print len(sys.argv)
	if len(sys.argv) != 4:
		print "extract_func.py <input_folder> <output_folder> <header_folder>\n"
		exit(-1)

	global input_foler
	global header_directory
	input_folder = sys.argv[1]
	header_directory = sys.argv[3]
	extract_funcs(sys.argv[1], sys.argv[2])

	#extract_ret_cfg(sys.argv[1])
