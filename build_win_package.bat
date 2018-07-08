@echo off

set BIN_NAME=sqlitebiter

pip install --upgrade pip
pip install --upgrade .[build]

echo "----- start build -----"
pyinstaller cli.py --onefile --name %BIN_NAME% --clean --noconfirm --specpath build
echo "----- complete build -----"

echo "----- start compress -----"
set DIST_DIR_NAME=dist
set BIN_PATH=%DIST_DIR_NAME%/%BIN_NAME%.exe
set ARCHIVE_PATH=%DIST_DIR_NAME%/%BIN_NAME%_win_x64.zip

echo %ARCHIVE_PATH%
powershell compress-archive -Force %BIN_PATH% %ARCHIVE_PATH%
echo "----- complete compress -----"
