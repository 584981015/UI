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
import threading  # 用于在单独线程中执行更新下载，避免阻塞UI线程
import traceback
import datetime

# 更新相关配置参数（可以考虑移到配置文件中统一管理，此处为示例方便暂放在代码里）
GITHUB_REPO_OWNER = "584981015"  # GitHub仓库拥有者
GITHUB_REPO_NAME = "UI"  # GitHub仓库名
UPDATE_URLS = [f'https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases']
APP_NAME = "UI"
APP_VERSION = "1.2"  # 初始版本号，需与实际发布版本一致
UPDATE_CHECK_INTERVAL = 60  # 更新检查的最小时间间隔（单位：秒）

# 上次更新检查时间，初始化为0，用于控制更新检查频率
last_update_check_time = 0

# 保存错误日志的函数
def save_error_log(error_message, error_exception=None):
    """
    保存错误日志到文件，包含错误信息、时间、堆栈跟踪（如果有异常）
    :param error_message: 错误描述信息
    :param error_exception: 捕获的异常对象（可选）
    """
    log_folder = "logs"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_file_path = os.path.join(log_folder, f"update_error_{current_time}.log")
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"Error Time: {current_time}\n")
        log_file.write(f"Error Message: {error_message}\n")
        if error_exception:
            # 修改此处按照正确的参数传递方式调用format_exception函数
            traceback_lines = traceback.format_exception(type(error_exception), error_exception, error_exception.__traceback__)
            log_file.write("Traceback:\n")
            log_file.write("".join(traceback_lines))


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
        # 创建配置字典
        config = {
            "APP_NAME": APP_NAME,
            "UPDATE_URLS": UPDATE_URLS
        }
        client = Client(config, refresh=True, progress_hooks=[])
        update_info = client.update_check(APP_NAME, APP_VERSION)  # 传入应用名称和版本号参数
        last_update_check_time = current_time
        current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        os_version = platform.platform()

        # 验证更新信息格式，确保包含'version'字段（可根据pyupdater实际返回结构调整）
        if update_info is None or'version' not in update_info:
            messagebox.showinfo("更新检查", f"未检测到更新或更新信息格式错误。\n当前时间：{current_time_str}\n当前版本：{APP_VERSION}\n操作系统：{os_version}")
            return None

        # 根据更新检查结果弹出相应提示框
        if update_info['version'] == APP_VERSION:
            messagebox.showinfo("更新检查", f"未检测到更新。\n当前时间：{current_time_str}\n当前版本：{APP_NAME}\n操作系统：{os_version}")
        else:
            messagebox.showinfo("更新检查", f"检测到更新，新版本号: {update_info['version']}\n当前时间：{current_time_str}\n当前版本：{APP_NAME}\n操作系统：{os_version}")
        return update_info
    except requests.RequestException as e:
        save_error_log(f"更新检查时网络请求出错: {str(e)}", e)
        if hasattr(e,'response') and e.response is not None:
            status_code = e.response.status_code
            if status_code == 404:
                messagebox.showerror("更新检查错误", "更新检查失败，找不到对应的更新资源，请检查配置。")
            elif status_code == 500:
                messagebox.showerror("更新检查错误", "更新检查失败，服务器内部出现错误，请稍后再试。")
            else:
                messagebox.showerror("更新检查错误", f"网络连接出现问题，更新检查失败，状态码: {status_code}")
        else:
            messagebox.showerror("更新检查错误", f"网络连接出现问题，更新检查失败: {str(e)}")
    except ValueError as e:
        save_error_log(f"更新检查时数据解析出错: {str(e)}", e)
        messagebox.showerror("更新检查错误", f"数据解析出现问题，更新检查失败: {str(e)}")
    except Exception as e:
        save_error_log(f"更新检查时未知错误: {str(e)}", e)
        messagebox.showerror("更新检查错误", f"更新检查出现未知错误: {str(e)}")
    return None


