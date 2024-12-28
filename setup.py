import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["cffi"],  # 将'cffi'添加到要包含的包列表中
    "includes": ["nacl.bindings", "nacl.sodium"],  # 添加可能相关的其他依赖模块
    "excludes": [],
    "include_files": [],
}

setup(
    name="UI",
    version="1.2",
    description="test",
    options={"build_exe": build_exe_options},
    executables=[Executable("UI.py")]
)