@echo off

set scriptsPath=./env/Scripts/

IF %1.==. GOTO activate 
IF %1==-a GOTO activate 
IF %1==-d GOTO deactivate

:activate
%scriptsPath%activate

:deactivate
%scriptsPath%deactivate 

exit /B 0