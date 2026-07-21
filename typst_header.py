# -*- coding: utf-8 -*-
# vim: expandtab tabstop=4 shiftwidth=4
# -*- indent-tabs-mode: nil; tab-width: 4 -*-

import os
import shutil
import time


def generate_typst_header():
    """
    Generates a Typst helper block at the top of instrumented .typ files.
    Provides diagnostic print/inspect wrappers for variable tracking.
    """
    return """// ==========================================
// TYPST INSTRUMENTATION HEADER (DEBUG MODE)
// ==========================================

#let _ad_debug_log(line_no, var_name, var_val) = {
  // Output diagnostic message during Typst compilation
  repr("[DEBUG Line " + str(line_no) + "] " + var_name + " = " + repr(var_val))
}

// ==========================================
"""


def inject_into_typst_file(file_path, max_depth=3):
    """
    Parses a .typ file line-by-line and wraps dynamic Typst expressions/statements
    in diagnostic tracking calls.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Sanitize non-breaking spaces
        raw_content = raw_content.replace('\xa0', ' ').replace('\u00a0', ' ')
        raw_lines = raw_content.splitlines()

        lines_meta = []
        in_block_comment = False

        # Phase 1: Track line state (ignore multi-line comments)
        for line in raw_lines:
            stripped = line.strip()
            line_starts_in_comment = in_block_comment

            i = 0
            while i < len(line):
                if in_block_comment:
                    if line[i:i + 2] == "*/":
                        in_block_comment = False
                        i += 2
                        continue
                    i += 1
                else:
                    if line[i:i + 2] == "/*":
                        in_block_comment = True
                        i += 2
                        continue
                    i += 1

            line_ends_in_comment = in_block_comment
            is_comment = (
                line_starts_in_comment or 
                line_ends_in_comment or 
                stripped.startswith("//")
            )
            lines_meta.append((line, is_comment))

        total_lines = len(lines_meta)
        transformed_lines = [None] * total_lines
        bracket_level = 0
        
        # Structural keywords in Typst script context
        structural_keywords = (
            '#import', '#include', '#let', '#set', '#show', 
            '#if', '#else', '#for', '#while', 'else', 'for', 'if', 'while'
        )

        # Phase 2: Instrumentation
        for idx in range(total_lines):
            line_text, is_comment = lines_meta[idx]

            content_part = line_text.lstrip(' \t')
            stripped_for_check = content_part.strip()

            # Calculate indentation level (4 spaces = 1 indent level)
            raw_indent = line_text[:len(line_text) - len(content_part)]
            total_space_weight = raw_indent.count(' ') + (raw_indent.count('\t') * 4)
            indent_level = max(0, total_space_weight // 4)

            indent_str = '    ' * indent_level
            normalized_line = indent_str + content_part

            # Leave empty lines or comment blocks untouched
            if not stripped_for_check or is_comment:
                transformed_lines[idx] = normalized_line
                continue

            prev_bracket_level = bracket_level
            bracket_level += (line_text.count('(') + line_text.count('[') + line_text.count('{'))
            bracket_level -= (line_text.count(')') + line_text.count(']') + line_text.count('}'))

            is_structural = any(
                stripped_for_check.startswith(k) for k in structural_keywords
            ) or stripped_for_check.endswith('{')

            # Instrument Typst code lines at valid depths
            if prev_bracket_level == 0 and bracket_level == 0 and not is_structural and indent_level <= max_depth:
                if stripped_for_check in (")", "]", "}", "),", "],", "},"):
                    transformed_lines[idx] = normalized_line
                elif stripped_for_check.startswith("#"):
                    # Insert a debug tracker before executing code expression
                    debug_marker = f"{indent_str}/* Line {idx + 1} */ #_ad_debug_log({idx + 1}, \"statement\", \"{stripped_for_check.replace('\"', '\\\"')}\")"
                    transformed_lines[idx] = f"{debug_marker}\n{normalized_line}"
                else:
                    transformed_lines[idx] = normalized_line
            else:
                transformed_lines[idx] = normalized_line

        # Reassemble document
        new_content = [generate_typst_header()] + transformed_lines
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_content) + "\n")
        return True

    except Exception as e:
        print(f"Injection Error in {file_path}: {e}")
        return False


def process_typst_project(source_dir, max_depth):
    """
    Creates a temporary instrumented project directory to preserve the original sources.
    """
    target_dir = source_dir.rstrip('\\/') + f"_TYPST_DEBUG_STATE_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    print("\n[START] Building instrumented Typst project sandbox...")

    for root, _, files in os.walk(source_dir):
        # Skip standard build/versioning folders
        if any(x in root for x in ['.git', '.typst-cache', 'build', 'dist']):
            continue

        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
            os.makedirs(os.path.dirname(dst), exist_ok=True)

            shutil.copy2(src, dst)

            # Only instrument Typst document files
            if file.endswith(".typ"):
                inject_into_typst_file(dst, max_depth)
                print(f"    Instrumented: {file}")

    print(f"\n[FINISH] Safe Typst sandbox initialized at:\n{target_dir}\n")


if __name__ == "__main__":
    p = input("Typst Project Path: ").strip().strip('"')
    try:
        d = int(input("Max Depth (default 3): ").strip() or 3)
    except ValueError:
        d = 3

    if os.path.isdir(p):
        process_typst_project(p, d)
    else:
        print("Invalid directory path provided.")
