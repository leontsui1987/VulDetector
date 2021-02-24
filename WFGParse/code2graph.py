#!/usr/bin/python
# -*- coding: UTF-8 -*-
# =================================================================================
# Copyright 2020 IIE, CAS
#
# This file generates WFGs given a raw CFG, sourcecode and sensitive line
# Input: raw CFG, sourecode, sensitive line
# Output: A set of WFGs
#
# Author: Lei Cui
# Contact: cuilei@iie.ac.cn
# =================================================================================

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
#import matplotlib
#matplotlib.use('Agg')
#from matplotlib.pyplot import *
#import matplotlib.pyplot as plt
import networkx as nx
from slicing import *
#from networkx.drawing.nx_pydot import to_pydot

sys.path.append('../')
sys.path.append('../SenLocate')
import config
from config import *

from ast_feature import *
from sensitive_parse import *
from wfg_mngr import *

#libclangPath = '/usr/lib/libclang.so.6.0'
#if Config.loaded==True:
#		pass
#else:
#		Config.set_library_file(libclangPath)


######################################################
# *************build_cfg && slice_cfg*****************
######################################################

def find_bid_by_fixedline(cfg,search_num,cut_blocklist):
	for bid in cfg.nodes():
		#print bid, cfg.node[bid]
		for num in cfg.node[bid]["blines"]:
			if(num==int(search_num)):
				cut_blocklist.append(bid)
				return bid

def find_preds_bid(cfg,pa_bid,cut_blocklist,depth, weight):
	if pa_bid == None: 
		return

	#print 'find pred bid'
	preds=list(cfg.predecessors(pa_bid))
	depth += 1
	if depth >= config.GRAPH_PRED_DEPTH:
		return
	if(preds==[]):
		return
	for bid in preds:
		if(bid>pa_bid) and (bid not in cut_blocklist):
			cut_blocklist.append(bid)
			if USE_WEIGHT:
				if len(cfg.node[bid]['blines']) == 0: cfg.node[bid]['node_weight'] = 0 
				else: cfg.node[bid]['node_weight'] = weight
				weight = weight * config.WEIGHT_PRED_RATIO
			find_preds_bid(cfg, bid, cut_blocklist, depth, weight)


def find_succs_bid(cfg,pa_bid,cut_blocklist, depth, weight):
	if pa_bid == None or pa_bid == 0:
		return

	#print 'find succs bid'
	succs=list(cfg.successors(pa_bid))
	depth += 1
	if depth >= config.GRAPH_SUCC_DEPTH:
		return
	if(succs==[]):
		return
	for bid in succs:
		if(bid<pa_bid) and (bid not in cut_blocklist):
			cut_blocklist.append(bid)
			if USE_WEIGHT:
				if len(cfg.node[bid]['blines']) == 0: cfg.node[bid]['node_weight'] = 0 
				else: cfg.node[bid]['node_weight'] = weight # set node weight
				weight = weight * config.WEIGHT_SUCC_RATIO
			find_succs_bid(cfg, bid, cut_blocklist, depth, weight)



