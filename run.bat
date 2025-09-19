@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Image Resizing System...
python main.py

pause

