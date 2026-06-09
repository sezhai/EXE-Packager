import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import sys

class ExeBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 转换为 EXE 打包工具")
        self.root.resizable(False, False)

        # === 窗口居中计算逻辑 ===
        window_width = 600
        window_height = 450
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # =========================

        padding = {'padx': 10, 'pady': 5}

        # --- 第一行：选择 Python 文件 ---
        tk.Label(root, text="Python 文件 (.py):").grid(row=0, column=0, sticky="e", **padding)
        self.py_path_var = tk.StringVar()
        tk.Entry(root, textvariable=self.py_path_var, width=50).grid(row=0, column=1, **padding)
        tk.Button(root, text="浏览...", command=self.browse_py).grid(row=0, column=2, **padding)

        # --- 第二行：选择 图标 文件 ---
        tk.Label(root, text="图标文件 (.ico) [可选]:").grid(row=1, column=0, sticky="e", **padding)
        self.ico_path_var = tk.StringVar()
        tk.Entry(root, textvariable=self.ico_path_var, width=50).grid(row=1, column=1, **padding)
        tk.Button(root, text="浏览...", command=self.browse_ico).grid(row=1, column=2, **padding)

        # --- 第三行：打包选项 ---
        options_frame = tk.Frame(root)
        options_frame.grid(row=2, column=0, columnspan=3, **padding)
        
        self.onefile_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="打包为单文件 (-F)", variable=self.onefile_var).pack(side="left", padx=10)
        
        self.noconsole_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="隐藏控制台黑框 (-w)", variable=self.noconsole_var).pack(side="left", padx=10)

        # --- 第四行：生成按钮 ---
        self.build_btn = tk.Button(root, text="🚀 开始生成 EXE", bg="#4CAF50", fg="white", font=("Microsoft YaHei", 12, "bold"), command=self.start_build)
        self.build_btn.grid(row=3, column=0, columnspan=3, pady=15)

        # --- 第五行：日志输出窗口 ---
        tk.Label(root, text="打包日志:").grid(row=4, column=0, sticky="w", padx=10)
        self.log_text = tk.Text(root, height=12, width=80, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
        self.log_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

    def browse_py(self):
        filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if filepath:
            self.py_path_var.set(filepath)

    def browse_ico(self):
        filepath = filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico")])
        if filepath:
            self.ico_path_var.set(filepath)

    def log(self, message):
        """将信息安全地插入到日志窗口，并滚动到底部"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_build(self):
        py_file = self.py_path_var.get()
        if not py_file or not os.path.exists(py_file):
            messagebox.showerror("错误", "请先选择有效的 Python (.py) 文件！")
            return

        self.build_btn.config(state=tk.DISABLED, text="打包中，请稍候...")
        self.log_text.delete(1.0, tk.END)
        self.log("开始准备打包...")

        threading.Thread(target=self.run_pyinstaller, args=(py_file,), daemon=True).start()

    def run_pyinstaller(self, py_file):
        cmd = ["pyinstaller", "-y"]

        if self.onefile_var.get():
            cmd.append("-F")
        if self.noconsole_var.get():
            cmd.append("-w")
            
        ico_file = self.ico_path_var.get()
        if ico_file and os.path.exists(ico_file):
            cmd.extend(["-i", ico_file])

        cmd.append(py_file)
        
        self.log(f"执行命令: {' '.join(cmd)}")
        self.log("-" * 50)

        try:
            # 这里的 CREATE_NO_WINDOW 将 PyInstaller 彻底关进黑箱，绝不弹窗
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # 强制将错误流合并到标准流，统一被我们的文本框捕获
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            # 实时读取日志并显示到 UI
            for line in process.stdout:
                self.root.after(0, self.log, line.strip())

            process.wait()

            if process.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo("成功", "打包完成！请在目标脚本所在目录的 dist 文件夹中查看。"))
            else:
                self.root.after(0, lambda: messagebox.showerror("失败", "打包过程中发生错误，请查看上方日志排查。"))

        except FileNotFoundError:
            self.root.after(0, lambda: messagebox.showerror("未找到 PyInstaller", "当前系统未安装 PyInstaller。请先在命令行执行 pip install pyinstaller"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("异常", f"发生未知错误: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.build_btn.config(state=tk.NORMAL, text="🚀 开始生成 EXE"))

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # 隐藏初始幽灵窗口
    app = ExeBuilderApp(root)
    root.deiconify() # 界面准备就绪后显形
    root.mainloop()