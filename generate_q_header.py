# -*- coding: utf-8 -*-
# ==============================================================================
# K & Q (kdb+) SCRIPT INSTRUMENTATION & DEBUGGER (V1.0)
# ==============================================================================
import os
import shutil
import time

def generate_q_header():
    """Generates Q/K native header routines for log management and output tracking."""
    return """/ ==============================================================================
/ K/Q INSTRUMENTATION HEADER - STATE TRACKER
/ ==============================================================================
\\d .debug

/ Initialize logging paths
debugLog: ":_DEBUG_ONLY.txt"
scriptLog: ":_SCRIPT_ONLY.txt"
combinedLog: ":_COMBINED_LOG.txt"
varLog: ":_VARIABLE_TRACKER.csv"

/ Helper to append lines to files
appendFile: {[path; text] path hopen text, "\\n"; hclose path}

/ Reset logs on startup
resetLogs: {[x]
    (hsym debugLog) 0: enlist "--- SESSION START: ", string .z.p;
    (hsym scriptLog) 0: enlist "--- SESSION START: ", string .z.p;
    (hsym combinedLog) 0: enlist "--- SESSION START: ", string .z.p;
    (hsym varLog) 0: enlist "Line,Variable,Value";
    }[]

/ Capture and log errors
logErr: {[lineNo; errStr]
    msg: "[DEBUG_ERROR] [", (string .z.p), "] Line ", (string lineNo), " Failed: ", errStr;
    0N! msg;
    (hsym debugLog) 0: enlist msg;
    (hsym combinedLog) 0: enlist msg;
    }

/ Capture script outputs
logScript: {[msg]
    formatted: "[SCRIPT] ", string msg;
    (hsym scriptLog) 0: enlist formatted;
    (hsym combinedLog) 0: enlist formatted;
    }

\\d .
/ ==============================================================================
"""


def inject_into_q_file(file_path):
    """Parses and instruments .q and .k files with error traps and logging."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Phase 1: Clean non-breaking space variants globally
        raw_content = raw_content.replace('\xa0', ' ').replace('\u00a0', ' ')
        raw_lines = raw_content.splitlines()

        transformed_lines = []
        in_multiline_comment = False

        for idx, line in enumerate(raw_lines):
            stripped = line.strip()

            # Handle Q multi-line comment blocks (/ ... \)
            if stripped == "/":
                in_multiline_comment = True
                transformed_lines.append(line)
                continue
            elif stripped == "\\" and in_multiline_comment:
                in_multiline_comment = False
                transformed_lines.append(line)
                continue

            # Pass through comments, empty lines, and system commands (\d, \p, etc.)
            if in_multiline_comment or not stripped or stripped.startswith("/") or stripped.startswith("\\"):
                transformed_lines.append(line)
                continue

            # Do not wrap multiline function definitions or assignments ending in opening braces/parentheses
            if stripped.startswith("{") or stripped.endswith("{") or stripped.endswith("("):
                transformed_lines.append(line)
                continue

            # Phase 2: Instrument top-level expressions using Q string-evaluation error traps @[value; string; error_handler]
            line_num = idx + 1
            escaped_code = line.replace('"', '\"')
            
            # Constructs a safe error-trapped execution line in Q:
            # @[value; "line code"; {.debug.logErr[line_num; x]}]
            instrumented = f'@[value; "{escaped_code}"; {{ .debug.logErr[{line_num}; x] }}];'
            transformed_lines.append(instrumented)

        new_content = [generate_q_header()] + transformed_lines
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_content) + "\n")
        return True

    except Exception as e:
        print(f"Injection Error on {file_path}: {e}")
        return False


def process_q_project(source_dir):
    """Copies source folder into a debug sandbox and instruments all .q and .k files."""
    target_dir = source_dir.rstrip('\\/') + f"_Q_DEBUG_STATE_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    print("\n[START] Building instrumented kdb+ / Q project layout...")
    
    for root, _, files in os.walk(source_dir):
        # Ignore common version-control and build output directories
        if any(x in root for x in ['.git', '.qhome', 'tick', 'par']):
            continue

        for file in files:
            if file.endswith(".q") or file.endswith(".k"):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                
                if inject_into_q_file(dst):
                    print(f"    Instrumented: {file}")
                else:
                    print(f"    Failed: {file}")

    print(f"\n[FINISH] Safe kdb+/Q sandbox initialized at:\n{target_dir}")


if __name__ == "__main__":
    p = input("Q/K Project Path: ").strip().strip('"')
    if os.path.isdir(p):
        process_q_project(p)
    else:
        print("Invalid directory path.")
