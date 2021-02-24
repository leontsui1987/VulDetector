#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__	 import division
import os
import sys
import re
#import clang.cindex
#import asciitree
from ctypes import *
import collections
#import clang.enumerations
#from clang.cindex import Config
#from clang.cindex import TypeKind
#from clang.cindex import CursorKind
import time
import math
import random
import copy

import commands
import networkx as nx
from slicing import *
#from networkx.drawing.nx_pydot import to_pydot

sys.path.append('../')
sys.path.append('../SenLocate')
import config
from config import *

def cal_line_cnt(file_path):
	with open(file_path, 'r') as fd: 
		lines = fd.readlines()
		print len(lines)
		return len(lines)


def exe_search_cmd(cmd):
	ret = commands.getstatusoutput(cmd) 
	if ret[0] == 0: 
		file_name = ret[1]
	else: 
		file_name = 0
	return file_name 


def find_graph_func_file(graph_dir, func_dir):
# Find the function that exist both in graph_dir and func_dir
	graph_func_dict = {}
	files = os.listdir(graph_dir)
	#files = files[]
	for s_file in files: #only about 2/3 of files can be converted into graphs
		items = s_file.split('#')
		file_name, func_name = items[0], items[1]
		combine_func_name = file_name + '#small#' + func_name.lower() + '#'
		cmd = 'ls %s | grep %s ' % (func_dir, combine_func_name) 
		found_func_file = exe_search_cmd(cmd) 
		print combine_func_name, found_func_file
		if found_func_file == 0: continue 
		else: graph_func_dict[s_file] = found_func_file 
	print graph_func_dict
	print len(graph_func_dict.keys())

	# Execute only once
	#graph_fd = open("/home/cuilei/code_sim/VulDetector/Data/outputs/openssl/graph_func_dict_1.0.2", 'w')
	#graph_fd.write(repr(graph_func_dict)) 
	#graph_fd.close() 
	return graph_func_dict


def count_func_lines_words_cnt(func_file):
	cmd = 'cat %s | wc -l' % func_file
	line_cnt = exe_search_cmd(cmd)
	cmd = 'cat %s | wc -w' % func_file
	word_cnt = exe_search_cmd(cmd)
	return line_cnt, word_cnt


def stat_graph_func_cnt():
# Get graph node count,	 line count, and identifier count of a function
	graph_dir = "/home/cuilei/dataset/code_sim/openssl/graphs/openssl-1.0.2"
	func_dir =	"/home/cuilei/dataset/code_sim/openssl/small_funcs/openssl-1.0.2/"

	# Binutils-2.29
	graph_dir = "/home/cuilei/dataset/code_sim/binutils/graph/binutils-2.29"
	func_dir =	"/home/cuilei/dataset/code_sim/binutils/small_funcs/binutils-2.29"

	# Qemu-1.7.1
	graph_dir = "/home/cuilei/dataset/code_sim/qemu/graph/qemu-1.7.1"
	func_dir =	"/home/cuilei/dataset/code_sim/qemu/small_funcs/qemu-1.7.1"
	graph_func_dict = find_graph_func_file(graph_dir, func_dir) 
	#return 

	files = graph_func_dict.keys()
	random.shuffle(files)
	graph_sizes = []
	line_sizes = []
	graph_cnt = 0
	gs_fd = open('/tmp/graphsize_qemu-1.7.1.log', 'w')
	start_t = time.time()
	for s_file in files: #only about 2/3 of files can be converted into graphs
		s_file_path = os.path.join(graph_dir, s_file)
		print s_file_path, '***********'

		try:
			ret = code2graph(s_file_path, 'no') # Get assosicated cfg_code_file of dumpCFG file
			if ret == None or len(ret) == 0 or ret[0] == None:
				continue
			print "=================== ", s_file, len(ret[0].nodes()), graph_cnt
		except Exception, err:
			print "Code2graph error : %s %s" % (s_file, str(err) )
			ret = [None] 

		if ret[0] == None:
			continue #print s_file 
		else:
			graph_cnt += 1 
			graph_sizes.append(len(ret[0].nodes()))
			func_file_path = os.path.join(func_dir, graph_func_dict[s_file])
			line_cnt, word_cnt = count_func_lines_words_cnt(func_file_path)
			gs_fd.write('%s, %s, %s, %s \n' %(s_file, len(ret[0].nodes()), line_cnt, word_cnt))
	#line_sizes.sort()
	#print len(line_sizes), line_sizes
	print graph_cnt
	graph_sizes.sort()
	print graph_sizes
	gs_fd.close()
	print 'Cost time ',	 time.time() - start_t


def load_testing_files():
	tested_files = {} 
	file_path = "/home/cuilei/code_sim/VulDetector/Data/outputs/openssl/test_garph_size_depth.txt" 
	file_path = "/home/cuilei/code_sim/VulDetector/Data/outputs/openssl/more_graphsize.log" 
	file_path = "/home/cuilei/code_sim/VulDetector/Data/outputs/openssl/manually_labelled_graphsize.txt" 
	fd = open(file_path, 'r') 
	lines = fd.readlines() 
	for line in lines:
		items = line.split()
		#tested_files[items[0].strip()] = [int(items[1]), int(items[2])] # items[1] denotes graph size, items[2] denotes line_count
		tested_files[items[0].strip()] = [int(items[1]), int(items[2])] # items[1] denotes graph size, items[2] denotes root_line

	return tested_files 


