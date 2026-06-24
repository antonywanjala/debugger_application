import os
import shutil
import time

def generate_header():
    # Returns an Elixir module header that mimics your original tracking engine.
    # It sets up concurrent-safe logging configurations for Elixir scripts.
    return """# ==========================================
# STRICT ELIXIR WRAPPER + STATE TRACKER (V1.0)
# ==========================================
defmodule DebugTracker do
  @debug_active true

  def reset_logs do
    log_files = ["_DEBUG_ONLY.txt", "_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt"]
    Enum.each(log_files, fn f_name ->
      File.write(f_name, "--- SESSION START: #{DateTime.utc_now()} ---\\n")
    end)
    
    File.write("_VARIABLE_TRACKER.csv", "Line,Variable,Value\\n")
  end

  def record_state(line_no, var_name, var_val) do
    if @debug_active do
      clean_val = "#{inspect(var_val)}" |> String.replace("\\n", " ") |> String.replace("\\r", "")
      File.write("_VARIABLE_TRACKER.csv", "#{line_no},#{var_name},#{clean_val}\\n", [:append])
    end
    var_val
  end

  def ad_script_output(msg, is_error \\\\ true) do
    if @debug_active do
      timestamp = DateTime.utc_now() |> To_string()
      formatted = if is_error, do: "[DEBUG_ERROR] [#{timestamp}] #{msg}", else: "[SCRIPT] #{msg}"
      IO.puts(formatted)
      
      targets = if is_error, do: ["_DEBUG_ONLY.txt", "_COMBINED_LOG.txt"], else: ["_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt"]
      Enum.each(targets, fn f_name ->
        File.write(f_name, formatted <> "\\n", [:append])
      end)
    end
  end
end

unless Process.whereis(:ad_logs_wiped) do
  DebugTracker.reset_logs()
  Process.register(self(), :ad_logs_wiped)
end
# ==========================================\n"""


def inject_into_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Eradicate potential hidden characters
        raw_content = raw_content.replace('\xa0', ' ').replace('\u00a0', ' ')
        raw_lines = raw_content.splitlines()

        lines_meta = []
        in_heredoc = False

        # State tracking for Elixir multi-line heredocs (""" )
        for line in raw_lines:
            stripped = line.strip()
            line_starts_in_literal = in_heredoc

            # Basic heredoc toggle check
            if '"""' in line:
                # If it occurs once, it flips the state
                if line.count('"""') % 2 != 0:
                    in_heredoc = not in_heredoc

            line_ends_in_literal = in_heredoc
            is_literal = line_starts_in_literal or line_ends_in_literal or stripped.startswith('"""')
            lines_meta.append((line, is_literal))

        total_lines = len(lines_meta)
        transformed_lines = []

        # Elixir structural indicators
        structural_keywords = ('defmodule', 'def', 'defp', 'defmacro', 'if', 'unless', 'case', 'cond', 'with', 'try', 'quote', 'fn')

        for idx, (line_text, trapped_in_literal) in enumerate(lines_meta):
            stripped = line_text.strip()
            
            # Find indentation to preserve structure
            indent_len = len(line_text) - len(line_text.lstrip(' \t'))
            indent_str = line_text[:indent_len]

            # Leave empty lines, comments, or strings untouched
            if not stripped or stripped.startswith('#') or trapped_in_literal:
                transformed_lines.append(line_text)
                continue

            # Determine if this expression marks a structural block introduction or block ending
            is_structural = any(stripped.startswith(k) for k in structural_keywords) or stripped.endswith('do') or stripped == 'end'

            # Inject a functional wrapper inside pipeline-safe expressions
            if not is_structural and '=' in stripped and not stripped.startswith('import') and not stripped.startswith('alias'):
                # Simple extraction of variable name in an assignment (e.g., x = 5)
                var_part = stripped.split('=').strip()
                # Ensure the variable side is an alphanumeric identifier
                if var_part.isalnum():
                    block = [
                        f"{indent_str}try do",
                        f"{indent_str}  {stripped}",
                        f"{indent_str}  DebugTracker.record_state({idx + 1}, \"{var_part}\", {var_part})",
                        f"{indent_str}rescue",
                        f"{indent_str}  e ->",
                        f"{indent_str}    DebugTracker.ad_script_output(\"Line {idx + 1} Failed: #{{inspect(e)}}\", true)",
                        f"{indent_str}    reraise e, __STACKTRACE__",
                        f"{indent_str}end"
                    ]
                    transformed_lines.append("\n".join(block))
                    continue

            transformed_lines.append(line_text)

        new_content = [generate_header()] + transformed_lines
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_content) + "\n")
        return True
    except Exception as e:
        print(f"Injection Error on {file_path}: {e}")
        return False


def process_project(source_dir):
    target_dir = source_dir.rstrip('\\/') + f"_ELIXIR_DEBUG_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    print(f"\n[START] Building instrumented Elixir project layout...")
    
    for root, _, files in os.walk(source_dir):
        if any(x in root for x in ['_build', 'deps', '.git', '.elixir_ls']):
            continue
        for file in files:
            if file.endswith(".ex") or file.endswith(".exs"):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                inject_into_file(dst)
                print(f"    Instrumented: {file}")
    print(f"\n[FINISH] Safe project sandbox initialized at: {target_dir}")


if __name__ == "__main__":
    p = input("Elixir Project Path: ").strip().strip('"')
    if os.path.isdir(p):
        process_project(p)
    else:
        print("Invalid directory path.")
