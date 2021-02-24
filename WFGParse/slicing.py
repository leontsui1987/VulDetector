#!/usr/bin/python
# -*- coding: UTF-8 -*-
# =================================================================================
# Copyright 2020 IIE, CAS
#
# This file slices sourcecode of a function from a root line
# Input: sourcecode, root line
# Output: lines of sliced sourecode, as well as line_weight
#
# Author: Lei Cui, Yang Jiao
# Contact: cuilei@iie.ac.cn
# =================================================================================

from __future__ import division
import re
import os
import sys
import time
import numpy
import commands

import collections
sys.path.append('../')
import config
from config import *


# Old
Pa_id = re.compile(r'identifier \'([a-z|_]+\d*)\'', re.I)
Pa_line = re.compile(r'\:([0-9]+)\:', re.I)
Pa_token = re.compile(r'([a-z|_]+) \'(.*)\'',re.I)

#Pa_id = re.compile(r'identifier \'[a-z|_]+\d*\'', re.I)
#Pa_line = re.compile(r'\:([0-9]+)\:', re.I)
#Pa_token = re.compile(r'([a-z|_]+) \'(.*)\'',re.I)

DEBUG_PRINT = False

# The first identifier is func_name
def to_find_fname(dwmpline):
	for line in dwmpline:
		m0=Pa_id.search(line)
		m1=Pa_line.search(line)
		if m0 and m1:
			return int(m1.group(1))


def find_id_lines(dwmpline,idlist):
	# Find lines containind identifier
	lines = []
	line_ids = {}
	if True:
		i=0
		for line in dwmpline:
			line = line.strip()
			if line == '': continue
			m0=Pa_line.search(line)
			#if m0 and m0.group(1).isdigit(): # is digit
			if m0: 
				line_no =int( m0.group(1) )# Get line number
				m1=Pa_id.search(line) # Get id
				#print 1.group(1), idlist
				#if m1 and m1.group(1) != "NULL" and m1.group(1) not in idlist:
				if m1 and m1.group(1) != "NULL":
					m2=re.search(r'[a-z]+',m1.group(1))
					if m2:
						m3=Pa_token.search(dwmpline[i+1])
						if m3 and m3.group(1) != "l_paren":
							m4=Pa_token.search(dwmpline[i-1])
							if m4 and m4.group(1)!="arrow" and m4.group(1)!="period":
								idlist.append(m1.group(1))
								lines.append(line_no) 
								if line_no not in line_ids.keys():  line_ids[line_no] = []
								line_ids[line_no].append(m1.group(1))
								#print line
							else:
								if DEBUG_PRINT: print 'm4 is None'
						else:
							if DEBUG_PRINT: print 'm3 is None'
					else:
						if DEBUG_PRINT: print 'm2 is None'
				else: 
					if DEBUG_PRINT: print 'm1 is None'
			else: 
				if DEBUG_PRINT: print 'm0 is None'
				#print 'LINE:  ', line
			i+=1
	#print len(lines)
	#print len(idlist)
	#idlist = list(set(idlist))
	#lines  = list(set(lines))
	#print len(idlist)
	#print len(lines)
	#lines.sort()
	#print lines
	for key in line_ids.keys():
		line_ids[key] = list(set(line_ids[key]))
	#print line_ids
	return line_ids


def new_to_find_id(argv, line_id_dict, idlist):
	new_idlist = []
	for arg in argv:
		if arg not in line_id_dict.keys(): continue
		for id in line_id_dict[arg]:
			if id not in idlist: 
				new_idlist.append(id)
	new_idlist = list(set(new_idlist))
	idlist.extend(new_idlist)
	idlist = list(set(idlist))
	return new_idlist

