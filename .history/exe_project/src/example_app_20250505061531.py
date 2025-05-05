"""
示例应用
"""
import customtkinter as ctk
from .components.custom_ctk_widgets import (
    StyledButton, StyledEntry, StyledLabel, FormFrame
)

class ExampleApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 配置窗口
        self.title("现代化UI示例")
        self.geometry("600x400")
        
        # 创建主容器
        self.main_frame = FormFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 添加标题
        self.title_label = StyledLabel(
            self.main_frame, 
            text="用户信息", 
            style="heading"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # 添加表单字段
        self.username_entry = self.main_frame.add_field("用户名:")
        self.email_entry = self.main_frame.add_field("邮箱:")
        self.role_entry = self.main_frame.add_field("角色:", readonly=True)
        self.role_entry.insert(0, "普通用户")
        
        # 添加按钮
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.save_button = StyledButton(
            self.button_frame,
            text="保存",
            command=self.save_clicked
        )
        self.save_button.pack(side="left", padx=10)
        
        self.cancel_button = StyledButton(
            self.button_frame,
            text="取消",
            style="secondary",
            command=self.cancel_clicked
        )
        self.cancel_button.pack(side="left", padx=10)
    
    def save_clicked(self):
        print("保存按钮被点击")
        print(f"用户名: {self.username_entry.get()}")
        print(f"邮箱: {self.email_entry.get()}")
        print(f"角色: {self.role_entry.get()}")
    
    def cancel_clicked(self):
        print("取消按钮被点击")
        self.username_entry.delete(0, "end")
        self.email_entry.delete(0, "end")

if __name__ == "__main__":
    app = ExampleApp()
    app.mainloop() 