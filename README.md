Syntax Error Detection, Correction, and Verification Tool (Restricted C Subset)An automated compiler design tool for detecting, localizing, auto-correcting, and re-parse verifying syntax errors in a restricted subset of the C programming language.Developed for Compiler Design Lab Assessment – 10 at Vellore Institute of Technology (VIT).📌 Project OverviewTraditional compilers halt execution and produce error logs when syntax errors are encountered. This tool introduces a closed-loop automated recovery pipeline:Detection & Localization: Tokenizes restricted C code and identifies line-by-line syntax errors (missing semicolons, unbalanced parentheses, or brace mismatches).Rule-Based Repair Engine: Applies fast, deterministic heuristics to correct common syntax violations.Verification Engine (gcc -fsyntax-only): Invokes standard GCC compilation flags via subprocess execution to guarantee that proposed fixes result in valid, compilable C syntax.LLM Fallback Architecture: Categorizes complex or ambiguous syntax errors (e.g., keyword typos, malformed expressions) that fail rule-based repair as candidate cases for LLM-assisted repair.🛠️ Project Structurec-syntax-corrector/
├── src/
│   └── main.py          # Main parser, repair heuristics, and GCC verification pipeline
├── tests/
│   ├── test1.c          # Missing semicolon test
│   ├── test2.c          # Missing closing parenthesis in 'if' condition
│   ├── test3.c          # Missing opening parenthesis in 'if' condition
│   ├── test4.c          # Missing closing curly brace
│   ├── test5.c          # Missing semicolon on variable assignment
│   ├── test6.c          # Failure Case: Missing semicolon on return statement
│   ├── test7.c          # Failure Case: Invalid type keyword ('integer')
│   ├── test8.c          # Failure Case: Malformed arithmetic expression
│   ├── test9.c          # Multiple missing semicolons
│   └── test10.c         # Compound syntax errors
└── README.md            # Project documentation
📋 PrerequisitesPython 3.8+GCC Compiler (must be accessible from system PATH)Check prerequisites by running:python --version
gcc --version
🚀 Execution Guide1. Run a Single Test CaseTo run error detection, correction, and verification on a single test file:python src/main.py tests/test1.c
2. Run Full Benchmark Test Suite (Batch Mode)To execute all 10 test cases in sequence and output a summary metric:python src/main.py all
📊 Evaluation SummaryMetricMeasured ValueTotal Test Cases Executed10Error Localization Accuracy100% (10/10)Verified Rule-Based Fix Rate70% (7/10)LLM Fallback Candidate Rate30% (3/10)Deterministic Successes (T01-T05, T09, T10): Semicolons and parentheses auto-repaired and verified by GCC.Failure Cases (T06-T08): Complex/Ambiguous syntax errors intentionally unhandled by rule heuristics to evaluate system fallback capabilities.👤 AuthorAarav SinhaVellore Institute of Technology
