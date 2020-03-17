# Documentation for FOparser

## Requirements
The program was written in Python 3.7.4 and uses the following libraries:  
sys, string, networkx, graphviz, pydot, matplotlib

graphviz must be installed using the [graphviz installer](https://graphviz.gitlab.io/_pages/Download/Download_windows.html). Individual libraries can be installed using `pip install library_name`.  
`C:\Program Files (x86)\Graphviz2.38\bin` must be added to system path in order for pydot to work.

## Running the program
The input file must be places in the same directory as the program file. The program can be run from the command line via:  
`python3 FOparser.py inputfile.txt`

If the input file is not specified, the program will prompt the user to give the name of the file. After executing the program, it will create a log file, `log.txt`, which will inform the user of any errors faced while reading the input file or parsing the formula. The log file only stores data for the last execution of the program.


If the input file is of the correct format, a grammar file, `grammar.txt`, will be produced which gives the sets of terminals, non-terminals and production rules. If any error occurs, the log file will clarify.


If the formula is valid, an abstract syntax tree will be given in `tree.png`. If the formula is found to be invalid, the log file will explain the error.

## Error Handling
The program has been tested to handle the following errors:
* Input File
  * Specified input file not found
  * Invalid set name in input file
  * Predicate with invalid arity
  * Duplicate name with variables, constants or predicates
  * Invalid number of elements specified for equality, connectives or quantifiers
* Formula
  * Invalid parenthesis
  * Invalid atoms
  * Incorrect use of predicate (missing parenthesis, conflicting arity)
  * Undefined symbol