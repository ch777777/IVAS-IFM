@echo off
echo IVAS-IFM 智能视频采集与分析系统
echo ==================================
echo 正在启动系统...

python run.py

if %errorlevel% neq 0 (
    echo 启动失败，请查看日志文件。
    echo 请确保已安装所需的依赖包。
    echo 如果问题仍然存在，请运行 run_fix.bat 修复系统。
    pause
) 