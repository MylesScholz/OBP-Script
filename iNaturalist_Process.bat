@REM Run bash script from task scheduler
c:
cd /d %~dp0

set /p input=Year to Query: 
bash -c "./iNaturalist_Process.bash --year %input%"
pause