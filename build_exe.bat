@echo off
REM ============================================================
REM Aistudio Chat to Markdown - PyInstaller 打包脚本
REM ============================================================

echo.
echo ============================================
echo   Aistudio 转 Markdown 打包工具
echo ============================================
echo.

REM 检查是否安装了 pyinstaller
if not exist "%USERPROFILE%\AppData\Roaming\Python\Python313\Scripts\pyinstaller.exe" (
    echo [1/5] 安装 PyInstaller...
    pip install pyinstaller
    echo.
)

REM 安装 tkinterdnd2 (支持拖放功能)
echo [2/5] 安装 tkinterdnd2 (拖放支持)...
pip install tkinterdnd2
echo.

REM 创建打包目录
if not exist "build_output" mkdir build_output

REM 清理旧的构建文件
echo [3/5] 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
del /q *.spec 2>nul
echo.

REM 执行打包
echo [4/5] 执行 PyInstaller 打包...
echo.
pyinstaller ^
    --name "Aistudio转Markdown工具" ^
    --onefile ^
    --windowed ^
    --icon "icon.ico" ^
    --add-data "aistudio_to_md_gui.py;." ^
    --clean ^
    --noconfirm ^
    aistudio_to_md_gui.py

echo.

REM 检查打包结果
echo [5/5] 检查打包结果...
if exist "dist\Aistudio转Markdown工具.exe" (
    echo.
    echo ============================================
    echo   ✅ 打包成功！
    echo ============================================
    echo.
    echo 输出文件: dist\Aistudio转Markdown工具.exe
    echo.
    echo 下次运行直接双击 EXE 文件即可！
    echo.
    pause
) else (
    echo.
    echo ============================================
    echo   ❌ 打包失败
    echo ============================================
    echo.
    echo 请检查上方错误信息并修复后重试
    echo.
    pause
)
