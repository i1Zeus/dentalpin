import os
import subprocess
import socket
import webbrowser
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# Set working directory to the directory of the script or the executable
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Look for compose file in the same directory or one level up
COMPOSE_FILE = os.path.join(BASE_DIR, "docker-compose.prod.yml")
if not os.path.exists(COMPOSE_FILE):
    # Try parent directory
    COMPOSE_FILE = os.path.join(os.path.dirname(BASE_DIR), "docker-compose.prod.yml")

def get_lan_ip():
    """Get the local network IP address of this computer."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external dummy address (doesn't need to be reachable)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class DentalPinLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("مساعد تشغيل DentalPin")
        self.root.geometry("500x380")
        self.root.resizable(False, False)
        
        # Configure grid/style
        self.root.configure(bg="#f3f4f6")
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Title Label
        title_frame = tk.Frame(self.root, bg="#1e3a8a", height=80)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame, 
            text="DentalPin Desktop Launcher", 
            font=("Arial", 16, "bold"), 
            fg="white", 
            bg="#1e3a8a"
        )
        title_label.pack(pady=15)
        
        # Info Frame
        info_frame = tk.LabelFrame(
            self.root, 
            text=" حالة الخادم المحلي (Local Server Status) ", 
            font=("Arial", 10, "bold"), 
            bg="#f3f4f6", 
            fg="#1e3a8a",
            padx=15, 
            pady=10
        )
        info_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Local Link
        self.local_ip = get_lan_ip()
        self.status_label = tk.Label(
            info_frame, 
            text="الحالة: متوقف", 
            font=("Arial", 11, "bold"), 
            fg="#dc2626", 
            bg="#f3f4f6"
        )
        self.status_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        tk.Label(
            info_frame, 
            text="رابط الوصول من هذا الجهاز:", 
            font=("Arial", 10), 
            bg="#f3f4f6"
        ).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.local_link_label = tk.Entry(info_frame, font=("Consolas", 10), width=35)
        self.local_link_label.insert(0, "http://localhost")
        self.local_link_label.config(state="readonly")
        self.local_link_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        tk.Label(
            info_frame, 
            text="رابط الوصول للأيباد والشبكة (Wi-Fi):", 
            font=("Arial", 10), 
            bg="#f3f4f6"
        ).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.wifi_link_label = tk.Entry(info_frame, font=("Consolas", 10), width=35)
        self.wifi_link_label.insert(0, f"http://{self.local_ip}")
        self.wifi_link_label.config(state="readonly")
        self.wifi_link_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Buttons Frame
        btn_frame = tk.Frame(self.root, bg="#f3f4f6")
        btn_frame.pack(pady=10)
        
        # Start button
        self.start_btn = tk.Button(
            btn_frame, 
            text="تشغيل النظام", 
            font=("Arial", 11, "bold"), 
            bg="#16a34a", 
            fg="white", 
            width=15, 
            height=2,
            command=self.start_system,
            relief=tk.FLAT
        )
        self.start_btn.grid(row=0, column=0, padx=10)
        
        # Stop button
        self.stop_btn = tk.Button(
            btn_frame, 
            text="إيقاف النظام", 
            font=("Arial", 11, "bold"), 
            bg="#dc2626", 
            fg="white", 
            width=15, 
            height=2,
            command=self.stop_system,
            relief=tk.FLAT
        )
        self.stop_btn.grid(row=0, column=1, padx=10)
        
        # Open Browser Button
        self.browser_btn = tk.Button(
            self.root, 
            text="فتح واجهة العيادة بالمتصفح", 
            font=("Arial", 10, "bold"), 
            bg="#2563eb", 
            fg="white", 
            width=25, 
            height=1,
            command=self.open_browser,
            relief=tk.FLAT
        )
        self.browser_btn.pack(pady=5)
        
        # Footer
        footer_label = tk.Label(
            self.root, 
            text="DentalPin 2.0 - نظام تشغيل أوفلاين مؤمن", 
            font=("Arial", 8), 
            fg="#9ca3af", 
            bg="#f3f4f6"
        )
        footer_label.pack(side=tk.BOTTOM, pady=10)
        
        # Initial check
        self.check_status()

    def run_cmd(self, args):
        """Run command silently without CMD window popup on Windows."""
        try:
            startupinfo = None
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW
                
            res = subprocess.run(
                args, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                creationflags=creationflags,
                text=True
            )
            return res.returncode == 0, res.stdout, res.stderr
        except Exception as e:
            return False, "", str(e)

    def check_status(self):
        """Check if containers are running."""
        success, stdout, _ = self.run_cmd(["docker", "compose", "-f", COMPOSE_FILE, "ps", "--format", "json"])
        if success and "frontend" in stdout:
            self.status_label.config(text="الحالة: يعمل بنجاح (Running)", fg="#16a34a")
            return True
        else:
            self.status_label.config(text="الحالة: متوقف (Stopped)", fg="#dc2626")
            return False

    def update_env(self):
        """Update .env file dynamically with current IP and startup seeds."""
        env_path = os.path.join(os.path.dirname(COMPOSE_FILE), ".env")
        ip = self.local_ip
        
        # Read lines if file exists
        lines = []
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except Exception:
                pass
                
        # Parse existing variables
        vars_dict = {}
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                parts = line_str.split("=", 1)
                vars_dict[parts[0].strip()] = parts[1].strip()
                
        # Update/Add specific keys
        vars_dict["PUBLIC_URL"] = f"http://{ip}"
        
        # Ensure SEED_ON_STARTUP and SEED_LANG are set if not present or need to be active
        if "SEED_ON_STARTUP" not in vars_dict:
            vars_dict["SEED_ON_STARTUP"] = "1"
        if "SEED_LANG" not in vars_dict:
            vars_dict["SEED_LANG"] = "en"
            
        # Keep defaults for standard DB config if missing
        if "POSTGRES_DB" not in vars_dict:
            vars_dict["POSTGRES_DB"] = "dental_clinic"
        if "POSTGRES_USER" not in vars_dict:
            vars_dict["POSTGRES_USER"] = "dental"
        if "POSTGRES_PASSWORD" not in vars_dict:
            vars_dict["POSTGRES_PASSWORD"] = "your_secure_password_here"
        if "SECRET_KEY" not in vars_dict:
            vars_dict["SECRET_KEY"] = "6d359215e1b1cb2d51b9398ca14c8afe6369b56c21b91a5bd07f71828fb39ccd"
            
        # Reconstruct the .env file
        new_lines = []
        new_lines.append("# Generated by DentalPin Launcher\n")
        for k, v in vars_dict.items():
            new_lines.append(f"{k}={v}\n")
            
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except Exception as e:
            print(f"Error updating .env: {e}")

    def start_system(self):
        self.status_label.config(text="جاري بدء التشغيل... برجاء الانتظار", fg="#ca8a04")
        self.root.update()
        
        # Check if compose file exists
        if not os.path.exists(COMPOSE_FILE):
            messagebox.showerror("خطأ", f"لم يتم العثور على ملف الإعدادات:\n{COMPOSE_FILE}")
            self.check_status()
            return
            
        # Dynamically write / update .env before starting containers
        self.update_env()
        
        success, _, stderr = self.run_cmd(["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"])
        if success:
            messagebox.showinfo("نجاح", "تم تشغيل نظام العيادة بنجاح!")
            self.check_status()
            self.open_browser()
        else:
            messagebox.showerror("خطأ في التشغيل", f"فشل تشغيل الحاويات. تأكد من عمل Docker Desktop.\n\nتفاصيل الخطأ:\n{stderr}")
            self.check_status()

    def stop_system(self):
        self.status_label.config(text="جاري الإيقاف...", fg="#ca8a04")
        self.root.update()
        
        success, _, stderr = self.run_cmd(["docker", "compose", "-f", COMPOSE_FILE, "stop"])
        if success:
            messagebox.showinfo("نجاح", "تم إيقاف خادم العيادة بأمان.")
        else:
            messagebox.showerror("خطأ", f"فشل إيقاف الحاويات:\n{stderr}")
        self.check_status()

    def open_browser(self):
        webbrowser.open(f"http://{self.local_ip}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DentalPinLauncher(root)
    root.mainloop()
