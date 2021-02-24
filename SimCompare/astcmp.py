#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__	 import division
import sys
import re
import clang.cindex
import asciitree
from ctypes import *
import collections
import clang.enumerations
from clang.cindex import Config
from clang.cindex import TypeKind
from clang.cindex import CursorKind
import time

libclangPath = '/usr/lib/libclang.so.6.0'
if Config.loaded==True:
		pass
else:
		Config.set_library_file(libclangPath)

def iterAST(cursor,i):
	if cursor:
		alist=list(cursor.get_children())
		print i,':\t',cursor.kind,'\t',cursor.spelling,'\t',len(alist)
		i+=1
		for cur in alist:
			# print i,':\t',cur.kind,'\t',cur.spelling,'\n'
			iterAST(cur,i)
		# print c

def sum_nodes(cursor,num):
	if cursor:
		alist=list(cursor.get_children())
		num = num + len(alist)
		# if cursor.kind.is_declaration() and  cursor.kind!= CursorKind.FUNCTION_DECL:
		#	  num=num-1
		for cur in alist:
			num=sum_nodes(cur,num)
	return num

def match_from_func_del(cursor,funcname):
	maxdp=0
	temp=None
	for cur in cursor.get_children():
		if cur.kind==CursorKind.FUNCTION_DECL:
			if cur.spelling.lower()== funcname.lower():
				if len(list(cur.get_children())) >= maxdp:
					temp=cur
					maxdp=len(list(cur.get_children()))
	return temp

def find_Stmt(cursor,temp):
	if cursor:
		for cur in cursor.get_children():
			if cur.kind == CursorKind.COMPOUND_STMT or cur.kind == CursorKind.IF_STMT \
			or cur.kind == CursorKind.SWITCH_STMT or  cur.kind == CursorKind.WHILE_STMT \
			or cur.kind == CursorKind.DO_STMT or cur.kind == CursorKind.FOR_STMT:
				temp.append(cur)
			find_Stmt(cur,temp)

def SimpleTreeMatching(A,B):
	if (not A) or (not B) or (A.kind.is_declaration() and A.kind != CursorKind.FUNCTION_DECL ) or (B.kind.is_declaration() and B.kind != CursorKind.FUNCTION_DECL ):
		return 0
	aChild=list(A.get_children())
	bChild=list(B.get_children())
	aChildNum=len(aChild)
	bChildNum=len(bChild)
	temp=0
	if A.kind!=B.kind:
		return 0
	if (aChildNum == 0 or bChildNum == 0):
		return 1
	m = [[0 for x in range(bChildNum+1)]for y in range(aChildNum+1)]  
	w = [[0 for x in range(bChildNum+1)]for y in range(aChildNum+1)]
	for i in range(1,aChildNum+1):
		for j in range(1,bChildNum+1):
			if w[i][j]== 0: 
				w[i][j] = SimpleTreeMatching(aChild[i-1], bChild[j-1])
				m[i][j] = max(m[i][j-1], m[i-1][j], m[i-1][j-1]+w[i][j])
	return m[aChildNum][bChildNum] + 1


# ---------------------------
def main(file1,file2):
	print("==== AST COMPARE: ====")
	index1 = clang.cindex.Index.create()
	index2 = clang.cindex.Index.create()
	# start=time.time()
	# tu1 = index1.parse(sys.argv[1])
	tu1 = index1.parse(file1)
	# print "index1.parse:",time.time()-start
	# tu2 = index2.parse(sys.argv[2])
	tu2 = index2.parse(file2)


	# extract_funcname1=re.search('(.+).c',sys.argv[1])
	# extract_funcname1=re.search('(.+).c',file1)
	extract_funcname1=re.search('#([^#]+)\.',file1)
	extract_funcname2=re.search('#([^#]+)\.',file2)
	#print extract_funcname1,extract_funcname2
	# extract_funcname2=re.search('(.+).c',sys.argv[2])
	# extract_funcname2=re.search('(.+).c',file2)

	match = 0
	num = 1

	func1 = None
	func2 = None

	if extract_funcname1 and extract_funcname2:
		func1_name=extract_funcname1.group(1)
		func2_name=extract_funcname2.group(1)

		func1=match_from_func_del(tu1.cursor,func1_name)
		func2=match_from_func_del(tu2.cursor,func2_name)
		print func1,func2
		if func1 and func2:
			temp1=[]
			temp2=[]
		# start=time.time()
			find_Stmt(func1,temp1)
			# print "find_Stmt:",time.time()-start
			find_Stmt(func2,temp2)
		# print temp1,len(temp1),'\n',temp2,len(temp2)
		# start=time.time()
			if temp1 and temp2:
				for cur1 in temp1:
					for cur2 in temp2:
						match=max(match,SimpleTreeMatching(cur1,cur2))
			# print "match:",time.time()-start
			else:
				print "Cannot get stmt"
		else:
			print "Cannot get func"
	else:
		print "Extarct failed"



	num=sum_nodes(func1,num)
	print match, num, (match/num)
	print ""
	return float(match)/num

if __name__=="__main__":
	main(sys.argv[1],sys.argv[3])
