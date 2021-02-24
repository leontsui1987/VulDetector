#!/bin/python

# =================================================================================
# Copyright 2020 IIE, CAS
#
# This file determines a set of keywords given a corpus of vulnerability patches using TF/DF
#
# Author: Lei Cui
# Contact: cuilei@iie.ac.cn
# =================================================================================

import os
import sys
import io
import string
import commands
import nltk
import operator
import re
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.append('../')
from config import *

#top_dir = os.path.join(OUTPUT_DIR, '/home/cuilei/code_sim/VulDetector/Data/outputs/openssl/test_keywords')
top_dir = os.path.join(OUTPUT_DIR, '/home/cuilei/code_sim/VulDetector/Data/outputs/openssl/test_keywords_linux')
stat_dir = os.path.join(top_dir, 'stat_data')
orig_dir = os.path.join(top_dir, 'orig_data')
#orig_dir = os.path.join(top_dir, 'orig_data', 'all_diff') #TODO, a little problem here, first use 'all_diff' in preprocess(), then remove it when counting TF
preprocessed_dir = os.path.join(top_dir, 'preprocessed_data')

def line_is_comment(line):
	# NOTE: maybe not accurate	
	comment_line = re.findall(r'(.*)\/\/(.*)', line)		 # ignore comments //
	if(comment_line):
		#print "Comment ", comment_line
		return True
	comment_line = re.findall(r'(.*)\/\*(.*)', line)		 # ignore comments /*
	if(comment_line):
		#print "Comment ", comment_line
		return True
	comment_line = re.findall(r'(.*)\*\/(.*)', line)		 # ignore comments */
	if(comment_line):
		#print "Comment ", comment_line
		return True
	comment_line = re.findall(r'^[-\+\s](\s*)\*(.*)', line)		 # ignore comments +/-/	 *
	if(comment_line):
		#print "Comment ", comment_line
		return True


def save_content(s_file, d_file, symbol):
	fd_d = open(d_file, 'w+')
	with io.open(s_file, 'r', encoding='utf-8') as fd_s:
		lines = fd_s.readlines()
		for line in lines:
			line = line.strip()
			if line == "":
				continue
			if line_is_comment(line): 
				continue
			if line[0].strip() == symbol:
				fd_d.write(line+'\n')
	fd_d.close()

def save_minus_content(s_file, d_file):
	save_content(s_file, d_file, '-')

def save_plus_content(s_file, d_file):
	save_content(s_file, d_file, '+')


def preprocess_each_orig_file():
	# Extract the '-' and '+' content of diff file and save them into each file
	orig_alldiff_dir = os.path.join(orig_dir, 'all_diff')
	cves = os.listdir(orig_alldiff_dir)
	for cve in cves:
		cve_ret_minus_dir = os.path.join(orig_dir, 'minus', cve) # Save the '-' result
		if not os.path.exists(cve_ret_minus_dir):
			os.mkdir(cve_ret_minus_dir)
		cve_ret_plus_dir = os.path.join(orig_dir, 'plus', cve) # Save the '+' result
		if not os.path.exists(cve_ret_plus_dir):
			os.mkdir(cve_ret_plus_dir)

		cve_dir = os.path.join(orig_alldiff_dir, cve)
		cve_files = os.listdir(cve_dir)
		for s_file in cve_files:
			s_file_path = os.path.join(cve_dir, s_file)
			cve_ret_minus_file = os.path.join(cve_ret_minus_dir, s_file+'_minus.c') # Save the result
			cve_ret_plus_file = os.path.join(cve_ret_plus_dir, s_file+'_plus.c') # Save the result

			save_minus_content(s_file_path, cve_ret_minus_file)
			save_plus_content(s_file_path, cve_ret_plus_file)
			


