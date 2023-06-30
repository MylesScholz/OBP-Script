@REM Updates local git repository
c:
cd /d %~dp0
git reset --hard origin/main
git pull
pause