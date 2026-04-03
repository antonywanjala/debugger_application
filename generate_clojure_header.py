import os
import shutil
import time
import re

# ==========================================
# 1. THE CLOJURE LOGGER HEADER (V7.0)
# ==========================================
def generate_clojure_header():
    """Generates Clojure-compatible logging and state tracking logic."""
    return """
;; ==========================================
;; CLOJURE STATE TRACKER & DEBUGGER
;; ==========================================
(require '[clojure.data.csv :as csv]
         '[clojure.java.io :as io])

(def ^:dynamic *ad-debug-active* true)

(defn- _record-state [line-no var-map]
  (when *ad-debug-active*
    (try
      (with-open [writer (io/writer "_VARIABLE_TRACKER.csv" :append true)]
        (csv/write-csv writer 
          (map (fn [[k v]] [line-no (str k) (pr-str v)]) var-map)))
      (catch Exception _ nil))))

(defn- _ad-log [msg is-error]
  (let [timestamp (.format (java.time.LocalDateTime/now) 
                           (java.time.format.DateTimeFormatter/ofPattern "yyyy-MM-dd HH:mm:ss"))
        tag (if is-error "[DEBUG_ERROR]" "[SCRIPT]")
        formatted (str tag " [" timestamp "] " msg)]
    (println formatted)
    (spit "_COMBINED_LOG.txt" (str formatted "\\n") :append true)))

;; ==========================================
"""

# ==========================================
# 2. THE CLOJURE PRE-PROCESSOR
# ==========================================
def clean_clojure_source(source):
    """Removes comments but preserves string literals for Clojure."""
    # Remove single line comments starting with ;
    source = re.sub(r';.*', '', source)
    return source

# ==========================================
# 3. THE CLOJURE INJECTION ENGINE
# ==========================================
def inject_into_clojure(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = clean_clojure_source(f.read())

        # Split by top-level forms (very basic heuristic: starts with '(')
        forms = re.split(r'\n(?=\()', content)
        new_content = [generate_clojure_header()]

        for i, form in enumerate(forms):
            if not form.strip(): continue
            
            # We wrap top-level forms in a try/catch to log failures
            # and inject a state recorder
            line_no = i + 1
            instrumented_form = f"""
(try
  (let [result {form.strip()}]
    (_record-state {line_no} {{'form-result result}})
    result)
  (catch Exception e
    (_ad-log (str "Line {line_no} Failed: " (.getMessage e)) true)
    (throw e)))"""
            new_content.append(instrumented_form)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_content))
        return True
    except Exception as e:
        print(f"Injection Error: {e}")
        return False

# ==========================================
# 4. RUNNER (Universal)
# ==========================================
def process_project(source_dir):
    target_dir = source_dir.rstrip('\\/') + f"_CLJ_DEBUG_{int(time.time())}"
    if not os.path.exists(target_dir): os.makedirs(target_dir)
    
    print(f"\n[START] Instrumenting Clojure Project...")
    
    for root, _, files in os.walk(source_dir):
        if any(x in root for x in ['target', '.git', '.lsp']): continue
        
        for file in files:
            if file.endswith((".clj", ".cljs", ".cljc")):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, os.path.relpath(src, source_dir))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                
                shutil.copy2(src, dst)
                inject_into_clojure(dst)
                print(f"    Instrumented: {file}")
                
    print(f"\n[FINISH] Instrumented project ready at: {target_dir}")

if __name__ == "__main__":
    p = input("Clojure Project Path: ").strip().strip('"')
    if os.path.isdir(p):
        process_project(p)
    else:
        print("Invalid path.")