def preprocess():
	# Save the files in dir_path into one 'big' file
	cves = os.listdir(orig_dir)
	
	for cve in cves:
		cve_ret_file = os.path.join(preprocessed_dir, cve+'.c') # Save the result
		cve_ret_minus_file = os.path.join(preprocessed_dir, cve+'_minus.c') # Save the result
		cve_ret_plus_file = os.path.join(preprocessed_dir, cve+'_plus.c') # Save the result
		cve_dir = os.path.join(orig_dir, cve)
		cve_files = os.listdir(cve_dir)
		print cve_files
		for s_file in cve_files:
			s_file_path = os.path.join(cve_dir, s_file)
			print s_file_path
			# Save all the diff content
			cmd = 'cat %s >> %s' % (s_file_path, cve_ret_file) 
			commands.getstatusoutput(cmd)
			
			# Save all the -- content
			#save_minus_content(s_file_path, cve_ret_minus_file) # TODO: maybe not used

			# Save all the ++ content
			#save_plus_content(s_file_path, cve_ret_plus_file) # TODO: maybe not used
			

def get_file_list(argv) :
	#path = argv[1]
	path = argv
	filelist = []
	files = os.listdir(path)
	for f in files :
		if(f[0] == '.') :
			pass
		else :
			filelist.append(f)
	return filelist,path

# Split the file into many tokens
def split_file(argv,path):
	# Save the results
	sFilePath = os.path.join(stat_dir, 'segfile')
	if not os.path.exists(sFilePath) : 
		os.mkdir(sFilePath)
	filename = argv
	f = open(path+filename,'r+')
	file_list = f.read()
	f.close()
	
	#print file_list
	seg_list = file_list.split() # split into tokens

	result = []
	for seg in seg_list :
		seg = ''.join(seg.split())
		if (seg != '' and seg != "\n" and seg != "\n\n") :
			result.append(seg)
	#for item in result:
	#	 print item
	# Save the splitted results
	f = open(sFilePath+"/"+filename+"-seg.txt","w+")
	f.write(' '.join(result))
	f.close()


symbols = ['-', '+', '*', '.', '[', ']', '(', ')', '{', '}', '*', '/', '=', '&', '!', '|', '<', '>', ';', ',', ':', '\'', '?', '#']
stop_words =	['', '-', '+', '/*', '8?', '@@', 
				'int', '{', '}', '(', ')', '*', 'char', 'unsigned',
				'=', 'return', 'the', 'diff', '---', '+++', '<', '>', '<=', '>=', 
				'||', '&', 
				'if', 'else', 'while', ''] # if, while, may be usfule
				# if && <=	seem important	


def handle_item(item):
	#print 'item ', item
	for symbol in symbols:
		while item.find(symbol) >= 0:
			item.remove(symbol)

	item = item.strip()
	if item in stop_words:
		return None
	if len(item) <= 2:
		return None

	return item


def line_to_items(line):
	# split line into a set of items
	line = line.encode('utf-8')
	items = []
	split_re = '' 
	for symbol in symbols:
		split_re = split_re + '\\'+symbol
	split_re = '[\s' + split_re + ']' 
	#print split_re	  

	item_list = re.split(split_re, line) 
	#item_list = re.split("[\s\.]", line) 
	#print item_list
	for item in item_list:
		item = handle_item(item)
		if item == None:
			continue
		else:
			items.append(item)
	#items = list(set(items))
	return items 


def split_file_new(argv,path):
	# Save the results
	sFilePath = os.path.join(stat_dir, 'segfile')
	if not os.path.exists(sFilePath) : 
		os.mkdir(sFilePath)
	filename = argv
	f = io.open(os.path.join(path,filename),'r+', encoding='utf-8')
	lines = f.readlines()
	f.close()
	

	#print file_list
	result = []
	for line in lines:
		print 'line ', line
		line = line.replace(u'\xa0', u' ')
		line = line.strip() 
		if line == "":
			continue
		seg_list = line_to_items(line) #line.split(' ') # split into tokens
		for item in seg_list:
			item = handle_item(item)
			if item == None:   
				continue
			#print 'item ', item
			result.append(item)

	#for item in result:
	#	 print item
	# Save the splitted results
	f = open(sFilePath+"/"+filename+"-seg.txt","w+")
	f.write(' '.join(result))
	f.close()


