
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
import os


_ad_logger(6, locals())
def generate_header():
    """
    Returns the logic-gating code to be inserted at the top of the file.
    _ad_logger(9, locals())
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

_ad_logger(37, locals())
"""


_ad_logger(40, locals())
def is_control_flow_continuation(line):
    _ad_logger(41, locals())
    stripped = line.strip()
    # Matches else, elif, except, finally
    _ad_logger(43, locals())
    pattern = r'^(else|elif|except|finally)\b'
    _ad_logger(44, locals())
    return bool(re.match(pattern, stripped))


_ad_logger(47, locals())
def is_safe_to_instrument(line):
    _ad_logger(48, locals())
    stripped = line.strip()
    _ad_logger(49, locals())
    if not stripped: return False
    _ad_logger(50, locals())
    if stripped.startswith('#'): return False
    _ad_logger(51, locals())
    if stripped.startswith('@'): return False
    if stripped.startswith('"""') or stripped.startswith("'''"): return False
    return True


def get_indentation(line):
    return line[:len(line) - len(line.lstrip())]


def instrument_file(input_path, output_path):
    # Normalize paths for cross-platform compatibility
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)

    print(f"Reading from: {input_path}")
    print(f"Writing to:   {output_path}")

    if not os.path.exists(input_path):
        print(f"\nError: The file '{input_path}' does not exist.")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    instrumented_lines = []
    instrumented_lines.append(generate_header())

    in_multiline_string = False

    for i, line in enumerate(lines):
        original_line = line
        stripped = line.strip()
        indent = get_indentation(line)
        line_num = i + 1

        _ad_logger(90, locals())
        if '"""' in stripped or "'''" in stripped:
            if stripped.count('"""') % 2 != 0 or stripped.count("'''") % 2 != 0:
                in_multiline_string = not in_multiline_string

        if (not in_multiline_string and
                is_safe_to_instrument(line) and
                not is_control_flow_continuation(line)):
            debug_stmt = f"{indent}_ad_logger({line_num}, locals())\n"
            instrumented_lines.append(debug_stmt)

        instrumented_lines.append(original_line)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(instrumented_lines)
        print(f"\nSuccess! Debuggable file created at:\n{output_path}")
    except Exception as e:
        print(f"Error writing output: {e}")


if __name__ == "__main__":
    # Check if user provided arguments
    if len(sys.argv) < 2:
        print("Usage: python auto_debugger.py <absolute_path_to_file.py> [optional_output_path.py]")
        print("Error: No input file specified.")
        sys.exit(1)

    input_arg = sys.argv[1]

    # Generate Output Path logic
    if len(sys.argv) >= 3:
        # User specified output
        output_arg = sys.argv[2]
    else:
        # Auto-generate output name in the SAME folder as the input
        # e.g., C:/Users/Me/script.py -> C:/Users/Me/script_debug.py
        dir_name = os.path.dirname(input_arg)
        base_name = os.path.basename(input_arg)
        name, ext = os.path.splitext(base_name)
        new_name = f"{name}_debug{ext}"
        output_arg = os.path.join(dir_name, new_name)

    instrument_file(input_arg, output_arg)
