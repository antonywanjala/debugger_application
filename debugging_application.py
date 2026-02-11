import inspect
import os
import types
import shutil
import time
import ast
import datetime


# ==========================================
# 0. DUAL-VERBOSITY LOGGER (Build Phase)
# ==========================================
class BuilderLogger:
    def __init__(self):
        self.logs = []
        self.target_dir = None
        self.expedited = False

    def log(self, message="", is_critical=False):
        tagged_msg = f"[DEBUGGER_BUILD] {message}"
        self.logs.append(tagged_msg)
        if not self.expedited or is_critical:
            print(tagged_msg)

    def save_report(self):
        if not self.target_dir: return
        report_path = os.path.join(self.target_dir, "_DEBUG_BUILD_REPORT.txt")
        header = f"\n{'=' * 60}\n FULL BUILD LOG: {datetime.datetime.now()}\n{'=' * 60}\n"
        with open(report_path, 'a', encoding='utf-8') as f:
            f.write(header + "\n".join(self.logs) + "\n")


builder = BuilderLogger()


# ==========================================
# 1. THE LOGGER HEADER (Execution-Time Logic)
# ==========================================
def generate_header(include_globals=False, interval=0):
    globals_flag = "True" if include_globals else "False"
    return f"""
# ==========================================
# AUTO-DEBUGGER INJECTION START
# ==========================================
import inspect
import os
import types
import datetime
import time

_AD_LAST_PUBLISH = 0
_AD_INTERVAL = {interval}

def _ad_logger(target_line_num, local_vars, active=True):
    global _AD_LAST_PUBLISH
    if not active: return
    try:
        frame = inspect.currentframe().f_back
        code_obj = frame.f_code
        filename = os.path.basename(code_obj.co_filename)
        current_debug_line = frame.f_lineno 

        include_globals = {globals_flag}
        vars_to_show = local_vars.copy()
        if include_globals:
            for k, v in frame.f_globals.items():
                if k not in vars_to_show: vars_to_show[k] = v

        summary_parts = []
        # Optimization: Prevent "Stuck" behavior on large objects
        primitives = (int, float, str, bool, type(None))
        containers = (list, dict, set, tuple)

        for k, v in vars_to_show.items():
            if k.startswith('_') or k in ('local_vars', 'In', 'Out'): continue
            try:
                if isinstance(v, primitives):
                    val_repr = repr(v)
                    summary_parts.append(f"{{k}}={{val_repr[:60]}}")
                elif isinstance(v, containers):
                    summary_parts.append(f"{{k}}({{type(v).__name__}} len={{len(v)}})")
                else:
                    summary_parts.append(f"{{k}}({{type(v).__name__}})")
            except: continue

        log_msg = f"[DEBUGGER] {{filename}}:{{current_debug_line}} | PRE-EXEC line {{target_line_num}} | Vars: {{', '.join(summary_parts)}}"
        print("\\n" + log_msg)

        timestamped_msg = f"[{{datetime.datetime.now()}}] {{log_msg}}\\n"

        # Route to Trace and Combined
        for fname in ["_DEBUG_TRACE_ONLY.txt", "_DEBUG_SUMMARY_COMBINED.txt"]:
            with open(fname, "a", encoding="utf-8") as f:
                f.write(timestamped_msg)
                f.flush()

        # Intermittent Summary Publication
        if _AD_INTERVAL > 0:
            current_now = time.time()
            if current_now - _AD_LAST_PUBLISH >= _AD_INTERVAL:
                pub_filename = f"DEBUG_SUMMARY_{{int(current_now)}}.txt"
                with open(pub_filename, "w", encoding="utf-8") as f:
                    f.write(f"--- [DEBUGGER] INTERMITTENT SUMMARY: {{datetime.datetime.now()}} ---\\n")
                    f.write(log_msg)
                _AD_LAST_PUBLISH = current_now
    except: pass 

def _ad_script_output(*args, **kwargs):
    # This captures all original print() and my_print() calls
    msg = " ".join(map(str, args))
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tagged_msg = f"[SCRIPTATLARGE] [{{timestamp}}] {{msg}}\\n"

    print(tagged_msg.strip())
    try:
        # Route to Script-Only and Combined
        for fname in ["_DEBUG_SCRIPT_ONLY.txt", "_DEBUG_SUMMARY_COMBINED.txt"]:
            with open(fname, "a", encoding="utf-8") as f:
                f.write(tagged_msg)
                f.flush()
    except: pass
# ==========================================
# AUTO-DEBUGGER INJECTION END
# ==========================================
"""


