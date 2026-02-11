
# ==========================================
# AUTO-DEBUGGER INJECTION START
# ==========================================
import inspect
import os
import types

def _ad_logger(original_line, local_vars, active=True):
    if not active:
        return

    frame = inspect.currentframe().f_back
    code_obj = frame.f_code
    func_name = code_obj.co_name
    abs_path = os.path.abspath(code_obj.co_filename)
    filename = os.path.basename(abs_path)
    debug_exec_line = frame.f_lineno
    func_start_line = code_obj.co_firstlineno

    if func_name == '<module>':
        rel_line = debug_exec_line
        display_func = "Main Script"
        offset_str = f"Line {rel_line}" 
    else:
        rel_line = debug_exec_line - func_start_line
        display_func = func_name
        offset_str = f"+{rel_line} (inside {display_func})"

    include_globals = True
    vars_to_show = local_vars.copy()

    if include_globals:
        for k, v in frame.f_globals.items():
            if k not in vars_to_show:
                vars_to_show[k] = v

    summary_parts = []

    # Standard primitive types that should display their VALUE
    primitives = (int, float, str, bool, type(None), list, dict, set, tuple)

    for k, v in vars_to_show.items():
        if k.startswith('_') or k in ('local_vars', 'In', 'Out'):
            continue

        # 1. Filter out Modules and Functions entirely
        if isinstance(v, (types.ModuleType, types.FunctionType, types.BuiltinFunctionType)):
            continue

        try:
            # 2. Check if it is a primitive (Value) or an Object (Description)
            if isinstance(v, primitives):
                summary_parts.append(f"{k} = {repr(v)}")
            else:
                # It is a complex object/class instance
                cls_name = type(v).__name__
                # Get the module (file) where the class is defined
                origin = getattr(v, '__module__', 'unknown_source')
                summary_parts.append(f"{k} is an instantiation of {cls_name} from {origin}")

        except:
            continue

    var_string = ", ".join(summary_parts)

    print(f"\n[DEBUG] {filename} | {display_func}")
    print(f"   Positions: Orig {original_line} | Debug {debug_exec_line} | Offset {offset_str}")
    if var_string:
        print(f"   Variables: {var_string}")
# ==========================================
# AUTO-DEBUGGER INJECTION END
# ==========================================
_ad_logger(1, locals())
import sys
_ad_logger(2, locals())
import re
_ad_logger(3, locals())
import argparse
_ad_logger(4, locals())
import keyword


_ad_logger(7, locals())
def generate_header():
    """
    Returns the logic-gating code to be inserted at the top of the file.
    _ad_logger(10, locals())
    """
    return """
# ==========================================
# AUTO-DEBUGGER INJECTION START
# ==========================================
import sys

# LOGIC GATES
_AD_DEBUG_MODE = True      # Set to False to disable all prints
_AD_SHOW_VARS = True       # Set to False to hide variable dumps

def _ad_logger(line_num, local_vars):
    if not _AD_DEBUG_MODE:
        return

    print(f"\\n[DEBUG] --> Line {line_num} executed")

    if _AD_SHOW_VARS:
        # Filter out internal python vars (starts with __) and the logger itself
        clean_vars = {k: repr(v) for k, v in local_vars.items() 
                      if not k.startswith('__') and k != '_ad_logger'}

        if clean_vars:
            print(f"    [VARS]: {clean_vars}")
# ==========================================
# AUTO-DEBUGGER INJECTION END
# ==========================================

_ad_logger(38, locals())
"""


_ad_logger(41, locals())
def is_control_flow_continuation(line):
    """
    Checks if a line starts with keywords that cannot have code inserted
    immediately before them (else, elif, except, finally).
    _ad_logger(45, locals())
    """
    _ad_logger(46, locals())
    stripped = line.strip()
    # Regex to match 'else:', 'elif ...:', 'except ...:', 'finally:'
    # We look for the keyword at the start of the line
    _ad_logger(49, locals())
    pattern = r'^(else|elif|except|finally)\b'
    _ad_logger(50, locals())
    return bool(re.match(pattern, stripped))


_ad_logger(53, locals())
def is_safe_to_instrument(line):
    """
    Determines if the line is actual code vs comments/empty/decorators.
    _ad_logger(56, locals())
    """
    _ad_logger(57, locals())
    stripped = line.strip()
    _ad_logger(58, locals())
    if not stripped: return False  # Empty line
    _ad_logger(59, locals())
    if stripped.startswith('#'): return False  # Comment
    _ad_logger(60, locals())
    if stripped.startswith('@'): return False  # Decorator (must be directly above func)
    if stripped.startswith('"""') or stripped.startswith("'''"): return False  # Docstrings (simplified)
    return True


def get_indentation(line):
    """Returns the whitespace string at the start of the line."""
    return line[:len(line) - len(line.lstrip())]


def instrument_file(input_path, output_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File {input_path} not found.")
        return

    instrumented_lines = []

    # Add the header logic gates
    instrumented_lines.append(generate_header())

    # Stack to track if we are inside a multi-line string (basic detection)
    in_multiline_string = False

    for i, line in enumerate(lines):
        original_line = line
        stripped = line.strip()
        indent = get_indentation(line)
        line_num = i + 1

        # Toggle multiline string state (simplified detection)
        _ad_logger(93, locals())
        if '"""' in stripped or "'''" in stripped:
            if stripped.count('"""') % 2 != 0 or stripped.count("'''") % 2 != 0:
                in_multiline_string = not in_multiline_string

        # LOGIC:
        # 1. Ignore lines inside multi-line strings
        # 2. Ignore comments/empty lines
        # 3. DO NOT insert before 'else', 'elif', 'except', 'finally'
        #    (We rely on the print statements inside the previous block or the next line)
        if (not in_multiline_string and
                is_safe_to_instrument(line) and
                not is_control_flow_continuation(line)):
            # Create the debug statement with matching indentation
            # passing `locals()` captures the state at that specific line
            debug_stmt = f"{indent}_ad_logger({line_num}, locals())\n"
            instrumented_lines.append(debug_stmt)

        instrumented_lines.append(original_line)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(instrumented_lines)
        print(f"Success! Instrumented file saved to: {output_path}")
        print("Run the new file to see debug output.")
    except Exception as e:
        print(f"Error writing output: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject debug print statements into a Python script.")
    parser.add_argument("input_file", help="The .py file to instrument")
    parser.add_argument("-o", "--output", help="The output file name (default: debug_output.py)", default="debug_output.py")

    args = parser.parse_args()

    instrument_file(args.input_file, args.output)