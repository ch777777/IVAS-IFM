@echo off
echo 正在启动TikHub API服务...
python run_tikhub_api.py
if errorlevel 1 (
    echo 启动TikHub API服务失败！
    pause
) else (
    echo TikHub API服务已成功启动！
)
pause 