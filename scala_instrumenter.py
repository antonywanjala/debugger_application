import os
import shutil
import time


def generate_header():
    """Generates a Scala utility singleton object for unified state and logging."""
    return """// ==========================================
// SCALA STATE TRACKER & WRAPPER UTILITY
// ==========================================
import java.io.{FileWriter, PrintWriter, File}
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

object _ScalaDebugTracker {
  private val formatter = DateTimeFormatter.ofPattern("Y-M-d H:m:s")
  
  def resetLogs(): Unit = {
    val logFiles = List("_DEBUG_ONLY.txt", "_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt", "_VARIABLE_TRACKER.csv")
    for (fName <- logFiles) {
      try {
        val pw = new PrintWriter(new File(fName))
        if (fName.endsWith(".csv")) {
          pw.write("Line,Variable,Value\\n")
        } else {
          pw.write(s"--- SESSION START: ${LocalDateTime.now()} ---\\n")
        }
        pw.close()
      } catch {
        case _: Exception => // Suppress
      }
    }
  }

  // Initialize logs once upon class load
  resetLogs()

  def recordState(lineNo: Int, varName: String, value: Any): Unit = {
    try {
      val fw = new FileWriter("_VARIABLE_TRACKER.csv", true)
      val cleanVal = s"$value".replace("\\n", " ").replace("\\r", "")
      fw.write(s"$lineNo,$varName,\\"$cleanVal\\"\\n")
      fw.close()
    } catch {
      case _: Exception => // Suppress
    }
  }

  def logOutput(msg: String, isError: Boolean = true): Unit = {
    val timestamp = LocalDateTime.now().format(formatter)
    val formatted = if (isError) s"[DEBUG_ERROR] [$timestamp] $msg" else s"[SCRIPT] $msg"
    
    // Fallback print to native stdout/stderr
    if (isError) System.err.println(formatted) else System.out.println(formatted)
    
    val targets = if (isError) List("_DEBUG_ONLY.txt", "_COMBINED_LOG.txt") else List("_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt")
    for (fName <- targets) {
      try {
        val fw = new FileWriter(fName, true)
        fw.write(formatted + "\\n")
        fw.close()
      } catch {
        case _: Exception => // Suppress
      }
    }
  }

  // Debugging wrapper alternative to raw println
  def debugPrint(msg: Any): Unit = {
    logOutput(s"$msg", isError = false)
  }
}
// ==========================================\n"""


def inject_into_file(file_path, max_depth=3):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Eradicate non-breaking spaces
        raw_content = raw_content.replace('\xa0', ' ').replace('\u00a0', ' ')
        raw_lines = raw_content.splitlines()

        lines_meta = []
        in_multiline_comment = False
        in_triple_quote = False

        # Build structural state machine mask for Scala syntax
        for line in raw_lines:
            stripped = line.strip()
            
            # Rough block-comment safety check
            if "/*" in line and "*/" not in line:
                in_multiline_comment = True
            elif "*/" in line and "/*" not in line:
                in_multiline_comment = False
                lines_meta.append((line, True))
                continue
                
            if '"""' in line and line.count('"""') % 2 != 0:
                in_triple_quote = not in_triple_quote

            is_literal_or_comment = (
                in_multiline_comment or 
                in_triple_quote or 
                stripped.startswith("//") or 
                stripped.startswith("/*") or 
                stripped.startswith("*") or
                not stripped
            )
            lines_meta.append((line, is_literal_or_comment))

        total_lines = len(lines_meta)
        transformed_lines = [None] * total_lines
        
        # Scala structural headers we don't want to wrap directly in try-catch
        structural_keywords = (
            'package ', 'import ', 'class ', 'object ', 'trait ', 'def ', 
            'if ', 'else ', 'for ', 'while ', 'match ', 'case '
        )

        for idx in range(total_lines):
            line_text, is_ignored = lines_meta[idx]
            content_part = line_text.lstrip(' \t')

            # Standardize indentation level based on 2 or 4 spaces (Scala default is usually 2 or 4)
            raw_indent = line_text[:len(line_text) - len(content_part)]
            total_space_weight = raw_indent.count(' ') + (raw_indent.count('\t') * 4)
            indent_level = max(0, total_space_weight // 2)  # Calculating at 2 spaces per step
            indent_str = '  ' * indent_level

            # Re-intercept standard println to use our custom sandboxed logger
            if "println(" in content_part and not is_ignored:
                content_part = content_part.replace("println(", "_ScalaDebugTracker.debugPrint(")

            if is_ignored:
                transformed_lines[idx] = indent_str + content_part
                continue

            is_structural = any(content_part.startswith(k) for k in structural_keywords) or content_part.endswith('{') or content_part.endswith('}')

            # Inject safely wrapper blocks for evaluable code expressions
            if not is_structural and indent_level <= (max_depth * 2):
                # Clean semicolon endings if needed
                stmt = content_part
                block = [
                    f"{indent_str}try {{",
                    f"{indent_str}  {stmt}",
                    f"{indent_str}}} catch {{",
                    f"{indent_str}  case e: Throwable => ",
                    f"{indent_str}    _ScalaDebugTracker.logOutput(\"Line {idx + 1} Failed: \" + e.getMessage, true)",
                    f"{indent_str}    throw e",
                    f"{indent_str}}}"
                ]
                transformed_lines[idx] = "\n".join(block)
            else:
                transformed_lines[idx] = indent_str + content_part

        # Assemble new file contents
        new_content = [generate_header()] + transformed_lines
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_content) + "\n")
        return True
    except Exception as e:
        print(f"Injection Error on {file_path}: {e}")
        return False


def process_project(source_dir, max_depth):
    target_dir = source_dir.rstrip('\\/') + f"_SCALA_DEBUG_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    print(f"\n[START] Building instrumented Scala project layout...")
    for root, _, files in os.walk(source_dir):
        # Ignore common Scala target build folders
        if any(x in root for x in ['target', '.git', '.bloop', '.metals', 'project/project']):
            continue
        for file in files:
            if file.endswith(".scala") or file.endswith(".sc"):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                inject_into_file(dst, max_depth)
                print(f"    Instrumented: {file}")
                
    print(f"\n[FINISH] Safe Scala sandbox initialized at: {target_dir}")


if __name__ == "__main__":
    p = input("Scala Project Path: ").strip().strip('"')
    try:
        d = int(input("Max Indent Depth for wrapping (default 3): ").strip() or 3)
    except:
        d = 3
    if os.path.isdir(p):
        process_project(p, d)
    else:
        print("Invalid directory path.")
