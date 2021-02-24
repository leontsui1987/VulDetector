#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__	 import division
import re
import os
import sys
import numpy
import math
import io
import time
from simhash import Simhash,SimhashIndex
import commands
#import funcslice_str
sys.path.append('../DataParse')
import slicing as funcslice_str

def get_features(s):
	width = 4
	s = s.lower()
	s = re.sub(r'[^\w]+', '', s)
	return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

def find_lcsubstr(s1,s2): 
	m=[[0 for i in range(len(s2)+1)]  for j in range(len(s1)+1)]  #生成0矩阵，为方便后续计算，比字符串长度多了一列
	mmax=0	 #最长匹配的长度
	p=0	 #最长匹配对应在s1中的最后一位
	for i in range(len(s1)):
		for j in range(len(s2)):
			if s1[i]==s2[j]:
				m[i+1][j+1]=m[i][j]+1
				if m[i+1][j+1]>mmax:
					mmax=m[i+1][j+1]
					p=i+1
	# print s1[p-mmax:p],'\n'	#返回最长子串及其长度
	return mmax
 
def find_lcseque(s1,s2):
	 # 生成字符串长度加1的0矩阵，m用来保存对应位置匹配的结果
	m = [ [ 0 for x in range(len(s2)+1) ] for y in range(len(s1)+1) ] 
	# d用来记录转移方向
	d = [ [ None for x in range(len(s2)+1) ] for y in range(len(s1)+1) ] 
 
	for p1 in range(len(s1)): 
		for p2 in range(len(s2)): 
			if s1[p1] == s2[p2]:			#字符匹配成功，则该位置的值为左上方的值加1
				m[p1+1][p2+1] = m[p1][p2]+1
				d[p1+1][p2+1] = 'ok'		  
			elif m[p1+1][p2] > m[p1][p2+1]:	 #左值大于上值，则该位置的值为左值，并标记回溯时的方向
				m[p1+1][p2+1] = m[p1+1][p2] 
				d[p1+1][p2+1] = 'left'			
			else:							#上值大于左值，则该位置的值为上值，并标记方向up
				m[p1+1][p2+1] = m[p1][p2+1]	  
				d[p1+1][p2+1] = 'up'		 
	(p1, p2) = (len(s1), len(s2)) 
	s = [] 
	while m[p1][p2]:	#不为None时
		c = d[p1][p2]
		if c == 'ok':	#匹配成功，插入该字符，并向左上角找下一个
			s.append(s1[p1-1])
			# print s
			p1-=1
			p2-=1 
		if c =='left':	#根据标记，向左找下一个
			p2 -= 1
		if c == 'up':	#根据标记，向上找下一个
			p1 -= 1
	s.reverse() 
	return s

def sim_hash(file1,file2):
	str1=open(file1,'r').read()
	str1=re.sub(r'#.*\n', "", str1)
	str1=re.sub(r'//.*\n', "", str1)
	str1=re.sub(r'/\*.*\*/', "", str1)
	str1=re.sub(r'var\d+','var',str1)
	str1=re.sub(r'func\d+','func',str1)


	str2=open(file2,'r').read()
	str2=re.sub(r'#.*\n', "", str2)
	str2=re.sub(r'//.*\n', "", str2)
	str2=re.sub(r'/\*.*\*/', "", str2)
	str2=re.sub(r'var\d+','var',str2)
	str2=re.sub(r'func\d+','func',str2)

	l1=re.split(r'[\s]',str1)
	l2=re.split(r'[\s]',str2)


	dist1=find_lcsubstr(l1,l2)
	sim1=(dist1/len(l1))

	dist2=len(find_lcseque(str1.split(),str2.split()))
	sim2=dist2/len(str1.split())

	dist3=Simhash(str1.split('\n')).distance(Simhash(str2.split('\n')))
	sim3=1-dist3/64
	#if sim3>=0.92:
	#	sim3=sim3*3

	sim=(sim1*5+sim2+sim3*3)/9
	print sim1, sim3, sim2
	return sim
# ,":",sim1/9,":",sim2/9,":",sim3/9

def call_tokenize(file_path):
	cmd1="clang -cc1  -dump-tokens "+file_path
	#print(cmd1)
	tokendump=commands.getoutput(cmd1)
	file_name=re.search(r"([^/]*)$",file_path).group(1)
	dumpf_path="tokendump/"+file_name+"-tkdump"
	dumpf=open(dumpf_path,'w')
	dumpf.write(str(tokendump))
	dumpf.close()
	file_new="tokenized_codes/"+file_name +'-new.c'
	# Hard-coded, bad. NOTE
	cmd2="/home/cuilei/code_sim/VulDetector/Codes/SimCompare/tokenize "+ dumpf_path+ ' '+ file_path + ' ' +file_new
	ret = commands.getoutput(cmd2)
	return file_new

