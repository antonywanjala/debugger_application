import os
import shutil
import time


def generate_header():
    # Modified header strictly compliant with GDScript formatting (Uses Tabs)
    return """# ==========================================
# GDSCRIPT STATE TRACKER & LOGGER
# ==========================================
const _AD_DEBUG_ACTIVE: bool = true

static func _reset_logs() -> void:
\tvar log_files = ["user://_DEBUG_ONLY.txt", "user://_SCRIPT_ONLY.txt", "user://_COMBINED_LOG.txt"]
\tfor f_name in log_files:
\t\tvar file = FileAccess.open(f_name, FileAccess.WRITE)
\t\tif file:
\t\t\tfile.store_line("--- SESSION START ---")

static func _ad_script_output(msg: String, is_error: bool = true) -> void:
\tif not _AD_DEBUG_ACTIVE: return
\tvar formatted = "[DEBUG_ERROR] " + msg if is_error else "[SCRIPT] " + msg
\tprint(formatted)
\tvar targets = ["user://_DEBUG_ONLY.txt", "user://_COMBINED_LOG.txt"] if is_error else ["user://_SCRIPT_ONLY.txt", "user://_COMBINED_LOG.txt"]
\tfor f_name in targets:
\t\tvar file = FileAccess.open(f_name, FileAccess.READ_WRITE)
\t\tif file:
\t\t\tfile.seek_end()
\t\t\tfile.store_line(formatted)

# ==========================================\n"""


def inject_into_file(file_path, max_depth=3):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        raw_lines = raw_content.splitlines()
        lines_meta = []
        in_multiline_comment = False

        # Build structural state machine mask for GDScript multiline strings/comments
        for line in raw_lines:
            stripped = line.strip()
            line_starts_in_literal = in_multiline_comment

            i = 0
            while i < len(line):
                if in_multiline_comment:
                    if line[i:i + 3] == '"""':
                        in_multiline_comment = False
                        i += 3
                        continue
                    i += 1
                else:
                    if line[i:i + 3] == '"""':
                        in_multiline_comment = True
                        i += 3
                        continue
                    elif line[i] == '"':
                        i += 1
                        while i < len(line) and line[i] != '"':
                            if line[i] == '\\':
                                i += 2
                            else:
                                i += 1
                        i += 1
                        continue
                    i += 1

            line_ends_in_literal = in_multiline_comment
            is_literal = (line_starts_in_literal or line_ends_in_literal or
                          stripped.startswith('"""') or stripped.endswith('"""') or
                          stripped.startswith('#'))
            lines_meta.append((line, is_literal))

        total_lines = len(lines_meta)
        transformed_lines = [None] * total_lines
        bracket_level = 0
        
        # Keywords native to structural GDScript branches
        structural_keywords = ('func ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ',
                               'match ', 'break', 'continue', 'pass', 'return', 'extends ', 'class_name ')

        for idx in range(total_lines):
            line_text, trapped_in_literal = lines_meta[idx]

            content_part = line_text.lstrip(' \t')
            stripped_for_check = content_part.strip()

            # UNIVERSAL CONVERSION: Convert space tabs to authentic GDScript \t layout
            raw_indent = line_text[:len(line_text) - len(content_part)]
            total_space_weight = raw_indent.count(' ') + (raw_indent.count('\t') * 4)
            indent_level = max(0, total_space_weight // 4)
            indent_str = '\t' * indent_level

            normalized_line = indent_str + content_part

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

            # Injection Phase: Wrap operations with real-time log tracking dumps
            if prev_bracket_level == 0 and bracket_level == 0 and not is_structural and indent_level <= max_depth:
                if stripped_for_check in (")", "]", "}", "),", "],", "},"):
                    transformed_lines[idx] = normalized_line
                else:
                    # GDScript does not use generic try/catch, we hook an execution log check right after runtime steps
                    block = [
                        f"{indent_str}{content_part}",
                        f"{indent_str}_ad_script_output(\"Passed Line {idx + 1}: {content_part.replace('\"', '\\\"')}\", false)"
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
    target_dir = source_dir.rstrip('\\/') + f"_DEBUG_GD_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    print(f"\n[START] Building instrumented GDScript layout...")
    for root, _, files in os.walk(source_dir):
        if any(x in root for x in ['.godot', '.git', 'addons']):
            continue
        for file in files:
            if file.endswith(".gd"):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                inject_into_file(dst, max_depth)
                print(f"    Instrumented GDScript: {file}")
    print(f"\n[FINISH] Safe GDScript sandbox initialized at: {target_dir}")


if __name__ == "__main__":
    p = input("Godot Project Path: ").strip().strip('"')
    try:
        d = int(input("Max Nesting Depth (default 3): ").strip() or 3)
    except:
        d = 3
    if os.path.isdir(p):
        process_project(p, d)
    else:
        print("Invalid directory path.")
