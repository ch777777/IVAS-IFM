@echo off
echo 开始测试TikHub API...

echo.
echo === 测试选项 ===
echo 1. 测试所有端点
echo 2. 测试基本端点
echo 3. 测试抖音视频
echo 4. 测试TikTok视频
echo 5. 测试小红书笔记
echo 6. 测试混合解析端点
echo 7. 直接测试TikHub原始API
echo.

set /p choice=请选择测试选项 (1-7): 

if "%choice%"=="1" (
    python test_all_endpoints.py --all
) else if "%choice%"=="2" (
    python test_all_endpoints.py --basic
) else if "%choice%"=="3" (
    python test_all_endpoints.py --douyin
) else if "%choice%"=="4" (
    python test_all_endpoints.py --tiktok
) else if "%choice%"=="5" (
    python test_all_endpoints.py --xiaohongshu
) else if "%choice%"=="6" (
    python test_all_endpoints.py --hybrid
) else if "%choice%"=="7" (
    python test_direct_api.py
) else (
    echo 无效选项，默认测试所有端点
    python test_all_endpoints.py --all
)

pause 