import os
import shutil
import time
import re


# ==========================================
# 1. THE LOGGER HEADER (V4.0 - Global Control)
# ==========================================
def generate_header():
    return """
# ==========================================
# STRICT RECURSIVE WRAPPER (V4.0)
# ==========================================
import datetime
import sys
import os

# --- GLOBAL SUPPRESSION FLAG ---
# Set to False to disable all debugger overhead at runtime
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
# 2. THE PRE-PROCESSOR (Strips Interference)
# ==========================================
def clean_source(source):
    # Removes all docstrings and single-line comments immediately
    pattern = r'(\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\'|#.*$)'
    return re.sub(pattern, "", source, flags=re.MULTILINE)


# ==========================================
# 3. THE INJECTION ENGINE (With Depth Limit)
# ==========================================
def inject_into_file(file_path, max_depth=3):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Phase 1: Clean the slate
        clean_content = clean_source(raw_content)
        lines = clean_content.splitlines()

        new_content = [generate_header()]
        bracket_level = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped: continue

            indent_str = line[:len(line) - len(line.lstrip())]
            # Calculate depth based on 4-space indentation standard
            current_depth = len(indent_str) // 4

            # --- BRACKET INTEGRITY CHECK ---
            prev_level = bracket_level
            bracket_level += (line.count('(') + line.count('[') + line.count('{'))
            bracket_level -= (line.count(')') + line.count(']') + line.count('}'))

            structural_keywords = (
                'def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ',
                'with ', 'try:', 'except', 'finally:', '@', 'import ', 'from ',
                'return ', 'yield ', 'break', 'continue', 'pass'
            )
            is_structural = any(stripped.startswith(k) for k in structural_keywords)

            # --- THE "STRICT" WRAP RULE ---
            # Added Depth Limit: Only wrap if depth <= max_depth
            if (prev_level == 0 and bracket_level == 0 and
                    not is_structural and current_depth <= max_depth):

                if stripped in (")", "]", "}", "),", "],", "},"):
                    new_content.append(line)
                else:
                    new_content.append(f"{indent_str}try:")
                    new_content.append(f"{indent_str}    {stripped}")
                    new_content.append(f"{indent_str}except Exception as e:")
                    new_content.append(f"{indent_str}    _ad_script_output(f'Line {i + 1} Failed: {{e}}')")
            else:
                new_content.append(line)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_content))
        return True
    except Exception as e:
        print(f"Injection Failure: {e}")
        return False


# ==========================================
# 4. RUNNER
# ==========================================
def process_project(source_dir, max_depth):
    target_dir = source_dir.rstrip('\\/') + f"_DEBUG_FINAL_{int(time.time())}"
    if not os.path.exists(target_dir): os.makedirs(target_dir)

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
                print(f"Wrapped (Max Depth {max_depth}): {rel}")


if __name__ == "__main__":
    path = input("Project Path: ").strip().strip('"')
    try:
        depth = int(input("Max Recursion Depth (Indentation Levels) to wrap (default 3): ") or 3)
    except:
        depth = 3

    if os.path.isdir(path):
        process_project(path, depth)
        print("\nBuild Complete. Use '_AD_DEBUG_ACTIVE = False' in header to suppress logs.")
