import inspect
import os
import types
import shutil
import time
import ast
import datetime


# ==========================================
# 0. DUAL-VERBOSITY LOGGER
# ==========================================
class BuilderLogger:
    def __init__(self):
        self.logs = []
        self.target_dir = None
        self.expedited = False

    def log(self, message="", is_critical=False):
        # Store everything for the text file
        self.logs.append(message)

        # Console output logic
        if not self.expedited or is_critical:
            print(message)

    def save_report(self):
        if not self.target_dir: return
        report_path = os.path.join(self.target_dir, "_DEBUG_SUMMARY.txt")
        header = f"\n{'=' * 60}\n FULL DEBUG BUILD REPORT: {datetime.datetime.now()}\n{'=' * 60}\n"
        with open(report_path, 'a', encoding='utf-8') as f:
            f.write(header + "\n".join(self.logs) + "\n")


builder = BuilderLogger()


# ==========================================
# 1. THE LOGGER HEADER (Real-time File Logging)
# ==========================================
def generate_header(include_globals=False):
    globals_flag = "True" if include_globals else "False"
    return f"""
# ==========================================
# AUTO-DEBUGGER INJECTION START
# ==========================================
import inspect
import os
import types
import datetime

def _ad_logger(target_line_num, local_vars, active=True):
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
        primitives = (int, float, str, bool, type(None), list, dict, set, tuple)
        for k, v in vars_to_show.items():
            if k.startswith('_') or k in ('local_vars', 'In', 'Out'): continue
            if isinstance(v, (types.ModuleType, types.FunctionType, types.BuiltinFunctionType)): continue
            try:
                if isinstance(v, primitives):
                    val_repr = repr(v)
                    summary_parts.append(f"{{k}}={{val_repr[:100]}}")
                else:
                    summary_parts.append(f"{{k}}({{type(v).__name__}})")
            except: continue

        log_msg = f"[DEBUG] {{filename}}:{{current_debug_line}} | PRE-EXEC line {{target_line_num}} | Vars: {{', '.join(summary_parts)}}"
        print("\\n" + log_msg)

        with open("_DEBUG_SUMMARY.txt", "a", encoding="utf-8") as f:
            f.write(f"[{{datetime.datetime.now()}}] {{log_msg}}\\n")
    except: pass 
# ==========================================
# AUTO-DEBUGGER INJECTION END
# ==========================================
"""


# ==========================================
# 2. INJECTION LOGIC (Expression-Aware)
# ==========================================
def inject_into_file(file_path, mode_choice, include_globals):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        proposed_content = [generate_header(include_globals)]
        bracket_level = 0
        in_multiline_string = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            indent = line[:len(line) - len(line.lstrip())]
            original_line_num = i + 1

            # Determine safety BEFORE updating bracket_level for the current line
            # This ensures we don't inject inside a function call like my_print(arg1, arg2)
            is_safe_to_start = (bracket_level == 0 and not in_multiline_string)

            # Update nesting state
            if '"""' in stripped or "'''" in stripped:
                if (stripped.count('"""') % 2 != 0) or (stripped.count("'''") % 2 != 0):
                    in_multiline_string = not in_multiline_string

            bracket_level += (stripped.count('(') + stripped.count('[') + stripped.count('{'))
            bracket_level -= (stripped.count(')') + stripped.count(']') + stripped.count('}'))

            # Rules for Pre-Line Injection
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
                proposed_content.append(f"{indent}_ad_logger({original_line_num}, locals())\n")

            proposed_content.append(line)

        # Validation
        full_script = "".join(proposed_content)
        try:
            ast.parse(full_script)
        except SyntaxError as se:
            builder.log(f"[BLOCK] Syntax Error in {os.path.basename(file_path)}: {se.msg} at line {se.lineno}",
                        is_critical=True)
            return False

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_script)
        return True

    except Exception as e:
        builder.log(f"[ERROR] Logic failure in {file_path}: {e}", is_critical=True)
        return False


# ==========================================
# 3. PROJECT PROCESSING
# ==========================================
def process_project(source_dir, mode_choice, include_globals):
    dir_name = os.path.basename(os.path.normpath(source_dir))
    target_dir = os.path.join(os.path.dirname(os.path.normpath(source_dir)),
                              f"{dir_name}_{int(time.time())}_debug_build")
    builder.target_dir = target_dir

    if not os.path.exists(target_dir): os.makedirs(target_dir)

    py_files = []
    builder.log(f"--- Cloned Project Directory: {target_dir} ---")

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

    builder.log("\n--- Starting Injection Phase ---", is_critical=True)
    for idx in indices:
        name, path = py_files[idx]
        builder.log(f"Processing: {name}")
        status = "SUCCESS" if inject_into_file(path, mode_choice, include_globals) else "FAILED"
        builder.log(f"[{status}] {name}", is_critical=True)

    builder.save_report()
    builder.log(f"\nFinal Summary saved to {target_dir}/_DEBUG_SUMMARY.txt", is_critical=True)


def main():
    print("--- Isolated Resilient Debugger v3.0 ---")
    path = input("Project Path: ").strip().strip('"').strip("'")
    if not os.path.isdir(path): return

    mode = input("\n1.Full | 2.Selective: ").strip()
    scope = input("1.Local | 2.Global+Local: ").strip()

    # NEW: Verbosity Choice
    v_choice = input("\nExpedited Console Readout? (y/n): ").strip().lower()
    builder.expedited = (v_choice == 'y')

    process_project(path, mode, scope == '2')


if __name__ == "__main__":
    main()
