import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import webbrowser
import requests
import os
import sys
import platform
import time
import psutil  # 用于获取系统资源信息
from pyupdater.client import Client

# 创建主窗口
root = tk.Tk()
root.title("我的第一个UI程序")
root.geometry("500x600")
root.resizable(False, False)

# 定义更新相关的配置变量，方便后续修改
UPDATE_URLS = ['https://github.com/584981015/UI/releases']
APP_NAME = "UI"
APP_VERSION = "1.2"  # 初始版本号，需与实际发布版本一致

# 创建全局的Client对象，避免重复创建
client = Client({"name": APP_NAME, "version": APP_VERSION}, update_urls=UPDATE_URLS)

# 定义打开网页并提示的函数，使用系统默认浏览器打开
def show_message():
    webbrowser.open("https://www.baidu.com")
    messagebox.showinfo("提示", "已经打开啦！")

# 新增功能：保存用户输入文本到本地文件的相关代码
def save_text_to_file():
    input_text = text_entry.get("1.0", tk.END).strip()  # 获取文本框中的文本内容
    if input_text:
        file_path = "保存内容.txt"  # 定义保存的文件名，可以根据需求修改路径和文件名
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
# 上次更新检查时间，初始化为0，用于控制更新检查频率
last_update_check_time = 0
# 定义更新检查的最小时间间隔（单位：秒），这里设置为60秒，可根据需求调整
UPDATE_CHECK_INTERVAL = 60


def check_for_updates():
    """
    检查程序是否有可用更新
    :return: 更新检查的结果信息（字典形式）或者None（如果检查出错）
    """
    global last_update_check_time
    current_time = time.time()
    # 判断距离上次更新检查是否超过设定的时间间隔
    if current_time - last_update_check_time < UPDATE_CHECK_INTERVAL:
        messagebox.showinfo("更新检查", "距离上次检查时间过短，暂不进行更新检查。")
        return None
    try:
        update_check_result = client.update_check(APP_NAME, APP_VERSION)  # 传入应用名称和版本号参数
        last_update_check_time = current_time
        current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        os_version = platform.platform()
        # 根据更新检查结果弹出相应提示框
        if update_check_result is None:
            messagebox.showinfo("更新检查", f"未检测到更新。\n当前时间：{current_time_str}\n当前版本：{APP_VERSION}\n操作系统：{os_version}")
        else:
            messagebox.showinfo("更新检查", f"检测到更新，状态: {update_check_result['status']}\n当前时间：{current_time_str}\n当前版：{APP_VERSION}\n操作系统：{os_version}")
        return update_check_result
    except requests.RequestException as e:
        messagebox.showerror("更新检查错误", f"网络连接出现问题，更新检查失败: {str(e)}")
    except ValueError as e:
        messagebox.showerror("更新检查错误", f"数据解析出现问题，更新检查失败: {str(e)}")
    except Exception as e:
        messagebox.showerror("更新检查错误", f"更新检查出现未知错误: {str(e)}")
    return None


def check_for_updates_button_click():
    """
    点击检查更新按钮后执行的函数，处理更新相关逻辑
    """
    update_check_result = check_for_updates()
    if update_check_result is not None:
        if update_check_result['status'] == 'available':
            # 弹出提示框询问用户是否下载更新
            result = messagebox.askyesno("更新提示", "有可用更新，是否下载？")
            if result:
                # 简单的进度提示示例，这里只是显示一个提示框，可以使用进度条组件完善
                messagebox.showinfo("更新下载", "正在下载更新，请稍候...")
                try:
                    client.download_update(update_check_result)
                    messagebox.showinfo("更新完成", "更新下载完成，程序将重新启动以应用更新。")
                    # 以下代码用于在Windows系统下重新启动程序
                    if sys.platform.startswith('win'):
                        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
                    else:
                        messagebox.showinfo("提示", "请手动重启程序以应用更新。")
                except requests.RequestException as e:
                    messagebox.showerror("更新下载错误", f"网络连接出现问题，更新下载失败: {str(e)}")
                except Exception as e:
                    messagebox.showerror("更新下载错误", f"更新下载出现未知错误: {str(e)}")
        else:
            # 当更新检查结果状态不是'available'时，可以在这里添加相应逻辑，目前暂时用pass占位
            pass


# 创建更新检查按钮
update_button = ttk.Button(root, text="检查更新", command=check_for_updates_button_click)
update_button.pack()

# 新增功能：显示更详细的系统资源信息（CPU和内存使用情况）
# 上次获取系统资源信息的时间，初始化为0
last_resource_check_time = 0
# 定义获取系统资源信息的最小时间间隔（单位：秒），这里设置为10秒，可根据需求调整
RESOURCE_CHECK_INTERVAL = 10


def show_system_resources():
    """
    显示系统当前的资源信息，包括CPU使用率、核心数以及内存使用情况等
    """
    global last_resource_check_time
    current_time = time.time()
    # 判断距离上次获取资源信息是否超过设定的时间间隔
    if current_time - last_resource_check_time < RESOURCE_CHECK_INTERVAL:
        messagebox.showinfo("系统资源", "距离上次查询时间过短，暂不进行资源信息查询。")
        return
    cpu_percent = psutil.cpu_percent(interval=1)  # 获取CPU使用率，间隔1秒
    cpu_count = psutil.cpu_count(logical=True)  # 获取CPU核心数（包含逻辑核心）
    memory = psutil.virtual_memory()
    memory_percent = memory.percent  # 获取内存使用率
    memory_total = memory.total / (1024 ** 3)  # 内存总量，转换为GB
    memory_used = memory.used / (1024 ** 3)  # 已使用内存量，转换为GB
    memory_free = memory.free / (1024 ** 3)  # 空闲内存量，转换为GB
    message = f"CPU使用率: {cpu_percent}%\n" \
              f"CPU核心数: {cpu_count}个\n" \
              f"内存使用率: {memory_percent}%\n" \
              f"内存总量: {memory_total:.2f}GB\n" \
              f"已使用内存: {memory_used:.2f}GB\n" \
              f"空闲内存: {memory_free:.2f}GB"
    messagebox.showinfo("系统资源", message)
    last_resource_check_time = current_time


# 创建显示系统资源信息的按钮并布局
resource_button = ttk.Button(root, text="显示系统资源", command=show_system_resources)
resource_button.pack()

# 新增功能：设置界面主题切换功能
def switch_theme():
    """
    切换界面主题，在亮色和暗色主题之间切换
    """
    current_style = style.theme_use()
    if current_style == 'clam':
        style.theme_use('alt')
    else:
        style.theme_use('clam')
    messagebox.showinfo("主题切换", "界面主题已切换！")


# 创建主题切换按钮
theme_button = ttk.Button(root, text="切换主题", command=switch_theme)
theme_button.pack()

# 新增功能：添加关于程序的信息展示窗口
def show_about_info():
    """
    展示关于程序的基本信息，如版本、作者、版权等
    """
    about_message = f"程序名称：{APP_NAME}\n" \
                    f"版本：{APP_VERSION}\n" \
                    f"作者：[晚安]\n" \
                    f"版权所有：[归晚安所有]\n"
    messagebox.showinfo("关于", about_message)


# 创建关于按钮
about_button = ttk.Button(root, text="关于", command=show_about_info)
about_button.pack()

if __name__ == "__main__":
    # 打印Python版本、操作系统、操作系统版本等环境相关信息
    print("Python 版本:", platform.python_version())
    print("操作系统:", platform.system())
    print("操作系统版本:", platform.release())
    root.mainloop()