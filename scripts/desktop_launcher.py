import os
import sys
import socket
import subprocess
import webbrowser
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Set working directory to script or executable location
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COMPOSE_FILE = os.path.join(BASE_DIR, "docker-compose.prod.yml")
if not os.path.exists(COMPOSE_FILE):
    COMPOSE_FILE = os.path.join(os.path.dirname(BASE_DIR), "docker-compose.prod.yml")


def get_lan_ip():
    """Get the local network IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


class ModernButton(tk.Canvas):
    """Custom pixel-perfect rounded pill button with smooth hover animations."""

    def __init__(self, parent, text, command, bg_color, hover_color, fg_color="#FFFFFF",
                 width=160, height=44, radius=14, font=("Segoe UI", 10, "bold")):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.width = width
        self.height = height
        self.radius = radius
        self.font = font
        self.text = text
        self.enabled = True

        self.draw(self.bg_color)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def draw_round_rect(self, color):
        self.delete("all")
        r = self.radius
        w = self.width
        h = self.height

        # Draw smooth rounded polygon
        points = [
            r, 0, w - r, 0,
            w, 0, w, r,
            w, h - r, w, h,
            w - r, h, r, h,
            0, h, 0, h - r,
            0, r, 0, 0
        ]
        self.create_polygon(points, fill=color, smooth=True)
        self.create_text(w / 2, h / 2, text=self.text, fill=self.fg_color, font=self.font)

    def draw(self, color):
        self.draw_round_rect(color)

    def on_enter(self, e):
        if self.enabled:
            self.config(cursor="hand2")
            self.draw(self.hover_color)

    def on_leave(self, e):
        if self.enabled:
            self.draw(self.bg_color)

    def on_click(self, e):
        if self.enabled and self.command:
            self.command()

    def set_state(self, enabled):
        self.enabled = enabled
        if enabled:
            self.draw(self.bg_color)
        else:
            self.config(cursor="")
            self.draw("#334155")


class DentalPinLauncherUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DentalPin — مركز التشغيل الإداري")
        self.geometry("580x720")
        self.resizable(False, False)
        self.configure(bg="#0B0F17")  # Deep Obsidian

        self.local_ip = get_lan_ip()
        self.is_running = False

        # Design Tokens
        self.C_BG = "#0B0F17"
        self.C_CARD = "#161E2E"
        self.C_CARD_BORDER = "#232F46"
        self.C_TEXT = "#F1F5F9"
        self.C_MUTED = "#94A3B8"
        self.C_BLUE = "#3B82F6"
        self.C_BLUE_HOVER = "#2563EB"
        self.C_GREEN = "#10B981"
        self.C_GREEN_HOVER = "#059669"
        self.C_RED = "#F43F5E"
        self.C_RED_HOVER = "#E11D48"

        self.build_ui()
        self.log_msg("تم فتح مركز التحكم بنجاح.")
        self.check_status_async()

    def build_ui(self):
        # Top Header Banner
        header = tk.Frame(self, bg="#111827", height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg="#111827")
        header_content.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)

        # Brand / Title
        brand_frame = tk.Frame(header_content, bg="#111827")
        brand_frame.pack(side=tk.RIGHT)

        tk.Label(
            brand_frame, text="DentalPin", font=("Segoe UI", 16, "bold"),
            fg="#F8FAFC", bg="#111827"
        ).pack(side=tk.RIGHT)

        tk.Label(
            brand_frame, text=" 📍 ", font=("Segoe UI", 14),
            fg=self.C_BLUE, bg="#111827"
        ).pack(side=tk.RIGHT)

        # Version Badge
        ver_badge = tk.Label(
            header_content, text="v2.0 Offline", font=("Segoe UI", 9, "bold"),
            fg="#60A5FA", bg="#1E293B", padx=10, pady=3
        )
        ver_badge.pack(side=tk.LEFT)

        # Main Container
        main = tk.Frame(self, bg=self.C_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        # 1. System Status Hero Card
        status_card = tk.Frame(main, bg=self.C_CARD, highlightbackground=self.C_CARD_BORDER, highlightthickness=1)
        status_card.pack(fill=tk.X, pady=(0, 16))

        sc_inner = tk.Frame(status_card, bg=self.C_CARD, padx=20, pady=16)
        sc_inner.pack(fill=tk.X)

        # Title & Badge Row
        st_row = tk.Frame(sc_inner, bg=self.C_CARD)
        st_row.pack(fill=tk.X, pady=(0, 14))

        tk.Label(
            st_row, text="حالة الخادم المحلي", font=("Segoe UI", 11, "bold"),
            fg=self.C_TEXT, bg=self.C_CARD
        ).pack(side=tk.RIGHT)

        self.lbl_status = tk.Label(
            st_row, text="● متوقف (Stopped)", font=("Segoe UI", 9, "bold"),
            fg="#FDA4AF", bg="#4C0519", padx=12, pady=4
        )
        self.lbl_status.pack(side=tk.LEFT)

        # Micro Container Indicators Row
        self.chip_frame = tk.Frame(sc_inner, bg=self.C_CARD)
        self.chip_frame.pack(fill=tk.X, pady=(0, 14))

        self.chip_db = self.create_chip(self.chip_frame, "قاعدة البيانات DB")
        self.chip_api = self.create_chip(self.chip_frame, "الخادم API")
        self.chip_web = self.create_chip(self.chip_frame, "الواجهة Web")
        self.chip_proxy = self.create_chip(self.chip_frame, "الشبكة Proxy")

        # Network Access Cards
        net_frame = tk.Frame(sc_inner, bg=self.C_CARD)
        net_frame.pack(fill=tk.X)

        # Localhost URL
        self.build_url_row(net_frame, "الوصول من هذا الجهاز:", "http://localhost", self.C_BLUE)
        # WiFi URL
        self.build_url_row(net_frame, "الوصول من الشبكة / iPad:", f"http://{self.local_ip}", self.C_GREEN)

        # 2. Main Control Action Buttons
        btn_box = tk.Frame(main, bg=self.C_BG)
        btn_box.pack(fill=tk.X, pady=(0, 16))

        self.btn_start = ModernButton(
            btn_box, text="▶  تشغيل النظام", command=self.start_system_async,
            bg_color=self.C_GREEN, hover_color=self.C_GREEN_HOVER, width=170, height=46
        )
        self.btn_start.pack(side=tk.RIGHT, padx=(0, 6))

        self.btn_browser = ModernButton(
            btn_box, text="🌐  فتح المتصفح", command=self.open_browser,
            bg_color=self.C_BLUE, hover_color=self.C_BLUE_HOVER, width=170, height=46
        )
        self.btn_browser.pack(side=tk.RIGHT, padx=6)

        self.btn_stop = ModernButton(
            btn_box, text="■  إيقاف", command=self.stop_system_async,
            bg_color=self.C_RED, hover_color=self.C_RED_HOVER, width=150, height=46
        )
        self.btn_stop.pack(side=tk.LEFT)

        # 3. Settings Box
        set_card = tk.Frame(main, bg=self.C_CARD, highlightbackground=self.C_CARD_BORDER, highlightthickness=1)
        set_card.pack(fill=tk.X, pady=(0, 16))

        set_inner = tk.Frame(set_card, bg=self.C_CARD, padx=16, pady=10)
        set_inner.pack(fill=tk.X)

        self.demo_var = tk.BooleanVar(value=self.get_env("DEMO_MODE", "true") == "true")
        chk = tk.Checkbutton(
            set_inner, text="تفعيل الوضع التجريبي لسهولة الاختبار (Demo Mode)",
            variable=self.demo_var, font=("Segoe UI", 9, "bold"),
            fg=self.C_TEXT, bg=self.C_CARD, selectcolor=self.C_BG,
            activebackground=self.C_CARD, activeforeground=self.C_TEXT,
            command=self.save_env
        )
        chk.pack(side=tk.RIGHT)

        # 4. Live Output Terminal Log
        log_card = tk.Frame(main, bg=self.C_CARD, highlightbackground=self.C_CARD_BORDER, highlightthickness=1)
        log_card.pack(fill=tk.BOTH, expand=True)

        log_inner = tk.Frame(log_card, bg=self.C_CARD, padx=14, pady=10)
        log_inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            log_inner, text="سجل النشاط والأحداث (Live Log)", font=("Segoe UI", 9, "bold"),
            fg=self.C_MUTED, bg=self.C_CARD
        ).pack(anchor="e", pady=(0, 6))

        self.txt_log = tk.Text(
            log_inner, font=("Consolas", 9), bg="#070A0F", fg="#A5F3FC",
            bd=0, relief=tk.FLAT, wrap=tk.WORD, height=7
        )
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        # Bottom Footer
        footer = tk.Label(
            self, text="DentalPin 2.0 — Secure Offline Management System",
            font=("Segoe UI", 8), fg="#64748B", bg=self.C_BG, pady=8
        )
        footer.pack(side=tk.BOTTOM)

    def create_chip(self, parent, label):
        chip = tk.Label(
            parent, text=f"⚪ {label}", font=("Segoe UI", 8),
            fg="#94A3B8", bg="#1E293B", padx=8, pady=3
        )
        chip.pack(side=tk.RIGHT, padx=3)
        return chip

    def build_url_row(self, parent, title, url, accent_color):
        row = tk.Frame(parent, bg=self.C_CARD)
        row.pack(fill=tk.X, pady=3)

        tk.Label(
            row, text=title, font=("Segoe UI", 9),
            fg=self.C_MUTED, bg=self.C_CARD, width=22, anchor="e"
        ).pack(side=tk.RIGHT)

        entry = tk.Entry(
            row, font=("Consolas", 10), bg="#0F172A", fg=accent_color,
            bd=1, relief=tk.FLAT, width=28
        )
        entry.insert(0, url)
        entry.config(state="readonly")
        entry.pack(side=tk.RIGHT, padx=8)

        btn_copy = tk.Button(
            row, text="نسخ", font=("Segoe UI", 8, "bold"),
            bg="#26334D", fg="#F1F5F9", activebackground="#3B82F6", activeforeground="#FFFFFF",
            bd=0, padx=10, pady=2, cursor="hand2",
            command=lambda: self.copy(url)
        )
        btn_copy.pack(side=tk.RIGHT)

    def log_msg(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.insert(tk.END, f"[{now}] {msg}\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state=tk.DISABLED)

    def copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.log_msg(f"تم نسخ الرابط بالحافظة: {text}")

    def run_cmd(self, args):
        try:
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW
            res = subprocess.run(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                creationflags=creationflags, text=True
            )
            return res.returncode == 0, res.stdout, res.stderr
        except Exception as e:
            return False, "", str(e)

    def check_status_async(self):
        threading.Thread(target=self._check_status_worker, daemon=True).start()

    def _check_status_worker(self):
        ok, stdout, _ = self.run_cmd(["docker", "compose", "-f", COMPOSE_FILE, "ps", "--format", "json"])
        
        def update():
            if ok and "frontend" in stdout:
                self.is_running = True
                self.lbl_status.config(text="● يعمل الآن (Running)", fg="#6EE7B7", bg="#064E3B")
                self.update_chip(self.chip_db, True, "قاعدة البيانات DB")
                self.update_chip(self.chip_api, True, "الخادم API")
                self.update_chip(self.chip_web, True, "الواجهة Web")
                self.update_chip(self.chip_proxy, True, "الشبكة Proxy")
            else:
                self.is_running = False
                self.lbl_status.config(text="● متوقف (Stopped)", fg="#FDA4AF", bg="#4C0519")
                self.update_chip(self.chip_db, False, "قاعدة البيانات DB")
                self.update_chip(self.chip_api, False, "الخادم API")
                self.update_chip(self.chip_web, False, "الواجهة Web")
                self.update_chip(self.chip_proxy, False, "الشبكة Proxy")

        self.after(0, update)

    def update_chip(self, chip, active, label):
        if active:
            chip.config(text=f"🟢 {label}", fg="#6EE7B7", bg="#064E3B")
        else:
            chip.config(text=f"🔴 {label}", fg="#FDA4AF", bg="#331019")

    def start_system_async(self):
        self.btn_start.set_state(False)
        self.log_msg("جاري إطلاق الحاويات وتشغيل خادم العيادة...")
        self.save_env()

        def worker():
            ok, stdout, stderr = self.run_cmd(["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"])

            def done():
                self.btn_start.set_state(True)
                if ok:
                    self.log_msg("تم تشغيل النظام بنجاح! 🚀")
                    self.check_status_async()
                    self.open_browser()
                else:
                    self.log_msg(f"خطأ أثناء التشغيل: {stderr}")
                    messagebox.showerror("خطأ التشغيل", f"فشل تشغيل الخدمات:\n{stderr}")

            self.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    def stop_system_async(self):
        self.btn_stop.set_state(False)
        self.log_msg("جاري إيقاف الخادم وسحب الخدمات بآمان...")

        def worker():
            ok, stdout, stderr = self.run_cmd(["docker", "compose", "-f", COMPOSE_FILE, "stop"])

            def done():
                self.btn_stop.set_state(True)
                if ok:
                    self.log_msg("تم إيقاف النظام بسلام 🛑")
                    self.check_status_async()
                else:
                    self.log_msg(f"خطأ الإيقاف: {stderr}")

            self.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    def open_browser(self):
        self.log_msg("فتح المتصفح على رابط العيادة...")
        webbrowser.open(f"http://{self.local_ip}")

    def get_env(self, key, default=""):
        env_path = os.path.join(os.path.dirname(COMPOSE_FILE), ".env")
        if not os.path.exists(env_path):
            return default
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith(f"{key}="):
                    return line.strip().split("=", 1)[1]
        return default

    def save_env(self):
        env_path = os.path.join(os.path.dirname(COMPOSE_FILE), ".env")
        vars_dict = {}
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    l = line.strip()
                    if l and not l.startswith("#") and "=" in l:
                        k, v = l.split("=", 1)
                        vars_dict[k.strip()] = v.strip()

        vars_dict["PUBLIC_URL"] = f"http://{self.local_ip}"
        vars_dict["DEMO_MODE"] = "true" if self.demo_var.get() else "false"

        lines = ["# Generated by DentalPin Launcher\n"]
        for k, v in vars_dict.items():
            lines.append(f"{k}={v}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        self.log_msg("تم حفظ الإعدادات بنجاح.")


if __name__ == "__main__":
    app = DentalPinLauncherUI()
    app.mainloop()
