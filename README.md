# VulDetector


## Description
* This project is for vulnerability detection using graph similarity.

## NOTE
* Sorry that the source code is unavaiable for a while. The previous project contained too much snippets and scripts for testing, so we are cleaning these code and making it modular to facilitate usage. In addition, we got many 'TabError' when deploying it in a new environment, and we are fixing these issues.  

## Modules
* CVECollect: Collect the {program, filename, functionname} of known vulnerabilities.
* DataPrepare: Extract function codes and CFGs from a program.
* SenLocate: Locate the sensitive lines.
* DataParse: Generate WFGs from CFGs.
* SimCompare: Compute the similarity of two WFGs