def call_funcslice_str(file1,search_num1):
	file1_dump="tokendump/"+file1+"-tkdump"
	file1_slice="tailored_codes/"+file1+"-slice"
	commands.getoutput("mkdir tailored_codes")
	funcslice_str.main(file1,file1_dump,search_num1,file1_slice)
	file1_c=call_tokenize(file1_slice)
	return file1_c


def main(file1,search_num1,file2,search_num2):
	#print("==== STR COMPARE: ====")
	commands.getoutput("mkdir tokendump")
	commands.getoutput("mkdir tokenized_codes")
	file1_new=call_tokenize(file1)
	file2_new=call_tokenize(file2)
	if(search_num1=="no"):
		file1_c=file1_new
	else:
		commands.getoutput("mkdir tokendump/tailored_codes/")
		commands.getoutput("mkdir tokenized_codes/tailored_codes/")
		file1_c=call_funcslice_str(file1,search_num1)

	if(search_num2=="no"):
		file2_c=file2_new
	else:
		commands.getoutput("mkdir tokendump/tailored_codes/")
		commands.getoutput("mkdir tokenized_codes/tailored_codes/")
		file2_c=call_funcslice_str(file2,search_num2)

	start_t = time.time()
	ret = sim_hash(file1_c,file2_c)
	end_t = time.time()
	print 'CMPTIME: ', end_t - start_t
	return ret


def lcseq_sim(s1, s2):
	l1 = list(s1)
	l2 = list(s2)
	dst = len(find_lcseque(l1, l2))
	sim = dst/len(l1) + dst/len(l2)
	sim = sim/2.0
	#if sim>0.8: print dst/len(l1),dst/len(l2), dst, len(l1), len(l2)
	return sim


def weighted_lcseq_sim_file(f1, f2):
	fd1 = open(f1, 'r') 
	fd2 = open(f2, 'r') 
	str1 = fd1.read() 
	str2 = fd2.read() 
	fd1.close() 
	fd2.close() 
	ret = weighted_lcseq_sim(str1, str2)  
	return ret	


# Add length_sim between s1 and s2
def weighted_lcseq_sim(s1, s2):
	l1 = list(s1.strip())
	l2 = list(s2.strip())
	while ' ' in l1: l1.remove(u' ')
	while ' ' in l2: l2.remove(u' ')
	start_t = time.time()
	if len(l1) == 0 or len(l2) == 0: return 0
	if abs(len(l1)-len(l2)) > min(len(l1), len(l2))/2.0: return 0
	# sim in sequence
	dst = len(find_lcseque(l1, l2))
	sim1 = dst/len(l1)
	sim2 = dst/len(l2)

	# substring
	if sim1>0.95 or sim2 > 0.95: str_sim = max(sim1, sim2)
	else: str_sim = (sim1 + sim2)/2

	# sim in length
	len_sim = float(min(len(l1), len(l2))) / max(len(l1), len(l2))

	sim = str_sim * math.sqrt(len_sim)
	end_t = time.time()
	#print "String time cost is ", end_t - start_t 
	#if sim>0.9: print dst/len(l1),dst/len(l2), dst, len(l1), len(l2)
	#print dst/len(l1),dst/len(l2), dst, len(l1), len(l2)
	return round(sim,6)

def search_version_sim(f1, f2):
	with io.open(f1, 'r', encoding='utf-8') as fd: s1 = fd.read()
	with io.open(f2, 'r', encoding='utf-8') as fd: s2 = fd.read()
	s1 = s1.replace(u'\xa0', u' ')
	s2 = s2.replace(u'\xa0', u' ')
	return weighted_lcseq_sim(s1, s2)


if __name__ == '__main__':
	#main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
	s1 = 'if (sk_SSL_CIPHER_find(allow, sk_SSL_CIPHER_value(prio, z)) < 0' 
	s2 = 'if (sk_SSL_CIPHER_find(cl,sk_SSL_CIPHER_value(cs,z)) < 0)' 
	#dst1 = find_lcsubstr(s1,s2) 
	#sim1=(dst1/len(s1))
	#print dst1, sim1, len(s1)
	print lcseq_sim(s1, s2)

