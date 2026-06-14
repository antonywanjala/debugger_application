import os
import shutil
import time
import re


def generate_header():
    # Injected informational header for the modified Bluespec source files
    return """// =================================================================
// AUTOMATIC SIMULATION TRACE WRAPPER (PURE SPACES GENERATED)
// This file has been instrumented with automated rule/method logging.
// =================================================================\n"""


def inject_into_file(file_path, max_depth=3):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Eradicate non-breaking spaces globally
        raw_content = raw_content.replace("\xa0", " ").replace("\u00a0", " ")
        raw_lines = raw_content.splitlines()

        transformed_lines = []
        filename = os.path.basename(file_path)

        # Regex patterns to capture rule and method names in BSV
        rule_pattern = re.compile(r"\brule\s+([a-zA-Z0-9_]+)")
        method_pattern = re.compile(r"\bmethod\s+([a-zA-Z0-9_]+(?!Action))")

        for idx, line in enumerate(raw_lines):
            transformed_lines.append(line)

            # Preserve formatting by tracking the leading indentation
            stripped = line.lstrip(" \t")
            leading_whitespace = line[: len(line) - len(stripped)]

            # Check if this line defines a firing element (rule or method)
            is_rule = rule_pattern.search(line)
            is_method = method_pattern.search(line)

            # Check if the block has opened (usually ends with a semicolon or is an action block)
            if (is_rule or is_method) and ";" in line:
                block_type = "RULE" if is_rule else "METHOD"
                block_name = (
                    is_rule.group(1) if is_rule else is_method.group(1)
                )

                # Construct a strict 4-space padded hardware simulation display statement
                # This automatically logs the execution time ($time), file, line number, and block name
                indent_str = leading_whitespace + "    "
                trace_statement = (
                    f'{indent_str}$display("[BSV_TRACE] [Time=%0d] File: {filename}, '
                    f'Line: {idx + 1} | Fired {block_type}: {block_name}", $time);'
                )

                transformed_lines.append(trace_statement)

        # Prepend the verification header notice
        new_content = [generate_header()] + transformed_lines

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_content) + "\n")
        return True

    except Exception as e:
        print(f"Instrumentation Error on {file_path}: {e}")
        return False


def process_project(source_dir, max_depth):
    # Establish a timestamped safe workspace folder mirroring your original code's design
    target_dir = source_dir.rstrip("\\/") + f"_BSV_DEBUG_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    print(f"\n[START] Building instrumented Bluespec project layout...")

    for root, _, files in os.walk(source_dir):
        # Skip common non-source directories
        if any(
            x in root
            for x in ["venv", ".git", "__pycache__", "build", "bdir", "simdir"]
        ):
            continue

        for file in files:
            # Target Bluespec SystemVerilog files
            if file.endswith(".bsv") or file.endswith(".bs"):
                src = os.path.join(root, file)
                dst = os.path.join(
                    target_dir, os.path.relpath(src, source_dir)
                )

                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)

                inject_into_file(dst, max_depth)
                print(f"    Instrumented: {file}")

    print(f"\n[FINISH] Safe Bluespec sandbox initialized at: {target_dir}")
    print(
        " Run your Bluespec compiler (bsc) on this new directory to view runtime cycle logs."
    )


if __name__ == "__main__":
    p = input("Bluespec Project Path: ").strip().strip('"')
    try:
        d = int(input("Max Depth (default 3): ").strip() or 3)
    except:
        d = 3

    if os.path.isdir(p):
        process_project(p, d)
    else:
        print("Invalid directory path.")