def check_for_updates_button_click():
    """
    点击检查更新按钮后执行的函数，处理更新相关逻辑
    """
    update_info = check_for_updates()
    if update_info is not None:
        if update_info['version'] > APP_VERSION:
            # 弹出提示框询问用户是否下载更新
            result = messagebox.askyesno("更新提示", "有可用更新，是否下载？")
            if result:
                # 创建进度条对话框显示更新下载进度
                progress_window = tk.Toplevel(root)
                progress_window.title("更新下载")
                progress_bar = ttk.Progressbar(progress_window, mode='determinate', length=300)
                progress_bar.pack(pady=10)
                progress_window.protocol("WM_DELETE_WINDOW", lambda: None)  # 禁止关闭窗口

                def download_update_thread():
                    """
                    在单独线程中执行更新下载任务，并更新进度条
                    """
                    try:
                        # 创建配置字典
                        config = {
                            "APP_NAME": APP_NAME,
                            "UPDATE_URLS": UPDATE_URLS
                        }
                        client = Client(config, refresh=True, progress_hooks=[])
                        client.download_update(update_info)
                        messagebox.showinfo("更新完成", "更新下载完成，程序将自动重启以应用更新。")
                        # 以下代码用于在Windows系统下重新启动程序（这里使用更通用的方式，通过脚本重新启动）
                        if sys.platform.startswith('win'):
                            restart_script_path = os.path.join(os.path.dirname(sys.executable), "restart.bat")
                            with open(restart_script_path, "w") as f:
                                f.write(f"@echo off\n{sys.executable} \"{os.path.abspath(__file__)}\"\n")
                            os.startfile(restart_script_path)
                            sys.exit(0)
                        else:
                            # 对于其他系统，提示用户手动重启（可根据实际情况完善更自动化的重启方式）
                            messagebox.showinfo("提示", "请手动重启程序以应用更新。")
                        progress_window.destroy()
                    except requests.RequestException as e:
                        save_error_log(f"更新下载时网络请求出错: {str(e)}", e)
                        messagebox.showerror("更新下载错误", f"网络连接出现问题，更新下载失败: {str(e)}")
                        progress_window.destroy()
                    except Exception as e:
                        save_error_log(f"更新下载时未知错误: {str(e)}", e)
                        messagebox.showerror("更新下载错误", f"更新下载出现未知错误: {str(e)}")
                        progress_window.destroy()

                download_thread = threading.Thread(target=download_update_thread)
                download_thread.start()


# 创建主窗口
root = tk.Tk()
root.title("我的第一个UI程序")
root.geometry("500x600")
root.resizable(False, False)

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

# 创建更新检查按钮
update_button = ttk.Button(root, text="检查更新", command=check_for_updates_button_click)
update_button.pack()

# 新增功能：显示更详细的系统资源信息（CPU和内存使用情况）
# 上次获取系统资源信息的时间，初始化为0
last_resource_check_time = 0
RESOURCE_CHECK_INTERVAL = 10  # 定义获取系统资源信息的最小时间间隔（单位：秒）


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
    memory_used = memory.used / (1024 ** 3)  # 已使用内存量，转换 to GB
    memory_free = memory.free / (1024 ** 3)  # 空闲内存量，转换 to GB
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

# 新增功能：设置界面主题切换功能，改为弹出列表供用户手动选择主题
def switch_theme():
    """
    切换界面主题，弹出主题列表供用户选择
    """
    # 定义可用的主题列表，这里列举了一些常见的tkinter主题，可根据实际需求添加或修改
    available_themes = ['clam', 'alt', 'default', 'classic']
    # 创建一个顶层窗口用于显示主题选择列表
    theme_choice_window = tk.Toplevel(root)
    theme_choice_window.title("选择主题")

    # 创建列表框用于展示主题选项
    theme_listbox = tk.Listbox(theme_choice_window, selectmode=tk.SINGLE)
    for theme in available_themes:
        theme_listbox.insert(tk.END, theme)
    theme_listbox.pack()

    # 创建确认按钮，点击后应用所选主题
    confirm_button = ttk.Button(theme_choice_window, text="确认",
                                command=lambda: apply_selected_theme(theme_listbox.get(tk.ACTIVE), theme_choice_window))
    confirm_button.pack(pady=10)


def apply_selected_theme(selected_theme, theme_choice_window):
    """
    根据用户选择的主题应用到界面
    :param selected_theme: 用户选择的主题名称
    :param theme_choice_window: 主题选择窗口，用于关闭窗口
    """
    style.theme_use(selected_theme)
    messagebox.showinfo("主题切换", f"界面主题已切换为 {selected_theme}！")
    theme_choice_window.destroy()


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
                    f"作者：[你的名字]\n" \
                    f"版权所有：[版权信息]\n"
    messagebox.showinfo("关于", about_message)


# 创建关于按钮
about_button = ttk.Button(root, text="关于", command=show_about_info)
about_button.pack()

if __name__ == "__main__":
    root.mainloop()