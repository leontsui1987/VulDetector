#!/usr/bin/python
# -*- coding: UTF-8 -*-

# =================================================================================
# Copyright 2020 IIE, CAS

# Author: Lei Cui
# Contact: cuilei@iie.ac.cn
# =================================================================================

from __future__	 import division
import os
import sys
from ctypes import *
import collections
import numpy
sys.path.append("../")
from config import *

#from matplotlib import pyplot as plt
import networkx as nx

# key1: graph file path
# key2: sensitive line no
g_graph_dict = {}

def graph2dict(graph):
	graph_dict = {}
	nodes = graph.nodes()
	edges = graph.edges()
	node_dict = {}
	for node_id in nodes: 
		node_dict[node_id] = graph.node[node_id]
	graph_dict['nodes'] = nodes
	graph_dict['edges'] = edges
	graph_dict['node_dicts'] = node_dict
	return graph_dict


def dict2graph(line):
	graph = nx.DiGraph() 
	graph_dict = eval(line)
	nodes = graph_dict['nodes']
	edges = graph_dict['edges']
	node_dict = graph_dict['node_dicts']
	
	graph.add_nodes_from(nodes) 
	graph.add_edges_from(edges) 
	for node_id in nodes: 
		graph.node[node_id] = node_dict[node_id]
	return graph


def store_wfg(wfg, wfg_file):
	wfg_dict = graph2dict(wfg)
	with open(wfg_file, 'w') as fd:
		print "Store wfg into ", wfg_file
		fd.write(repr(wfg_dict))


def load_wfg(wfg_file):
	try:
		with open(wfg_file, 'r') as fd:
			wfg_dict = fd.readline()
			wfg = dict2graph(wfg_dict)
			return wfg
	except Exception, e:
		print "Load wfg file %s failed %s" % (wfg_file, str(e))
		return None


def load_global_graph_dict():
	global g_graph_dict
	if not LOAD_GLOBAL_GRAPH: 
		return

	graph_dict_path = GRAPH_DICT_PATH
	if not os.path.exists(graph_dict_path): 
		return

	fd = open(graph_dict_path, 'r')
	lines = fd.readlines()
	for line in lines: 
		graph_path, line_no, value = line.split('@')[0], line.split('@')[1], line.split('@')[2]
		if graph_path not in g_graph_dict.keys(): 
			g_graph_dict[graph_path] = {}
		g_graph_dict[graph_path][line_no] = dict2graph(value)
	print 'g_graph_dict', g_graph_dict

	fd.close() 


def store_global_graph_dict():
	global g_graph_dict
	if not LOAD_GLOBAL_GRAPH: 
		return
	graph_dict_path = GRAPH_DICT_PATH
	fd = open(graph_dict_path, 'w+')
	if fd == None:
		print 'fd is none'
	
	print graph_dict_path, fd

	for graph_path, value1 in g_graph_dict.items(): 
		for line_no, value2 in value1.items():
			dict_ret = graph2dict(value2)
			#print dict_ret
			content = '%s@%s@%s\n' % (graph_path, line_no, repr(dict_ret) )
			print content[:10]
			fd.write(content)
	fd.close() 
	print 'Global dict is stored' 
	g_graph_dict = {} 

	
