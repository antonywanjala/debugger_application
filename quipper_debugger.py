# -*- coding: utf-8 -*-
import os
import shutil
import time

def generate_header():
    # Added Universal IDE Modelines to force the editor engine to lock to spaces.
    # The injected header strictly uses 4-space blocks for its internal hierarchy.
    return """# -*- coding: utf-8 -*-
# vim: expandtab tabstop=4 shiftwidth=4
# -*- indent-tabs-mode: nil; tab-width: 4 -*-
# ==========================================
# STRICT RECURSIVE WRAPPER + STATE TRACKER (V7.4 - PURE SPACES)
# ==========================================
import datetime as _dt
import sys
import os
import builtins
import csv

_AD_DEBUG_ACTIVE = True
_ORIGINAL_PRINT = builtins.print

def _reset_logs():
    log_files = ["_DEBUG_ONLY.txt", "_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt"]
    for f_name in log_files:
        try:
            with open(f_name, "w", encoding="utf-8") as f:
                f.write(f"--- SESSION START: {_dt.datetime.now()} ---\\n")
        except:
            pass

    try:
        with open("_VARIABLE_TRACKER.csv", "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Line", "Variable", "Value"])
    except:
        pass

if not hasattr(builtins, '_AD_LOGS_WIPED'):
    _reset_logs()
    builtins._AD_LOGS_WIPED = True

def _record_state(line_no, local_vars):
    if not _AD_DEBUG_ACTIVE: return
    try:
        with open("_VARIABLE_TRACKER.csv", "a", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            for var_name, var_val in local_vars.items():
                if var_name.startswith('_'): continue
                clean_val = str(var_val).replace('\\n', ' ').replace('\\r', '')
                writer.writerow([line_no, var_name, clean_val])
    except:
        pass

def _ad_script_output(msg, is_error=True):
    if not _AD_DEBUG_ACTIVE: return
    timestamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[DEBUG_ERROR] [{timestamp}] {msg}" if is_error else f"[SCRIPT] {msg}"
    _ORIGINAL_PRINT(formatted)
    target = ["_DEBUG_ONLY.txt", "_COMBINED_LOG.txt"] if is_error else ["_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt"]
    for f_name in target:
        try:
            with open(f_name, "a", encoding="utf-8") as f: 
                f.write(formatted + "\\n")
        except:
            pass

def print(*args, **kwargs):
    output = " ".join(map(str, args))
    _ad_script_output(output, is_error=False)

builtins.print = print
# ==========================================\n"""


def inject_into_file(file_path, max_depth=3):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Phase 1: Eradicate hidden non-breaking space variants globally
        raw_content = raw_content.replace('\xa0', ' ').replace('\u00a0', ' ')
        raw_lines = raw_content.splitlines()

        lines_meta = []
        in_triple_quote = False
        quote_char = None

        # Build structural state machine mask across lines
        for line in raw_lines:
            stripped = line.strip()
            line_starts_in_literal = in_triple_quote

            i = 0
            while i < len(line):
                if in_triple_quote:
                    if line[i:i + 3] == quote_char:
                        in_triple_quote = False
                        quote_char = None
                        i += 3
                        continue
                    i += 1
                else:
                    if line[i:i + 3] in ('"""', "'''"):
                        in_triple_quote = True
                        quote_char = line[i:i + 3]
                        i += 3
                        continue
                    elif line[i] in ('"', "'"):
                        s_char = line[i]
                        i += 1
                        while i < len(line) and line[i] != s_char:
                            if line[i] == '\\':
                                i += 2
                            else:
                                i += 1
                        i += 1
                        continue
                    i += 1

            line_ends_in_literal = in_triple_quote
            is_literal = (line_starts_in_literal or line_ends_in_literal or
                          stripped.startswith(('"""', "'''")) or stripped.endswith(('"""', "'''")))
            lines_meta.append((line, is_literal))

        total_lines = len(lines_meta)
        transformed_lines = [None] * total_lines
        bracket_level = 0
        structural_keywords = ('def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ',
                               'with ', 'try:', 'except', 'finally:', '@', 'import ', 'from ')

        for idx in range(total_lines):
            line_text, trapped_in_literal = lines_meta[idx]

            # Extract JUST the intra-line expression, leaving all internal/trailing spaces completely intact
            content_part = line_text.lstrip(' \t')
            stripped_for_check = content_part.strip()

            # UNIVERSAL SPACE CONVERSION (Applied to EVERYTHING to satisfy IDE heuristics)
            raw_indent = line_text[:len(line_text) - len(content_part)]
            total_space_weight = raw_indent.count(' ') + (raw_indent.count('\t') * 4)
            indent_level = max(0, total_space_weight // 4)

            # Construct the new, strictly space-instantiated preceding spacing (4 spaces per level)
            indent_str = '    ' * indent_level

            # Reattach the pure-space prefix to the fully preserved invocation
            normalized_line = indent_str + content_part

            # Leave empty lines and internal string literal blocks untouched structurally (but formatted with spaces)
            if not stripped_for_check:
                transformed_lines[idx] = indent_str  # Preserve empty lines as pure spaces or completely empty
                continue

            if trapped_in_literal:
                transformed_lines[idx] = normalized_line
                continue

            prev_bracket_level = bracket_level
            bracket_level += (line_text.count('(') + line_text.count('[') + line_text.count('{'))
            bracket_level -= (line_text.count(')') + line_text.count(']') + line_text.count('}'))

            is_structural = any(
                stripped_for_check.startswith(k) for k in structural_keywords) or stripped_for_check.endswith(':')

            # Phase 3: Injection (Using strict 4-space string increments for the block hierarchy)
            if prev_bracket_level == 0 and bracket_level == 0 and not is_structural and indent_level <= max_depth:
                if stripped_for_check in (")", "]", "}", "),", "],", "},"):
                    transformed_lines[idx] = normalized_line
                else:
                    block = [
                        f"{indent_str}try:",
                        f"{indent_str}    {content_part}",
                        f"{indent_str}    _record_state({idx + 1}, locals())",
                        f"{indent_str}except Exception as e:",
                        f"{indent_str}    _ad_script_output(f'Line {idx + 1} Failed: {{e}}', is_error=True)",
                        f"{indent_str}    raise"
                    ]
                    transformed_lines[idx] = "\n".join(block)
            else:
                transformed_lines[idx] = normalized_line

        new_content = [generate_header()] + transformed_lines
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_content) + "\n")
        return True
    except Exception as e:
        print(f"Injection Error: {e}")
        return False


def process_project(source_dir, max_depth):
    target_dir = source_dir.rstrip('\\/') + f"_DEBUG_STATE_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    print(f"\n[START] Building instrumented project layout...")
    for root, _, files in os.walk(source_dir):
        if any(x in root for x in ['venv', '.git', '__pycache__']):
            continue
        for file in files:
            if file.endswith(".py"):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                inject_into_file(dst, max_depth)
                print(f"    Instrumented: {file}")
    print(f"\n[FINISH] Safe project sandbox initialized at: {target_dir}")


if __name__ == "__main__":
    p = input("Project Path: ").strip().strip('"')
    try:
        d = int(input("Max Depth (default 3): ").strip() or 3)
    except:
        d = 3
    if os.path.isdir(p):
        process_project(p, d)
    else:
        print("Invalid directory path.")
