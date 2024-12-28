import sys
from cx_Freeze import setup, Executable

# 构建可执行文件的选项配置
build_exe_options = {
    # 要包含的Python包列表，此处添加了'requests'包，你可根据项目实际依赖的其他包进行添加或修改
    # 例如，如果项目还依赖'numpy'、'pandas'等包，可将它们添加到此列表中，格式为 ["requests", "numpy", "pandas"]
    "packages": ["requests"],  
    # 要排除的包列表，当前为空，表示不排除任何包。若存在某些不需要打包进可执行文件的包，可将其名称添加在此处
    # 例如，若不想打包某个测试相关的包，可以写成 ["tests_package"]，注意是包的名称，不是文件名哦
    "excludes": [],  
    # 要包含的其他文件列表，若项目中有配置文件、数据文件等需要一起打包的内容，在此添加其路径等相关信息
    # 例如，如果有一个名为'config.ini'的配置文件在项目根目录下，可写成 ["config.ini"]，也可以使用相对路径指定其他目录下的文件
    "include_files": []  
}

# 根据不同操作系统设置基础参数，用于控制程序启动相关行为
base = None
# 判断当前操作系统是否为Windows系统（'win32'代表32位Windows，在64位Windows下也是使用这个标识）
if sys.platform == "win32":  
    # 将base设置为'Win32GUI'，这意味着程序会被当作图形用户界面（GUI）应用程序来启动
    # 在Windows系统下运行打包后的可执行文件时，默认就不会显示命令提示符窗口（黑框），达到隐藏黑框的效果
    base = "Win32GUI"  

# 使用setup函数进行项目配置和打包设置
setup(
    # 项目名称，可按照实际情况自行命名，建议取一个能清晰体现项目功能或特点的名字
    name="UI",  
    # 项目版本号，根据项目实际的版本情况填写，每次有功能更新、修复问题等版本迭代时进行相应修改
    version="1.0",  
    # 项目描述，简要说明项目的功能、用途或者一些重要特性，方便后续查看代码时能快速了解项目大概情况
    description="test",  
    # 指定构建可执行文件的选项，将前面配置好的build_exe_options传递进来，这样打包时就会按照这些配置进行操作
    options={"build_exe": build_exe_options},  
    # 指定可执行文件的入口点以及相关启动参数设置
    # 这里的'UI.py'是程序的主脚本，也就是程序从'UI.py'开始执行
    # base参数使用前面根据操作系统判断设置好的值，用于控制窗口显示情况，在Windows下将其设为'Win32GUI'可隐藏黑框
    executables=[Executable("UI.py", base=base)]  
)