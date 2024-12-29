import setuptools
import pyupdater

APP_NAME = 'UI'
APP_VERSION = 1.2.1'

setuptools.setup(
    name=APP_NAME,
    version=APP_VERSION,
    description='test',
    author='WanAn',
    author_email='584981015@qq.com',
    url='https://github.com/584981015/UI',
    packages=setuptools.find_packages(),
    install_requires=[
        'pyupdater',
        # 其他依赖项
    ],
    entry_points={
        'console_scripts': [
            'your_app_name = your_package_name.main:main',
        ],
    },
    classifiers=[
        # 分类信息，可根据实际情况填写
    ],
    cmdclass={
        'pyupdater': pyupdater.PyUpdaterCommand,
    },
)