@REM Run bash script from task scheduler
c:
cd /d %~dp0
python pull_and_format.py
pause