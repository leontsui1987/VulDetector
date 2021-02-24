#!/bin/python

# =================================================================================
# Copyright 2020 IIE, CAS
#
# This file extract all the CFGs in a log produced from scan_build dumpCFG
# Input: the log file
# Output: A directory of CFGs, named as file.c#func_name
#
# Author: Lei Cui
# Contact: cuilei@iie.ac.cn
# =================================================================================


import os
import sys
import re
import copy
import commands

re_ansi = re.compile(r'\x1b[^m]*m')
file_types = ['.c', '.cpp']

DEBUG = 1

def safe_exec(cmd):
	try:
		os.system(cmd)
	except Exception, err:
		return 0

def safe_exec_ret(cmd):
	try:
		ret = commands.getstatusoutput(cmd)
	except Exception, err:
		return None
	if ret[0] == 0:
		return ret[1]

# Performance is too bad!!
def handle_one_graph(log_file, start_line, end_line, out_dir):
# Write lines into one graph
	# get func name
	func_str = 'sed -n \'%dp\' %s' % (start_line, log_file)
	func_str = 'cat %s | head -n %d | tail -n +%d' % (log_file, start_line, start_line)
	ret = safe_exec_ret(func_str)
	func_name = re.findall(r"([\w]*\()", ret) 
	print func_name
	if func_name:
		func_name = func_name[0].split('(')[0].strip()
		print func_name

	# file name
	file_str = 'sed -n \'%dp\' %s' % (start_line+5, log_file)
	file_str = 'cat %s | head -n %d | tail -n +%d' % (log_file, start_line+5, start_line+5)
	ret = safe_exec_ret(file_str)
	#file_name = re.findall(r"([\w\/]*\.[c|h]\:[0-9]*)", ret)	 
	file_name = re.findall(r"([\w\/]*\.[c]\:[0-9]*)", ret)	   # NOTE: Only care about **.c file
	print file_name
	if file_name:
		file_name = file_name[0].split(":")[0]
		print file_name
		file_name = "_".join(file_name.split('/'))
		if file_name[0] == "_":
			file_name = file_name[1:]
		print file_name
	else:
		return

	new_func_file = "%s#%s" % (file_name, func_name)
	# Write graph into the file
	cmd = 'sed -n -e \'%d,%dp\' %s > %s' % (start_line, end_line, log_file, os.path.join(out_dir, new_func_file) )
	cmd = 'cat %s | head -n %d | tail -n +%d  > %s' % (log_file, end_line, start_line, os.path.join(out_dir, new_func_file) )
	safe_exec_ret(cmd)



def traverse_log(log_file, output_dir):
	entry_lines = safe_exec_ret("grep -n \'%s\' %s " % ( '(ENTRY)\]', log_file) )	 
	exit_lines = safe_exec_ret("grep -n \'%s\' %s " % ( '\[B0 (EXIT)\]' , log_file) )	 
	
	entry_line_items = entry_lines.split('\n')
	exit_line_items = exit_lines.split('\n')
	#print entry_line_items[0]
	print len(entry_line_items)
	print len(exit_line_items)
	assert len(entry_line_items) == len(exit_line_items), "Count of ENTRY and EXIT should be the same"
	fd = open(log_file, 'r')
	index = 0
	last_left = None
	shift = 0
	line_cnt = 1
	invalid_line_cnt = 0  # Warning count
	invalid_line_cnt2 = 0 # Wrong funcname
	invalid_line_cnt3 = 0 # Count of functions in header files
	for index in range(len(entry_line_items)):
		start = int(entry_line_items[index].split(':')[0])
		end = int(exit_line_items[index].split(':')[0])
		start = start -1 # shift to function name string
		end = end + 1 # shift to the end of graph, NOTE the end here is not accurate, so shift it later
		# NOTE: old method, poor performance
		#handle_one_graph(log_file, start, end, output_dir)

		while line_cnt > start:
			print ">>>>>>>>>>>" , line_cnt, start
			exit(0) #break
			break
		while line_cnt < start:
			for i in range(start-line_cnt):
				fd.readline() # ignore some warnings
			line_cnt = start
			invalid_line_cnt += 1 # warning count

		# Handle a block
		lines = []
		for i in range(end-start):
			line = fd.readline() 
			lines.append(line)
		line_cnt += end-start
		if line_cnt != end: print '%d %d not equal' % (line_cnt, end)

		# more lines at tge EXIT node
		while True:
			line = fd.readline() 
			line_cnt += 1
			if line.strip() != "":	
				#print(line)
				lines.append(line)
			else: # end here
				break
		
		# get func name
		func_str = lines[0] # the first line
		func_name = re.findall(r"([\w]*\()", func_str) 
		if func_name:
			func_name = func_name[0].split('(')[0].strip()
		else:
			#print 'no func'
			invalid_line_cnt2 += 1

		# Try to get the file name
		line_index = 5 
		file_name = None 
		while line_index < len(lines): 
			file_str = lines[line_index] 
			file_name = re.findall(r"([\w\/]*\.[c]\:[0-9]*)", file_str)		# NOTE: only handle **.c file, so that a large number functions are ignored!!
			if file_name:
				file_name = file_name[0].split(":")[0]
				file_name = "_".join(file_name.split('/'))
				if file_name[0] == '_':
					file_name = file_name[1:]
				break
			line_index += 1

		if not file_name:
			invalid_line_cnt3 += 1
			#print 'no file' 
			continue

		#file_name = re.findall(r"([\w\/]*\.[c|h]\:[0-9]*)", file_str)	   # **.c or **.h file
		#NOTE: CFG extraction fails for a few blocks.

		new_func_file = "%s#%s" % (file_name, func_name)
		new_func_file = os.path.join( output_dir, new_func_file)
		# Write graph into the file
		new_fd = open(new_func_file, 'w')
		for line in lines:
			new_fd.write(line)
		new_fd.close()
	fd.close()

	print invalid_line_cnt, invalid_line_cnt2, invalid_line_cnt3

if __name__ == '__main__':

	if len(sys.argv) != 3:
		print "extract_cfg_desc.py <graph_log>	 <output_folder>\n"
		exit(-1)

	print sys.argv[1]
	print sys.argv[2]
	traverse_log(sys.argv[1], sys.argv[2])