def build_CFG(cfg_data, ast_feature, reserved_lines):
	dwmpline0=cfg_data
	#print cfg_data
	nodelist=[]
	edgelist=[]
	CFG=nx.DiGraph()
	Pa_Entry = re.compile(r'(\(ENTRY\))', re.I)
	Pa_Bid = re.compile(r'\[B([0-9]+)[^.]*\]', re.I)
	Pa_NodeBid = re.compile(r'B([0-9]+)',re.I)
	Pa_Succs = re.compile(r'Succs \([0-9]+\): ((B[0-9]+[ ]*)+)',re.I)
	Pa_T = re.compile(r'^T\:',re.I)
	Pa_line_cfg = re.compile(r'\.c:([0-9]+):', re.I) # *.c:line_no
	i=0

	while i<len(dwmpline0):
		line = dwmpline0[i]
		m0=Pa_Entry.search(line)
		if(m0):
			break
		i+=1
		
	#print len(dwmpline0)
	while i<len(dwmpline0):
		line = dwmpline0[i]
		m0 = None
		m_id = None
		m_succ = None
		m_line = None
		#print 'line ', line
		m0 = Pa_Bid.search(line)
		if m0:
			cur_bid=int(m0.group(1))
			nodelist.append(cur_bid)
			bline=[]
			bv=[]
			ast_feature = [0]*len(all_kinds)
			while i<len(dwmpline0)-1:
				i += 1
				line=dwmpline0[i]
				m_id=Pa_Bid.search(line);
				m_succ=Pa_Succs.search(line);
				m_line=Pa_line_cfg.search(line);
				m_T=Pa_T.search(line);
				#if(cur_bid == 1):
				#	print line

				if(m_id):
					break
				elif(m_succ):
					temp=m_succ.group(1).split()
					for next_bid in temp:
						next_bid=int(Pa_NodeBid.search(next_bid).group(1))
						edgelist.append([cur_bid,next_bid])
				elif(m_line):
					line_no = int(m_line.group(1))
					#print line_no
					if len(reserved_lines.keys()) > 0 and (line_no not in reserved_lines.keys()):
						#print 'not in reserved lines'
						continue
					if(line_no not in bline):
						bline.append(line_no)
					#if cur_bid == 1: print line
						#print int(m_line.group(1))
				elif(m_T): # look the symbol before T:
					pass
				else:
					continue # NOTE: meanless lines

				# Normal information, extract features
				# NOTE: here we reserve the feature of .h files, may test and remove them later if it works not well
				index = line_feature_index(line) # Assign AST features
				#print line
				if index != -1:
					ast_feature[index] += 1
				else:
					pass

			#i -= 1
			CFG.add_node(cur_bid)
			CFG.node[cur_bid]["blines"]=bline
			#bv=blk_vector_generator(bline,ast_feature)
			bv=ast_feature
			CFG.node[cur_bid]["blk_vector"]=copy.deepcopy(bv)
		if(m_id):
			continue
		i+=1  
	CFG.add_edges_from(edgelist)
	#print CFG.nodes()
	return CFG


######################################################
# *************get graph and subcfg*******************
######################################################
# Assign a graph node with line weight, since a node may 
# contain multiple lines, therefore we use the max weight
# Line weight is calculated when slicing
def set_line_weight(cfg, line_weight_dict):
	nodes = cfg.nodes()
	for node_id in range(len(nodes)):
		node_lines = cfg.node[node_id]['blines'] 
		#print node_id, node_lines 
		weights = [line_weight_dict[line_id] for line_id in node_lines] 
		#print node_id, node_lines,	 weights
		if len(weights) == 0: cfg.node[node_id]['line_weight'] = 0.0
		else: cfg.node[node_id]['line_weight'] = max(weights) 


def get_cfg(src_path, cfg_data, src_file='None', root_line = -1):
	ast_feature=[]
	#get_ast_feature(src_path,ast_feature)

	# Get sliced lines rooted from root_line
	reserved_lines = {}
	if DEBUG: start_t = time.time() 
	if (root_line == -1):
		reserved_lines = {}
	else:
		# Sliced lines need reserved
		reserved_lines = slicing(src_file, root_line) 
	if DEBUG: end_t = time.time() 
	if DEBUG: print 'slicing time, ', end_t - start_t 
	if DEBUG: start_t = time.time() 

	cfg=build_CFG(cfg_data, ast_feature, reserved_lines)

	if DEBUG: end_t = time.time() 
	if DEBUG: print 'build_CFGs, ', end_t - start_t 
	#print reserved_lines

	# Need to set line_weigth for cfg nodes
	#print 'get_cfg, ', root_line
	if root_line != -1 and USE_WEIGHT:
		set_line_weight(cfg, reserved_lines)
	return cfg


def init_node_weight(cfg, val=0.0):
	nodes = cfg.nodes()
	for node_id in range(len(nodes)): 
		cfg.node[node_id]['node_weight'] = val


def get_subcfg(cfg,search_num=-1):
	if(search_num==-1):
		return cfg

	#print 'CFG', cfg.nodes() 
	cut_blocklist=[]
	if True: 
		#print 'Search num, ', search_num
		bid=find_bid_by_fixedline(cfg, search_num, cut_blocklist)
		if not bid:
			debug_print(DEBUG_WARN, 'Bid is None ')
			if USE_WEIGHT: init_node_weight(cfg, 1) # Cannot get subcfg, so use the whole graph, node_weight is 1
			return cfg
	
		init_weight = 1.0
		cur_weight = init_weight 
		if USE_WEIGHT:
			# init node_weight as 0
			init_node_weight(cfg, 0) # Can use subcfg, so node_weight of unrelated nodes is 0
			# Set the root node
			cfg.node[bid]['node_weight'] = cur_weight
			cur_weight = init_weight 

		find_preds_bid(cfg, bid, cut_blocklist, 0, cur_weight*config.WEIGHT_PRED_RATIO)
		find_succs_bid(cfg, bid, cut_blocklist, 0, cur_weight*config.WEIGHT_SUCC_RATIO)
		subCFG=cfg.subgraph(cut_blocklist)
		#print "---------------- ", subCFG.nodes()
	#print "SubCFG ",  subCFG.nodes() 
	return subCFG


