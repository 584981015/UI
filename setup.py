from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 对于有UI的Windows程序，设置base为Win32GUI以隐藏控制台

setup(
    name="YourProgramName",  # 程序名称，可以自定义
    version="1.0",  # 程序版本号
    description="uiTest",  # 程序的简单描述
    executables=[Executable("UI.py", base=base)]
)