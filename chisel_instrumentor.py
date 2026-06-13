import os
import shutil
import time
from pathlib import Path


def generate_header():
    # Added Universal IDE Modelines to force the editor engine to lock to spaces.
    # The injected header strictly uses 4-space blocks for its internal hierarchy.
    # OPTIMIZED: File handles are cached in builtins to prevent I/O overhead on every line execution.
    return """# -*- coding: utf-8 -*-
# vim: expandtab tabstop=4 shiftwidth=4
# -*- indent-tabs-mode: nil; tab-width: 4 -*-
# ==========================================
# STRICT RECURSIVE WRAPPER + STATE TRACKER (V7.5 - OPTIMIZED)
# ==========================================
import datetime as _dt
import sys
import os
import builtins
import csv

_AD_DEBUG_ACTIVE = True
_ORIGINAL_PRINT = builtins.print

def _init_logs():
    log_files = ["_DEBUG_ONLY.txt", "_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt"]
    for f_name in log_files:
        try:
            with open(f_name, "w", encoding="utf-8") as f:
                f.write(f"--- SESSION START: {_dt.datetime.now()} ---\\n")
        except Exception:
            pass
            
    try:
        builtins._AD_CSV_FILE = open("_VARIABLE_TRACKER.csv", "w", encoding="utf-8", newline='')
        builtins._AD_CSV_WRITER = csv.writer(builtins._AD_CSV_FILE)
        builtins._AD_CSV_WRITER.writerow(["Line", "Variable", "Value"])
    except Exception:
        pass

if not hasattr(builtins, '_AD_LOGS_WIPED'):
    _init_logs()
    builtins._AD_LOGS_WIPED = True

def _record_state(line_no, local_vars):
    if not _AD_DEBUG_ACTIVE or not hasattr(builtins, '_AD_CSV_WRITER'): return
    try:
        for var_name, var_val in local_vars.items():
            if var_name.startswith('_'): continue
            clean_val = str(var_val).replace('\\n', ' ').replace('\\r', '')
            builtins._AD_CSV_WRITER.writerow([line_no, var_name, clean_val])
        builtins._AD_CSV_FILE.flush()
    except Exception:
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
        except Exception:
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
        # \xa0 and \u00a0 are effectively the same character in Python strings
        raw_content = raw_content.replace('\xa0', ' ')
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
            is_literal = (
                line_starts_in_literal or 
                line_ends_in_literal or
                stripped.startswith(('"""', "'''")) or 
                stripped.endswith(('"""', "'''"))
            )
            lines_meta.append((line, is_literal))

        total_lines = len(lines_meta)
        transformed_lines = [None] * total_lines
        bracket_level = 0
        
        # Tuple optimization for C-level startswith checks instead of python generators
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

            # Leave empty lines and internal string literal blocks untouched structurally
            if not stripped_for_check:
                transformed_lines[idx] = indent_str
                continue

            if trapped_in_literal:
                transformed_lines[idx] = normalized_line
                continue

            prev_bracket_level = bracket_level
            bracket_level += (line_text.count('(') + line_text.count('[') + line_text.count('{'))
            bracket_level -= (line_text.count(')') + line_text.count(']') + line_text.count('}'))

            # Quick structural check utilizing native tuple mapping
            is_structural = stripped_for_check.startswith(structural_keywords) or stripped_for_check.endswith(':')

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
        print(f"Injection Error on {file_path}: {e}")
        return False


def process_project(source_dir, max_depth):
    src_path = Path(source_dir).resolve()
    target_dir = src_path.parent / f"{src_path.name}_DEBUG_STATE_{int(time.time())}"
    
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[START] Building instrumented project layout...")
    
    ignore_dirs = {'venv', '.git', '__pycache__'}
    
    for root, dirs, files in os.walk(src_path):
        # Mutate dirs list in-place so os.walk skips ignored directories immediately
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file.endswith(".py"):
                src_file = Path(root) / file
                rel_path = src_file.relative_to(src_path)
                dst_file = target_dir / rel_path
                
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
                
                if inject_into_file(dst_file, max_depth):
                    print(f"    Instrumented: {rel_path}")
                    
    print(f"\n[FINISH] Safe project sandbox initialized at: {target_dir}")


if __name__ == "__main__":
    p = input("Project Path: ").strip().strip('"')
    try:
        d_input = input("Max Depth (default 3): ").strip()
        d = int(d_input) if d_input else 3
    except ValueError:
        d = 3
        
    if os.path.isdir(p):
        process_project(p, d)
    else:
        print("Invalid directory path.")
