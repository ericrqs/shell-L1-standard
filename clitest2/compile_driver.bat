@echo off
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ok
) else (
    echo This program must be run from an administrator cmd prompt
    goto :fail
)

@echo on

pip install cloudshell-core

pyinstaller --onefile driver.spec

taskkill /f /im Clitest2.exe

timeout 3

set driverdir="c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers"
IF EXIST %driverdir% GOTO :havecs
set driverdir="c:\Program Files (x86)\QualiSystems\TestShell\Server\Drivers"
:havecs


copy dist\Clitest2.exe                     %driverdir%
copy clitest2_runtime_configuration.json %driverdir%



copy clitest2_datamodel.xml               release\
copy dist\Clitest2.exe                      release\
copy clitest2_runtime_configuration.json  release\

:fail