def to_find_line(dwmpline,idefline,specialline,idlist):
	nollist=[]
	i=0
	while i<len(dwmpline):
		line = dwmpline[i]
		#print line
		m0=Pa_line.search(line)
		if m0:num=m0.group(1)
		num=int(num)
		m1=Pa_token.match(line)
		if m1 and num not in idefline and  num not in specialline:
			if m1.group(1) == 'identifier':
				for id in idlist:
						if m1.group(2) == id:
							m4=Pa_token.match(dwmpline[i-1])
							if m4 :
								if m4.group(1)=="identifier" and num not in idefline:
									idefline.append(num)
								elif m4.group(1)!="arrow" and m4.group(1)!="period":
									nollist.append(num)
			elif m1.group(1) == 'for' or m1.group(1) == 'while' or m1.group(1) == 'if':
				templ=[]
				# while Pa_token.search(dwmpline[i+1]).group(1) != "r_paren":
				while Pa_line.search(dwmpline[i+1]).group(1) == str(num):
					i=i+1
					m2=Pa_id.search(dwmpline[i])
					m3=Pa_token.match(dwmpline[i-1])
					if m2 and m3 and m3.group(1)!="arrow" and m3.group(1)!="period":
						templ.append(m2.group(1))
				for x in templ:
					for y in idlist:
						if x == y:
							nollist.append(num)
							break
			elif m1.group(1) == 'do' and Pa_token.search(dwmpline[i+1]).group(1) == "l_brace":
				specialline.append(num)
		i+=1
	nollist = list(set(nollist))
	#print nollist
	return nollist

def to_find_special_line(srcline,specialline,idefline,idlist,numlist):
	i=0
	while i<len(srcline):
		line = srcline[i]
		m0=re.search(r'[{}]',line)
		m1=re.search(r'(,([\w= *])+)+;',line)
		m5=re.search(r'else[^{]*$',line)
		m6=re.match(r'#.*',line)
		if i+1 not in specialline:
			if m0:
				specialline.append(i+1)
			elif m1:
				for id in idlist:
					m2=re.search(re.escape(id)+r'[,| |=]',line)
					m3=re.search(re.escape(id)+r'[=| =]([a-zA-Z_]+\d*)+',line)
					m4=re.search(r'([a-zA-Z_]+\d*)+(\s)*=(\s)*'+re.escape(id),line)
					if m2 and i+1 not in idefline:
						idefline.append(i+1)
					if m3 and m3.group(1) != "NULL" and m3.group(1) not in idlist:
						idlist.append(m3.group(1))
					if m4 and m4.group(1) != "NULL" and m4.group(1) not in idlist:
						idlist.append(m4.group(1))
			elif m5:
				if (i+2 in numlist) and (i+1 not in specialline):
					specialline.append(i+1)
			elif m6:
				flag1=False
				if (not flag1) and re.match(r'^(\s)*#(\s)*((include)|(undef)|(define)|(ifdef)|(if)|(ifndef)|(elif)|(endif))',line):
					specialline.append(i+1)
					if re.match(r'^.*\\$',line):
						flag1=True
					while flag1:
						i=i+1
						line = srcline[i]
						if re.match(r'^.*[\\]$',line):
							specialline.append(i+1)
						else:
							specialline.append(i+1)
							flag1=False
		i+=1
	return 0



# start line is denoted in filename
def get_start_line(src_file):
    start_line = int(src_file[:-2].split("#")[-1])
    return start_line