def stat_graph_cnt_depth(depth=0):
# Get graph node count when different depth is set 
	graph_dir = "/home/cuilei/dataset/code_sim/openssl/graphs/openssl-1.0.2"
	func_dir =	"/home/cuilei/dataset/code_sim/openssl/small_funcs/openssl-1.0.2/"

	# Load the saved dict file 
	graph_func_dict_path = "/home/cuilei/code_sim/VulDetector/Data/outputs/openssl/graph_func_dict_1.0.2" 
	graph_fd = open(graph_func_dict_path, 'r') 
	dict_content = graph_fd.read() 
	graph_func_dict = eval(dict_content) 

	# We only select a smaller set of files for testing
	tested_files = load_testing_files() 
	files = tested_files.keys()
	graph_sizes = []
	line_sizes = []
	graph_cnt = 0
	gs_fd = open('/tmp/more_graphsize%d.log' % depth, 'w+')
	start_t = time.time()
	for s_file in files: #only about 2/3 of files can be converted into graphs
		s_file_path = os.path.join(graph_dir, s_file)

		try:
			func_code_path = os.path.join(func_dir, graph_func_dict[s_file])
			#os.system("cp %s %s" % (func_code_path, "/tmp/graph_filetest")) # For manually label the sensitive line 
			#continue  
			root_line = str(int(tested_files[s_file][1])) # If root_line is not specified, simply select the middle line
			#print	func_code_path, root_line
			ret = code2graph(s_file_path, func_code_path, root_line)
			if ret == None or len(ret) == 0 or ret[0] == None:
				print "Graph is NONE *******************"
				continue
			print "=========== ", s_file, tested_files[s_file][0], len(ret[0].nodes()) #, graph_cnt
			#print len(ret[0].nodes()) #, graph_cnt
		except Exception, err:
			print "Code2graph error : %s %s" % (s_file, str(err) )
			ret = [None] 

		if ret[0] == None:
			continue #print s_file 
		else:
			graph_cnt += 1 
			graph_sizes.append(len(ret[0].nodes()))
			gs_fd.write('%s, %s \n' %(s_file, len(ret[0].nodes())))
	#print len(line_sizes), line_sizes
	print graph_sizes
	print graph_cnt
	#graph_sizes.sort()
	#print graph_sizes
	gs_fd.close()


def stat_graph_cnt_varying_depth():
	depth = [3,4,5,6,8,10,12,14,16,18,20]
	depth = [15]
	for i in depth: 
		config.GRAPH_PRED_DEPTH = config.GRAPH_SUCC_DEPTH=i 
		config.WEIGHT_PRED_RATIO = config.WEIGHT_SUCC_RATIO = 0.8 
		config.update_weight(i, i, 0.8, 0.8)  

		print i
		stat_graph_cnt_depth(i)



def old_stat_graph_info(): 
	# arg1: directory or a dumpCFG log file
	# arg2: directory or a source code file	 OR 'no'
	# arg3: vulnerable line_no OR 'no'


	#graph_func_dict = find_graph_func_file("/home/cuilei/dataset/code_sim/openssl/graphs/openssl-1.0.2", "/home/cuilei/dataset/code_sim/openssl/small_funcs/openssl-1.0.2/") 

	if os.path.isfile(sys.argv[1]): # a single file
		if sys.argv[2]	== 'no':
			ret = code2graph(sys.argv[1],sys.argv[2])
		else:
			ret = code2graph(sys.argv[1],sys.argv[2], sys.argv[3])

		if ret == None:
			print 'None' 
			exit(0)
		print "Graph size ", len(ret[0].nodes())
		#dump_graph(ret[0]) 
		exit(0)

	directory = sys.argv[1] # a directory of files
	files = os.listdir(directory)
	random.shuffle(files)
	graph_sizes = []
	line_sizes = []
	graph_cnt = 0
	gs_fd = open('/tmp/graphsize_qemu-1.7.1.log', 'w')
	start_t = time.time()
	for s_file in files: #only about 2/3 of files can be converted into graphs
		s_file_path = os.path.join(directory, s_file)
		#if s_file.find('small')<0:
		#	print 'find small ', s_file
		#	continue
		#line_cnt = cal_line_cnt(s_file_path)
		#line_sizes.append(line_cnt)
		#continue

		try:
			ret = code2graph(s_file_path, sys.argv[2]) # Get assosicated cfg_code_file of dumpCFG file
			if ret == None or len(ret) == 0 or ret[0] == None:
				continue
			print "======== ", s_file, len(ret[0].nodes()), graph_cnt
		except Exception, err:
			print "Code2graph error : %s %s" % (s_file, str(err) )
			ret = [None] 

		if ret[0] == None:
			continue #print s_file 
		else:
			graph_cnt += 1 
			graph_sizes.append(len(ret[0].nodes()))
			gs_fd.write('%s \n' %(len(ret[0].nodes())))
	#line_sizes.sort()
	#print len(line_sizes), line_sizes
	print graph_cnt
	print graph_sizes
	graph_sizes.sort()
	print graph_sizes

	#for s in line_sizes: gs_fd.write('%s \n' % str(s))
	gs_fd.close()
	print 'Cost time ',	 time.time() - start_t


if __name__=="__main__":
	if len(sys.argv) != 4:
		print "python code2graph.py <func_cfg_desc> <func_code> <sensitive_line_no>"
		exit(-1)
	code2graph(sys.argv[1], sys.argv[2], sys.argv[3])
	#stat_graph_func_cnt() # NOTE: use this is better
	#stat_graph_cnt_varying_depth()
	#old_stat_graph_info()

