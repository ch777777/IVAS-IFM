import tkinter as tk
from tkinter import messagebox

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("我的第一个EXE程序")
        self.root.geometry("400x300")
        
        # 创建标签和按钮
        self.label = tk.Label(root, text="欢迎使用我的应用程序!", font=("Arial", 14))
        self.label.pack(pady=20)
        
        self.button = tk.Button(root, text="点击我", command=self.show_message)
        self.button.pack(pady=10)
        
    def show_message(self):
        messagebox.showinfo("消息", "您点击了按钮！")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop() 