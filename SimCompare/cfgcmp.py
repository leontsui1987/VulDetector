#!/usr/bin/python
# -*- coding: UTF-8 -*-
# =================================================================================
# Copyright 2020 IIE, CAS
#
# This file computes the similarity of two WFGs
# Input: Two wfgs
# Output: Similairity
#
# Author: Lei Cui
# Contact: cuilei@iie.ac.cn
# =================================================================================


from __future__	 import division
import os
import sys
import re
from ctypes import *
import collections
import time
import numpy
import math
sys.path.append("../")
from WFGParse.code2graph import *
from WFGParse.wfg_mngr import *
from config import *

try:
	import hungarian
except Exception, e:
	import hungarian

#from matplotlib import pyplot as plt
import networkx as nx
import commands


DEBUG = False
#DEBUG = True

######################################################
# *************graph_edit_distance********************
######################################################
def graph_node_distance(g1, g2):
	MAX_VALUE=10000
	cost_matrix = []
	g1_indexs = list(g1.nodes())
	g2_indexs = list(g2.nodes())
	#print g1_indexs, g2_indexs, len(g1_indexs), len(g2_indexs)
  
	matrix_len = max(len(g1), len(g2))
	min_len = min(len(g1), len(g2))
	if min_len == 0:
		return MAX_VALUE
	diff = min_len *1.0 / matrix_len
	# print diff
	if diff < 0.5:
		return MAX_VALUE
	for row_id in xrange(matrix_len):
		row = []
		for column_id in xrange(matrix_len):
			src = obtain_node_feature(g1, g1_indexs, row_id)
			dst = obtain_node_feature(g2, g2_indexs, column_id)
			cost = cal_nodecost(src, dst)
			#print row_id, column_id,  src, dst, cost
			if USE_WEIGHT:
				src_weight = obtain_node_weight(g1, g1_indexs, row_id)
				dst_weight = obtain_node_weight(g2, g2_indexs, column_id)
				#cost_weight =1-(1-cost)*src_weight*dst_weight
				cost_weight =(cost)*(src_weight+dst_weight)/2
				cost = cost_weight
			row.append(cost)
		cost_matrix.append(row)
	if len(cost_matrix) == 0:
		return MAX_VALUE
	mapping = hungarian.lap(cost_matrix)
	#print '-------------- cost matrix -------------'
	#print cost_matrix

	#print '-------------- matrix mapping-------------'
	#print mapping
	distance = caldistance(mapping, cost_matrix)
	return distance

def graph_edge_distance(g1, g2):
	cost_matrix = []
	#print g1.edges(), g2.edges()
	g1_indexs = list(g1.edges())
	g2_indexs = list(g2.edges())
	matrix_len = max(len(g1), len(g2))
	min_len = min(len(g1), len(g2))
	if min_len == 0: 
		return 0
	diff = min_len *1.0 / matrix_len
	# print diff
	if diff < 0.5:
		return 100
	for row_id in xrange(matrix_len):
		row = []
		for column_id in xrange(matrix_len):
			src = obtain_edge_feature(g1, g1_indexs, row_id)
			dst = obtain_edge_feature(g2, g2_indexs, column_id)

			if src is None or dst is None: cost = 0
			else: cost = cal_edgecost(src, dst)
			# use weight
			if USE_WEIGHT:
				src_weight = obtain_edge_weight(g1, g1_indexs, row_id)
				dst_weight = obtain_edge_weight(g2, g2_indexs, column_id)
				cost_weight = (cost)*(src_weight+dst_weight)/2
				#cost_weight = 1-(1-cost)*src_weight*dst_weight
				cost = cost_weight
				#print 'Edge: ', cost, src_weight, dst_weight
			#print 'SRC, DST ', src, dst
			#cost = cal_edgecost(src, dst)
			row.append(cost)
		cost_matrix.append(row)
	if len(cost_matrix) == 0:
		return -1
	mapping = hungarian.lap(cost_matrix)
	# print cost_matrix,mapping
	distance = caldistance(mapping, cost_matrix)
	return distance

def cal_edgecost(edge1, edge2):
	src_cost = cal_nodecost(edge1[0], edge2[0])
	dst_cost = cal_nodecost(edge1[1], edge2[1])
	#print src_cost,  dst_cost
	return (src_cost + dst_cost)/2

def cal_nodecost(node1_vec, node2_vec):
	if(node1_vec=="dummy_node" or node2_vec=="dummy_node"):
		return 1;
	if node1_vec == node2_vec:
		return 0;
	sim = (node_ecul_sim(node1_vec,node2_vec) + node_cos_sim(node1_vec, node2_vec) ) /2.0
	val = 1-sim 
	return val


