#!/bin/python

# =================================================================================
# Copyright 2020 IIE, CAS
#
# This file analyzes the ast expression for selecting 'important' ast features
#
# Author: Lei Cui
# Contact: cuilei@iie.ac.cn
# =================================================================================

import sys
import re
import csv
import copy
import commands
import time
import operator

from search_include import handle_one_file

re_ansi = re.compile(r'\x1b[^m]*m')
file_types = ['.c', '.cpp']

input_folder = ''
global features
global header_directory

def load_ast_features(feature_file):
	feature_list = []
	with open(feature_file, 'r') as fd:
		line = fd.readline()
		items = line.split(',')
		for item in items:
			tmp_items = item.strip().split('.')[1].split('_')
			key="".join(tmp_items)
			feature_list.append(key)
#	 print feature_list
	return feature_list


def safe_exec(cmd):
	try:
		os.system(cmd)
		#commands.getstatusoutput(cmd)
	except Exception, err:
		return 0

def correct_file_types(file_name):
	ret = os.path.splitext(file_name)
	if len(ret) == 0:
		return False
	if ret[1] not in file_types:
		return False
	return True


def sum_dict(*objs):
	_keys = set(sum([obj.keys() for obj in objs],[]))
	_total = {}
	for _key in _keys:
		_total[_key] = sum([obj.get(_key,0) for obj in objs])
	return _total


def stat_feature(temp_file):
	global features
	feature_dict = {}
	for key in features: 
		cmd = "cat %s | grep -i %s | wc -l " % (temp_file, key)
		ret = commands.getstatusoutput(cmd) 
		value = int(ret[1])	 
		#print key, value
		feature_dict[key] = value  
	return feature_dict 


def get_ast(input_file, temp_file):
	global input_folder
	global header_directory
	#header_folder = os.path.join(input_folder, 'include')
	DEBUG = 0
	cmd = ''
	if os.path.exists(temp_file):
		os.remove(temp_file)

	ret = handle_one_file(input_file, temp_file, header_directory)

	if not os.path.exists(temp_file):
		print 'Generate results fail'
		return {}
	else:
		return stat_feature(temp_file)

def show(feature_dict):
	print '---------------'
	for key, value in feature_dict.items():
		if value > 0:
			print key,value

def stat_ast_features(input_folder, output_folder):
	if os.path.isdir(input_folder):
		file_list = os.listdir(input_folder)
	else:
		#file_list = [input_folder]
		file_name = input_folder.split('/')[-1].strip()
		if not correct_file_types(file_name):
			return

		print 'Extract funcs is done\n'
		return

	if not os.path.exists(output_folder):
		os.system("mkdir %s" %(output_folder))

	feature_dict = {}

	index = 0
	for file_name in file_list:
		file_folder = os.path.join(input_folder, file_name)
		if os.path.isdir(file_folder):
			for subdir, _, file_list in os.walk(file_folder):
				for file_one in file_list:
					file_path = os.path.join(subdir, file_one)
					if not correct_file_types(file_one):
						continue
					file_dict = get_ast(file_path, '/tmp/tmp.file')
					#print file_dict
					if feature_dict == {}:
						feature_dict.update(file_dict)
					else: 
						feature_dict = sum_dict(feature_dict, file_dict)
						show(feature_dict)
		else:
			if not correct_file_types(file_name):
				continue
			file_dict = get_ast(file_folder, '/tmp/tmp.file')
			#print file_dict
			if feature_dict == {}:
				feature_dict.update(file_dict)
			else: 
				feature_dict = sum_dict(feature_dict, file_dict)
		#TODO:
		
	print("Extract funcs is done\n" )
	#print feature_dict
	sorted_dict = sorted(feature_dict.items(), key=operator.itemgetter(1))
	print sorted_dict


if __name__ == '__main__':
	if len(sys.argv) != 4:
		print "extract_func.py <input_folder> <output_folder> <header_folder>\n"
		exit(-1)

	global input_foler
	global features
	global header_directory
	features = load_ast_features('./ast_feature_list')
	input_folder = sys.argv[1]
	header_directory = sys.argv[3]
	stat_ast_features(sys.argv[1], sys.argv[2])
	
