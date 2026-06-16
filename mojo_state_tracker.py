import os
import shutil
import time


def generate_header():
    # Tailored Mojo/Python universal modelines and logger blocks
    # Uses 4-space blocks for structured indentation compliance.
    return """# -*- coding: utf-8 -*-
# vim: expandtab tabstop=4 shiftwidth=4
# -*- indent-tabs-mode: nil; tab-width: 4 -*-
# =====================================================================
# MOJO COMPATIBLE WRAPPER + STATE LOGGER (PURE SPACES)
# =====================================================================
# Note: Mojo requires explicit typing/imports if handled natively. 
# This header writes to external telemetry streams sequentially.

def _ad_log_event(line_no: int, msg: str, is_error: bool = False):
    try:
        prefix = "[MOJO_DEBUG_ERR]" if is_error else "[MOJO_STATE]"
        formatted = prefix + " [Line " + str(line_no) + "] " + msg
        print(formatted)
        
        # Append to active log sessions safely
        f_name = "_COMBINED_LOG.txt" if not is_error else "_DEBUG_ONLY.txt"
        with open(f_name, "a", encoding="utf-8") as f:
            f.write(formatted + "\\n")
    except:
        pass

# =====================================================================\n"""


def inject_into_file(file_path, max_depth=3):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Phase 1: Clean hidden non-breaking space anomalies variants globally
        raw_content = raw_content.replace('\xa0', ' ').replace('\u00a0', ' ')
        raw_lines = raw_content.splitlines()

        lines_meta = []
        in_triple_quote = False
        quote_char = None

        # State machine mask across lines to skip multi-line docstrings/strings
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
        
        # Structural keywords updated to capture Mojo's 'fn', 'struct', 'var', 'let', and 'trait'
        structural_keywords = (
            'def ', 'fn ', 'struct ', 'trait ', 'class ', 'if ', 'elif ', 'else:', 
            'for ', 'while ', 'with ', 'try:', 'except', 'finally:', '@', 'import ', 'from '
        )

        for idx in range(total_lines):
            line_text, trapped_in_literal = lines_meta[idx]

            # Extract the raw instruction, retaining exact trailing/internal layouts
            content_part = line_text.lstrip(' \t')
            stripped_for_check = content_part.strip()

            # Universal space conversion for compatibility
            raw_indent = line_text[:len(line_text) - len(content_part)]
            total_space_weight = raw_indent.count(' ') + (raw_indent.count('\t') * 4)
            indent_level = max(0, total_space_weight // 4)

            indent_str = '    ' * indent_level
            normalized_line = indent_str + content_part

            # Leave empty blocks or active string literal environments un-instrumented 
            if not stripped_for_check:
                transformed_lines[idx] = indent_str  
                continue

            if trapped_in_literal:
                transformed_lines[idx] = normalized_line
                continue

            prev_bracket_level = bracket_level
            bracket_level += (line_text.count('(') + line_text.count('[') + line_text.count('{'))
            bracket_level -= (line_text.count(')') + line_text.count(']') + line_text.count('}'))

            is_structural = any(
                stripped_for_check.startswith(k) for k in structural_keywords) or stripped_for_check.endswith(':')

            # Phase 3: Try-Except Block Injection tailored for Mojo execution tracking
            if prev_bracket_level == 0 and bracket_level == 0 and not is_structural and indent_level <= max_depth:
                if stripped_for_check in (")", "]", "}", "),", "],", "},"):
                    transformed_lines[idx] = normalized_line
                else:
                    # Injected fallback tracking block
                    block = [
                        f"{indent_str}try:",
                        f"{indent_str}    {content_part}",
                        f"{indent_str}    _ad_log_event({idx + 1}, 'Step Executed Successfully')",
                        f"{indent_str}except e:",
                        f"{indent_str}    _ad_log_event({idx + 1}, 'Block Context Execution Failed', is_error=True)",
                        f"{indent_str}    raise e"
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
    target_dir = source_dir.rstrip('\\/') + f"_MOJO_DEBUG_STATE_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    print(f"\n[START] Building instrumented Mojo sandbox environment...")
    
    for root, _, files in os.walk(source_dir):
        # Prevent traversal into heavy project cache directories
        if any(x in root for x in ['venv', '.git', '__pycache__', '.mojo_cache']):
            continue
        for file in files:
            # Targets both standard Python files, Mojo extensions, and magic-fire extensions
            if file.endswith((".py", ".mojo", ".🔥")):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                inject_into_file(dst, max_depth)
                print(f"    Instrumented: {file}")
                
    print(f"\n[FINISH] Safe Mojo project sandbox initialized at:\n => {target_dir}")


if __name__ == "__main__":
    p = input("Mojo/Python Project Path: ").strip().strip('"')
    try:
        d = int(input("Max Nesting Depth (default 3): ").strip() or 3)
    except:
        d = 3
        
    if os.path.isdir(p):
        process_project(p, d)
    else:
        print("Invalid directory path provided.")
