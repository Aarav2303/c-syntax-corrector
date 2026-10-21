import re
import os
import sys
import subprocess

# --- 1. LEXER & PARSER ENGINE ---
TOKENS = [
    ('INT', r'\bint\b'),
    ('IF', r'\bif\b'),
    ('RETURN', r'\breturn\b'),
    ('NUMBER', r'\b\d+\b'),
    ('ID', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('ASSIGN', r'='),
    ('SEMI', r';'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('OP', r'[><=!+*-]+'),
    ('SKIP', r'[ \t\r\n]+'),
]

def analyze_syntax(code_str):
    """
    Parses restricted C subset line-by-line to detect syntax errors.
    Returns (is_valid, error_line, error_message).
    """
    lines = code_str.splitlines()
    for line_num, line in enumerate(lines, 1):
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("//"):
            continue
            
        # Check missing semicolon on statements
        if (trimmed.startswith("int ") or ("=" in trimmed and not trimmed.startswith("if"))) and not trimmed.endswith(";") and not trimmed.endswith("{") and not trimmed.endswith("}"):
            return False, line_num, f"Missing semicolon ';' at line {line_num}"
            
        # Check unmatched opening parenthesis in 'if' condition
        if trimmed.startswith("if") and "(" in trimmed and ")" not in trimmed:
            return False, line_num, f"Missing closing parenthesis ')' in condition at line {line_num}"
            
        # Check unmatched closing parenthesis in 'if' condition
        if trimmed.startswith("if") and "(" not in trimmed and ")" in trimmed:
            return False, line_num, f"Missing opening parenthesis '(' in condition at line {line_num}"

    # Check balanced braces across entire file
    if code_str.count('{') != code_str.count('}'):
        return False, len(lines), "Mismatched curly braces '{' / '}'"

    return True, None, "No syntax errors detected."


# --- 2. VERIFICATION ENGINE ---
def verify_code(code_str):
    """
    Verifies code using GCC if available, otherwise uses internal parser.
    """
    # Quick internal parser verification
    is_valid, line, err = analyze_syntax(code_str)
    if not is_valid:
        return False, f"Internal Parser Error: {err}"

    # Try GCC syntax check (-fsyntax-only) if GCC is installed
    temp_file = "_temp_check.c"
    try:
        with open(temp_file, "w") as f:
            f.write(code_str)
        
        result = subprocess.run(["gcc", "-fsyntax-only", temp_file], capture_output=True, text=True)
        if result.returncode == 0:
            return True, "GCC Syntax Check PASSED"
        else:
            return False, f"GCC Error: {result.stderr.strip()}"
    except FileNotFoundError:
        # GCC not installed on system; rely on internal parser pass
        return True, "Internal Parser Check PASSED (GCC not found)"
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


# --- 3. RULE-BASED CORRECTION ENGINE ---
def apply_rule_based_fix(code_str):
    """
    Applies deterministic pattern fixes for restricted C syntax errors.
    """
    lines = code_str.splitlines()
    fixed_lines = []

    for line in lines:
        trimmed = line.strip()
        fixed = line

        # Rule 1: Missing Semicolon
        if (trimmed.startswith("int ") or ("=" in trimmed and not trimmed.startswith("if"))) and not trimmed.endswith(";") and not trimmed.endswith("{") and not trimmed.endswith("}"):
            fixed = line + ";"

        # Rule 2: Missing ')' in if-statement
        elif trimmed.startswith("if") and "(" in trimmed and ")" not in trimmed:
            if "{" in line:
                fixed = line.replace("{", ") {")
            else:
                fixed = line + ")"

        # Rule 3: Missing '(' in if-statement
        elif trimmed.startswith("if") and "(" not in trimmed and ")" in trimmed:
            fixed = line.replace("if ", "if (")

        fixed_lines.append(fixed)

    result_code = "\n".join(fixed_lines)

    # Rule 4: Missing Closing Brace
    if result_code.count('{') > result_code.count('}'):
        result_code += "\n}"

    return result_code


# --- 4. MAIN PIPELINE ---
def process_file(filepath):
    print("=" * 60)
    print(f"PROCESSING FILE: {filepath}")
    print("=" * 60)

    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return

    with open(filepath, "r") as f:
        original_code = f.read()

    print("\n--- ORIGINAL SOURCE CODE ---")
    print(original_code)
    print("-" * 30)

    # Step 1: Detect Initial Syntax Error
    is_valid, err_msg = verify_code(original_code)
    if is_valid:
        print("\n[RESULT] Source code is already valid! No corrections needed.")
        return

    print(f"\n[DETECTED ERROR]: {err_msg}")

    # Step 2: Attempt Rule-Based Fix
    print("\nAttempting Rule-Based Correction...")
    corrected_code = apply_rule_based_fix(original_code)

    print("\n--- PROPOSED CORRECTION ---")
    print(corrected_code)
    print("-" * 30)

    # Step 3: Re-parse Verification
    verified, ver_msg = verify_code(corrected_code)
    if verified:
        print(f"\n[VERIFICATION SUCCESSFUL]: {ver_msg}")
        print("Status: Fixed and Verified!")
    else:
        print(f"\n[VERIFICATION FAILED]: {ver_msg}")
        print("Status: Core rules failed. (LLM fallback triggering option)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file(sys.argv[1])
    else:
        print("Usage: python src/main.py <path_to_c_file>")