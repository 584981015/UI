import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import webbrowser
import requests
import os
import sys
import platform
import time
import psutil
from pyupdater.client import Client
import threading
import traceback
import datetime


# 模拟的白名单，实际应用中应从安全的数据源获取
WHITELIST = ["hwid123", "hwid456", "hwid789"]  

# 更新相关配置参数
GITHUB_REPO_OWNER = "584981015"
GITHUB_REPO_NAME = "UI"
UPDATE_URLS = [f'https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases']
APP_NAME = "UI"
APP_VERSION = "1.2.2"
UPDATE_CHECK_INTERVAL = 60
last_update_check_time = 0


def save_error_log(error_message, error_exception=None):
    log_folder = "logs"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    current_time = datetime.datetime.now().strftime("%Y-%m-d-%H-%M-%S")
    log_file_path = os.path.join(log_folder, f"update_error_{current_time}.log")
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"Error Time: {current_time}\n")
        log_file.write(f"Error Message: {error_message}\n")
        if error_exception:
            traceback_lines = traceback.format_exception(type(error_exception), error_exception, error_exception.__traceback__)
            log_file.write("Traceback:\n")
            log_file.write("".join(traceback_lines))


def get_machine_hwid():
    # 这里只是一个模拟的获取机器码的函数，实际应用中需要使用真实可靠的方法获取机器的唯一标识符
    return "hwid123"  


def check_for_updates():
    global last_update_check_time
    current_time = time.time()
    if current_time - last_update_check_time < UPDATE_CHECK_INTERVAL:
        messagebox.showinfo("更新检查", "距离上次检查时间过短，暂不进行更新检查。")
        return None
    try:
        config = {
            "APP_NAME": APP_NAME,
            "UPDATE_URLS": UPDATE_URLS
        }
        client = Client(config, refresh=True, progress_hooks=[])
        messagebox.showinfo("配置信息", f"Configured APP_NAME: {APP_NAME}\nConfigured UPDATE_URLS: {UPDATE_URLS}\nClient object created with config: {config}")

        response = client._http_get_request(UPDATE_URLS[0])
        if response is not None and response.status_code == 200:
            messagebox.showinfo("请求响应", "Successfully made request to the update server and got a valid response.")
            messagebox.showinfo("响应内容预览", f"Response content (partial preview): {response.text[:100]}")
        else:
            messagebox.showinfo("请求响应", f"Failed to get valid response from server. Status code: {response.status_code if response else 'None'}")

        update_info = client.update_check(APP_NAME, APP_VERSION)
        last_update_check_time = current_time
        current_time_str = time.strftime("%Y-%m-d %H:%M:%S", time.localtime())
        os_version = platform.platform()

        if update_info is None or'version' not in update_info:
            messagebox.showinfo("更新检查", f"未检测到更新或更新信息格式错误。\n当前时间：{current_time_str}\n当前版本：{APP_VERSION}\n操作系统：{os_version}")
            return None

        if update_info['version'] == APP_VERSION:
            messagebox.showinfo("更新检查", "未检测到更新。\n当前时间：{current_time_str}\n当前版本：{APP_NAME}\n操作系统：{os_version}")
        else:
            messagebox.showinfo("更新检查", "检测到更新，新版本号: {update_info['version']}\n当前时间：{current_time_str}\n当前版本：{APP_NAME}\n操作系统：{os_version}")
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
    update_info = check_for_updates()
    if update_info is not None:
        if update_info['version'] > APP_VERSION:
            result = messagebox.askyesno("更新提示", "有可用更新，是否下载？")
            if result:
                progress_window = tk.Toplevel(root)
                progress_window.title("更新下载")
                progress_bar = ttk.Progressbar(progress_window, mode='determinate', length=300)
                progress_bar.pack(pady=10)
                progress_window.protocol("WM_DELETE_WINDOW", lambda: None)

                def download_update_thread():
                    try:
                        config = {
                            "APP_NAME": APP_NAME,
                            "UPDATE_URLS": UPDATE_URLS
                        }
                        client = Client(config, refresh=True, progress_hooks=[])
                        client.download_update(update_info)
                        messagebox.showinfo("更新完成", "更新下载完成，程序将自动重启以应用更新。")
                        if sys.platform.startswith('win'):
                            restart_script_path = os.path.join(os.path.dirname(sys.executable), "restart.bat")
                            with open(restart_script_path, "w") as f:
                                f.write(f"@echo off\n{sys.executable} \"{os.path.abspath(__file__)}\"\n")
                            os.startfile(restart_script_path)
                            sys.exit(0)
                        else:
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