def obtain_edge_weight(g, g_indexes, edge_id):
	g_len = len(g_indexes)
	if edge_id <= (g_len - 1):
		edge = g_indexes[edge_id]
		#print 'obtain edge', edge
		if 'weight' in g.node[edge[0]]:
			src = g.node[edge[0]]['weight']
		else:
			src = 0
		if 'weight' in g.node[edge[1]]:
			dst = g.node[edge[1]]['weight']
		else:
			dst = 0
		return max(src, dst)
	else:
		return 0


def obtain_edge_feature(g, g_indexes, edge_id):
	g_len = len(g_indexes)
	if edge_id <= (g_len - 1):
		edge = g_indexes[edge_id]
		#print 'obtain edge', edge
		if 'blk_vector' in g.node[edge[0]]:
			src = g.node[edge[0]]['blk_vector']
		else:
			src = 'dummy_node'
			print 'dummy_node'
		if 'blk_vector' in g.node[edge[1]]:
			dst = g.node[edge[1]]['blk_vector']
		else:
			dst = 'dummy_node'
			print 'dummy_node'
		return (src, dst)
	else:
		return None #("dummy_node","dummy_node")


def obtain_node_weight(g, g_indexes, node_id):
	if not USE_WEIGHT:
		return 1.0
	g_len = len(g_indexes)
	if node_id <=(g_len - 1):
		node=g_indexes[node_id]
		return g.node[node]['weight']
	else:
		return 1.0


def obtain_node_feature(g, g_indexes, node_id):
	g_len = len(g_indexes)
	if node_id <=(g_len - 1):
		node=g_indexes[node_id]
		return g.node[node]['blk_vector']
	else:
		return "dummy_node"


def obtain_zero_cnt(g):
	# Get zero node count
	g_indexes = list(g.nodes()) 
	zero_node_cnt = 0
	for index in g_indexes:
		node_v = g.node[index]['blines']
		if len(node_v) == 0: zero_node_cnt+=1
	return zero_node_cnt


def caldistance(mapping, cost_matrix):
	cost = 0 
	for i in xrange(len(mapping[0])):
		cost += cost_matrix[i][mapping[0][i]]
	return cost

def node_cos_sim(vector1,vector2):
# Use cos value to compute the similarity of two nodes
	dot_product = 0.0
	normA = 0.0
	normB = 0.0
	for a,b in zip(vector1,vector2):
		dot_product += a*b
		normA += a**2
		normB += b**2
	if normA == 0.0 or normB == 0.0:
		return 0   
	else:
		return dot_product / ((normA*normB)**0.5)


def node_ecul_sim(v1, v2):
# Use eculidean value to compute the similarity of two nodes
	v1 = numpy.array(v1)
	v2 = numpy.array(v2)
	v1_norm = numpy.linalg.norm(v1) 
	v2_norm = numpy.linalg.norm(v2) 
	#if v1_norm == 0 and v2_norm == 0: # v1 == v2 also return 1
	#	return 1  
	if v1_norm == 0 or v2_norm == 0:
		return 0
	dis = numpy.linalg.norm(v1 - v2)
	return 1.0-float(dis)/(v1_norm*v2_norm)


######################################################
# *************main function************************** 
######################################################
# Calculate the weighted similarity by the node distance, edge distance and node count of two graphs
def weighted_similarity(g_node1, g_node2, node_dis, edge_dis, zero_cnt1, zero_cnt2):
	feature_dis = (node_dis + math.sqrt(edge_dis)) / (g_node1 + g_node2) # difference by feature
	size_dis = abs(float(g_node1 - g_node2)) / (g_node1 + g_node2) # difference by size
	zero_dis = abs(float(zero_cnt1 - zero_cnt2))/(g_node1 + g_node2)	 

	alpha = 1.15
	beta = 0.05
	gamma = 0.05 
	dis = feature_dis*alpha + size_dis*beta + zero_dis*gamma
	sim = 1 - dis
	return sim if sim > 0 else 0


