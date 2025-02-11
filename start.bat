@echo off
REM Script để tự động activate môi trường Conda và chạy main.py

REM Kích hoạt Conda
CALL conda activate workflow

REM Chạy script Python
uvicorn api.main:app --port 5001 --reload

REM Giữ cửa sổ terminal mở sau khi hoàn thành
echo.
echo === Script đã chạy xong, nhấn phím bất kỳ để thoát ===
pause >nul