# ==========================================
# 2. INJECTION LOGIC (Deep Tagging)
# ==========================================
def inject_into_file(file_path, mode_choice, include_globals, interval):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        proposed_content = [generate_header(include_globals, interval)]
        bracket_level = 0
        in_multiline_string = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            indent = line[:len(line) - len(line.lstrip())]

            # --- CHANGE: AUTO-TAG SCRIPT OUTPUT ---
            # Replaces original prints with our routed logger
            if "print(" in line:
                line = line.replace("print(", "_ad_script_output(").replace("my_print(", "_ad_script_output(")

            # --- TRACE INJECTION LOGIC ---
            is_safe_to_start = (bracket_level == 0 and not in_multiline_string)
            if '"""' in stripped or "'''" in stripped:
                if (stripped.count('"""') % 2 != 0) or (stripped.count("'''") % 2 != 0):
                    in_multiline_string = not in_multiline_string

            bracket_level += (stripped.count('(') + stripped.count('[') + stripped.count('{'))
            bracket_level -= (stripped.count(')') + stripped.count(']') + stripped.count('}'))

            is_comment = stripped.startswith('#')
            is_block_continuation = any(
                stripped.startswith(w) for w in ('elif ', 'else:', 'except', 'finally:', ')', ']', '}'))
            is_decorator = stripped.startswith('@')

            should_inject = False
            if is_safe_to_start and stripped and not is_comment and not is_block_continuation and not is_decorator:
                if mode_choice == '1':
                    should_inject = True
                elif mode_choice == '2' and "# DEBUG" in line:
                    should_inject = True

            if should_inject:
                proposed_content.append(f"{indent}_ad_logger({i + 1}, locals())\n")

            proposed_content.append(line)

        full_script = "".join(proposed_content)
        ast.parse(full_script)  # Safety check

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_script)
        return True
    except Exception as e:
        builder.log(f"[ERROR] Logic failure in {file_path}: {e}", is_critical=True)
        return False


# ==========================================
# 3. PROJECT PROCESSING
# ==========================================
def process_project(source_dir, mode_choice, include_globals, interval):
    dir_name = os.path.basename(os.path.normpath(source_dir))
    target_dir = os.path.join(os.path.dirname(os.path.normpath(source_dir)),
                              f"{dir_name}_{int(time.time())}_debug_build")
    builder.target_dir = target_dir
    if not os.path.exists(target_dir): os.makedirs(target_dir)

    py_files = []
    for root, _, files in os.walk(source_dir):
        if any(x in root for x in ['venv', '.git', '__pycache__']): continue
        for file in files:
            if file.endswith(".py"):
                source_path = os.path.join(root, file)
                rel_path = os.path.relpath(source_path, source_dir)
                target_path = os.path.join(target_dir, rel_path)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copy2(source_path, target_path)
                py_files.append((rel_path, target_path))

    for idx, (rel, _) in enumerate(py_files):
        print(f"[{idx + 1}] {rel}")

    selection = input("\nFiles to inject (e.g. '1, 3-5', 'all'): ").strip()
    indices = []
    try:
        if selection.lower() == 'all':
            indices = list(range(len(py_files)))
        else:
            for part in selection.split(','):
                part = part.strip()
                if '-' in part:
                    s, e = map(int, part.split('-'))
                    indices.extend(range(s - 1, e))
                else:
                    indices.append(int(part) - 1)
    except:
        print("Invalid selection. Exiting.")
        return

    builder.log("\n--- Starting Injection Phase ---", is_critical=True)
    for idx in indices:
        name, path = py_files[idx]
        builder.log(f"Processing: {name}")
        status = "SUCCESS" if inject_into_file(path, mode_choice, include_globals, interval) else "FAILED"
        builder.log(f"[{status}] {name}", is_critical=True)

    builder.save_report()
    builder.log(f"\nTriple-Log Build Complete at: {target_dir}", is_critical=True)


def main():
    print("--- Isolated Resilient Debugger v3.3 (Deep Print Catch) ---")
    path = input("Project Path: ").strip().strip('"').strip("'")
    if not os.path.isdir(path): return

    mode = input("\n1.Full | 2.Selective: ").strip()
    scope = input("1.Local | 2.Global+Local: ").strip()
    v_choice = input("Expedited Console Readout? (y/n): ").strip().lower()

    try:
        interval = int(input("Seconds between Intermittent DEBUG_SUMMARY publications (0 for none): ").strip())
    except:
        interval = 0

    builder.expedited = (v_choice == 'y')
    process_project(path, mode, scope == '2', interval)


if __name__ == "__main__":
    main()
