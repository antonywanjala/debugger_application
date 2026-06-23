import os
import shutil
import time


def generate_header():
    """
    Returns the required tracking block for Haskell scripts.
    Ensures Debug.Trace is available for injecting pure-functional logs.
    """
    return """-- =================================================================
-- AUTOMATED HASKELL DEBUG STATE TRACKER & INSTRUMENTATION WRAPPER
-- =================================================================
import qualified Debug.Trace as _Tr

{- DEBUG UTILITIES -}
_logState :: String -> a -> a
_logState msg expr = _Tr.trace ("[DEBUG] " ++ msg) expr
-- =================================================================
"""


def inject_into_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        raw_lines = raw_content.splitlines()
        transformed_lines = []
        in_block_comment = False
        has_module_decl = False
        module_end_idx = 0

        # Structural Keywords & Identifiers to skip wrapping
        skip_prefixes = ('import ', 'module ', '--', 'data ', 'type ', 'newtype ', 'instance ', 'class ')

        for idx, line in enumerate(raw_lines):
            stripped = line.strip()
            line_no = idx + 1

            # Handle Block Comments {- ... -}
            if '{-' in stripped:
                in_block_comment = True
            if '-}' in stripped:
                in_block_comment = False
                transformed_lines.append(line)
                continue

            if in_block_comment or not stripped:
                transformed_lines.append(line)
                continue

            # Track where the module header ends to safely inject imports
            if stripped.startswith('module '):
                has_module_decl = True
                
            if has_module_decl and 'where' in stripped:
                module_end_idx = len(transformed_lines) + 1

            # Determine structural eligibility
            is_structural = stripped.startswith(skip_prefixes)
            is_type_signature = ':' in stripped and not stripped.startswith(('let', 'in')) and '::' in stripped

            # If it's a standard execution line (like a function body or binding)
            if not is_structural and not is_type_signature and '=' in stripped:
                # Split the declaration from its assignment
                parts = line.split('=', 1)
                lhs = parts
                rhs = parts

                # Ensure it's not a syntax fragment
                if rhs.strip():
                    # Inject Debug.Trace tracking wrapper safely around the execution block
                    clean_msg = f"Evaluating Line {line_no}: {lhs.strip()[:20]}..."
                    instrumented_rhs = f" (_logState \"{clean_msg}\" ({rhs.strip()}))"
                    transformed_lines.append(f"{lhs}={instrumented_rhs}")
                    continue

            transformed_lines.append(line)

        # Inject tracking header cleanly right after the module declaration
        if has_module_decl:
            transformed_lines.insert(module_end_idx, generate_header())
        else:
            transformed_lines.insert(0, generate_header())

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(transformed_lines) + "\n")
        return True

    except Exception as e:
        print(f"Injection Error on {file_path}: {e}")
        return False


def process_project(source_dir):
    target_dir = source_dir.rstrip('\\/') + f"_HASKELL_DEBUG_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    print(f"\n[START] Building instrumented Haskell project sandbox...")
    
    for root, _, files in os.walk(source_dir):
        # Ignore common package/build folders
        if any(x in root for x in ['.stack-work', 'dist', 'dist-newstyle', '.git']):
            continue
            
        for file in files:
            if file.endswith(".hs") or file.endswith(".lhs"):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                
                shutil.copy2(src, dst)
                inject_into_file(dst)
                print(f"    Instrumented: {file}")
                
    print(f"\n[FINISH] Safe project sandbox initialized at:\n👉 {target_dir}")


if __name__ == "__main__":
    p = input("Haskell Project Path: ").strip().strip('"')
    if os.path.isdir(p):
        process_project(p)
    else:
        print("Invalid directory path.")
