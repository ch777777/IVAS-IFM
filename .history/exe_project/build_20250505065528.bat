@echo off
setlocal enabledelayedexpansion

REM Parse command line arguments
set VERSION=1.1.0
set OUTDIR=dist

:parse_args
if "%~1"=="" goto start
if /i "%~1"=="--version" (
    set VERSION=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--outdir" (
    set OUTDIR=%~2
    shift
    shift
    goto parse_args
)
echo Unknown argument: %~1
shift
goto parse_args

:start
echo Building IVAS-IFM version %VERSION%...

REM Create output directory if it doesn't exist
if not exist %OUTDIR% mkdir %OUTDIR%

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Create logs folder if it doesn't exist
if not exist logs mkdir logs

REM Create build timestamp
set TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

REM Update version number in config
echo Updating version number...
python src/utils/update_version.py --version %VERSION%

REM Run PyInstaller
echo Packaging application...
pyinstaller ^
    --name="IVAS-IFM-%VERSION%" ^
    --windowed ^
    --icon=assets/icon.ico ^
    --add-data="assets;assets" ^
    --add-data="src;src" ^
    --clean ^
    --noconfirm ^
    src/main.py

REM Copy important files to dist folder
echo Copying additional files...
copy README.md %OUTDIR%\
copy requirements.txt %OUTDIR%\
if not exist %OUTDIR%\logs mkdir %OUTDIR%\logs

echo Build complete. Output: %OUTDIR%\IVAS-IFM-%VERSION%.exe

endlocal 
 
 