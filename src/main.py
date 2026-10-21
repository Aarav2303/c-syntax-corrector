import re
import os
import sys
import subprocess

# --- 1. LEXER & PARSER ENGINE ---
def analyze_syntax(code_str):
    lines = code_str.splitlines()
    for line_num, line in enumerate(lines, 1):
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("//"):
            continue
            
        if (trimmed.startswith("int ") or ("=" in trimmed and not trimmed.startswith("if"))) and not trimmed.endswith(";") and not trimmed.endswith("{") and not trimmed.endswith("}"):
            return False, line_num, f"Missing semicolon ';' at line {line_num}"
            
        if trimmed.startswith("if") and "(" in trimmed and ")" not in trimmed:
            return False, line_num, f"Missing closing parenthesis ')' in condition at line {line_num}"

        if trimmed.startswith("if") and "(" not in trimmed and ")" in trimmed:
            return False, line_num, f"Missing opening parenthesis '(' in condition at line {line_num}"

    if code_str.count('{') != code_str.count('}'):
        return False, len(lines), "Mismatched curly braces '{' / '}'"

    return True, None, "No syntax errors detected by internal rules."

# --- 2. VERIFICATION ENGINE ---
def verify_code(code_str):
    is_valid, line, err = analyze_syntax(code_str)
    
    temp_file = "_temp_check.c"
    try:
        with open(temp_file, "w") as f:
            f.write(code_str)
        
        result = subprocess.run(["gcc", "-fsyntax-only", temp_file], capture_output=True, text=True)
        if result.returncode == 0:
            return True, "GCC Syntax Check PASSED"
        else:
            return False, f"GCC Error: {result.stderr.strip().splitlines()[0] if result.stderr else 'Syntax Error'}"
    except FileNotFoundError:
        if is_valid:
            return True, "Internal Parser Check PASSED"
        return False, f"Internal Parser Error: {err}"
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

# --- 3. RULE-BASED CORRECTION ENGINE ---
def apply_rule_based_fix(code_str):
    lines = code_str.splitlines()
    fixed_lines = []

    for line in lines:
        trimmed = line.strip()
        fixed = line

        if (trimmed.startswith("int ") or ("=" in trimmed and not trimmed.startswith("if"))) and not trimmed.endswith(";") and not trimmed.endswith("{") and not trimmed.endswith("}"):
            fixed = line + ";"
        elif trimmed.startswith("if") and "(" in trimmed and ")" not in trimmed:
            if "{" in line:
                fixed = line.replace("{", ") {")
            else:
                fixed = line + ")"
        elif trimmed.startswith("if") and "(" not in trimmed and ")" in trimmed:
            fixed = line.replace("if ", "if (")

        fixed_lines.append(fixed)

    result_code = "\n".join(fixed_lines)
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
        return False, False

    with open(filepath, "r") as f:
        original_code = f.read()

    print("\n--- ORIGINAL SOURCE CODE ---")
    print(original_code)
    print("-" * 30)

    is_valid, err_msg = verify_code(original_code)
    if is_valid:
        print("\n[RESULT] Source code is already valid! No corrections needed.")
        return True, True

    print(f"\n[DETECTED ERROR]: {err_msg}")
    print("\nAttempting Rule-Based Correction...")
    corrected_code = apply_rule_based_fix(original_code)

    print("\n--- PROPOSED CORRECTION ---")
    print(corrected_code)
    print("-" * 30)

    verified, ver_msg = verify_code(corrected_code)
    if verified:
        print(f"\n[VERIFICATION SUCCESSFUL]: {ver_msg}")
        print("Status: Fixed and Verified!")
        return True, True
    else:
        print(f"\n[VERIFICATION FAILED]: {ver_msg}")
        print("Status: Unresolved by rule-engine (Requires LLM fallback).")
        return True, False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "all":
        process_file(sys.argv[1])
    else:
        # Batch execution over tests directory
        test_dir = "tests"
        if os.path.exists(test_dir):
            files = [os.path.join(test_dir, f) for f in os.listdir(test_dir) if f.endswith('.c')]
            files.sort(key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)
            
            passed = 0
            total = len(files)
            
            for f in files:
                det, ver = process_file(f)
                if ver:
                    passed += 1
                print("\n")
                
            print("=" * 60)
            print(f"BATCH SUMMARY: {passed}/{total} Test Cases Verified Successfully")
            print("=" * 60)