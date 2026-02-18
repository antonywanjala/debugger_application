import os
import shutil
import time


# ==========================================
# 1. THE LOGGER HEADER (V11.0 - Column E Overflow Fix)
# ==========================================
def generate_header():
    return """
# ==========================================
# FUNCTION-LOCAL VARIABLE TRACKER (V11.0)
# ==========================================
import datetime
import sys
import os
import builtins  
import csv
import types
import inspect

_AD_DEBUG_ACTIVE = True
_ORIGINAL_PRINT = builtins.print  

if not hasattr(builtins, '_PROJECT_BASELINE_VARS'):
    builtins._PROJECT_BASELINE_VARS = set(globals().keys()) | set(dir(builtins))

def _reset_logs():
    try:
        with open("_VARIABLE_TRACKER.csv", "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL) # Force quoting on all fields
            writer.writerow(["File", "Line", "Variable", "Value"])
    except: pass

if not hasattr(builtins, '_AD_LOGS_WIPED'):
    _reset_logs()
    builtins._AD_LOGS_WIPED = True

def _record_state(file_path, line_no, local_vars):
    if not _AD_DEBUG_ACTIVE: return
    try:
        current_frame = inspect.currentframe().f_back
        if current_frame.f_code.co_name == '<module>':
            return

        baseline = getattr(builtins, '_PROJECT_BASELINE_VARS', set())

        with open("_VARIABLE_TRACKER.csv", "a", encoding="utf-8", newline='') as f:
            # Using QUOTE_ALL ensures that even numbers are wrapped in "", 
            # preventing Column E overflow.
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)

            for var_name, var_val in local_vars.items():
                if var_name.startswith('_') or var_name in baseline: 
                    continue 

                if isinstance(var_val, (type, types.FunctionType, types.ModuleType, types.MethodType)):
                    continue

                # --- ADVANCED SANITIZATION FOR COLUMN E OVERFLOW ---
                # Convert to string and replace literal newlines/carriages
                val_str = str(var_val).replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' ')

                # Remove brackets and quotes which are the primary cause of the "None]" artifact
                # This ensures the data cannot be misinterpreted as a multi-column array.
                sanitized_val = val_str.replace("'", "").replace("[", "").replace("]", "").strip()

                if not sanitized_val:
                    sanitized_val = "None"

                # Construct the rigid 4-column row
                row = [
                    os.path.basename(file_path),
                    line_no,
                    var_name,
                    sanitized_val
                ]

                writer.writerow(row)
    except: pass

def _ad_script_output(msg, is_error=True):
    if not _AD_DEBUG_ACTIVE: return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[DEBUG_ERROR] [{timestamp}] {msg}" if is_error else f"[SCRIPT] {msg}"
    _ORIGINAL_PRINT(formatted)
    for f_name in ["_DEBUG_ONLY.txt", "_COMBINED_LOG.txt"] if is_error else ["_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt"]:
        try:
            with open(f_name, "a", encoding="utf-8") as f: f.write(formatted + "\\n")
        except: pass

def print(*args, **kwargs):
    output = " ".join(map(str, args))
    _ad_script_output(output, is_error=False)
# ==========================================
"""


# ==========================================
# 2. THE PRE-PROCESSOR (Logic unchanged)
# ==========================================
def clean_source(source):
    result, i, n = [], 0, len(source)
    quote_type, in_comment, last_valuable_char, preserve_triple = None, False, "", False
    while i < n:
        char = source[i]
        if in_comment:
            if char == '\n': in_comment = False; result.append('\n')
            i += 1;
            continue
        if quote_type:
            if quote_type in ('"""', "'''"):
                if source[i:i + 3] == quote_type:
                    if preserve_triple: result.append(quote_type)
                    quote_type = None;
                    i += 3;
                    continue
                else:
                    if preserve_triple: result.append(char)
                    i += 1
            else:
                if char == quote_type and (i == 0 or source[i - 1] != '\\'):
                    result.append(char);
                    quote_type = None
                else:
                    result.append(char)
                i += 1
            continue
        if source[i:i + 3] in ('"""', "'''"):
            quote_type = source[i:i + 3]
            preserve_triple = (last_valuable_char == '=')
            if preserve_triple: result.append(quote_type)
            i += 3
        elif char in ('"', "'"):
            quote_type = char;
            result.append(char);
            i += 1
        elif char == '#':
            in_comment = True;
            i += 1
        else:
            if not char.isspace(): last_valuable_char = char
            result.append(char);
            i += 1
    return "".join(result)


# ==========================================
# 3. THE INJECTION ENGINE
# ==========================================
def inject_into_file(file_path, max_depth=3):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        clean_content = clean_source(raw_content)
        lines = clean_content.splitlines()
        new_content = [generate_header()]
        bracket_level, in_triple_quote = 0, False

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                new_content.append(line);
                continue

            triple_count = line.count('"""') + line.count("'''")
            starts_or_ends_triple = triple_count % 2 != 0
            indent_len = len(line) - len(line.lstrip())
            indent_str = line[:indent_len]

            prev_level = bracket_level
            bracket_level += (line.count('(') + line.count('[') + line.count('{'))
            bracket_level -= (line.count(')') + line.count(']') + line.count('}'))

            structural_keywords = ('def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ',
                                   'with ', 'try:', 'except', 'finally:', '@', 'import ', 'from ')
            is_structural = any(stripped.startswith(k) for k in structural_keywords) or stripped.endswith(':')

            if (not in_triple_quote and prev_level == 0 and bracket_level == 0 and
                    not is_structural and (indent_len // 4) <= max_depth):

                if stripped in (")", "]", "}", "),", "],", "},") or starts_or_ends_triple:
                    new_content.append(line)
                else:
                    new_content.append(f"{indent_str}try:")
                    new_content.append(f"{indent_str}    {stripped}")
                    new_content.append(f"{indent_str}    _record_state(__file__, {i + 1}, locals())")
                    new_content.append(f"{indent_str}except Exception as e:")
                    new_content.append(
                        f"{indent_str}    _ad_script_output(f'Line {i + 1} Failed: {{e}}', is_error=True)")
            else:
                new_content.append(line)

            if starts_or_ends_triple: in_triple_quote = not in_triple_quote

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_content))
        return True
    except Exception as e:
        print(f"Injection Error: {e}");
        return False


# ==========================================
# 4. RUNNER
# ==========================================
def process_project(source_dir, max_depth):
    target_dir = source_dir.rstrip('\\/') + f"_DEBUG_STATE_{int(time.time())}"
    if not os.path.exists(target_dir): os.makedirs(target_dir)
    print(f"\n[START] Building project with function-only variable tracking...")
    for root, _, files in os.walk(source_dir):
        if any(x in root for x in ['venv', '.git', '__pycache__']): continue
        for file in files:
            if file.endswith(".py"):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                inject_into_file(dst, max_depth)
                print(f"  Instrumented: {file}")
    print(f"\n[FINISH] Project ready at: {target_dir}")


if __name__ == "__main__":
    p = input("Project Path: ").strip().strip('"')
    try:
        d = int(input("Max Depth (default 3): ").strip() or 3)
    except:
        d = 3
    if os.path.isdir(p):
        process_project(p, d)
    else:
        print("Invalid path.")
