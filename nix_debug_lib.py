import os
import re
import shutil
import time

def generate_nix_debug_lib():
    """Returns pure Nix helper utilities for deep tracing and log formatting."""
    return '''# Nix Debugging Helpers (Generated)
rec {
  # Wraps a value to print its label and contents during evaluation
  traceVal = label: val: builtins.trace "${label}:${builtins.toJSON val}" val;

  # Recursively traces deep attribute sets safely
  traceDeep = label: val:
    let
      tryJson = builtins.tryEval (builtins.toJSON val);
      safeVal = if tryJson.success then tryJson.value else "<unserializable/lambda>";
    in
    builtins.trace "[NIX_DEBUG] ${label} =${safeVal}" val;
}
'''

def inject_into_nix_file(file_path):
    """Instruments a .nix file by injecting trace wrappers around key bindings."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Clean non-breaking spaces
        content = content.replace('\xa0', ' ').replace('\u00a0', ' ')
        
        # Helper: Inject builtins.trace into `let ... in` assignments
        # Matches: variableName = expression;
        def trace_let_binding(match):
            var_name = match.group(1)
            expr = match.group(2)
            # Avoid re-instrumenting or tracing internal builtins
            if var_name.startswith('_') or var_name in ['pkgs', 'lib', 'config', 'options']:
                return match.group(0)
            return f'{var_name} = builtins.trace "[DEBUG] Evaluated {var_name}" ({expr});'

        # Regex targeting standard Nix let-bindings: key = val;
        let_pattern = r'([a-zA-Z0-9_\-\.]+)\s*=\s*([^;]+);'
        instrumented = re.sub(let_pattern, trace_let_binding, content)

        # Inject builtins.trace at top of evaluation
        rel_path = os.path.basename(file_path)
        header_trace = f'builtins.trace "[NIX_SESSION] Evaluating file: {rel_path}"\n'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(header_trace + instrumented)
            
        return True
    except Exception as e:
        print(f"Injection Error in {file_path}: {e}")
        return False


def process_nix_project(source_dir):
    """Duplicates project and instruments all .nix files."""
    target_dir = source_dir.rstrip('\\/') + f"_NIX_DEBUG_{int(time.time())}"
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    print("\n[START] Initializing Nix debug sandbox...")

    # Write Nix tracing helpers
    lib_path = os.path.join(target_dir, "_debug_helpers.nix")
    with open(lib_path, 'w', encoding='utf-8') as f:
        f.write(generate_nix_debug_lib())

    for root, _, files in os.walk(source_dir):
        if any(x in root for x in ['.git', 'result', '.nix-defexpr', 'node_modules']):
            continue
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            
            shutil.copy2(src, dst)
            
            if file.endswith(".nix") and file != "_debug_helpers.nix":
                inject_into_nix_file(dst)
                print(f"    Instrumented: {file}")

    print(f"\n[FINISH] Safe Nix debug sandbox built at: {target_dir}")
    print("\n[HINT] Build or evaluate using:")
    print(f"  nix-instantiate --eval {target_dir}/default.nix")
    print(f"  nix build -f {target_dir}")


if __name__ == "__main__":
    path = input("Nix Project Directory Path: ").strip().strip('"')
    if os.path.isdir(path):
        process_nix_project(path)
    else:
        print("Invalid directory path.")
