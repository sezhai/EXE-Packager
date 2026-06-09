import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys

# 引入 PyInstaller 核心运行模块，成为“母体”
import PyInstaller.__main__

class ExeBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("独立 EXE 终极打包器 (内置引擎版)")
        self.root.resizable(False, False)

        # === 窗口居中计算逻辑 ===
        window_width = 600
        window_height = 220 # 去除日志框后，高度大幅缩小
        
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # =========================

        padding = {'padx': 10, 'pady': 10}

        # --- 第一行：选择 Python 文件 ---
        tk.Label(root, text="Python 文件 (.py/.pyw):").grid(row=0, column=0, sticky="e", **padding)
        self.py_path_var = tk.StringVar()
        tk.Entry(root, textvariable=self.py_path_var, width=50).grid(row=0, column=1, pady=10)
        tk.Button(root, text="浏览...", command=self.browse_py).grid(row=0, column=2, padx=10)

        # --- 第二行：选择 图标 文件 ---
        tk.Label(root, text="图标文件 (.ico) [可选]:").grid(row=1, column=0, sticky="e", **padding)
        self.ico_path_var = tk.StringVar()
        tk.Entry(root, textvariable=self.ico_path_var, width=50).grid(row=1, column=1)
        tk.Button(root, text="浏览...", command=self.browse_ico).grid(row=1, column=2, padx=10)

        # --- 第三行：打包选项 ---
        options_frame = tk.Frame(root)
        options_frame.grid(row=2, column=0, columnspan=3, pady=(15, 5))
        
        self.onefile_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="打包为单文件 (-F)", variable=self.onefile_var).pack(side="left", padx=20)
        
        self.noconsole_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="隐藏控制台黑框 (-w)", variable=self.noconsole_var).pack(side="left", padx=20)

        # --- 第四行：生成按钮 ---
        self.build_btn = tk.Button(root, text="🚀 启动内置引擎打包", bg="#4CAF50", fg="white", font=("Microsoft YaHei", 12, "bold"), command=self.start_build)
        self.build_btn.grid(row=3, column=0, columnspan=3, pady=15)

    def browse_py(self):
        # 💡 这里允许同时筛选出 .py 和 .pyw 文件
        filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py *.pyw"), ("All Files", "*.*")])
        if filepath:
            self.py_path_var.set(filepath)

    def browse_ico(self):
        filepath = filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico"), ("All Files", "*.*")])
        if filepath:
            self.ico_path_var.set(filepath)

    def start_build(self):
        py_file = self.py_path_var.get()
        if not py_file or not os.path.exists(py_file):
            messagebox.showerror("错误", "请先选择有效的 Python 脚本文件！")
            return

        self.build_btn.config(state=tk.DISABLED, text="引擎运转中，请查看弹出的控制台窗口...")

        # 放入子线程运行，防止界面假死
        threading.Thread(target=self.run_pyinstaller_internal, args=(py_file,), daemon=True).start()

    def run_pyinstaller_internal(self, py_file):
        # 构建参数列表
        cmd_args = ["-y"]

        if self.onefile_var.get():
            cmd_args.append("-F")
        if self.noconsole_var.get():
            cmd_args.append("-w")
            
        ico_file = self.ico_path_var.get()
        if ico_file and os.path.exists(ico_file):
            cmd_args.extend(["-i", ico_file])

        cmd_args.append(py_file)

        try:
            # 🔥 直接调用 PyInstaller 核心 API 进行打包
            PyInstaller.__main__.run(cmd_args)
            
            # 如果没有触发退出异常，说明正常完成
            self.root.after(0, lambda: messagebox.showinfo("成功", "打包完成！\n请在目标脚本所在目录的 dist 文件夹中查看。"))
            
        except SystemExit as e:
            if e.code == 0 or e.code is None or str(e) == '0':
                self.root.after(0, lambda: messagebox.showinfo("成功", "打包完成！\n请在目标脚本所在目录的 dist 文件夹中查看。"))
            else:
                self.root.after(0, lambda: messagebox.showerror("失败", f"打包失败，退出码: {e.code}\n可能出现了语法错误或缺少核心依赖。"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("异常", f"发生未知内部错误: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.build_btn.config(state=tk.NORMAL, text="🚀 启动内置引擎打包"))

if __name__ == "__main__":
    root = tk.Tk()
    
    # 消除界面闪烁的障眼法
    root.withdraw() 
    app = ExeBuilderApp(root)
    root.deiconify() 
    
    root.mainloop()