# Compute similarity of two WFGs
def compare_wfg(subcfg1, subcfg2):
	cfg_node_cnt1 = len(subcfg1.nodes())
	cfg_node_cnt2 = len(subcfg2.nodes())
	if cfg_node_cnt1 == 0 or cfg_node_cnt2 == 0:
		#print "CFG node cnt is %s, %s" % (cfg_node_cnt1, cfg_node_cnt2)
		return 0
	min_cnt = min([cfg_node_cnt1, cfg_node_cnt2])
	max_cnt = max([cfg_node_cnt1, cfg_node_cnt2])
	if max_cnt > 3*min_cnt:
		#print cfg_node_cnt1, cfg_node_cnt2, 0
		return 0
	#print cfg_node_cnt1, cfg_node_cnt2
	#print subcfg1.edges()
	#print subcfg2.edges()
	if DEBUG_TIME: start_t = time.time()
	start_t = time.time()
	node_dis = graph_node_distance(subcfg1,subcfg2)
	if DEBUG_TIME: end_t = time.time()
	if DEBUG_TIME: print 'graph node distance: ', end_t - start_t
	if DEBUG_TIME: start_t = time.time()
	edge_dis = graph_edge_distance(subcfg1,subcfg2)
	if DEBUG_TIME: end_t = time.time()
	if DEBUG_TIME: print 'graph edge distance: ', end_t - start_t
	#print("Node-distance:", node_dis)
	#print("Edge-distance:", edge_dis)
	zero_cnt1 = obtain_zero_cnt(subcfg1)
	zero_cnt2 = obtain_zero_cnt(subcfg2)
	#print("Edge-distance:", edge_dis)
	sim = weighted_similarity(cfg_node_cnt1, cfg_node_cnt2, node_dis, edge_dis, zero_cnt1, zero_cnt2 )
	end_t = time.time()
	#print 'CMPTIME ', end_t - start_t
	commands.getoutput("rm *.plist")
	#print cfg_node_cnt1, cfg_node_cnt2, node_dis, edge_dis, sim
	return round(sim,3)


def _build_graph(graph_path, code_path, line_no):
# graph_path denotes the graph dump file
# line no denotes the sensitive line 
	global g_graph_dict
	# Try to get graph from dict first
	try:
		subcfg = g_graph_dict[graph_path][line_no]
		#print 'Get graph from ', graph_path
	except Exception, e:
		#print "Cannot get graph from dict ", graph_path
		if DEBUG: print graph_path, code_path
		cfg = code2graph(graph_path, code_path, line_no)
		if cfg == None : #return 0
			return None
		subcfg = cfg[0] # remove the null nodes
		if graph_path not in g_graph_dict.keys(): 
			g_graph_dict[graph_path] = {}
		g_graph_dict[graph_path][line_no] = subcfg # fill into global dict, depth is also a variant
	return subcfg


def main(src_path1, src_code1, search_num1, src_path2, src_code2, search_num2):
	if DEBUG:
		print("==== CFG COMPARE: ====")

	cfg_file1 = None 
	cfg_node_cnt1 = 0
	cfg_file2 = None 
	cfg_node_cnt2 = 0


	#load_global_graph_dict()
	subcfg1 = _build_graph(src_path1, src_code1, search_num1)
	subcfg2 = _build_graph(src_path2, src_code2, search_num2)
	#return 0 # TODO
	if subcfg1 == None or subcfg2 == None: 
		return 0
	
	return compare_wfg(subcfg1, subcfg2)

	#store_global_graph_dict()

	#print subcfg1.node[0]['weight'], ' cfg1'
	#print subcfg2.node[0]['weight'], ' cfg2'


# fig = plt.figure()
# ax1 = fig.add_subplot(2,1,1)
# nx.draw_networkx(subcfg1)
# ax2 = fig.add_subplot(2,1,2)
# nx.draw_networkx(subcfg2)
# plt.show()


if __name__=="__main__":
	# "searchnum = no if slicing is not required"
	# arg1: source cfg dump file
	# arg2: source c file, used for slicing, or 'no' to denote no slicing
	# arg3: line_no of vulnerable codes, or 'no' for identifying sensitive lines
	# arg4,5,6: same meanings but for target code

	global DEBUG 
	DEBUG = False

	if len(sys.argv) != 3:
		print "python cfgcmp.py <wfg_file1> <wfg_file2>"
		exit(-1)

	wfg1 = load_wfg(sys.argv[1])
	wfg2 = load_wfg(sys.argv[2])
	if wfg1 == None or wfg2 == None:
		print 'WFG is None'
                return
	sim = compare_wfg(wfg1, wfg2)
	print "Similarity of two WFGs: ", sim
	exit(0)


    # Code below is expired
	if len(sys.argv) == 5:
		main(sys.argv[1],sys.argv[2], 'no', sys.argv[3],sys.argv[4], 'no')
	elif len(sys.argv) == 7:
		main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4], sys.argv[5], sys.argv[6])
	else:
		print 'Wrong arg cnt ', len(sys.argv)
