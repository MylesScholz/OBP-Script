@REM Run Python script from task scheduler
c:
cd /d %~dp0
python pull_and_format.py
python merge.py