@echo off
echo 开始打包IFMCM应用程序...
echo.

:: 检查Python环境
python --version
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python，请确保已安装Python并添加到PATH环境变量
    exit /b 1
)

:: 检查是否需要更新版本
set UPDATE_VERSION=0
set VERSION=
set UPDATE_ARG=

if "%1"=="--version" (
    set UPDATE_VERSION=1
    set VERSION=%2
    set UPDATE_ARG=--version %2
)

:: 如果指定了版本，先更新版本信息
if %UPDATE_VERSION%==1 (
    echo 更新版本信息: %VERSION%
    python manage_versions.py %UPDATE_ARG%
    if %errorlevel% neq 0 (
        echo 错误: 版本更新失败
        exit /b 1
    )
    echo 版本已更新为 %VERSION%
    echo.
)

:: 安装依赖
echo 安装项目依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    exit /b 1
)

:: 创建assets目录和图标（如果不存在）
if not exist assets (
    echo 创建assets目录...
    mkdir assets
)

:: 如果图标不存在，则转换示例图标
if not exist assets\icon.ico (
    echo 警告: 未找到图标文件，将使用默认图标
)

:: 读取版本信息
for /f "tokens=2 delims==" %%a in ('findstr "VERSION =" src\config\settings.py') do (
    set APP_VERSION=%%a
)
set APP_VERSION=%APP_VERSION:"=%
set APP_VERSION=%APP_VERSION:'=%
set APP_VERSION=%APP_VERSION: =%

echo 应用版本: %APP_VERSION%

:: 打包应用
echo 正在使用PyInstaller打包应用...
pyinstaller --onefile ^
            --windowed ^
            --clean ^
            --name="IFMCM_%APP_VERSION%" ^
            --add-data="assets;assets" ^
            --icon=assets\icon.ico ^
            src\main.py

echo.
if %errorlevel% neq 0 (
    echo 打包过程中出现错误
) else (
    echo 打包完成! 可执行文件位于 dist 目录
    echo 文件名: IFMCM_%APP_VERSION%.exe
    echo.
    echo 提示: 首次运行可能会出现Windows安全警告，这是因为程序没有数字签名
)

pause 
 