def extract_include_dir(src_file):
	# NOTE: need to modify here for directory format change!!
	top = extract_top_dir(src_file)
	upper = os.path.join(top, 'include')
	return upper


def extract_top_dir(src_file):
	return None 
	#upper = os.path.dirname(src_file)
	#print(upper)
	#upper = os.path.dirname(upper)
	#print(upper)
	#return upper
	#version = upper.split('/')[-1]
	#top = os.path.join(upper, version)
	#return top
	

######################################################
#***** Use the DumpCFG ret of scan-build checker *****
######################################################
def cfg_dump(src_file):
	ret_lines = None
	with open(src_file, 'r') as fd:
		lines = fd.readlines()
		lines = lines[1:] # remove the function_name line
		ret_lines = [line.strip() for line in lines]
	return ret_lines 


# May produce small graphs, e.g., B2(ENTRY), B1, B0(EXIT)
# Just remove them directly
def remove_small_graphs(cfg_data):
	#print("==== remove small graphs ====")
	graphs = [] # [node,node_cnt, start_line, end_line]
	#print len(cfg_data) # [node,node_cnt, start_line, end_line]
	for cfg_line_index in range(len(cfg_data)):
		cfg_line = cfg_data[cfg_line_index].strip()
		#print cfg_line
		if cfg_line == "":
			continue
		if cfg_line.find('(ENTRY)') >=0: # start_line
			graph = []
			if len(cfg_line) > 15:	#  [B*** (ENTRY)]
				continue 
			m = re.findall( r"(B[0-9]*)", cfg_line)
			if m == None or m == []: # Function name may contain 'ENTRY'
				print 'm is null'  
				continue 
			node_cnt = int(m[0][1:])
			graph.append(node_cnt) # node_cnt
			graph.append(cfg_line_index) # start_line
			#print cfg_data[cfg_line_index] 
			cfg_line_index += 1
			while True: # search the end_line, e.g., [B0 (EXIT)]
				if cfg_data[cfg_line_index].strip() == "[B0 (EXIT)]":
					end_line = cfg_line_index + 1 # end_line
					#print cfg_data[end_line]
					graph.append(end_line)
					#print 'Find Exit'
					break
				cfg_line_index += 1
				if cfg_line_index >= len(cfg_data): # impossible
					graph.append(cfg_line_index)
					print("Can not find the end_line, should not happen") 
					break
			graphs.append(graph)

	#print(graphs)
	if len(graphs) == 0:
		if DEBUG:
			print "Cannot get graph" 
		return None, None
	if len(graphs) == 1:
		return graphs[0][0], cfg_data[ graphs[0][1] : graphs[0][2] ]

	# Using the method that extracts a graph from log file produced from scan_build,
	# there will be only one graph in a log file
	selected_graph = graphs[0]
	for index in range(1, len(graphs)):
		if graphs[index][0] > selected_graph[0]: # select the graph with maximun node_cnt
			selected_graph = graphs[index] 

	if selected_graph[0] == 2:
		if DEBUG:
			print "Graphs are small" 
		return None, None # graph is too small

	#print selected_graph[0]
	#print cfg_data[selected_graph[1]:selected_graph[2]]
	return selected_graph[0], cfg_data[selected_graph[1]:selected_graph[2]]


######################################################
# *************main function************************** 
######################################################

def draw_graph(cfg, name):
	#print 'draw graph %s' % name 
	#print cfg_node_cnt1, cfg_node_cnt2, node_dis, edge_dis, sim
	#pos = nx.spring_layout(cfg)
	#print dir(nx)
	#nx.draw(cfg)
	#plt.draw()
	#plt.savefig(name)

	print 'HELLO '
	print 'nodes = ', cfg.nodes()
	print 'edges = ', cfg.edges() 
	#p = nx.write_dot(cfg, name) # wrong
	#p.write_jpeg(name) # wrong
	pass


