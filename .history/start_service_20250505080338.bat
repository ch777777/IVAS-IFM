@echo off
cls
echo.
echo ===== IVAS-IFM 视频平台API集成服务 =====
echo.
echo 请选择要启动的服务:
echo.
echo [1] 启动原始API服务 (端口8000)
echo [2] 启动TikHub API服务 (端口8002)
echo [3] 退出
echo.

set /p choice=请输入选项 (1-3): 

if "%choice%"=="1" (
    cls
    echo 正在启动原始API服务...
    start cmd /k "python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"
    echo 原始API服务已启动，可通过 http://localhost:8000/docs 访问文档
    goto end
)

if "%choice%"=="2" (
    cls
    echo 正在启动TikHub API服务...
    start cmd /k "python run_tikhub_api.py"
    echo TikHub API服务已启动，可通过 http://localhost:8002/docs 访问文档
    goto end
)

if "%choice%"=="3" (
    exit
)

echo 无效选项，请重新运行
pause

:end
echo.
echo 服务已启动，按任意键返回主菜单...
pause
call %0 