#!/bin/python

# =================================================================================
# Copyright 2020 IIE, CAS
#
# This file automatically processes the CFG generation, sourcecode generation from projects
# Input: the directory of projects file
#
# Author: Lei Cui
# Contact: cuilei@iie.ac.cn
# =================================================================================

import os
import sys
import time
import threading
import commands

lock = threading.Lock()
failed_versions = []

CFG_CMD = 0 # scan-build -enable-checker debug.DumpCFG make 2> ./tmp.log
GRAPH_CMD = 1 # python ***/extract_scanbuild.py src_code/version/tmp.log  output_dir/version
SMALL_FUNC_CMD = 2 # python **/extract_func.py **/version  output_dir/version **/version

OUTPUT_DIR = "/home/cuilei/dataset/code_sim/"

def handle_one_version(version_dir, versions, cmd, cmd_id=0):
	global lock
	global failed_versions
	software_name = 'qemu'
	while len(versions):
		lock.acquire()
		if len(versions) == 0: break
		cur_version = versions[0]
		versions.remove(cur_version)  # delete the version
		lock.release()

		version_path = os.path.join(version_dir, cur_version)
		os.chdir(version_path)
		start = time.time()
		if cmd_id == CFG_CMD:
			ret = commands.getstatusoutput(cmd)
		elif cmd_id == GRAPH_CMD:
			log_path = os.path.join(version_path, 'tmp.log')
			output_dir = os.path.join(OUTPUT_DIR, software_name, 'graphs')#"/home/cuilei/dataset/code_sim/%s/graphs" % software_name
			output_ver_dir = os.path.join(output_dir, cur_version)
			if not os.path.exists(output_ver_dir):
				os.mkdir(output_ver_dir)
			exe_cmd = "%s %s %s" % (cmd, log_path, output_ver_dir)
			print '++++++ ', exe_cmd 
			ret = commands.getstatusoutput(exe_cmd)
		elif cmd_id == SMALL_FUNC_CMD:
			output_dir = os.path.join(OUTPUT_DIR, software_name, 'small_funcs') #"/home/cuilei/dataset/code_sim/%s/small_funcs" % software_name
			output_ver_dir = os.path.join(output_dir, cur_version)
			if not os.path.exists(output_ver_dir):
				os.mkdir(output_ver_dir)
			exe_cmd = "%s %s %s %s" % (cmd, version_path, output_ver_dir, version_path)
			print '+++++++ ', exe_cmd
			ret = commands.getstatusoutput(exe_cmd)

		else:
			print 'Use formated cmd'

		end = time.time()
		#print "Version: %s, Time: %s" % (cur_version, end-start)
		if ret[0] != 0: 
			failed_versions.append(cur_version)
			print "Fail. Version: %s, Cmd: %s, Ret: %s " % (cur_version, cmd, ret[0])
		else:
			print "Success. Version: %s" % (cur_version)

		time.sleep(1)


def main():
	app_dir = sys.argv[1]
	sub_dirs = os.listdir(app_dir)
	print sub_dirs
	sub_dirs = ['qemu-2.6.0', 'qemu-2.10.0', 'qemu-3.1.0'] # Provide your own project directory
	print sub_dirs

	config_cmd = "scan-build ./config"
	#test_cmd = "ls -l ./config"
	make_cmd = "scan-build -enable-checker debug.DumpCFG make 2> tmp.log"  # Generate CFG description using clang
	graph_cmd = "python /home/cuilei/code_sim/VulDetector/Codes/DataPrepare/extract_cfg_desc.py " # Generate CFGs for each function
	small_func_cmd = "python /home/cuilei/code_sim/VulDetector/Codes/DataPrepare/extract_func.py " # Generate sourcecode for each function

	THREAD_CNT = 12
	threads = []
	for i in range(THREAD_CNT):
		# Uncomment when executing the desired cmd

		#thread = threading.Thread(target=handle_one_version, args=(app_dir, sub_dirs, config_cmd, CFG_CMD) )
		#thread = threading.Thread(target=handle_one_version, args=(app_dir, sub_dirs, make_cmd, CFG_CMD) )
		#thread = threading.Thread(target=handle_one_version, args=(app_dir, sub_dirs, graph_cmd, GRAPH_CMD) )
		thread = threading.Thread(target=handle_one_version, args=(app_dir, sub_dirs, small_func_cmd, SMALL_FUNC_CMD) )
		time.sleep(0.4)


		threads.append(thread)
		thread.start()	

	for thread in threads:
		thread.join()	

	print 'Finish'
	print failed_versions
	print len(failed_versions)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "batch_process.py <project directory>"
		exit(-1)
	#exit(0)
	main()
