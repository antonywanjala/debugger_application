import os
import shutil
import datetime
import time


# ==========================================
# 1. THE LOGGER HEADER (V4.2 - Global Control)
# ==========================================
def generate_header():
    return """
# ==========================================
# STRICT RECURSIVE WRAPPER (V4.2)
# ==========================================
import datetime
import sys
import os

_AD_DEBUG_ACTIVE = True

def _ad_script_output(msg):
    if not _AD_DEBUG_ACTIVE: return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[DEBUG_ERROR] [{timestamp}] {msg}"
    print(formatted)
    try:
        with open("_DEBUG_CRASH_LOG.txt", "a", encoding="utf-8") as f:
            f.write(formatted + "\\n")
    except: pass
# ==========================================
"""


# ==========================================
# 2. THE PRE-PROCESSOR (Context-Aware Machine)
# ==========================================
def clean_source(source):
    """
    Strips comments and docstrings.
    Crucially: Preserves triple-quoted strings assigned to variables.
    """
    result = []
    i = 0
    n = len(source)
    quote_type = None
    in_comment = False
    last_valuable_char = ""

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
                    if preserve_triple:
                        result.append(quote_type)
                    quote_type = None
                    i += 3
                    continue
                else:
                    if preserve_triple:
                        result.append(char)
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
            if preserve_triple:
                result.append(quote_type)
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
# 3. THE INJECTION ENGINE (Updated for Data Safety)
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

            # --- Triple Quote Detection for Data Safety ---
            # If the line contains an odd number of triple quotes, we toggled state
            # This handles cases where data begins or ends on a line
            triple_count = line.count('"""') + line.count("'''")
            starts_or_ends_triple = triple_count % 2 != 0

            indent_len = len(line) - len(line.lstrip())
            indent_str = line[:indent_len]
            current_depth = indent_len // 4

            prev_level = bracket_level
            bracket_level += (line.count('(') + line.count('[') + line.count('{'))
            bracket_level -= (line.count(')') + line.count(']') + line.count('}'))

            structural_keywords = (
                'def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ',
                'with ', 'try:', 'except', 'finally:', '@', 'import ', 'from ',
                'return ', 'yield ', 'break', 'continue', 'pass'
            )
            is_structural = any(stripped.startswith(k) for k in structural_keywords) or stripped.endswith(':')

            # Logic: Do not wrap if we are inside a multi-line string (data)
            if (not in_triple_quote and prev_level == 0 and bracket_level == 0 and
                    not is_structural and current_depth <= max_depth):

                if stripped in (")", "]", "}", "),", "],", "},") or starts_or_ends_triple:
                    new_content.append(line)
                else:
                    new_content.append(f"{indent_str}try:")
                    new_content.append(f"{indent_str}    {stripped}")
                    new_content.append(f"{indent_str}except Exception as e:")
                    new_content.append(f"{indent_str}    _ad_script_output(f'Line {i + 1} Failed: {{e}}')")
            else:
                new_content.append(line)

            # Update state after processing the line
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
    ts_readable = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target_dir = source_dir.rstrip('\\/') + f"_DEBUG_FINAL_{ts_seconds}"

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    print(f"\n[START] Build initiated at {ts_readable}")
    print(f"[INFO] Target: {target_dir}\n")

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

    print(f"\n[FINISH] Build Complete")
    print(f"Folder Timestamp: {ts_seconds}")


if __name__ == "__main__":
    path = input("Project Path: ").strip().strip('"')
    try:
        depth = int(input("Max Depth (default 3): ") or 3)
    except:
        depth = 3

    if os.path.isdir(path):
        process_project(path, depth)
    else:
        print("Invalid path.")
