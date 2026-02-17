import os
import shutil
import datetime
import time

# ==========================================
# 1. THE LOGGER HEADER (V5.1 - Auto-Reset & Triple Log)
# ==========================================
def generate_header():
    return """
# ==========================================
# STRICT RECURSIVE WRAPPER (V5.1)
# ==========================================
import datetime
import sys
import os
import builtins  

_AD_DEBUG_ACTIVE = True
_ORIGINAL_PRINT = builtins.print  

# This wipes the logs fresh at the start of each execution
def _reset_logs():
    log_files = ["_DEBUG_ONLY.txt", "_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt"]
    for f_name in log_files:
        try:
            with open(f_name, "w", encoding="utf-8") as f:
                f.write(f"--- SESSION START: {datetime.datetime.now()} ---\\n")
        except: pass

# Global flag to ensure we only wipe logs once per session, even with imports
if not hasattr(builtins, '_AD_LOGS_WIPED'):
    _reset_logs()
    builtins._AD_LOGS_WIPED = True

def _ad_script_output(msg, is_error=True):
    if not _AD_DEBUG_ACTIVE: return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if is_error:
        formatted = f"[DEBUG_ERROR] [{timestamp}] {msg}"
        target_files = ["_DEBUG_ONLY.txt", "_COMBINED_LOG.txt"]
    else:
        formatted = f"[SCRIPTATLARGE] {msg}"
        target_files = ["_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt"]

    _ORIGINAL_PRINT(formatted)

    for file_name in target_files:
        try:
            with open(file_name, "a", encoding="utf-8") as f:
                f.write(formatted + "\\n")
        except: pass

def print(*args, **kwargs):
    output = " ".join(map(str, args))
    _ad_script_output(output, is_error=False)

# ==========================================
"""

# ==========================================
# 2. THE PRE-PROCESSOR (Context-Aware Machine)
# ==========================================
def clean_source(source):
    result = []
    i, n = 0, len(source)
    quote_type = None
    in_comment = False
    last_valuable_char = ""
    preserve_triple = False

    while i < n:
        char = source[i]
        if in_comment:
            if char == '\n':
                in_comment = False
                result.append('\n')
            i += 1
            continue
        if quote_type:
            if quote_type in ('"""', "'''"):
                if source[i:i + 3] == quote_type:
                    if preserve_triple: result.append(quote_type)
                    quote_type = None
                    i += 3
                    continue
                else:
                    if preserve_triple: result.append(char)
                    i += 1
            else:
                if char == quote_type and (i == 0 or source[i - 1] != '\\'):
                    result.append(char)
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
            quote_type = char
            result.append(char)
            i += 1
        elif char == '#':
            in_comment = True
            i += 1
        else:
            if not char.isspace():
                last_valuable_char = char
            result.append(char)
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
        bracket_level = 0
        in_triple_quote = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                new_content.append(line)
                continue

            triple_count = line.count('"""') + line.count("'''")
            starts_or_ends_triple = triple_count % 2 != 0

            indent_len = len(line) - len(line.lstrip())
            indent_str = line[:indent_len]

            prev_level = bracket_level
            bracket_level += (line.count('(') + line.count('[') + line.count('{'))
            bracket_level -= (line.count(')') + line.count(']') + line.count('}'))

            structural_keywords = (
                'def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ',
                'with ', 'try:', 'except', 'finally:', '@', 'import ', 'from ',
                'return ', 'yield ', 'break', 'continue', 'pass'
            )
            is_structural = any(stripped.startswith(k) for k in structural_keywords) or stripped.endswith(':')

            if (not in_triple_quote and prev_level == 0 and bracket_level == 0 and
                    not is_structural and (indent_len // 4) <= max_depth):

                if stripped in (")", "]", "}", "),", "],", "},") or starts_or_ends_triple:
                    new_content.append(line)
                else:
                    new_content.append(f"{indent_str}try:")
                    new_content.append(f"{indent_str}    {stripped}")
                    new_content.append(f"{indent_str}except Exception as e:")
                    new_content.append(
                        f"{indent_str}    _ad_script_output(f'Line {i + 1} Failed: {{e}}', is_error=True)")
            else:
                new_content.append(line)

            if starts_or_ends_triple:
                in_triple_quote = not in_triple_quote

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_content))
        return True
    except Exception as e:
        print(f"Injection Error: {e}")
        return False

# ==========================================
# 4. RUNNER
# ==========================================
def process_project(source_dir, max_depth):
    ts_seconds = int(time.time())
    target_dir = source_dir.rstrip('\\/') + f"_DEBUG_FINAL_{ts_seconds}"

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    print(f"\n[START] Build initiated...")

    for root, _, files in os.walk(source_dir):
        if any(x in root for x in ['venv', '.git', '__pycache__']): continue
        for file in files:
            if file.endswith(".py"):
                src = os.path.join(root, file)
                rel = os.path.relpath(src, source_dir)
                dst = os.path.join(target_dir, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                inject_into_file(dst, max_depth)
                print(f"  Processed: {rel}")

    print(f"\n[FINISH] Build Complete: {target_dir}")

if __name__ == "__main__":
    path = input("Project Path: ").strip().strip('"')
    try:
        depth_input = input("Max Depth (default 3): ").strip()
        depth = int(depth_input) if depth_input else 3
    except:
        depth = 3

    if os.path.isdir(path):
        process_project(path, depth)
    else:
        print("Invalid path.")
