#!/usr/bin/python
# =================================================================================
# Copyright 2020 IIE, CAS
#
# This file assists generating the ast_feature_vector with selected ast kinds
#
# Author: Lei Cui
# Contact: cuilei@iie.ac.cn
# =================================================================================


from __future__	 import division
import os
import sys
import re
from ctypes import *




#all_kinds=clang.cindex.CursorKind.get_all_kinds() # Too many types

selected_kinds = [	"VarDecl",		  "FunctionDecl",	"FieldDecl",		  "DeclRefExpr", \
					"IntegerLiteral", "TypeDefDecl",	"EnumConstantDecl",	 "BinaryOperator", \
					"ParenExpr",	  "CStyleCastExpr", "CallExpr",			  "UnaryOperator", \
					"CompoundStmt",	  "IfStmt",			"StringLiteral",	  "ArraySubscriptExpr",\
					"PureAttr",		  "ConstAttr",		"DeclStmt",			  "ReturnStmt",\
					"InitListExpr",	 "GotoStmt",	   "AsmLabelAttr",		"ConditionalOperator",\
					"EnumDecl",		  "CaseStmt",		"AsmStmt",			  "NullStmt",\
					"StmtExpr",		  "ForStmt",		"BreakStmt",		  "DoStmt",\
					"WhileStmt",	  "SwitchStmt",		"ContinueStmt", "ImplicitCastExpr"				  
]
# FunctionDecl
# NOTE: quite different from the value acquired by AST
# Detailed type: e.g., ImplicitCastExpr-> LValueToRValue, BitCast, etc.
selected_kinds = [	"VarDecl",			"FunctionDecl",		"FieldDecl",			"DeclRefExpr", \
					"IntegerLiteral",	"TypeDefDecl",		"EnumConstantDecl",		"BinaryOperator", \
					"ParenExpr",		"CStyleCastExpr",	"CallExpr",				"UnaryOperator", \
					"CompoundStmt",		"IfStmt",			"StringLiteral",		"ArraySubscriptExpr",\
					"PureAttr",			"ConstAttr",		"DeclStmt",				"ReturnStmt",\
					"InitListExpr",		"goto",				"AsmLabelAttr",			"ConditionalOperator",\
					"EnumDecl",			"case",				"AsmStmt",				"NullStmt",\
					"StmtExpr",			"ContinueStmt",		"ImplicitCastExpr",					\
					"for",				"do",				"while",  \
					"switch",			"case",				"if",					"else", \
					"continue",			"return",			"goto",					"break"		 
] 

all_kinds = selected_kinds

symbols = ['-', '+', '*', '.', '[', ']', '(', ')', '{', '}', '*', '/', '=', '&', '!', '|', '<', '>', ';', ',', ':', '\'', '?', '#']

split_re = ''
for symbol in symbols: split_re = split_re + '\\'+symbol
split_re = '[\s' + split_re + ']'

def line_feature_index(line):
	global all_kinds
	for index in range(len(all_kinds)):
		items = re.split(split_re, line) 
		if all_kinds[index] in items:
		#if line.find(all_kinds[index]) >= 0:
			return index
	return -1
	


# --------------NOTE: The code below is expired  --------------- #
def select_key_features(vector):
	# only use the key features to construct the vector
	pass


def ast_feature_generator(cursor,ast_feature):
	Pa_line_ast = re.compile(r', line ([0-9]+),', re.I)
	if cursor:
		#print help(cursor)
		alist=list(cursor.get_children())
		#print len(alist)
		loc=str(cursor.location)
		#print "loc is ", loc
		m=Pa_line_ast.search(loc)
		# print m.group(1),':\t',cursor.kind
		line_index=int(m.group(1))
		#print line_index

		try:
			kind=cursor.kind
			if kind not in all_kinds: # we just ignore them
				ast_feature.append((line_index, -1) )
			else:
				kind_index=all_kinds.index(kind)
				#print kind_index
				ast_feature.append((line_index,kind_index))
			for cur in alist:
				ast_feature_generator(cur,ast_feature)
		except Exception, e:
			print "Handld line error, ", str(e)
			ast_feature.append((line_index, -1)) 
	else:
		#print help(cursor)
		#print 'Cursor is none'
		pass


def get_ast_feature(src_file,ast_feature):
	index1 = clang.cindex.Index.create()
	tu1 = index1.parse(src_file)
	ast_feature_generator(tu1.cursor,ast_feature)
	#print(ast_feature)
	return ast_feature


def blk_vector_generator(blk,ast_feature):
	blk_vector=[0]*len(all_kinds)
	# TODO: compute the shift automatically 
	shift = 58
	for num in blk:
		for ast_f in ast_feature:
			if(ast_f[0]==num-shift):
				blk_vector[ast_f[1]]+=1
	return blk_vector


