# game_ui_wrapper.py
import sys
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class ProcTerminal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text Adventure UI")
        self.geometry("900x600")
        self.configure(bg="#0f1020")

        self.proc = None
        self.q = queue.Queue()
        self.reader_thread = None
        self.script_path = None

        self._init_theme()
        self._build_ui()
        self.after(50, self._drain_queue)

    def _init_theme(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame", background="#0f1020")
        s.configure("Top.TFrame", background="#0f1020")
        s.configure("TButton", background="#22233b", foreground="#e6e7ff", padding=8)
        s.map("TButton", background=[("active", "#2b2d4a")])
        s.configure("TLabel", background="#0f1020", foreground="#e6e7ff")
        s.configure("Title.TLabel", background="#0f1020", foreground="#e6e7ff", font=("Segoe UI Semibold", 14))

    def _build_ui(self):
        top = ttk.Frame(self, style="Top.TFrame"); top.pack(fill="x", padx=12, pady=8)
        ttk.Label(top, text="Text Adventure UI (no code changes)", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="Open Script…", command=self._choose_script).pack(side="right", padx=(6,0))
        ttk.Button(top, text="Restart", command=self._restart).pack(side="right", padx=(6,0))
        ttk.Button(top, text="Quit", command=self._quit).pack(side="right")

        mid = ttk.Frame(self); mid.pack(fill="both", expand=True, padx=12, pady=(0,8))
        self.text = tk.Text(mid, wrap="word", bg="#17182b", fg="#e6e7ff",
                            insertbackground="#e6e7ff", font=("Consolas", 12))
        yscroll = ttk.Scrollbar(mid, command=self.text.yview)
        self.text.configure(yscrollcommand=yscroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="left", fill="y")

        bottom = ttk.Frame(self); bottom.pack(fill="x", padx=12, pady=(0,12))
        self.entry = ttk.Entry(bottom, font=("Segoe UI", 12))
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self._send_line())
        ttk.Button(bottom, text="Send", command=self._send_line).pack(side="left", padx=(6,0))

        self._set_input_state(False)

    def _set_input_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.entry.configure(state=state)

    def _choose_script(self):
        path = filedialog.askopenfilename(
            title="Select your game script",
            filetypes=[("Python files","*.py"), ("All files","*.*")]
        )
        if not path:
            return
        self.script_path = path
        self._start_process()

    def _start_process(self):
        self._stop_process()
        if not self.script_path:
            return
        self.text.delete("1.0", "end")
        self._append(f"Launching: {self.script_path}\n\n")

        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"

            self.proc = subprocess.Popen(
                [sys.executable, "-u", self.script_path],  # -u for unbuffered output
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=0,   # no buffering on our end either
                env=env,
            )
        except Exception as e:
            messagebox.showerror("Launch error", str(e))
            self.proc = None
            return

        self._set_input_state(True)
        self.reader_thread = threading.Thread(target=self._reader, daemon=True)
        self.reader_thread.start()

    # ---- updated reader: reads character-by-character ----
    def _reader(self):
        try:
            while True:
                if not self.proc:
                    break
                ch = self.proc.stdout.read(1)
                if not ch:
                    break
                self.q.put(ch)
        except Exception as e:
            self.q.put(f"\n[Reader error: {e}]\n")
        finally:
            self.q.put("\n[Process ended]\n")

    def _drain_queue(self):
        try:
            while True:
                item = self.q.get_nowait()
                self._append(item)
        except queue.Empty:
            pass
        if self.proc and self.proc.poll() is not None:
            self._set_input_state(False)
        self.after(50, self._drain_queue)

    def _append(self, s: str):
        self.text.insert("end", s)
        self.text.see("end")

    def _send_line(self):
        if not self.proc or self.proc.poll() is not None:
            return
        line = self.entry.get()
        try:
            self.proc.stdin.write(line + "\n")
            self.proc.stdin.flush()
        except Exception:
            pass
        self.entry.delete(0, "end")

    def _restart(self):
        if not self.script_path:
            self._append("Select a script first.\n")
            return
        self._start_process()

    def _stop_process(self):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
            except Exception:
                pass
            try:
                self.proc.wait(timeout=2)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
        self.proc = None
        self._set_input_state(False)

    def _quit(self):
        self._stop_process()
        self.destroy()

if __name__ == "__main__":
    ProcTerminal().mainloop()