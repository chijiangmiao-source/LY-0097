@echo off
echo ========================================
echo 体育器材管理系统 - 启动脚本
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2/3] 安装依赖...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo 警告: 依赖安装可能有问题，请手动检查
)

echo.
echo [3/3] 初始化数据库...
python scripts/init_db.py
if errorlevel 1 (
    echo 错误: 数据库初始化失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 启动服务...
echo 默认账号: admin / admin123
echo 访问地址: http://localhost:8000
echo ========================================
echo.

python main.py
pause
