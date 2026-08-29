import os
import shutil
import time

def generate_asp_header(engine="vbscript"):
    """
    Generates an ASP-compatible debug header and file-logging mechanism
    tailored to VBScript or JScript.
    """
    if engine.lower() == "jscript":
        return """<%@ Language="JScript" %>
<%
// ==========================================
// ASP JSCRIPT DEBUG & STATE TRACKER
// ==========================================
var _AD_DEBUG_ACTIVE = true;

function _ad_log(msg, isError) {
    if (!_AD_DEBUG_ACTIVE) return;
    try {
        var fso = Server.CreateObject("Scripting.FileSystemObject");
        var logFile = Server.MapPath("_ASP_DEBUG_LOG.txt");
        var file = fso.OpenTextFile(logFile, 8, true);
        var timeStamp = new Date().toISOString();
        file.WriteLine("[" + (isError ? "ERROR" : "INFO") + "] [" + timeStamp + "] " + msg);
        file.Close();
    } catch(e) {}
}

function _record_state(lineNo, varDict) {
    if (!_AD_DEBUG_ACTIVE) return;
    try {
        var fso = Server.CreateObject("Scripting.FileSystemObject");
        var csvFile = Server.MapPath("_VARIABLE_TRACKER.csv");
        var file = fso.OpenTextFile(csvFile, 8, true);
        for (var k in varDict) {
            var val = String(varDict[k]).replace(/\\r?\\n|\\r/g, " ");
            file.WriteLine(lineNo + ',"' + k + '","' + val + '"');
        }
        file.Close();
    } catch(e) {}
}
%>
"""
    else: # Default: VBScript
        return """<%@ Language="VBScript" %>
<%
' ==========================================
' ASP VBSCRIPT DEBUG & STATE TRACKER
' ==========================================
Dim _AD_DEBUG_ACTIVE
_AD_DEBUG_ACTIVE = True

Sub _ad_log(msg, isError)
    If Not _AD_DEBUG_ACTIVE Then Exit Sub
    On Error Resume Next
    Dim fso, logPath, file, prefix
    Set fso = Server.CreateObject("Scripting.FileSystemObject")
    logPath = Server.MapPath("_ASP_DEBUG_LOG.txt")
    Set file = fso.OpenTextFile(logPath, 8, True)
    If isError Then prefix = "[ERROR] " Else prefix = "[INFO] "
    file.WriteLine(prefix & "[" & Now() & "] " & msg)
    file.Close()
    On Error GoTo 0
End Sub

Sub _record_var(lineNo, varName, varValue)
    If Not _AD_DEBUG_ACTIVE Then Exit Sub
    On Error Resume Next
    Dim fso, csvPath, file, cleanVal
    Set fso = Server.CreateObject("Scripting.FileSystemObject")
    csvPath = Server.MapPath("_VARIABLE_TRACKER.csv")
    Set file = fso.OpenTextFile(csvPath, 8, True)
    cleanVal = Replace(Replace(CStr(varValue), vbCrLf, " "), vbLf, " ")
    file.WriteLine(lineNo & ',"' & varName & '","' & cleanVal & '"')
    file.Close()
    On Error GoTo 0
End Sub
%>
"""

def inject_into_asp_file(file_path, engine="vbscript"):
    """
    Parses ASP scripts and wraps line executions with error handlers 
    and log traps suitable for ASP server runtime environments.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_lines = f.readlines()

        transformed_lines = []
        
        if engine.lower() == "vbscript":
            # Enable ASP VBScript Runtime Error Trapping
            transformed_lines.append('<% On Error Resume Next %>\n')
            
            for idx, line in enumerate(raw_lines):
                trimmed = line.strip()
                
                # Skip ASP directives, pure HTML lines, comments, and structural code blocks
                if not trimmed or not ('<%' in line or '%>' in line) and not line.strip().startswith(('Dim', 'Set', 'Response.', 'Session', 'Application')):
                    transformed_lines.append(line)
                    continue

                if trimmed.startswith("'") or trimmed.startswith("<%") or trimmed.endswith("%>") or trimmed.lower().startswith(("if", "sub", "function", "else", "end", "loop", "next")):
                    transformed_lines.append(line)
                else:
                    # Inject line execution validation block
                    block = (
                        f"{line.rstrip()}\n"
                        f"<% If Err.Number <> 0 Then "
                        f"_ad_log \"Line {idx + 1} Error: \" & Err.Description, True : "
                        f"Err.Clear : End If %>\n"
                    )
                    transformed_lines.append(block)
                    
        elif engine.lower() == "jscript":
            for idx, line in enumerate(raw_lines):
                trimmed = line.strip()
                if not trimmed or trimmed.startswith("//") or trimmed.startswith("<%") or trimmed.endswith("%>") or trimmed.startswith(("if", "function", "else", "for", "while", "try", "catch")):
                    transformed_lines.append(line)
                else:
                    block = (
                        f"<% try {{ %>\n"
                        f"{line.rstrip()}\n"
                        f"<% }} catch(e) {{ _ad_log('Line {idx + 1} Failed: ' + e.description, true); }} %>\n"
                    )
                    transformed_lines.append(block)

        # Prepend ASP Debug Header
        new_content = [generate_asp_header(engine)] + transformed_lines
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
        return True

    except Exception as e:
        print(f"Error instrumenting {file_path}: {e}")
        return False


def process_asp_project(source_dir, engine):
    target_dir = source_dir.rstrip('\\/') + f"_ASP_DEBUG_{int(time.time())}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    print("\n[START] Building instrumented ASP project layout...")
    
    for root, _, files in os.walk(source_dir):
        for file in files:
            # Match standard ASP extensions
            if file.lower().endswith((".asp", ".inc")):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                
                inject_into_asp_file(dst, engine)
                print(f"    Instrumented ASP Script: {file}")

    print(f"\n[FINISH] Instrumented ASP project created at:\n--> {target_dir}")
    print("\nNote: Make sure IIS permissions allow write operations to '_ASP_DEBUG_LOG.txt' and '_VARIABLE_TRACKER.csv' in the target directory.")


if __name__ == "__main__":
    path = input("ASP Project Path: ").strip().strip('"')
    
    print("Select Scripting Engine:\n1. VBScript (Default)\n2. JScript")
    choice = input("Choice (1/2): ").strip()
    
    engine_choice = "jscript" if choice == "2" else "vbscript"

    if os.path.isdir(path):
        process_asp_project(path, engine_choice)
    else:
        print("Invalid directory path.")
