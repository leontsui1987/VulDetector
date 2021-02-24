import os

DEBUG_TIME = 0

DUMP_GRAPH = 0
# 
DEBUG_INFO = 0
DEBUG = 0
DEBUG_WARN = 2
DEBUG_ERROR = 3
g_level = DEBUG_INFO
#g_level = DEBUG_ERROR

LOAD_GLOBAL_GRAPH=True

# -----------Modify parameters here ----------------- #
USE_WEIGHT = 1 # default is 1

WEIGHT_PRED_RATIO = 0.85 # decay ratio: predecessor
WEIGHT_SUCC_RATIO = 0.85  # decay ratio: successor
GRAPH_PRED_DEPTH = 5   # graph depth: predecessor
GRAPH_SUCC_DEPTH = 5   # graph depth: successor
# ------------------------------ #



# Graph and src file directory
GRAPH_DIR  = '/home/cuilei/dataset/code_sim/openssl/graphs'
FUNC_DIR = '/home/cuilei/dataset/code_sim/openssl/small_funcs'

FIXED_GRAPH_DIR	 = '/home/cuilei/dataset/code_sim/openssl/fixed_graphs'
FIXED_FUNC_DIR = '/home/cuilei/dataset/code_sim/openssl/fixed_funcs'

# Output directory
INPUT_DIR = '/home/cuilei/code_sim/VulDetector/Data/inputs'
OUTPUT_DIR = '/home/cuilei/code_sim/VulDetector/Data/outputs'

# Store the sub graphs of functions
GRAPH_DICT_PATH = '/home/cuilei/dataset/code_sim/openssl/global_dict'

# Mode of code representations
GRAPH=1
STRING=2
TREE=3
SIMIAN=4
CPD=5
REDEBUG=6
NICAD=7

# Test mode
ACROSS_VERSIONS = 1
ACROSS_CVES = 2
ACROSS_ALLFILES = 3
ACROSS_APPLICATIONS = 4
ACROSS_APP_ALLFILES = 5


weight_path = '/tmp/weight'
def update_weight(pred_depth, succ_depth, pred_ratio, succ_ratio):
	global WEIGHT_PRED_RATIO
	global WEIGHT_SUCC_RATIO
	global GRAPH_PRED_DEPTH
	global GRAPH_SUCC_DEPTH
	WEIGHT_PRED_RATIO = pred_ratio
	WEIGHT_SUCC_RATIO = succ_ratio
	GRAPH_PRED_DEPTH = pred_depth
	GRAPH_SUCC_DEPTH = succ_depth
	with open(weight_path, 'w+') as fd:
		fd.write(repr([pred_ratio, succ_ratio, pred_depth, succ_depth]))


def load_weight():
	global WEIGHT_PRED_RATIO
	global WEIGHT_SUCC_RATIO
	global GRAPH_PRED_DEPTH
	global GRAPH_SUCC_DEPTH
	if not os.path.exists(weight_path): return WEIGHT_PRED_RATIO, WEIGHT_SUCC_RATIO, GRAPH_PRED_DEPTH, GRAPH_SUCC_DEPTH
	with open(weight_path, 'r') as fd:
		ret= eval(fd.read())
		#print ret 
	WEIGHT_PRED_RATIO = ret[0]
	WEIGHT_SUCC_RATIO = ret[1]
	GRAPH_PRED_DEPTH = ret[2]
	GRAPH_SUCC_DEPTH = ret[3]
	return WEIGHT_PRED_RATIO, WEIGHT_SUCC_RATIO, GRAPH_PRED_DEPTH, GRAPH_SUCC_DEPTH

def debug_print(level, content):
	if level < g_level:
		return

	if level == DEBUG_INFO:
		print "INFO: ", content
	elif level == DEBUG_WARN:
		print 'WARNING: ', content
	elif level == DEBUG_ERROR:
		print 'ERROR: ', content
	elif level == DEBUG:
		print 'DEBUG: ', content
	else:
		pass
