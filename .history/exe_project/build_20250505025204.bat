@echo off
echo 开始打包EXE程序...
echo.

:: 检查Python环境
python --version
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python，请确保已安装Python并添加到PATH环境变量
    exit /b 1
)

:: 安装依赖
echo 安装项目依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    exit /b 1
)

:: 打包应用
echo 正在使用PyInstaller打包应用...
pyinstaller --onefile --windowed --clean --name="我的应用程序" src/main.py

echo.
if %errorlevel% neq 0 (
    echo 打包过程中出现错误
) else (
    echo 打包完成! 可执行文件位于 dist 目录
)

pause 