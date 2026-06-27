# -*- coding: utf-8 -*-
# vim: expandtab tabstop=4 shiftwidth=4
# -*- indent-tabs-mode: nil; tab-width: 4 -*-
# ==============================================================================
# AUTOMATED ELM FLOW INSTRUMENTER & TRACER (PURE SPACES)
# ==============================================================================
import os
import shutil
import time


def inject_into_elm_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Clean non-breaking spaces
        raw_content = raw_content.replace("\xa0", " ").replace("\u00a0", " ")
        raw_lines = raw_content.splitlines()

        lines_meta = []
        in_triple_quote = False
        in_block_comment = False

        # Phase 1: Structural State Machine Mask for Elm Literals & Comments
        for line in raw_lines:
            stripped = line.strip()
            line_starts_protected = in_triple_quote or in_block_comment

            i = 0
            while i < len(line):
                # Handle Elm Multi-line Strings
                if in_triple_quote:
                    if line[i : i + 3] == '"""':
                        in_triple_quote = False
                        i += 3
                        continue
                    i += 1
                # Handle Elm Multi-line Comments
                elif in_block_comment:
                    if line[i : i + 2] == "-}":
                        in_block_comment = False
                        i += 2
                        continue
                    i += 1
                else:
                    if line[i : i + 3] == '"""':
                        in_triple_quote = True
                        i += 3
                        continue
                    elif line[i : i + 2] == "{-":
                        in_block_comment = True
                        i += 2
                        continue
                    elif line[i : i + 2] == "--":
                        # Single-line comment; ignore rest of the line
                        break
                    i += 1

            line_ends_protected = in_triple_quote or in_block_comment
            is_protected = (
                line_starts_protected
                or line_ends_protected
                or stripped.startswith(("--", "{-", '"""'))
            )
            lines_meta.append((line, is_protected))

        total_lines = len(lines_meta)
        transformed_lines = [None] * total_lines

        # Phase 2: Structural Pipeline Injection
        for idx in range(total_lines):
            line_text, is_protected = lines_meta[idx]
            stripped = line_text.strip()
            line_num = idx + 1

            # Skip empty lines and code blocks masked as strings/comments
            if not stripped or is_protected:
                transformed_lines[idx] = line_text
                continue

            # Strict architectural filters to prevent breaking type definitions/imports
            if (
                any(
                    stripped.startswith(k)
                    for k in ["import", "module", "type", "port"]
                )
                or ":" in line_text
            ):  # Avoid type signatures
                transformed_lines[idx] = line_text
                continue

            # Avoid mutating complex conditional controls inline
            if any(
                k in line_text for k in ["if ", "then ", "else ", "let ", "in "]
            ):
                transformed_lines[idx] = line_text
                continue

            # Avoid splitting logic operators
            if any(
                op in line_text
                for op in ["==", "<=", ">=", "!=", "++", "|>", "<|"]
            ):
                transformed_lines[idx] = line_text
                continue

            # Target Case Branches (Pattern matching flow tracking)
            if "->" in line_text:
                left, right = line_text.split("->", 1)
                clean_tag = left.strip().replace('"', '\\"')
                transformed_lines[idx] = (
                    f'{left}-> Debug.log "[Line {line_num}] Branch ({clean_tag})" <| {right}'
                )

            # Target Value Assignments and Function Declarations
            elif "=" in line_text:
                left, right = line_text.split("=", 1)
                clean_tag = left.strip().replace('"', '\\"')
                transformed_lines[idx] = (
                    f'{left}= Debug.log "[Line {line_num}] Eval ({clean_tag})" <| {right}'
                )

            else:
                transformed_lines[idx] = line_text

        # Write out instrumented source script
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(transformed_lines) + "\n")
        return True

    except Exception as e:
        print(f"    [!] Injection Error on {file_path}: {e}")
        return False


def process_elm_project(source_dir):
    target_dir = source_dir.rstrip("\\/") + f"_ELM_DEBUG_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    print(f"\n[START] Building instrumented Elm sandbox architecture...")

    for root, _, files in os.walk(source_dir):
        # Prevent mutating build collateral, dependency trees, or hidden metadata
        if any(
            x in root for x in ["elm-stuff", "node_modules", ".git", "tests"]
        ):
            continue

        for file in files:
            if file.endswith(".elm"):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                os.makedirs(os.path.dirname(dst), exist_ok=True)

                shutil.copy2(src, dst)
                success = inject_into_elm_file(dst)
                if success:
                    print(f"    Instrumented: {os.path.relpath(src, source_dir)}")

    print(f"\n[FINISH] Safe Elm debug sandbox initialized at: {target_dir}")
    print(
        "> Note: Compile your code inside this folder using 'elm make' without the '--optimize' flag."
    )


if __name__ == "__main__":
    project_path = input("Elm Project Path: ").strip().strip('"')
    if os.path.isdir(project_path):
        process_elm_project(project_path)
    else:
        print("Invalid directory path provided.")