def tf(filelist):

	path = os.path.join(stat_dir, 'segfile')
	sFilePath = os.path.join(stat_dir, 'tffile')
	if not os.path.exists(sFilePath) : 
		os.mkdir(sFilePath)

	for ff in filelist :
		fname = os.path.join(path, ff+'-seg.txt')
		f = open(fname,'r+')
		content = f.read()
		content_l = content.split(' ')
		print type(content_l)
		
		f.close()
		tf_ret = nltk.FreqDist(content_l)
		tf_ret.most_common

		print "write tf-idf in %s " % ( sFilePath+'/'+ff+'.txt')
		f = open(sFilePath+'/'+ff+'.txt','w+')
		sorted_tf = sorted(tf_ret.items(),key=operator.itemgetter(1), reverse=True)
		for key in sorted_tf:
			#f.write(str(key) + " " + str(sorted_tf[key])+"\n")
			print key 
			f.write(str(key[0]) + " " + str(key[1])+"\n")
		f.close()
			

# Read files and compute TF-IDF
def Tfidf(filelist) :
	path = os.path.join(stat_dir, 'segfile')
	corpus = []	 
	for ff in filelist :
		fname = os.path.join(path, ff+'-seg.txt')
		f = open(fname,'r+')
		content = f.read()
		f.close()
		corpus.append(content)	 

	sFilePath = os.path.join(stat_dir, 'tfidffile')
	if not os.path.exists(sFilePath) : 
		os.mkdir(sFilePath)

	vectorizer = CountVectorizer()	  
	transformer = TfidfTransformer()
	tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
	
	word = vectorizer.get_feature_names() # Get all tokens
	weight = tfidf.toarray()			  # Transform into tfidf array

	# Save the TF-IDF of keywords
	for i in range(len(weight)) :
		print "write tf-idf in %d %s " % (i, sFilePath+'/'+string.zfill(i,5)+'.txt')
		f = open(sFilePath+'/'+string.zfill(i,5)+'.txt','w+')
		for j in range(len(word)) :
			if weight[i][j] - 0 < 0.0001 : # Ignore 0 tokens
				continue
			f.write(word[j]+"	 "+str(weight[i][j])+"\n")
		f.close()
			
def file_totalcnt_keycnt(s_file, keyword):
	# Calculate the count of all words and keywords
	total_cnt = 0
	tmp_total_cnt = 0
	key_cnt = 0
	with io.open(s_file, 'r', encoding='utf-8') as fd:
		lines = fd.readlines()
		for line in lines:
			line = line.replace(u'\xa0', u' ')
			line = line.strip()
			if line == "":
				continue
			#print line
			items = line_to_items(line) #line.split(' ')
			total_cnt += len(items) # NOTE: may contain ' ' words
			for item in items:
				item = item.strip()
				if item == '':
					continue
				tmp_total_cnt += 1 # Use this count
				#print item, keyword
				if item.find(keyword) >= 0:
					key_cnt += 1
	#print total_cnt, tmp_total_cnt, key_cnt
	return tmp_total_cnt, key_cnt

