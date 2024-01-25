@REM Updates local git repository
c:
cd /d %~dp0
git fetch origin
git reset --hard origin/main
pause