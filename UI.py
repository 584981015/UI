import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import webbrowser

root = tk.Tk()
root.title("我的第一个UI程序")
root.geometry("500x600")
root.resizable(False, False)

def show_message():
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
    webbrowser.get('edge').open("https://www.baidu.com")
    messagebox.showinfo("提示", "已经打开啦！")

style = ttk.Style(root)
# 配置按钮样式，设置边框宽度、边框颜色、背景颜色和内边距
style.configure('TButton', borderwidth=2, relief="solid", bordercolor="blue", background="lightgray",
                padding=(20, 10))  # (20, 10)表示水平方向内边距为20像素，垂直方向内边距为10像素


button = ttk.Button(root, text="打开百度", command=show_message)
button.place(x = 1, y = 1)
button.pack()



root.mainloop()