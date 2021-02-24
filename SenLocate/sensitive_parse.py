#/bin/python

# =================================================================================
# Copyright 2020 IIE, CAS
#
# This file locates the sensitive lines given sourcecode of a function
# Input: The sourecode of a function
# Output: Located sensitive line and matched keyword
#
# Author: Lei Cui
# Contact: cuilei@iie.ac.cn
# =================================================================================

import sys

#global keywords
keywords = ["memcpy", "strcpy", "read", "free", "buf" ] #NOTE: Define your own keywords here

def contain_keywords(string):
	global keywords
	for keyword in keywords:
		if string.find(keyword) >= 0:
			return keyword
	return None

def extract_sensitive_keywords(src_file):
	fd = open(src_file, 'r')
	lines = fd.readlines()
	
	sensitive_ret = []
	for index in range(2, len(lines)): # line 1 and 2 normally are function name
		line = lines[index]
		ret = contain_keywords(line) # NOTE: optimize here later
		if ret:
			sensitive_ret.append( [index+1, ret] ) # nOTE: +1
	return sensitive_ret


def vulnerable_file(src_file):
	if src_file.find('vulnerable') >= 0:
		return True
	return False


def extract_sensitive_lines(src_file):
# For known vulnerable codes, vulnerable line is given
# For testing codes, sensitive lines are provided
	if vulnerable_file(src_file):
		pass
	# Line is provided in the name?

	sensitive_lines = extract_sensitive_keywords(src_file)
	sen_lines = [val[0] for val in sensitive_lines]  # val format is [line_no, keywords]
	#print sen_lines
	return sen_lines



if __name__ == "__main__":
	
	sen_ret = extract_sensitive_keywords(sys.argv[1])
	print 'matched keyword and line: ', sen_ret
