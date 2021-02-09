REM @echo off
:: %DATE:~4,10% %TIME%
echo %DATE:~4,10% %TIME% - Starting SendPlot.flask
echo %DATE:~4,10% %TIME% - Logging to log/access.log
title SendPlot.flask server running...
:RUNNING
echo %DATE:~4,10% %TIME% - Server running...
python WebServer\app.py
title SendPlot.flask server stopped!!!
echo %DATE:~4,10% %TIME% - Restarting
goto RUNNING
echo done