def keyword_distribution(keyword, cwe_id=None):
	# Files containing the keyword and the count
	orig_diff_dir = os.path.join(orig_dir, 'all_diff')
	cve_alldiff_dirs = os.listdir(orig_diff_dir) # all diff
	orig_minus_dir = os.path.join(orig_dir, 'minus')
	if os.path.exists(orig_minus_dir):
		cve_minus_dirs = os.listdir(orig_minus_dir) # minus
	else:
		cve_minus_dirs = []

	orig_plus_dir = os.path.join(orig_dir, 'plus')
	if os.path.exists(orig_plus_dir):
		cve_plus_dirs = os.listdir(orig_plus_dir) # plus
	else:
		cve_plus_dirs = []

	orig_dirs = [ orig_diff_dir, orig_minus_dir, orig_plus_dir]
	cve_dirs = [cve_alldiff_dirs, cve_minus_dirs, cve_plus_dirs]
	INDEX = 0 # Choose all_diff, minus or plus
	for sub_dir in cve_dirs[INDEX]:
		if cwe_id and sub_dir != str(cwe_id):
			continue
		cve_dir_path = os.path.join(orig_dirs[INDEX], sub_dir)
		files = os.listdir(cve_dir_path)
		file_cnt = 0
		file_freq = []
		dir_total_cnt = 0
		dir_key_cnt = 0
		for s_file in files:
			s_file_path = os.path.join(cve_dir_path, s_file)
			cmd = 'cat %s | grep -i %s | wc -l' % (s_file_path, keyword)
			ret = commands.getstatusoutput(cmd)
			if ret[0] != 0: # Cmd failed
				continue
			if ret[1] == '0': # count of keyword is 0
				continue
			file_cnt += 1
			file_freq.append(int(ret[1]))

			file_total_cnt, file_key_cnt = file_totalcnt_keycnt(s_file_path, keyword)
			dir_total_cnt += file_total_cnt
			dir_key_cnt += file_key_cnt

		key_cnt = sum(file_freq)
		if dir_total_cnt  == 0:
			tf = 0
		else:
			tf = float(dir_key_cnt)/dir_total_cnt
		df = float(file_cnt)/len(files)
		#print '-- ', sub_dir, len(files), file_cnt, file_freq, sum(file_freq), dir_total_cnt, dir_key_cnt, tf, df
		print '-- ', keyword, sub_dir, round(tf,3), round(df,3), round(tf*df, 4)
		return	keyword, sub_dir, round(tf,3), round(df,3), round(tf*df, 4)


def get_keywords(file_path):
	keywords = []
	fd = open(file_path)
	lines = fd.readlines()
	for line in lines:
		if line.strip() == "": continue 
		keyword= line.split(' ')[0].strip()
		keywords.append(keyword)

	fd.close()
	return keywords


if __name__ == "__main__" : 

	# Step 1: Preprocess: Put all diffs of a CVE category into one file, required
	# Only execute once
	# preprocess() # Save the whole diff, '-' and '+' part into big files
	# preprocess_each_orig_file() # Save the whole diff, '-' and '+' part into small files
	#exit(0)


	# Step 2: split the CVE file into tokens, required
	#(all_file,path) = get_file_list(preprocessed_dir)
	#for ff in all_file:
		#split_file(ff, path)
	#	 split_file_new(ff, path)
	#exit(0)

	# Step 3: Compute TF-IDF of tokens for each CVE category, required
	#Tfidf(all_file) # Not used now
	#tf(all_file)
	#exit(0)
	
	exit(0)

	# Test 
	if True:
		full_keywords = ['buf', 'len', 'data', 'mem', 'read', 'write', 'rw', 'io', 'free']
		#full_keywords = get_keywords("/home/cuilei/code_sim/VulDetector/Data/outputs/openssl/test_keywords/stat_data/tffile/399.c.txt")
		full_keywords = get_keywords("/home/cuilei/code_sim/VulDetector/Data/outputs/openssl/test_keywords_linux/stat_data/tffile/200.c.txt")
		#keywords = ['\&\&', 'print']
		print len(full_keywords)
		keyword_tfs = []
		for key in full_keywords:
			ret = keyword_distribution(key, 200) # cwe id is associated with file_path in get_keywords
			keyword_tfs.append(ret)
	
		print 'RET'
		for ret in keyword_tfs:
			print ret
		exit(0)
	#------- Test End ------#
