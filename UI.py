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

import requests
import os
import sys
from pyupdater.client import Client

APP_NAME = "UI"
APP_VERSION = "1.0"  # 初始版本号，需与实际发布版本一致

def check_for_updates():
    client = Client(APP_NAME, APP_VERSION, update_urls=['https://github.com/your_username/UIProgramRepo/releases'])
    update_info = client.update_check()
    if update_info is not None:
        print("有可用更新！")
        if update_info['status'] == 'available':
            client.download_update(update_info)
            print("更新下载完成。")
            # 以下代码用于在Windows系统下重新启动程序
            if sys.platform.startswith('win'):
                os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
            else:
                os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        print("没有可用更新。")

if __name__ == "__main__":
    check_for_updates()
    # 这里添加主程序的其他代码，如启动UI等
    # 假设你的UI启动代码在start_ui函数中
    # start_ui()