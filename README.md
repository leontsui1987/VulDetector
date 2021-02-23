# VulDetector

## Description
* VulDetector is a static-analysis tool to detect C/C++ vulnerabilities based on graph comparison at the granularity of function. At the key of VulDetector is a weighted feature graph (WFG) model which characterizes function with a small yet semantically rich graph. It first pinpoints vulnerability-sensitive keywords to slice the control flow graph of a function, thereby reducing the graph size without compromising security-related semantics. Then, each sliced subgraph is characterized using WFG, which provides both syntactic and semantic features in varying degrees of security. Here we provide the key modules on WFG generation and comparison. 
* Please refer our [paper](https://ieeexplore.ieee.org/document/9309254) for more details. 
 

## NOTE
* Sorry that the source code is unavaiable for a while. The previous project contained too much snippets and scripts for testing, so we are cleaning these code and making it modular to facilitate usage. In addition, we got many 'TabError' when deploying it in a new environment, and we are fixing these issues.  

## Key Modules
* DataPrepare: Extract function codes and CFGs from a program.
* SenLocate: Locate the sensitive lines.
* WFGParse: Generate WFGs from CFGs.
* SimCompare: Compute the similarity of two WFGs


## Setup:
### Install packages
* Python packages (python2.7 currently): clang, matplotlib, hungarian
* sklearn is only required for determining keywords

### Setup LLVM
* Download sourcecode of LLVM-7.0.0
* Replace files of LLVM-7.0.0 with files in directory llvm-clang:
	* tools/clang/include/clang/Analysis/CFG.h<br>
	* tools/clang/lib/Analysis/CFG.cpp<br>
	* tools/clang/lib/AST/ASTDumper.cpp<br>
	* tools/clang/lib/StaticAnalyzer/Checkers/DebugCheckers.cpp<br>
* Build LLVM

* NOTE: Just compiling clang probably works, yet not tested. Make sure the existence of /usr/local/lib/libclang.so.6.0


## Usage
### CFG Description Generation
* Generate raw CFG description for a project (e.g., OpenSSL). 
* Output: The cfg_desc.log records the parsed CFGs for the entire project
	* 1. `cd input/OpenSSL`
	* 2. `scan-build -enable-checker debug.DumpCFG make 2> output/OpenSSL/cfg_desc.log`
*  NOTE: make sure using clang to compile the project

### CFG Extraction 
* Extract CFG description for each function from cfg_desc.log
* Input: generated cfg_desc.log in the above step
* Output: output/OpenSSL_cfg_dir now contains the CFGs for each function 
	* 1. `cd DataPrepare`
	* 2. `python extract_cfg_desc.py output/cfg_desc.log ./output/OpenSSL_cfg_dir/`
	*  Example: `python extract_cfg_desc.py  ../data/cfg_desc/cfg_desc.log  ../data/func_cfg/`
  
### Code Extraction 
* Extract raw code for each function from sourcecode
* Input: source code directory of the project
* Output: output/OpenSSL_code_dir now contains the raw code for each function
* 1. `cd DataPrepare`
* 2. `python extract_func.py input/OpenSSL/ output/OpenSSL_code_dir input/OpenSSL/`


### Sensitive Line Location 
* Get sensitive lines for a function
* Input: source code of a function
* Output: a list of matched keyword and line_no
	*  `cd SenLocate`
	* ` python sensitive_parse.py output/OpenSSL_code_dir/file_name`
	*  Example: `python sensitive_parse.py ../data/func_code/cms_smime.c#small#do_free_upto#126.c`
*  NOTE: You can provide your own keywords in sensitive_parse.py

### Generate WFG from CFG_desc and sourcecode
*  NOTE: You can i)use the full graph as WFG (no slicing), ii) provide sensitive_line_no by yourself, or iii) leave it automatically
*  cd WFGParse
*  i) python code2graph.py output/OpenSSL_cfg_dir/func_cfg no -1
*  Example: python code2graph.py ../data/func_cfg/cms_smime.c#do_free_upto  no -1
*  Output: Dump the node {lines, ast_feature, weight} of the WFG, meanwhile storing the WFG as dict into /tmp/
  
*  ii) python code2graph.py output/OpenSSL_cfg_dir/func_cfg output/OpenSSL_code_dir/func_code -1
*  Example: python code2graph.py ../data/func_cfg/cms_smime.c#do_free_upto  ../data/func_code/cms_smime.c#small#do_free_upto#126.c  -1
*  Output: Automated seach of sensitive lines, and generate WFG for each sensitive line.
  
*  iii) python code2graph.py output/OpenSSL_cfg_dir/func_cfg output/OpenSSL_code_dir/func_code line_no
*  Example: python code2graph.py ../data/func_cfg/cms_smime.c#do_free_upto  ../data/func_code/cms_smime.c#small#do_free_upto#126.c  7
*  Output: Use the line_no is arg as root line to generate WFG
  
*  NOTE: Two key parameters, i.e., weigh_depth and decay_ratio, can be modified in config.py
  

### Compare two WFG
*  cd SimCompare
*  python cfgcmp.py wfg1_file wfg2_file 
*  Example: python cfgcmp.py  ../data/wfgs/cms_smime.c#do_free_upto_-1  ../data/wfgs/cms_smime.c#do_free_upto_131


## Others:
* ./DataPrepare/stat_keywords.py is used to determine keywords for your own corpus
* ./DataPrepare/stat_ast_features.py is used to determine ast_features for your own corpus.