def slicing(src_file, root_line):
# Slicing a source code file, return the lines to be deleted

	if root_line <= 2:
		return {}

	#root_line = root_line - 1 # NOTE: line_content starts from 0
    # Step1: Produce the tokendump file
	config.WEIGHT_PRED_RATIO, config.WEIGHT_SUCC_RATIO, config.GRAPH_PRED_DEPTH, config.GRAPH_SUCC_DEPTH =  config.load_weight() 
	tmp_dump_file =  "%s_tokendump.dump" % src_file
	cmd = "clang -cc1 -dump-tokens %s 2> %s" % (src_file, tmp_dump_file )
	ret = commands.getstatusoutput(cmd)
	#print cmd, ret
	if not os.path.exists(tmp_dump_file) : #ret[0] != 0:
		print "Cannot get the tokendump file" 
	dwmpf=open(tmp_dump_file,'r')

	dwmpline=dwmpf.readlines()

    # Step2: Slicing
	srcf=open(src_file,'r')
	srcline=srcf.readlines()

	dwmpf.close()
	srcf.close()
	os.remove(tmp_dump_file)


	idlist=[]
	numlist=[]
	specialline=[]
	idefline=[]

	tmp_idlist=[]
        
	if USE_WEIGHT:
		line_weight = collections.OrderedDict()
		init_weight = 1

	startline=to_find_fname(dwmpline)
	specialline.append(startline)

	line_id_dict = find_id_lines(dwmpline, tmp_idlist)
    # find lines containing the identifiers in root_line
	new_idlist = new_to_find_id([root_line], line_id_dict, idlist)

	if USE_WEIGHT:
		line_weight[root_line] = init_weight
		cur_weight = init_weight
		cur_pred_weight = init_weight
		cur_succ_weight = init_weight

	oldlen = 0
	newlen = 0

	if DEBUG: start_t = time.time()
	while new_idlist: # and newlen == 0 or newlen > oldlen:
		#to_find_special_line(srcline,specialline,idefline,idlist,numlist)
		temp = to_find_line(dwmpline,idefline,specialline,new_idlist)
		numlist = list(set(numlist).union(set(temp)))
		oldlen = newlen

		new_idlist = new_to_find_id(numlist, line_id_dict, idlist)
		numlist.sort()
		newlen = len(idlist)

        # deal with lines in num_list
		if USE_WEIGHT:
			#print '------------- ', config.WEIGHT_PRED_RATIO
			#print '------------- ', config.WEIGHT_SUCC_RATIO
			cur_pred_weight = cur_pred_weight*config.WEIGHT_PRED_RATIO
			cur_succ_weight = cur_succ_weight*config.WEIGHT_SUCC_RATIO
			for num in numlist:
				if num not in line_weight.keys():
					if num < root_line: line_weight[num] = cur_pred_weight
					else: line_weight[num] = cur_succ_weight
	if DEBUG: end_t = time.time()
	#if DEBUG: print 'slicing, while find line time, ', end_t - start_t

	#to_find_special_line(srcline,specialline,idefline,idlist,numlist)

	#print 'numlist, ', len(numlist) #, numlist
	#print 'speciallist, ', len(specialline) #, specialline
	#print 'id, ', len(idefline) #, idefline

	numlist = list(set(numlist).union(set(idefline)))
	numlist.sort()
	#print len(numlist) , numlist

    # deal with lines in idefline
	if USE_WEIGHT:
		for id_line in idefline:
			if id_line not in line_weight.keys():
				line_weight[id_line] = cur_weight

		#print line_weight

	#print srcline[root_line]
	#for index in numlist:
	#    print index, srcline[index-1].strip()

    # Step 3: Get root line
	start_line = get_start_line(src_file) #int(src_file[:-2].split("#")[-1])
	if DEBUG_PRINT:
	    print start_line
	ret_list = [start_line+num-1 for num in numlist]
	if DEBUG_PRINT:
	    print ret_list

	new_line_weight = collections.OrderedDict()
	for key in range(len(srcline)):
		new_line_weight[start_line+key] = 0 # initial

	for key in numlist:
		if USE_WEIGHT:
			#print line_weight[key]
			new_line_weight[start_line+key-1] = line_weight[key] # Varying weight
		else:
			new_line_weight[start_line+key-1] = 1 # Weight of lines are identical

	return new_line_weight
	#return ret_list

if __name__ == '__main__':
    # arg1: source code file
    # arg2: root line of slicing
	if len(sys.argv) != 3:
		print "python slicing.py  <code_file>  <root_line>"
		exit(-1)

	#global DEBUG_PRINT
	DEBUG_PRINT = False
	#root_line = [ int(sys.argv[2]) ]
	root_line = int( sys.argv[2] )
	#print root_line
	ret = slicing(sys.argv[1], root_line)
	# key denotes line_no, value detnotes line weight
	print "line_no : line_weight "
	for key, value in ret.items():
		print "%s : \t%s " % (key, value)
	#print ret.keys()
