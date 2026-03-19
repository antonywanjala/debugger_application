
# ==========================================
# STRICT RECURSIVE WRAPPER + STATE TRACKER (V6.4)
# ==========================================
import datetime as _dt
import sys
import os
import builtins 
import csv

_AD_DEBUG_ACTIVE = True
_ORIGINAL_PRINT = builtins.print 

def _reset_logs():
    log_files = ["_DEBUG_ONLY.txt", "_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt"]
    for f_name in log_files:
        try:
            with open(f_name, "w", encoding="utf-8") as f:
                f.write(f"--- SESSION START: {_dt.datetime.now()} ---\n")
        except: pass

    try:
        with open("_VARIABLE_TRACKER.csv", "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Line", "Variable", "Value"])
    except: pass

if not hasattr(builtins, '_AD_LOGS_WIPED'):
    _reset_logs()
    builtins._AD_LOGS_WIPED = True

def _record_state(line_no, local_vars):
    if not _AD_DEBUG_ACTIVE: return
    try:
        with open("_VARIABLE_TRACKER.csv", "a", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            for var_name, var_val in local_vars.items():
                if var_name.startswith('_'): continue
                clean_val = str(var_val).replace('\n', ' ').replace('\r', '')
                writer.writerow([line_no, var_name, clean_val])
    except: pass

def _ad_script_output(msg, is_error=True):
    """Restores the SCRIPT and DEBUG_ERROR tags for console/file parity."""
    if not _AD_DEBUG_ACTIVE: return
    timestamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    formatted = f"[DEBUG_ERROR] [{timestamp}] {msg}" if is_error else f"[SCRIPT] {msg}"

    _ORIGINAL_PRINT(formatted)

    target = ["_DEBUG_ONLY.txt", "_COMBINED_LOG.txt"] if is_error else ["_SCRIPT_ONLY.txt", "_COMBINED_LOG.txt"]
    for f_name in target:
        try:
            with open(f_name, "a", encoding="utf-8") as f: f.write(formatted + "\n")
        except: pass

def print(*args, **kwargs):
    output = " ".join(map(str, args))
    _ad_script_output(output, is_error=False)

builtins.print = print
# ==========================================

import csv
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime, timedelta


try:
    BG_MAIN = "#0f172a"
    _record_state(7, locals())
except Exception as e:
    _ad_script_output(f'Line 7 Failed: {e}', is_error=True)
    raise
try:
    BG_CARD = "#1e293b"
    _record_state(8, locals())
except Exception as e:
    _ad_script_output(f'Line 8 Failed: {e}', is_error=True)
    raise
try:
    ACCENT = "#38bdf8"
    _record_state(9, locals())
except Exception as e:
    _ad_script_output(f'Line 9 Failed: {e}', is_error=True)
    raise
try:
    TEXT_COLOR = "#f8fafc"
    _record_state(10, locals())
except Exception as e:
    _ad_script_output(f'Line 10 Failed: {e}', is_error=True)
    raise
try:
    DANGER = "#ef4444"
    _record_state(11, locals())
except Exception as e:
    _ad_script_output(f'Line 11 Failed: {e}', is_error=True)
    raise
try:
    WARNING = "#f59e0b"
    _record_state(12, locals())
except Exception as e:
    _ad_script_output(f'Line 12 Failed: {e}', is_error=True)
    raise


class Activity:
    def __init__(self, name, act_type, start, end):
        try:
            self.name = name
            _record_state(17, locals())
        except Exception as e:
            _ad_script_output(f'Line 17 Failed: {e}', is_error=True)
            raise
        try:
            self.act_type = act_type
            _record_state(18, locals())
        except Exception as e:
            _ad_script_output(f'Line 18 Failed: {e}', is_error=True)
            raise
        try:
            self.start = start
            _record_state(19, locals())
        except Exception as e:
            _ad_script_output(f'Line 19 Failed: {e}', is_error=True)
            raise
        try:
            self.end = end
            _record_state(20, locals())
        except Exception as e:
            _ad_script_output(f'Line 20 Failed: {e}', is_error=True)
            raise


class ActivitySchedulerPro:
    def __init__(self, root):
        try:
            self.root = root
            _record_state(25, locals())
        except Exception as e:
            _ad_script_output(f'Line 25 Failed: {e}', is_error=True)
            raise
        try:
            self.root.title("Activity Scheduler Pro")
            _record_state(26, locals())
        except Exception as e:
            _ad_script_output(f'Line 26 Failed: {e}', is_error=True)
            raise
        try:
            self.root.geometry("1100x800")
            _record_state(27, locals())
        except Exception as e:
            _ad_script_output(f'Line 27 Failed: {e}', is_error=True)
            raise
        try:
            self.root.configure(bg=BG_MAIN)
            _record_state(28, locals())
        except Exception as e:
            _ad_script_output(f'Line 28 Failed: {e}', is_error=True)
            raise
        try:
            self.root.minsize(900, 700)
            _record_state(29, locals())
        except Exception as e:
            _ad_script_output(f'Line 29 Failed: {e}', is_error=True)
            raise

        try:
            self.activities = []
            _record_state(31, locals())
        except Exception as e:
            _ad_script_output(f'Line 31 Failed: {e}', is_error=True)
            raise
        try:
            self.sort_column = None
            _record_state(32, locals())
        except Exception as e:
            _ad_script_output(f'Line 32 Failed: {e}', is_error=True)
            raise
        try:
            self.sort_clicks = 0
            _record_state(33, locals())
        except Exception as e:
            _ad_script_output(f'Line 33 Failed: {e}', is_error=True)
            raise

        
        try:
            self.type_colors = {}
            _record_state(36, locals())
        except Exception as e:
            _ad_script_output(f'Line 36 Failed: {e}', is_error=True)
            raise
        try:
            self.color_palette = ["#1e3a8a", "#581c87", "#064e3b", "#7c2d12", "#4c1d95", "#831843"]
            _record_state(37, locals())
        except Exception as e:
            _ad_script_output(f'Line 37 Failed: {e}', is_error=True)
            raise

        try:
            self.setup_styles()
            _record_state(39, locals())
        except Exception as e:
            _ad_script_output(f'Line 39 Failed: {e}', is_error=True)
            raise
        try:
            self.create_widgets()
            _record_state(40, locals())
        except Exception as e:
            _ad_script_output(f'Line 40 Failed: {e}', is_error=True)
            raise

    def setup_styles(self):
        try:
            style = ttk.Style()
            _record_state(43, locals())
        except Exception as e:
            _ad_script_output(f'Line 43 Failed: {e}', is_error=True)
            raise
        try:
            style.theme_use("clam")
            _record_state(44, locals())
        except Exception as e:
            _ad_script_output(f'Line 44 Failed: {e}', is_error=True)
            raise
        style.configure("Treeview",
                        background=BG_CARD,
                        foreground=TEXT_COLOR,
                        fieldbackground=BG_CARD,
                        rowheight=35,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#334155",
                        foreground=ACCENT,
                        relief="flat",
                        font=("Segoe UI", 10, "bold"))
        try:
            style.map("Treeview", background=[('selected', ACCENT)], foreground=[('selected', "black")])
            _record_state(56, locals())
        except Exception as e:
            _ad_script_output(f'Line 56 Failed: {e}', is_error=True)
            raise

    def create_widgets(self):
        
        try:
            self.main_container = tk.Frame(self.root, bg=BG_MAIN)
            _record_state(60, locals())
        except Exception as e:
            _ad_script_output(f'Line 60 Failed: {e}', is_error=True)
            raise
        try:
            self.main_container.pack(fill="both", expand=True, padx=20, pady=10)
            _record_state(61, locals())
        except Exception as e:
            _ad_script_output(f'Line 61 Failed: {e}', is_error=True)
            raise

        
        tk.Label(self.main_container, text="ACTIVITY SCHEDULER PRO", font=("Segoe UI", 26, "bold"),
                 bg=BG_MAIN, fg=ACCENT).pack(pady=(10, 20))

        
        tk.Label(self.main_container, text="ADD NEW ACTIVITY", font=("Segoe UI", 12, "bold"),
                 bg=BG_MAIN, fg=TEXT_COLOR).pack(pady=5)

        input_frame = tk.Frame(self.main_container, bg=BG_CARD, padx=20, pady=20,
                               highlightthickness=1, highlightbackground="#334155")
        try:
            input_frame.pack(fill="x", pady=10)
            _record_state(73, locals())
        except Exception as e:
            _ad_script_output(f'Line 73 Failed: {e}', is_error=True)
            raise

        
        try:
            labels = ["NAME", "TYPE", "START (YYYY-MM-DD HH:MM)", "END (YYYY-MM-DD HH:MM)"]
            _record_state(76, locals())
        except Exception as e:
            _ad_script_output(f'Line 76 Failed: {e}', is_error=True)
            raise
        try:
            self.entries = {}
            _record_state(77, locals())
        except Exception as e:
            _ad_script_output(f'Line 77 Failed: {e}', is_error=True)
            raise
        try:
            vars_map = ["ent_name", "ent_type", "ent_start", "ent_end"]
            _record_state(78, locals())
        except Exception as e:
            _ad_script_output(f'Line 78 Failed: {e}', is_error=True)
            raise

        for i in range(4):
            try:
                input_frame.columnconfigure(i, weight=1)
                _record_state(81, locals())
            except Exception as e:
                _ad_script_output(f'Line 81 Failed: {e}', is_error=True)
                raise
            try:
                f = tk.Frame(input_frame, bg=BG_CARD)
                _record_state(82, locals())
            except Exception as e:
                _ad_script_output(f'Line 82 Failed: {e}', is_error=True)
                raise
            try:
                f.grid(row=0, column=i, padx=10, sticky="ew")
                _record_state(83, locals())
            except Exception as e:
                _ad_script_output(f'Line 83 Failed: {e}', is_error=True)
                raise

            try:
                tk.Label(f, text=labels[i], bg=BG_CARD, fg="#94a3b8", font=("Segoe UI", 8, "bold")).pack(anchor="w")
                _record_state(85, locals())
            except Exception as e:
                _ad_script_output(f'Line 85 Failed: {e}', is_error=True)
                raise
            try:
                ent = tk.Entry(f, bg="#0f172a", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 11))
                _record_state(86, locals())
            except Exception as e:
                _ad_script_output(f'Line 86 Failed: {e}', is_error=True)
                raise
            try:
                ent.pack(fill="x", pady=5)
                _record_state(87, locals())
            except Exception as e:
                _ad_script_output(f'Line 87 Failed: {e}', is_error=True)
                raise
            try:
                self.entries[vars_map[i]] = ent
                _record_state(88, locals())
            except Exception as e:
                _ad_script_output(f'Line 88 Failed: {e}', is_error=True)
                raise

        self.btn_add = tk.Button(input_frame, text="ADD TO TIMELINE", command=self.add_activity,
                                 bg=ACCENT, fg="black", font=("Segoe UI", 10, "bold"),
                                 relief="flat", cursor="hand2", padx=20, pady=5)
        try:
            self.btn_add.grid(row=1, column=0, columnspan=4, pady=(15, 0))
            _record_state(93, locals())
        except Exception as e:
            _ad_script_output(f'Line 93 Failed: {e}', is_error=True)
            raise

        
        try:
            filter_frame = tk.Frame(self.main_container, bg=BG_MAIN)
            _record_state(96, locals())
        except Exception as e:
            _ad_script_output(f'Line 96 Failed: {e}', is_error=True)
            raise
        try:
            filter_frame.pack(fill="x", pady=10)
            _record_state(97, locals())
        except Exception as e:
            _ad_script_output(f'Line 97 Failed: {e}', is_error=True)
            raise

        tk.Label(filter_frame, text="Filter by Type:", bg=BG_MAIN, fg="#94a3b8", font=("Segoe UI", 10)).pack(
            side="left")
        try:
            self.filter_var = tk.StringVar(value="All")
            _record_state(101, locals())
        except Exception as e:
            _ad_script_output(f'Line 101 Failed: {e}', is_error=True)
            raise
        try:
            self.filter_menu = ttk.Combobox(filter_frame, textvariable=self.filter_var, state="readonly", width=20)
            _record_state(102, locals())
        except Exception as e:
            _ad_script_output(f'Line 102 Failed: {e}', is_error=True)
            raise
        try:
            self.filter_menu.pack(side="left", padx=10)
            _record_state(103, locals())
        except Exception as e:
            _ad_script_output(f'Line 103 Failed: {e}', is_error=True)
            raise
        try:
            self.filter_menu.bind("<<ComboboxSelected>>", lambda e: self.update_table())
            _record_state(104, locals())
        except Exception as e:
            _ad_script_output(f'Line 104 Failed: {e}', is_error=True)
            raise

        
        try:
            self.table_frame = tk.Frame(self.main_container, bg=BG_MAIN)
            _record_state(107, locals())
        except Exception as e:
            _ad_script_output(f'Line 107 Failed: {e}', is_error=True)
            raise
        try:
            self.table_frame.pack(fill="both", expand=True)
            _record_state(108, locals())
        except Exception as e:
            _ad_script_output(f'Line 108 Failed: {e}', is_error=True)
            raise

        try:
            columns = ("NAME", "TYPE", "START", "END")
            _record_state(110, locals())
        except Exception as e:
            _ad_script_output(f'Line 110 Failed: {e}', is_error=True)
            raise
        try:
            self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
            _record_state(111, locals())
        except Exception as e:
            _ad_script_output(f'Line 111 Failed: {e}', is_error=True)
            raise

        for col in columns:
            try:
                self.tree.heading(col, text=col, command=lambda _col=col: self.sort_by_column(_col))
                _record_state(114, locals())
            except Exception as e:
                _ad_script_output(f'Line 114 Failed: {e}', is_error=True)
                raise
            try:
                self.tree.column(col, anchor="center", width=150)
                _record_state(115, locals())
            except Exception as e:
                _ad_script_output(f'Line 115 Failed: {e}', is_error=True)
                raise

        try:
            scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
            _record_state(117, locals())
        except Exception as e:
            _ad_script_output(f'Line 117 Failed: {e}', is_error=True)
            raise
        try:
            self.tree.configure(yscroll=scrollbar.set)
            _record_state(118, locals())
        except Exception as e:
            _ad_script_output(f'Line 118 Failed: {e}', is_error=True)
            raise

        try:
            self.tree.pack(side="left", fill="both", expand=True)
            _record_state(120, locals())
        except Exception as e:
            _ad_script_output(f'Line 120 Failed: {e}', is_error=True)
            raise
        try:
            scrollbar.pack(side="right", fill="y")
            _record_state(121, locals())
        except Exception as e:
            _ad_script_output(f'Line 121 Failed: {e}', is_error=True)
            raise

        
        try:
            btn_bar = tk.Frame(self.main_container, bg=BG_MAIN, pady=20)
            _record_state(124, locals())
        except Exception as e:
            _ad_script_output(f'Line 124 Failed: {e}', is_error=True)
            raise
        try:
            btn_bar.pack(fill="x")
            _record_state(125, locals())
        except Exception as e:
            _ad_script_output(f'Line 125 Failed: {e}', is_error=True)
            raise

        
        for i in range(4): btn_bar.columnconfigure(i, weight=1)

        tk.Button(btn_bar, text="Find Free Slot", command=self.open_free_slot_window, bg="#334155", fg="white",
                  relief="flat", font=("Segoe UI", 10), pady=10).grid(row=0, column=0, padx=5, sticky="ew")

        tk.Button(btn_bar, text="Import Activities", command=self.import_csv, bg="#334155", fg="white",
                  relief="flat", font=("Segoe UI", 10), pady=10).grid(row=0, column=1, padx=5, sticky="ew")

        tk.Button(btn_bar, text="Export Activities", command=self.export_csv, bg="#334155", fg="white",
                  relief="flat", font=("Segoe UI", 10), pady=10).grid(row=0, column=2, padx=5, sticky="ew")

        tk.Button(btn_bar, text="Purge All", command=self.purge_all, bg=DANGER, fg="white",
                  relief="flat", font=("Segoe UI", 10, "bold"), pady=10).grid(row=0, column=3, padx=5, sticky="ew")

    def add_activity(self):
        try:
            vals = {k: v.get().strip() for k, v in self.entries.items()}
            _record_state(143, locals())
        except Exception as e:
            _ad_script_output(f'Line 143 Failed: {e}', is_error=True)
            raise

        if not all(vals.values()):
            try:
                messagebox.showwarning("Incomplete Data", "All fields (Name, Type, Start, End) must be entered.")
                _record_state(146, locals())
            except Exception as e:
                _ad_script_output(f'Line 146 Failed: {e}', is_error=True)
                raise
            try:
                return
                _record_state(147, locals())
            except Exception as e:
                _ad_script_output(f'Line 147 Failed: {e}', is_error=True)
                raise

        try:
            try:
                start_dt = datetime.strptime(vals['ent_start'], "%Y-%m-%d %H:%M")
                _record_state(150, locals())
            except Exception as e:
                _ad_script_output(f'Line 150 Failed: {e}', is_error=True)
                raise
            try:
                end_dt = datetime.strptime(vals['ent_end'], "%Y-%m-%d %H:%M")
                _record_state(151, locals())
            except Exception as e:
                _ad_script_output(f'Line 151 Failed: {e}', is_error=True)
                raise

            if end_dt <= start_dt:
                messagebox.showerror("Time Error", "End time must be after Start time.")
                return

            
            try:
                conflicts = [a for a in self.activities if not (end_dt <= a.start or start_dt >= a.end)]
                _record_state(158, locals())
            except Exception as e:
                _ad_script_output(f'Line 158 Failed: {e}', is_error=True)
                raise

            if conflicts:
                msg = f"The proposed activity conflicts with {len(conflicts)} existing activities:\n"
                for c in conflicts:
                    msg += f"- {c.name} ({c.start.strftime('%H:%M')} - {c.end.strftime('%H:%M')})\n"
                msg += "\nDo you want to add it anyway?"
                if not messagebox.askyesno("Conflict Detected", msg):
                    return

            try:
                new_act = Activity(vals['ent_name'], vals['ent_type'], start_dt, end_dt)
                _record_state(168, locals())
            except Exception as e:
                _ad_script_output(f'Line 168 Failed: {e}', is_error=True)
                raise
            try:
                self.activities.append(new_act)
                _record_state(169, locals())
            except Exception as e:
                _ad_script_output(f'Line 169 Failed: {e}', is_error=True)
                raise
            try:
                self.update_filter_list()
                _record_state(170, locals())
            except Exception as e:
                _ad_script_output(f'Line 170 Failed: {e}', is_error=True)
                raise
            try:
                self.update_table()
                _record_state(171, locals())
            except Exception as e:
                _ad_script_output(f'Line 171 Failed: {e}', is_error=True)
                raise

            
            for ent in self.entries.values(): ent.delete(0, tk.END)

        except ValueError:
            try:
                messagebox.showerror("Format Error", "Please use YYYY-MM-DD HH:MM format.\nExample: 2026-03-13 12:05")
                _record_state(177, locals())
            except Exception as e:
                _ad_script_output(f'Line 177 Failed: {e}', is_error=True)
                raise

    def update_table(self):
        try:
            self.tree.delete(*self.tree.get_children())
            _record_state(180, locals())
        except Exception as e:
            _ad_script_output(f'Line 180 Failed: {e}', is_error=True)
            raise
        try:
            filter_val = self.filter_var.get()
            _record_state(181, locals())
        except Exception as e:
            _ad_script_output(f'Line 181 Failed: {e}', is_error=True)
            raise

        for act in self.activities:
            if filter_val == "All" or act.act_type == filter_val:
                tag = act.act_type
                if tag not in self.type_colors:
                    self.type_colors[tag] = self.color_palette[len(self.type_colors) % len(self.color_palette)]

                self.tree.tag_configure(tag, background=self.type_colors[tag])
                self.tree.insert("", "end", values=(act.name, act.act_type,
                                                    act.start.strftime("%m/%d/%Y %H:%M"),
                                                    act.end.strftime("%m/%d/%Y %H:%M")),
                                 tags=(tag,))

    def update_filter_list(self):
        try:
            types = sorted(list(set(a.act_type for a in self.activities)))
            _record_state(196, locals())
        except Exception as e:
            _ad_script_output(f'Line 196 Failed: {e}', is_error=True)
            raise
        try:
            self.filter_menu['values'] = ["All"] + types
            _record_state(197, locals())
        except Exception as e:
            _ad_script_output(f'Line 197 Failed: {e}', is_error=True)
            raise

    def sort_by_column(self, col):
        if self.sort_column == col:
            try:
                self.sort_clicks += 1
                _record_state(201, locals())
            except Exception as e:
                _ad_script_output(f'Line 201 Failed: {e}', is_error=True)
                raise
        else:
            try:
                self.sort_column = col
                _record_state(203, locals())
            except Exception as e:
                _ad_script_output(f'Line 203 Failed: {e}', is_error=True)
                raise
            try:
                self.sort_clicks = 1
                _record_state(204, locals())
            except Exception as e:
                _ad_script_output(f'Line 204 Failed: {e}', is_error=True)
                raise

        try:
            reverse = (self.sort_clicks % 2 == 0)
            _record_state(206, locals())
        except Exception as e:
            _ad_script_output(f'Line 206 Failed: {e}', is_error=True)
            raise
        try:
            sort_map = {"NAME": "name", "TYPE": "act_type", "START": "start", "END": "end"}
            _record_state(207, locals())
        except Exception as e:
            _ad_script_output(f'Line 207 Failed: {e}', is_error=True)
            raise
        try:
            attr = sort_map[col]
            _record_state(208, locals())
        except Exception as e:
            _ad_script_output(f'Line 208 Failed: {e}', is_error=True)
            raise

        try:
            self.activities.sort(key=lambda x: getattr(x, attr), reverse=reverse)
            _record_state(210, locals())
        except Exception as e:
            _ad_script_output(f'Line 210 Failed: {e}', is_error=True)
            raise
        try:
            self.update_table()
            _record_state(211, locals())
        except Exception as e:
            _ad_script_output(f'Line 211 Failed: {e}', is_error=True)
            raise

    def purge_all(self):
        if not self.activities:
            try:
                messagebox.showinfo("Purge All", "No activities are available to be purged from said activity box.")
                _record_state(215, locals())
            except Exception as e:
                _ad_script_output(f'Line 215 Failed: {e}', is_error=True)
                raise
            try:
                return
                _record_state(216, locals())
            except Exception as e:
                _ad_script_output(f'Line 216 Failed: {e}', is_error=True)
                raise

        if messagebox.askyesno("Confirm Purge", "Are you sure you want to purge all activities?"):
            try:
                self.activities = []
                _record_state(219, locals())
            except Exception as e:
                _ad_script_output(f'Line 219 Failed: {e}', is_error=True)
                raise
            try:
                self.update_filter_list()
                _record_state(220, locals())
            except Exception as e:
                _ad_script_output(f'Line 220 Failed: {e}', is_error=True)
                raise
            try:
                self.filter_var.set("All")
                _record_state(221, locals())
            except Exception as e:
                _ad_script_output(f'Line 221 Failed: {e}', is_error=True)
                raise
            try:
                self.update_table()
                _record_state(222, locals())
            except Exception as e:
                _ad_script_output(f'Line 222 Failed: {e}', is_error=True)
                raise

    def export_csv(self):
        if not self.activities:
            try:
                messagebox.showwarning("Export CSV", "There are no activities to export.")
                _record_state(226, locals())
            except Exception as e:
                _ad_script_output(f'Line 226 Failed: {e}', is_error=True)
                raise
            try:
                return
                _record_state(227, locals())
            except Exception as e:
                _ad_script_output(f'Line 227 Failed: {e}', is_error=True)
                raise

        try:
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            _record_state(229, locals())
        except Exception as e:
            _ad_script_output(f'Line 229 Failed: {e}', is_error=True)
            raise
        if path:
            try:
                with open(path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["NAME", "TYPE", "START", "END"])
                    for a in self.activities:
                        writer.writerow([a.name, a.act_type,
                                         a.start.strftime("%Y-%m-%d %H:%M"),
                                         a.end.strftime("%Y-%m-%d %H:%M")])
                messagebox.showinfo("Success", "Export successful.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

    def import_csv(self):
        try:
            path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            _record_state(244, locals())
        except Exception as e:
            _ad_script_output(f'Line 244 Failed: {e}', is_error=True)
            raise
        if not path: return

        try:
            new_list = []
            _record_state(247, locals())
        except Exception as e:
            _ad_script_output(f'Line 247 Failed: {e}', is_error=True)
            raise
        try:
            with open(path, 'r') as f:
                reader = csv.DictReader(f)
                required = {"NAME", "TYPE", "START", "END"}
                if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                    raise ValueError("Format Mismatch")

                for row in reader:
                    s = datetime.strptime(row['START'], "%Y-%m-%d %H:%M")
                    e = datetime.strptime(row['END'], "%Y-%m-%d %H:%M")
                    new_list.append(Activity(row['NAME'], row['TYPE'], s, e))

            if not new_list:
                raise ValueError("Empty File")

            try:
                self.activities = new_list
                _record_state(263, locals())
            except Exception as e:
                _ad_script_output(f'Line 263 Failed: {e}', is_error=True)
                raise
            try:
                self.update_filter_list()
                _record_state(264, locals())
            except Exception as e:
                _ad_script_output(f'Line 264 Failed: {e}', is_error=True)
                raise
            try:
                self.filter_var.set("All")
                _record_state(265, locals())
            except Exception as e:
                _ad_script_output(f'Line 265 Failed: {e}', is_error=True)
                raise
            try:
                self.update_table()
                _record_state(266, locals())
            except Exception as e:
                _ad_script_output(f'Line 266 Failed: {e}', is_error=True)
                raise
            try:
                messagebox.showinfo("Success", "Import successful. Timeline updated.")
                _record_state(267, locals())
            except Exception as e:
                _ad_script_output(f'Line 267 Failed: {e}', is_error=True)
                raise
        except Exception:
            messagebox.showerror("Import Error",
                                 "The imported CSV does not meet the requirements (format, column names, 'NAME', 'TYPE', 'START', 'END', etc.).")

    def open_free_slot_window(self):
        if not self.activities:
            messagebox.showwarning("Find Free Slot",
                                   "It is not possible to request free slots in the event that there are no activities in the activity box.")
            try:
                return
                _record_state(276, locals())
            except Exception as e:
                _ad_script_output(f'Line 276 Failed: {e}', is_error=True)
                raise

        try:
            win = tk.Toplevel(self.root)
            _record_state(278, locals())
        except Exception as e:
            _ad_script_output(f'Line 278 Failed: {e}', is_error=True)
            raise
        try:
            win.title("Activity Scheduler Pro - Find Free Slots")
            _record_state(279, locals())
        except Exception as e:
            _ad_script_output(f'Line 279 Failed: {e}', is_error=True)
            raise
        try:
            win.geometry("600x650")
            _record_state(280, locals())
        except Exception as e:
            _ad_script_output(f'Line 280 Failed: {e}', is_error=True)
            raise
        try:
            win.configure(bg=BG_CARD)
            _record_state(281, locals())
        except Exception as e:
            _ad_script_output(f'Line 281 Failed: {e}', is_error=True)
            raise
        try:
            win.transient(self.root)
            _record_state(282, locals())
        except Exception as e:
            _ad_script_output(f'Line 282 Failed: {e}', is_error=True)
            raise

        try:
            tk.Label(win, text="FIND FREE SLOTS", font=("Segoe UI", 18, "bold"), bg=BG_CARD, fg=ACCENT).pack(pady=20)
            _record_state(284, locals())
        except Exception as e:
            _ad_script_output(f'Line 284 Failed: {e}', is_error=True)
            raise

        try:
            p_frame = tk.Frame(win, bg=BG_CARD)
            _record_state(286, locals())
        except Exception as e:
            _ad_script_output(f'Line 286 Failed: {e}', is_error=True)
            raise
        try:
            p_frame.pack(fill="x", padx=40)
            _record_state(287, locals())
        except Exception as e:
            _ad_script_output(f'Line 287 Failed: {e}', is_error=True)
            raise

        
        try:
            p_frame.columnconfigure(0, weight=1)
            _record_state(290, locals())
        except Exception as e:
            _ad_script_output(f'Line 290 Failed: {e}', is_error=True)
            raise

        def create_field(parent, label):
            try:
                tk.Label(parent, text=label, bg=BG_CARD, fg="white", font=("Segoe UI", 9)).pack(anchor="w", pady=(10, 0))
                _record_state(293, locals())
            except Exception as e:
                _ad_script_output(f'Line 293 Failed: {e}', is_error=True)
                raise
            e = tk.Entry(parent, bg="#0f172a", fg="white", insertbackground="white", relief="flat",
                         font=("Segoe UI", 11))
            try:
                e.pack(fill="x", pady=5)
                _record_state(296, locals())
            except Exception as e:
                _ad_script_output(f'Line 296 Failed: {e}', is_error=True)
                raise
            try:
                return e
                _record_state(297, locals())
            except Exception as e:
                _ad_script_output(f'Line 297 Failed: {e}', is_error=True)
                raise

        try:
            e_win_s = create_field(p_frame, "Search Window Start (YYYY-MM-DD HH:MM)")
            _record_state(299, locals())
        except Exception as e:
            _ad_script_output(f'Line 299 Failed: {e}', is_error=True)
            raise
        try:
            e_win_e = create_field(p_frame, "Search Window End (YYYY-MM-DD HH:MM)")
            _record_state(300, locals())
        except Exception as e:
            _ad_script_output(f'Line 300 Failed: {e}', is_error=True)
            raise
        try:
            e_len = create_field(p_frame, "Required Activity Length (Minutes)")
            _record_state(301, locals())
        except Exception as e:
            _ad_script_output(f'Line 301 Failed: {e}', is_error=True)
            raise

        try:
            res_box = tk.Text(win, height=10, bg="#0f172a", fg=ACCENT, font=("Consolas", 10), padx=10, pady=10)
            _record_state(303, locals())
        except Exception as e:
            _ad_script_output(f'Line 303 Failed: {e}', is_error=True)
            raise
        try:
            res_box.pack(pady=20, padx=40, fill="both", expand=True)
            _record_state(304, locals())
        except Exception as e:
            _ad_script_output(f'Line 304 Failed: {e}', is_error=True)
            raise

        def generate():
            try:
                s_val, e_val, l_val = e_win_s.get(), e_win_e.get(), e_len.get()
                _record_state(307, locals())
            except Exception as e:
                _ad_script_output(f'Line 307 Failed: {e}', is_error=True)
                raise
            if not all([s_val, e_val, l_val]):
                messagebox.showwarning("Incomplete Data", "Required values are not available.", parent=win)
                return

            try:
                search_s = datetime.strptime(s_val, "%Y-%m-%d %H:%M")
                search_e = datetime.strptime(e_val, "%Y-%m-%d %H:%M")
                min_dur = timedelta(minutes=int(l_val))

                
                relevant = sorted(
                    [(a.start, a.end) for a in self.activities if a.end > search_s and a.start < search_e])

                free_slots = []
                current_time = search_s

                for b_start, b_end in relevant:
                    if b_start > current_time:
                        if (b_start - current_time) >= min_dur:
                            free_slots.append((current_time, b_start))
                    current_time = max(current_time, b_end)

                if search_e > current_time and (search_e - current_time) >= min_dur:
                    free_slots.append((current_time, search_e))

                res_box.delete("1.0", tk.END)
                if not free_slots:
                    res_box.insert(tk.END, "No free slots found within these parameters.")
                else:
                    for s, e in free_slots:
                        res_box.insert(tk.END,
                                       f"SLOT FOUND:\nFROM: {s.strftime('%m/%d/%Y %H:%M')}\nTO:   {e.strftime('%m/%d/%Y %H:%M')}\n{'-' * 30}\n")

            except ValueError:
                messagebox.showerror("Error", "Invalid format or numeric value entered.")

        tk.Button(win, text="GENERATE SLOTS", command=generate, bg=ACCENT, fg="black",
                  font=("Segoe UI", 11, "bold"), relief="flat", padx=30, pady=10).pack(pady=(0, 20))


if __name__ == "__main__":
    try:
        root = tk.Tk()
        _record_state(349, locals())
    except Exception as e:
        _ad_script_output(f'Line 349 Failed: {e}', is_error=True)
        raise
    try:
        app = ActivitySchedulerPro(root)
        _record_state(350, locals())
    except Exception as e:
        _ad_script_output(f'Line 350 Failed: {e}', is_error=True)
        raise
    try:
        root.mainloop()
        _record_state(351, locals())
    except Exception as e:
        _ad_script_output(f'Line 351 Failed: {e}', is_error=True)
        raise