def verify_machine():
    hwid = get_machine_hwid()
    if hwid in WHITELIST:
        return True
    else:
        messagebox.showerror("错误", "此机器未授权，程序即将关闭！")
        root.destroy()
        return False


def start_program():
    # 先进行机器码验证，验证通过才继续显示界面其他功能
    if not verify_machine():
        sys.exit(0)

    root = tk.Tk()
    root.title("我的第一个UI程序")
    root.geometry("500x600")
    root.resizable(False, False)

    def show_message():
        webbrowser.open("https://www.baidu.com")
        messagebox.showinfo("提示", "已经打开啦！")

    def save_text_to_file():
        input_text = text_entry.get("1.0", tk.END).strip()
        if input_text:
            file_path = "保存内容.txt"
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(input_text)
                messagebox.showinfo("提示", "文本已成功保存到本地文件！")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时出现错误: {str(e)}")
        else:
            messagebox.showwarning("警告", "请先输入要保存的文本内容！")

    style = ttk.Style(root)
    style.configure('TButton', borderwidth=2, relief="solid", bordercolor="blue", background="lightgray",
                    padding=(20, 10))

    button = ttk.Button(root, text="打开百度", command=show_message)
    button.pack()

    text_entry = tk.Text(root, height=10, width=40)
    text_entry.pack(pady=20)

    save_button = ttk.Button(root, text="保存文本", command=save_text_to_file)
    save_button.pack()

    update_button = ttk.Button(root, text="检查更新", command=check_for_updates_button_click)
    update_button.pack()

    last_resource_check_time = 0
    RESOURCE_CHECK_INTERVAL = 10


    def show_system_resources():
        global last_resource_check_time
        current_time = time.time()
        if current_time - last_resource_check_time < RESOURCE_CHECK_INTERVAL:
            messagebox.showinfo("系统资源", "距离上次查询时间过短，暂不进行资源信息查询。")
            return
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=True)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_total = memory.total / (1024 ** 3)
        memory_used = memory.used / (1024 ** 3)
        memory_free = memory.free / (1024 ** 3)
        message = f"CPU使用率: {cpu_percent}%\n" \
                  f"CPU核心数: {cpu_count}个\n" \
                  f"内存使用率: {memory_percent}%\n" \
                  f"内存总量: {memory_total:.2f}GB\n" \
                  f"已使用内存: {memory_used:.2f}GB\n" \
                  f"空闲内存: {memory_free:.2f}GB"
        messagebox.showinfo("系统资源", message)
        last_resource_check_time = current_time


    resource_button = ttk.Button(root, text="显示系统资源", command=show_system_resources)
    resource_button.pack()

    def switch_theme():
        available_themes = ['clam', 'alt', 'default', 'classic']
        theme_choice_window = tk.Toplevel(root)
        theme_choice_window.title("选择主题")

        theme_listbox = tk.Listbox(theme_choice_window, selectmode=tk.SINGLE)
        for theme in available_themes:
            theme_listbox.insert(tk.END, theme)
        theme_listbox.pack()

        confirm_button = ttk.Button(theme_choice_window, text="确认",
                                    command=lambda: apply_selected_theme(theme_listbox.get(tk.ACTIVE), theme_choice_window))
        confirm_button.pack(pady=10)


    def apply_selected_theme(selected_theme, theme_choice_window):
        style.theme_use(selected_theme)
        messagebox.showinfo("主题切换", f"界面主题已切换为 {selected_theme}！")
        theme_choice_window.destroy()


    theme_button = ttk.Button(root, text="切换主题", command=switch_theme)
    theme_button.pack()

    def show_about_info():
        about_message = f"程序名称：{APP_NAME}\n" \
                        f"版本：{APP_VERSION}\n" \
                        f"作者：[WanAn]\n" \
                        f"版权所有：[WanAn]\n"
        messagebox.showinfo("关于", about_message)


    about_button = ttk.Button(root, text="关于", command=show_about_info)
    about_button.pack()

    root.mainloop()


if __name__ == "__main__":
    start_program()