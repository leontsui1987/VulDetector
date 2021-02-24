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


## Setup
### Install packages
* Python packages (python2.7 currently)
* Necessary: hungarian
* On-demand: 
	* sklearn is required for determining keywords in stat_keywords.py
	* matplotlib is required for drawing graphs in code2graph.py, commented now  

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
  
### Code Extraction 
* Extract raw code for each function from sourcecode
* Input: source code directory input/OpenSSL/ of the project
* Output: output/OpenSSL_code_dir now contains the raw code for each function
* Cmds
	* `cd DataPrepare`
	* `python2.7 extract_func.py input/OpenSSL/ output/OpenSSL_code_dir input/OpenSSL/`

### CFG Description Generation
* Generate raw CFG description for a project (e.g., OpenSSL). 
* Output: The cfg_desc.log records the parsed CFGs for the entire project
* Cmds
	* `cd input/OpenSSL`
	* `scan-build -enable-checker debug.DumpCFG make 2>  data/cfg_desc/cfg_desc.log`
*  NOTE: make sure using clang to compile the project

### CFG Extraction 
* Extract CFG description for each function from cfg_desc.log
* Input: generated cfg_desc.log in the above step
* Output: ../data/func_cfg now contains the CFGs for each function 
* Cmds
	* `cd DataPrepare`
	* `python2.7 extract_cfg_desc.py  ../data/cfg_desc/cfg_desc.log  ../data/func_cfg/`

### Sensitive Line Location 
* Get sensitive lines for a function
* Input: source code of a function
* Output: a list of matched keyword and line_no
* Cmds
	* `cd ../SenLocate`
	* `python2.7 sensitive_parse.py ../data/func_code/cms_smime.c#small#do_free_upto#126.c`
*  NOTE: You can provide your own keywords in sensitive_parse.py

### WFG Generation 
* Generate WFGs from CFG and sourcecode
* Input: cfg_file (necessary), code_file, and sensitive_line_no. The code_file and sensitive_line_no can be set 'no' for different requirements.
* Output: Dump the node {lines, ast_feature, weight} of the WFG, meanwhile storing the WFG as dict into ../data/wfgs
*  i) leave code_file as 'no' to use the full graph as WFG (no slicing)	
	*  `cd ../WFGParse`
	*  `python2.7 code2graph.py ../data/func_cfg/cms_smime.c#do_free_upto  no -1`
  
*  ii) leave sensitive_line_no as '-1' to automated seach sensitive lines and generate WFG for each sensitive line.
	*  `python2.7 code2graph.py ../data/func_cfg/cms_smime.c#do_free_upto  ../data/func_code/cms_smime.c#small#do_free_upto#126.c  -1`
  
*  iii) pass the specific sensitive_line_no to generate WFG
	*  `python2.7 code2graph.py ../data/func_cfg/cms_smime.c#do_free_upto  ../data/func_code/cms_smime.c#small#do_free_upto#126.c  7`
  
*  NOTE: Two key parameters, i.e., weigh_depth and decay_ratio, can be modified in config.py
  
### WFG Comparison
* Compute the similarity of two WFGs
* Input: WFG file path
* Output: Similarity
* Cmds
	*  `cd ../SimCompare`
	*  `python2.7 cfgcmp.py  ../data/wfgs/cms_smime.c#do_free_upto_-1  ../data/wfgs/cms_smime.c#do_free_upto_131`

### Others:
* ./DataPrepare/stat_keywords.py is used to determine keywords for your own corpus
* ./DataPrepare/stat_ast_features.py is used to determine ast_features for your own corpus.
