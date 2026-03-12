import os
import shutil
import time
import re

# ==========================================
# 1. THE C++ LOGGER GENERATOR (Header & Source)
# ==========================================
def generate_cpp_header():
    return """#ifndef AD_DEBUG_LOGGER_H
#define AD_DEBUG_LOGGER_H
#include <string>
#include <iostream>
#include <fstream>
#include <mutex>

class AdDebugLogger {
private:
    static std::mutex logMutex;
public:
    static void logTrace(const char* file, int line);
};

// The macro we will inject everywhere
#define AD_TRACE_LINE() AdDebugLogger::logTrace(__FILE__, __LINE__)

#endif // AD_DEBUG_LOGGER_H
"""

def generate_cpp_source():
    return """#include "AdDebugLogger.h"

std::mutex AdDebugLogger::logMutex;

void AdDebugLogger::logTrace(const char* file, int line) {
    std::lock_guard<std::mutex> guard(logMutex);
    std::string msg = "[TRACE] Executing " + std::string(file) + " @ Line " + std::to_string(line) + "\\n";
    
    // Print to console
    std::cout << msg;
    
    // Append to log file
    std::ofstream logFile("_COMBINED_LOG.txt", std::ios_base::app);
    if (logFile.is_open()) {
        logFile << msg;
    }
}
"""

# ==========================================
# 2. THE INJECTION ENGINE (C++ Syntax)
# ==========================================
def inject_into_cpp_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_content = []
        has_included = False
        in_block_comment = False
        
        for line in lines:
            stripped = line.strip()
            indent_len = len(line) - len(line.lstrip())
            indent_str = line[:indent_len]

            # Handle block comments roughly (to avoid injecting inside them)
            if "/*" in stripped: in_block_comment = True
            if "*/" in stripped: in_block_comment = False; new_content.append(line); continue
            if in_block_comment: new_content.append(line); continue

            # Inject the include statement after any existing includes or at the top
            if not has_included and not stripped.startswith("#include"):
                # Use relative pathing based on standard project structures, or just root
                new_content.append('#include "AdDebugLogger.h"\n')
                has_included = True

            # Skip empty lines, comments, macros, or class/struct definitions
            if (not stripped or 
                stripped.startswith(('//', '#', 'class ', 'struct ', 'public:', 'private:', 'protected:', 'namespace '))):
                new_content.append(line)
                continue

            # Heuristic: Inject trace before standard statements ending in ';'
            # Avoid breaking control flow (return, break, continue, goto)
            control_keywords = ('return', 'break', 'continue', 'goto', 'throw')
            
            if stripped.endswith(';') and not any(stripped.startswith(k) for k in control_keywords):
                new_content.append(f'{indent_str}AD_TRACE_LINE();\n')
                new_content.append(line)
            else:
                new_content.append(line)

        # Fallback if the file was entirely includes
        if not has_included:
            new_content.insert(0, '#include "AdDebugLogger.h"\n')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
        return True
    except Exception as e:
        print(f"Injection Error: {e}")
        return False

# ==========================================
# 3. RUNNER
# ==========================================
def process_cpp_project(source_dir):
    suffix = int(time.time())
    target_dir = source_dir.rstrip('\\/') + f"_CPP_DEBUG_{suffix}"
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    print(f"\n[START] Building instrumented C++ project...")
    
    # Generate Logger Utility at the root of the new project
    with open(os.path.join(target_dir, "AdDebugLogger.h"), "w", encoding="utf-8") as f:
        f.write(generate_cpp_header())
    with open(os.path.join(target_dir, "AdDebugLogger.cpp"), "w", encoding="utf-8") as f:
        f.write(generate_cpp_source())
    
    for root, _, files in os.walk(source_dir):
        # Skip common build directories
        if any(x in root for x in ['.git', 'build', 'out', 'bin', 'Debug', 'Release']): continue
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            
            # Instrument .cpp and .cc files. (We usually avoid modifying headers .h/.hpp to prevent inline circular dependencies)
            if file.endswith((".cpp", ".cc", ".cxx")):
                shutil.copy2(src, dst)
                inject_into_cpp_file(dst)
                print(f"   Instrumented: {file}")
            else:
                shutil.copy2(src, dst)
                
    print(f"\n[FINISH] Project ready at: {target_dir}")
    print("\n[NOTE] Don't forget to add 'AdDebugLogger.cpp' to your compilation command or CMakeLists.txt!")

if __name__ == "__main__":
    p = input("C++ Project Path: ").strip().strip('"')
    if os.path.isdir(p):
        process_cpp_project(p)
    else:
        print("Invalid path.")
