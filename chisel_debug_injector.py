import os
import shutil
import time

def generate_header():
    """
    Returns a unified header to inject at the top of Scala/Chisel files
    if helper logging utilities are required.
    """
    return """/* =========================================================================
  STRICT RECURSIVE CHISEL DEBUG WRAPPER + STATE TRACKER (V1.0 - PURE SPACES)
 =========================================================================
*/
import chisel3._
import chisel3.util._
"""

def inject_into_file(file_path, max_depth=3):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Eradicate non-breaking spaces
        raw_content = raw_content.replace('\xa0', ' ').replace('\u00a0', ' ')
        raw_lines = raw_content.splitlines()

        lines_meta = []
        in_multiline_comment = False

        # Build basic structural mask for Scala comments/blocks
        for line in raw_lines:
            stripped = line.strip()
            line_starts_in_comment = in_multiline_comment

            # Simple state machine for multiline comments (/* ... */)
            if not in_multiline_comment and "/*" in line:
                in_multiline_comment = True
            if in_multiline_comment and "*/" in line:
                in_multiline_comment = False

            is_literal_or_comment = (
                line_starts_in_comment or 
                in_multiline_comment or 
                stripped.startswith("//") or 
                stripped.startswith("import") or
                stripped.startswith("package")
            )
            lines_meta.append((line, is_literal_or_comment))

        total_lines = len(lines_meta)
        transformed_lines = [None] * total_lines
        bracket_level = 0

        for idx in range(total_lines):
            line_text, is_exempt = lines_meta[idx]
            content_part = line_text.lstrip(' \t')
            stripped_for_check = content_part.strip()

            # Normalize indentation rules
            raw_indent = line_text[:len(line_text) - len(content_part)]
            total_space_weight = raw_indent.count(' ') + (raw_indent.count('\t') * 4)
            indent_level = max(0, total_space_weight // 4)
            indent_str = '    ' * indent_level
            normalized_line = indent_str + content_part

            if not stripped_for_check or is_exempt:
                transformed_lines[idx] = normalized_line
                continue

            # Track nesting levels via hardware/software block scopes
            prev_bracket_level = bracket_level
            bracket_level += line_text.count('{') - line_text.count('}')

            # Identify valid Chisel assignments to track (val signalName = Wire(...))
            # Checks for assignments targeting wires, regs, or IO blocks
            is_chisel_assignment = (
                stripped_for_check.startswith("val ") or 
                stripped_for_check.startswith("var ")
            ) and "=" in stripped_for_check

            if prev_bracket_level > 0 and is_chisel_assignment and indent_level <= max_depth:
                # Safely extract variable name
                parts = stripped_for_check.split("=")
                declaration = parts.replace("val ", "").replace("var ", "").strip()
                # Split off types if explicit (e.g., val mySignal: UInt = ...)
                var_name = declaration.split(":").strip()

                # Build injection payload using Chisel's hardware runtime printf
                # Note: Chisel prints require wrapping names in p"${...}" to resolve at runtime
                block = [
                    f"{normalized_line}",
                    f'{indent_str}chisel3.printf(p"[DEBUG_STATE] Line {idx + 1} | {var_name} = ${{{var_name}}}\\n")'
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
    target_dir = source_dir.rstrip('\\/') + f"_CHISEL_DEBUG_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    print(f"\n[START] Building instrumented Chisel project layout...")
    for root, _, files in os.walk(source_dir):
        # Ignore common build artifacts and configuration targets
        if any(x in root for x in ['target', '.git', '.bsp', '.metals', 'project']):
            continue
        for file in files:
            # Chisel modules are authored within Scala files
            if file.endswith(".scala"):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                inject_into_file(dst, max_depth)
                print(f"    Instrumented: {file}")
                
    print(f"\n[FINISH] Safe hardware sandbox initialized at: {target_dir}")

if __name__ == "__main__":
    p = input("Chisel/Scala Project Directory Path: ").strip().strip('"')
    try:
        d = int(input("Max Nesting Depth (default 3): ").strip() or 3)
    except:
        d = 3
    if os.path.isdir(p):
        process_project(p, d)
    else:
        print("Invalid directory path.")