def dump_graph(graph):
	if graph == None:
		print 'graph is none'
		return

	print '------ WFG information ------'
	nodes = graph.nodes() 
	edges = graph.edges() 
	print "EDGES: " ,edges 

	for node in nodes: 
		if 'weight' in graph.node[node].keys(): # full cfg has no weight
			print "NODE:", node, graph.node[node]["blines"], graph.node[node]["blk_vector"], graph.node[node]['weight']
		else:
			print node, graph.node[node]["blines"], graph.node[node]["blk_vector"]


# Generate a WFG given cfg_desc, source code, and line_no
def code2wfg(src_cfg_path, cfg_data, src_code_file, line_no=-1):

	# STEP1: trim unrelated lines, similar to string slicing
	cfg = get_cfg(src_cfg_path, cfg_data, src_code_file, line_no) 

	# STEP2: trim faraway blocks, get a smaller subgraph
	subcfg = get_subcfg(cfg, line_no)
	
	# STEP3: assign weight
	if USE_WEIGHT:
		nodes = subcfg.nodes()
		for node_id in nodes:
			if line_no == -1: # no sensitive line is denoted, weight of nodes are identical
				subcfg.node[node_id]['weight'] = 1 # 
			else:
				subcfg.node[node_id]['weight'] = math.sqrt(subcfg.node[node_id]['line_weight']) * subcfg.node[node_id]['node_weight']
	if DUMP_GRAPH: dump_graph(subcfg)

	commands.getoutput("rm *.plist")

	return subcfg


# Generate a set of WFGs for a function
def code2graph(src_cfg_path, src_code_file, line_no=-1):
	config.WEIGHT_PRED_RATIO, config.WEIGHT_SUCC_RATIO, config.GRAPH_PRED_DEPTH, config.GRAPH_SUCC_DEPTH  = config.load_weight() 
	cfg_data=cfg_dump(src_cfg_path)
	cfg_file = None 
	cfg_node_cnt = 0

	# When raw sourcecode file is unavailable, the entire graph will be built
	if src_code_file == 'no':  
		wfg = code2wfg(src_cfg_path, cfg_data, 'None', -1)
		# save wfg to /tmp
		wfg_file = os.path.join('../data/wfgs/', src_cfg_path.split('/')[-1]+'_-1')
		store_wfg(wfg, wfg_file)
		return [wfg]

    # When raw sourcecode file is available
	if line_no in ['no', -1, '-1']:
		# Sensitive line is not provided, then try to find from raw code
		sensitive_lines = extract_sensitive_lines(src_code_file)  
	elif line_no.isdigit():	
		# Sensitive line is denoted in arg
		sensitive_lines = [int(line_no) ]
	else:
		print 'Wrong parameter of line_no: ', line_no  
		exit(0)	 

	wfgs = []
	if sensitive_lines == []: # No sensitive line, so use the full graph
		sensitive_lines.append(-1)

	if DEBUG: start_t = time.time()
	#print "Sensitive lines: ", sensitive_lines 
	for sen_line in sensitive_lines:
		print sen_line
		if sen_line != -1:	
			sen_line = sen_line + get_start_line(src_code_file)-1 # change to the line_no is raw file
		
		wfg = code2wfg(src_cfg_path, cfg_data, src_code_file, sen_line)
		#print len(wfg.nodes())

		wfg_file = os.path.join('../data/wfgs/', src_cfg_path.split('/')[-1]+"_"+str(sen_line))
		store_wfg(wfg, wfg_file)

		if DUMP_GRAPH: dump_graph(wfg)

		wfgs.append(wfg)

	if DEBUG: end_t = time.time()
	if DEBUG: print "for sensitive_lines time: ", end_t-start_t

	return wfgs


if __name__=="__main__":
	if len(sys.argv) != 4:
		print "python code2graph.py <func_cfg_desc> <func_code> <sensitive_line_no>"
		print " -- set <func_code> as no if a full cfg is desired"
		print " -- set <sensitive_line_no> as -1 for automated searching of sensitive lines"
		exit(-1)
	wfgs = code2graph(sys.argv[1], sys.argv[2], sys.argv[3])
	#NOTE: The generated wfgs are stored into /tmp
	for wfg in wfgs:
		dump_graph(wfg)




	#stat_graph_func_cnt()
	#stat_graph_cnt_varying_depth()

