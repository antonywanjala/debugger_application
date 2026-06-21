# -*- coding: utf-8 -*-
import os
import shutil
import time
import re

def generate_header():
    """
    Generates a Haskell instrumentation header using unsafe IO hooks 
    to replicate the multi-file logging behavior of the original Python script.
    """
    return """{- ==========================================
   STRICT RECURSIVE WRAPPER + STATE TRACKER (HASKELL V1.0)
   ========================================== -}
import qualified System.IO.Unsafe as _Unsafe
import qualified Data.Time.Clock as _Clock
import qualified System.IO as _IO

{-# NOINLINE _ad_log_raw #-}
_ad_log_raw :: String -> String -> Bool
_ad_log_raw filename msg = _Unsafe.unsafePerformIO $ do
    _IO.appendFile filename (msg ++ "\\n")
    return True

{-# NOINLINE _record_state #-}
_record_state :: Show a => Int -> String -> a -> a
_record_state lineNo varName value = _Unsafe.unsafePerformIO $ do
    time <- _Clock.getCurrentTime
    let cleanVal = map (\\c -> if c == '\\n' then ' ' else c) (show value)
    let logMsg = "[DEBUG] [" ++ show time ++ "] Line " ++ show lineNo ++ " -> " ++ varName ++ " = " ++ cleanVal
    let csvMsg = show lineNo ++ "," ++ varName ++ "," ++ cleanVal
    
    -- Replicate multi-file logging topology
    let _ = _ad_log_raw "_COMBINED_LOG.txt" logMsg
    let _ = _ad_log_raw "_VARIABLE_TRACKER.csv" csvMsg
    return (value)

{- ========================================== -}
"""

def inject_into_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Normalize layout spacing (remove tabs and non-breaking spaces)
        raw_content = raw_content.replace('\xa0', ' ').replace('\u00a0', ' ').replace('\t', '    ')
        raw_lines = raw_content.splitlines()

        transformed_lines = []
        in_block_comment = False

        for idx, line in enumerate(raw_lines):
            stripped = line.strip()
            line_no = idx + 1

            # Handle block comment toggles
            if "{-" in line: in_block_comment = True
            if "-}" in line: in_block_comment = False

            # Skip transformations if inside comments, imports, module headers, or empty lines
            if (in_block_comment or stripped.startswith("--") or not stripped or 
                stripped.startswith("import ") or stripped.startswith("module ")):
                transformed_lines.append(line)
                continue

            # Target standard variable/function equations: "name ... = expression"
            # Avoid matching operators like ==, >=, <= or type signatures (::)
            match = re.match(r"^(\s*)([a-zA-Z0-9_'\s]+)(?<![<>=!])=(?![=])(.*)$", line)
            
            if match:
                indent, binding_part, expression = match.groups()
                tokens = binding_part.split()
                
                if tokens:
                    # The bound identifier (variable name or function name)
                    var_name = tokens[0]
                    
                    # Ensure we aren't instrumenting special keywords
                    if var_name not in ['let', 'in', 'where', 'case', 'of', 'do']:
                        # Inject the state tracker around the right-hand expression side
                        instrumented_line = f"{indent}{binding_part}= (_record_state {line_no} \"{var_name}\" ({expression}))"
                        transformed_lines.append(instrumented_line)
                        continue

            transformed_lines.append(line)

        # Prepend tracking infrastructure to the file
        new_content = [generate_header()] + transformed_lines
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_content) + "\n")
        return True
    except Exception as e:
        print(f"Injection Error on {file_path}: {e}")
        return False

def process_project(source_dir):
    # Initialize separate sandbox environment
    target_dir = source_dir.rstrip('\\/') + f"_HASKELL_DEBUG_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    print(f"\n[START] Building instrumented Haskell sandbox...")
    
    # Initialize baseline diagnostic logs
    for log_file in ["_COMBINED_LOG.txt", "_VARIABLE_TRACKER.csv"]:
        with open(os.path.join(target_dir, log_file), "w", encoding="utf-8") as f:
            if log_file.endswith(".csv"):
                f.write("Line,Variable,Value\n")
            else:
                f.write(f"--- HASKELL SESSION START: {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")

    for root, _, files in os.walk(source_dir):
        # Ignore common build artifacts environments
        if any(x in root for x in ['.stack-work', 'dist', 'dist-newstyle', '.git']):
            continue
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            
            shutil.copy2(src, dst)
            if file.endswith(".hs"):
                inject_into_file(dst)
                print(f"    Instrumented: {file}")
                
    print(f"\n[FINISH] Safe Haskell project sandbox initialized at:\n{target_dir}")

if __name__ == "__main__":
    p = input("Haskell Project Path: ").strip().strip('"')
    if os.path.isdir(p):
        process_project(p)
    else:
        print("Invalid directory path.")
