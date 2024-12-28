import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import webbrowser
import requests
import os
import sys
from pyupdater.client import Client

# 创建主窗口
root = tk.Tk()
root.title("我的第一个UI程序")
root.geometry("500x600")
root.resizable(False, False)

# 定义打开网页并提示的函数
def show_message():
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
    webbrowser.get('edge').open("https://www.baidu.com")
    messagebox.showinfo("提示", "已经打开啦！")

# 新增功能：保存用户输入文本到本地文件的相关代码
def save_text_to_file():
    input_text = text_entry.get("1.0", tk.END).strip()  # 获取文本框中的文本内容
    if input_text:
        file_path = "user_input.txt"  # 定义保存的文件名，可以根据需求修改路径和文件名
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(input_text)
            messagebox.showinfo("提示", "文本已成功保存到本地文件！")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件时出现错误: {str(e)}")
    else:
        messagebox.showwarning("警告", "请先输入要保存的文本内容！")

# 配置按钮样式，设置边框宽度、边框颜色、背景颜色和内边距
style = ttk.Style(root)
style.configure('TButton', borderwidth=2, relief="solid", bordercolor="blue", background="lightgray",
                padding=(20, 10))  # (20, 10)表示水平方向内边距为20像素，垂直方向内边距为10像素

# 创建打开百度的按钮并布局
button = ttk.Button(root, text="打开百度", command=show_message)
button.pack()

# 创建文本输入框
text_entry = tk.Text(root, height=10, width=40)
text_entry.pack(pady=20)

# 创建保存文本的按钮
save_button = ttk.Button(root, text="保存文本", command=save_text_to_file)
save_button.pack()

# 以下是用于程序更新检查的代码
APP_NAME = "UI"
APP_VERSION = "1.1"  # 初始版本号，需与实际发布版本一致

def check_for_updates():
    app_config = {
        "name": APP_NAME,
        "version": APP_VERSION,
    }
    print("开始执行 check_for_updates 函数...")
    try:
        client = Client(app_config, update_urls=['https://github.com/584981015/UI/releases'])
        update_info = client.update_check(APP_NAME, APP_VERSION)  # 传入应用名称和版本号参数
        print("完成 update_check 操作，返回结果:", update_info)
        return update_info
    except Exception as e:
        print(f"更新检查出现错误: {str(e)}")
        return None


def check_for_updates_button_click():
    print("点击了检查更新按钮，开始 check_for_updates_button_click 函数执行...")
    update_info = check_for_updates()
    if update_info is not None:
        print("有更新信息返回，进行后续判断...")
        if update_info['status'] == 'available':
            # 弹出提示框询问用户是否下载更新
            result = messagebox.askyesno("更新提示", "有可用更新，是否下载？")
            if result:
                client = Client(app_config, update_urls=['https://github.com/584981015/UI/releases'])
                client.download_update(update_info)
                print("更新下载完成。")
                # 以下代码用于在Windows系统下重新启动程序
                if sys.platform.startswith('win'):
                    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
                else:
                    os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            messagebox.showinfo("提示", "没有可用更新。")
            os.execv(sys.executable, [sys.executable] + sys.argv)


# 创建更新检查按钮
update_button = ttk.Button(root, text="检查更新", command=check_for_updates_button_click)
update_button.pack()

if __name__ == "__main__":
    root.mainloop()